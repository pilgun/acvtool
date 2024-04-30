import os
import shutil
import subprocess
import re
import threading
import signal
import logging
import time, sched
import multiprocessing
from .config import config
from .granularity import Granularity
from .entities.wd import WorkingDirectory
from .instrumenting import manifest_instrumenter
from .instrumenting import apktool
from .instrumenting.smali_instrumenter import Instrumenter
from .instrumenting.utils import timeit
from .instrumenting.utils import Utils
from .instrumenting.acv_classes import AcvInstrumentation
from .instrumenting.apkil.smalitree import SmaliTree
from .instrumenting.acv_classes import AcvStoring
from .instrumenting.acv_classes import AcvCalculator
from .instrumenting.acv_classes import AcvFlushing
from .instrumenting.acv_classes import AcvReporter
from .operations import terminal
from .operations import adb

apk_info_pattern = re.compile("package: name='(?P<package>.*?)'")


CRASH_REPORT_FILENAME = "errors.txt"

def install(new_apk_path):
    logging.info("installing {}".format(os.path.basename(new_apk_path)))
    cmd = '{} install -r --no-incremental "{}"'.format(config.adb_path, new_apk_path)
    out = terminal.request_pipe(cmd)
    
    logging.info(out)


def install_multiple(apks):
    logging.info("installing multiple...")
    def run():
        cmd = "adb install-multiple -r --no-incremental {}".format(" ".join(apks))
        out = terminal.request_pipe(cmd)
        logging.info(out)
    p = multiprocessing.Process(target=run)
    p.start()
    p.join(120)
    alive = p.is_alive()
    if alive:
        logging.info("could not install in time")
        p.terminate()
        install_multiple(apks)


def uninstall(package):
    logging.info("uninstalling")
    cmd = '{} uninstall "{}"'.format(config.adb_path, package)
    out = terminal.request_pipe(cmd)

    logging.info(out)

def request_pipe(cmd):
    terminal.request_pipe(cmd)

def get_apk_properties(path):
    info_cmd = "{} dump badging {}".format(config.aapt_path, path)
    out = terminal.request_pipe(info_cmd)

    matched = re.match(apk_info_pattern, out)
    package_name = matched.group('package')
    
    return apkinfo(package_name, "", "")


def get_package_files_list(package_name):
    cmd = '{} shell ls "/sdcard/Download/{}/"'.format(config.adb_path, package_name)
    out = terminal.request_pipe(cmd)
    files = [f for f in out.split() if not f.endswith('/')]
    return files  

def get_execution_results(package_name, ec_dir, images_dir):
    result_files = get_package_files_list(package_name)
    coverage_files = [f for f in result_files if f.endswith(".ec")]
    images_files = [f for f in result_files if f.endswith(".png")]
    crash_file = CRASH_REPORT_FILENAME if CRASH_REPORT_FILENAME in result_files else None

    if not (coverage_files or crash_file):
        raise Exception("No coverage or crash report files have been detected on the device for {} package.\n\
        Run acvtool with \'-start\' argument to produce coverage.".format(package_name))
    
    if not os.path.isdir(ec_dir):
        Utils.recreate_dir(ec_dir)
    # Utils.recreate_dir(images_dir)
    
    pull_files(ec_dir, coverage_files, package_name)
    pull_files(images_dir, images_files, package_name)
    if crash_file:
        pull_files(ec_dir, [crash_file], package_name)


def pull_files(dir_name, file_list, package_name):
    for f in file_list:
        adb_pull(package_name, f, dir_name)
        adb_delete_files(package_name, f)


def adb_pull(package_name, file_path, pull_to):
    cmd = "{} pull /sdcard/Download/{}/{} {}".format(config.adb_path, package_name, file_path, os.path.abspath(pull_to))
    out = terminal.request_pipe(cmd)
    logging.info(out)


def adb_delete_files(package_name, file_name):
    cmd = "{} shell rm /sdcard/Download/{}/{}".format(config.adb_path, package_name, file_name)
    out = terminal.request_pipe(cmd)


def grant_storage_permission(package):
    read_storage_cmd = "{0} shell pm grant {1} android.permission.READ_EXTERNAL_STORAGE".format(config.adb_path, package)
    subprocess.call(read_storage_cmd, shell=True)

    write_storage_cmd = "{0} shell pm grant {1} android.permission.WRITE_EXTERNAL_STORAGE".format(config.adb_path, package)
    subprocess.call(write_storage_cmd, shell=True)


def activate(package):
    grant_storage_permission(package)
    adb.create_app_sdcard_dir(package)


def start_instrumenting(package, release_thread=False, onstop=None, timeout=None):
    grant_storage_permission(package)
    lock_thread = "" if release_thread else "-w"
    cmd = '{} shell am instrument {} {}/{}'.format(config.adb_path, lock_thread, package, config.INSTRUMENTING_NAME)
    if release_thread:
        os.system(cmd)
        locked = sdcard_path_exists(package) # dir is created, service started # to be change to another lock file on start
        timeout = config.default_onstop_timeout if timeout is None else timeout
        while not locked and timeout:
            time.sleep(1)
            logging.info("wait for coverage service activation {}".format(package))
            locked = sdcard_path_exists(package)
            timeout -= 1
        if not locked:
            raise Exception("Coverage service did not start in time ({})".format(package))
        return
    out = ''
    def run():
        out = terminal.request_pipe(cmd)
        logging.info(out)
        
    original_sigint = signal.getsignal(signal.SIGINT)
    
    def stop(signum, frame):
        signal.signal(signal.SIGINT, original_sigint)
        stop_instrumenting(package, timeout)
        if onstop:
            onstop()

    t = threading.Thread(target=run)
    t.start()
    
    print("Press Ctrl+C to finish ...")
    signal.signal(signal.SIGINT, stop)


def sdcard_path_exists(path):
    cmd = "{} shell \"test -e /sdcard/Download/{} > /dev/null 2>&1 && echo \'1\' || echo \'0\'\"".format(config.adb_path, path)
    logging.debug('Command to check lock file:' + cmd)
    locked = subprocess.check_output(cmd, shell=True).replace("\n","").replace("\r", "")
    return locked == '1'


def coverage_is_locked(package_name):
    lock_file = "{}.lock".format(package_name)
    return sdcard_path_exists(lock_file)


def stop_instrumenting(package_name, timeout=None):
    cmd = "{} shell am broadcast -a 'tool.acv.finishtesting' -p '{}'".format(config.adb_path, package_name)
    logging.info("finish testing")
    result = subprocess.call(cmd, shell=True)
    logging.info(result)
    locked = coverage_is_locked(package_name)
    if timeout is None:
        timeout = config.default_onstop_timeout
    while locked and timeout:
        logging.info("wait until the coverage file is saved {}".format(package_name))
        time.sleep(1)
        locked = coverage_is_locked(package_name)
        timeout -= 1

    files = get_package_files_list(package_name)
    coverage_files = [f for f in files if f.endswith(".ec")]
    crash_file = CRASH_REPORT_FILENAME if CRASH_REPORT_FILENAME in files else None

    logging.info("coverage files at /sdcard/Download/{0}:".format(package_name))
    logging.info("\n".join(coverage_files))
    if crash_file:
        logging.info("crash report /sdcard/Download/{0}/{1}".format(package_name, crash_file))


# refactor: to put this in a separate controller
def flush(package_name):
    logging.info("flush")
    cmd = "{} shell am broadcast -a 'tool.acv.flush' -p '{}'".format(config.adb_path, package_name)
    result = subprocess.call(cmd, shell=True)


def calculate(package_name):
    logging.info('calculate (see for "ACV" tag in logcat)')
    cmd = "{} shell am broadcast -a 'tool.acv.calculate' -p '{}'".format(config.adb_path, package_name)
    result = subprocess.call(cmd, shell=True)


def snap(package_name, i=0, output=None):
    logging.info("ec: {}".format(i))
    snap_cmd = "{} shell am broadcast -a 'tool.acv.snap' -p '{}'".format(config.adb_path, package_name)
    result = subprocess.call(snap_cmd, shell=True)

    if output:
        if not os.path.exists(output):
            os.makedirs(output)
        files = [f for f in get_package_files_list(package_name) if f.endswith(".ec")]
        pull_files(output, files, package_name)
            
    #screens
    # files = get_package_files_list(package_name)
    # adb_files_ec_set = [f for f in files if f.endswith('.ec')]
    # if len(adb_files_ec_set) > 0:
    #     new_ec = adb_files_ec_set[-1]
    #     time_mark = new_ec.split('_')[1][:-3]
    #     logging.info("screen..")
    #     scrn_cmd = "{} shell screencap -p /sdcard/Download/{}/{}.png".format(config.adb_path, package_name, time_mark)
    #     result = subprocess.call(scrn_cmd)
    # else:
    #     logging.info("No ec files saved on sdcard.")
    # return


def save_ec_and_screen(package_name, delay=10, output=None, snap_number=722): # 720 per 10s is 2 hours
    i = 1
    logging.info("scheduler: {}, {} sec output: {}".format(package_name, delay, output))
    schedule = sched.scheduler(time.time, time.sleep)
    while i < snap_number:
        schedule.enter(delay*i, i, snap, (package_name, i, output))
        i += 1
    schedule.run()


def instrument_app(wd, smali_dirs, dbg_start=None, dbg_end=None, installation=False, granularity=Granularity.default, mem_stats=None, ignore_filter=None, keep_unpacked=False, target_cl=None, target_mtd=None):
    manifest_instrumenter.instrument_manifest(wd.manifest_path)
    instrument_smali_code(smali_dirs, wd.pickle_dir, wd.package, granularity, dbg_start, dbg_end, mem_stats, ignore_filter, target_cl, target_mtd)
    logging.info("instrumented")


@timeit
def instrument_apk(apk_path, result_dir, dbg_start=None, dbg_end=None, installation=False, granularity=Granularity.default, mem_stats=None, ignore_filter=None, keep_unpacked=False, target_cl=None, target_mtd=None):
    '''
    I assume that the result_dir is empty is checked.
    '''
    package = get_apk_properties(apk_path).package
    logging.info("package: {}".format(package))
    wd = WorkingDirectory(package, result_dir)
    apktool.decode(apk_path, wd.unpacked_apk)
    logging.info("decompiled {0}".format(wd.package))
    smali_dirs = Utils.get_smali_dirs(wd.unpacked_apk) # smali_code_path
    instrument_app(wd, smali_dirs, dbg_start, dbg_end, installation, granularity, mem_stats, ignore_filter, keep_unpacked, target_cl, target_mtd)
    Utils.rm_if_exists(wd.instrumented_package_path)
    apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    if not keep_unpacked:
        Utils.rm_tree(wd.unpacked_apk)
    logging.info("built")

    sign_align_apk(wd.instrumented_package_path, wd.instrumented_apk_path)

    logging.info("apk instrumented: {0}".format(wd.instrumented_apk_path))
    logging.info("package name: {0}".format(wd.package))
    if installation:
        install(wd.instrumented_apk_path)
    return (wd.package, wd.instrumented_apk_path, wd.pickle_dir)


def build_dir(apktool_dir, result_dir, signature=False, installation=False):
    build_pkg_path = os.path.join(result_dir, "build_temp.apk")
    apktool.build(apktool_dir, build_pkg_path)
    package = get_apk_properties(build_pkg_path).package
    result_apk_path = build_pkg_path
    if signature:
        result_apk_path = os.path.join(result_dir, "build_{0}.apk".format(package))
        sign_align_apk(build_pkg_path, result_apk_path)
        print('apk was built and signed: {0}'.format(result_apk_path))
    else:
        print('apk was built: {0}'.format(result_apk_path))
    if installation:
        install(result_apk_path)
    return result_apk_path


def get_path_to_insrumented_apk(apk_path, result_dir):
    apk_dir, apk_fname = os.path.split(apk_path)
    new_apk_fname = "{}_{}".format("instr", apk_fname)
    pth = os.path.join(result_dir, new_apk_fname)
    return pth


def apply_ignore_filter(smali_tree, ignore_filter):
    if not os.path.exists(ignore_filter):
        return
    with open(ignore_filter, 'r') as f:
        lines = f.readlines()
        smali_tree.update_class_ref_dict()
        for l in lines:
            parts = l.strip().split('->')
            klass = parts[0]
            if klass in smali_tree.class_ref_dict:
                if len(parts) == 2 and parts[1] in smali_tree.class_ref_dict[klass].meth_ref_dict:
                    smali_tree.class_ref_dict[klass].meth_ref_dict[parts[1]].ignore = True
                else:
                    smali_tree.class_ref_dict[klass].ignore = True


def instrument_manifest(manifest_path):
    manifest_instrumenter.instrument_manifest(manifest_path)

# -- MULTIDEX
def instrument_smali_code(input_smali_dirs, pickle_dir, package, granularity, dbg_start=None, dbg_end=None, mem_stats=None, ignore_filter=None, target_cl=None, target_mtd=None):
    acv_classes_dir = Instrumenter.choose_acv_files_smali_dir(input_smali_dirs)
    for tree_id, pth in enumerate(input_smali_dirs, 1):
        tree = SmaliTree(tree_id, pth)
        if ignore_filter:
            apply_ignore_filter(tree, ignore_filter)
        smali_instrumenter = Instrumenter(tree, acv_classes_dir, granularity, package, dbg_start, dbg_end, mem_stats, target_cl, target_mtd)
        classes_info = smali_instrumenter.save_instrumented_smalitrees()
        AcvReporter.save(acv_classes_dir, tree_id, classes_info)
        #https://stackoverflow.com/a/54960728/5268585
        # 16-bit uint can represent a maximum value of 65535, divided by 4, equals 16383.75.
        # Ltool/acv/AcvReporter1;,=0< getArray generates 19644 insns
        smali_instrumenter.save_pickle(pickle_dir)
    Utils.copytree(Instrumenter.instrumentation_smali_path, acv_classes_dir)
    AcvStoring.add_reporter_calls(len(input_smali_dirs), acv_classes_dir, package)
    AcvFlushing.add_reporter_calls(len(input_smali_dirs), acv_classes_dir, package)
    AcvCalculator.add_reporter_calls(len(input_smali_dirs), acv_classes_dir, package)
    AcvInstrumentation.change_package(package, acv_classes_dir)
    acv_tree = SmaliTree(999, acv_classes_dir)
    # class_number = len(acv_tree.classes)
    fields_number =  sum([len(cl.fields) for cl in acv_tree.classes])
    # methods_number =  sum([len(cl.methods) for cl in acv_tree.classes])
    if fields_number > 65400: #65535
        acv_reporter_classes = [cl for cl in acv_tree.classes if cl.name.startswith("Ltool/acv/AcvReporter")]
        fields_number_counter = 0
        classes_to_move = []
        for i, cl in enumerate(acv_reporter_classes):
            fields_number_counter += len(cl.fields)
            if fields_number_counter > 65000:
                classes_to_move.append(cl.file_path)
        if classes_to_move:
            move_classes_to_new_dex(classes_to_move, acv_classes_dir)
    # print("classes {}".format(class_number))
    # print("fields {}".format(fields_number))
    # print("methods {}".format(methods_number))


def refresh_wd_no_smali(wd, apk_path):
    '''We actually need app files except smali dirs.
    The smali dirs to be recover from the smalitree.'''
    logging.info("removing smali dirs")
    if os.path.exists(wd.unpacked_apk):
        shutil.rmtree(wd.unpacked_apk)
    apktool.unpack(apk_path, wd.unpacked_apk)
    dex_files = [file for file in os.listdir(wd.unpacked_apk) if file.endswith('.dex')]
    for f in dex_files:
        os.remove(os.path.join(wd.unpacked_apk, f))


# --MULTIDEX
def move_classes_to_new_dex(classes_to_move, acv_classes_dir):
    next_dex_number = int(os.path.basename(acv_classes_dir)[13:]) + 1
    next_dex_path = os.path.join(os.path.dirname(acv_classes_dir), "smali_classes{}".format(next_dex_number))
    new_acv_dir = os.path.join(next_dex_path, "tool", "acv")
    if not os.path.exists(new_acv_dir):
        os.makedirs(new_acv_dir)
    for cl in classes_to_move:
        shutil.move(cl, new_acv_dir)
        print("{} moved to new the dex directory {}".format(os.path.basename(cl), next_dex_path))


def sign_align_apk(instrumented_package_path, output_apk):
    aligned_apk_path = instrumented_package_path.replace('.apk', '_signed_tmp.apk')
    align_cmd = '"{}" -f 4 "{}" "{}"'.format(config.zipalign, instrumented_package_path, aligned_apk_path)
    terminal.request_pipe(align_cmd)

    apksigner_cmd = '{} sign --ks {} --ks-pass pass:{} --out {} {}'\
        .format(config.apksigner_path, config.keystore_path, config.keystore_password, output_apk, aligned_apk_path)
    terminal.request_pipe(apksigner_cmd)
    os.remove(aligned_apk_path)


class apkinfo(object):
    """Properties of the apk file."""
    def __init__(self, package=None, sdkversion=None, targetsdkverion=None):
        self.package = package
        self.sdkversion = sdkversion
        self.targetsdkversion = targetsdkverion

    def __repr__(self):
        return "{} {} {}".format(self.package, self.sdkversion, self.targetsdkversion)
