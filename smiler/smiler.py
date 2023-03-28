import os
import subprocess
import re
import shutil
import threading
import signal
import logging
import time
from config import config
from granularity import Granularity
from instrumenting import manifest_instrumenter
from libs.libs import Libs
from instrumenting.apkil.smalitree import SmaliTree
from instrumenting.apktool_interface import ApktoolInterface
from instrumenting.smali_instrumenter import Instrumenter
from instrumenting.utils import timeit
from instrumenting.utils import Utils

apk_info_pattern = re.compile("package: name='(?P<package>.*?)'")

CRASH_REPORT_FILENAME = "errors.txt"

def install(new_apk_path):
    logging.info("installing")
    cmd = '{} install -r "{}"'.format(config.adb_path, new_apk_path)
    out = request_pipe(cmd)
    
    logging.info(out)

def uninstall(package):
    logging.info("uninstalling")
    cmd = '{} uninstall "{}"'.format(config.adb_path, package)
    out = request_pipe(cmd)

    logging.info(out)

def request_pipe(cmd):
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = pipe.communicate()

    res = out
    if not out:
        res = err
    
    if pipe.returncode > 0:
        raise Exception("----------------------------------------------------\n\
Out: %s\nError: %s" % (out, err))

    return res

def get_apk_properties(path):
    info_cmd = "%s dump badging %s" % (config.aapt_path, path)
    out = request_pipe(info_cmd)
    matched = re.match(apk_info_pattern, out)

    package_name = matched.group('package')
    
    return apkinfo(package_name, "", "")


def get_package_files_list(package_name):
    cmd = '%s shell ls "/sdcard/Download/%s/"' % (config.adb_path, package_name)
    out = request_pipe(cmd)
    files = [f for f in out.split() if not f.endswith('/')]
    return files  

def get_execution_results(package_name, output_dir):
    result_files = get_package_files_list(package_name)
    coverage_files = [f for f in result_files if f.endswith(".ec")]
    crash_file = CRASH_REPORT_FILENAME if CRASH_REPORT_FILENAME in result_files else None

    if not (coverage_files or crash_file):
        raise Exception("No coverage or crash report files have been detected on the device for {} package.\n\
        Run acvtool with \'-start\' argument to produce coverage.".format(package_name))
    
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    for f in result_files:
        adb_pull(package_name, f, output_dir)
        adb_delete_files(package_name, f)
    if crash_file:
        adb_pull(package_name, crash_file, output_dir)
        adb_delete_files(package_name, crash_file)

def adb_pull(package_name, file_path, pull_to):
    cmd = "%s pull /sdcard/Download/%s/%s %s" % (config.adb_path, package_name, file_path, os.path.abspath(pull_to))
    out = request_pipe(cmd)
    logging.info(out)

def adb_delete_files(package_name, file_name):
    cmd = "%s shell rm /sdcard/Download/%s/%s" % (config.adb_path, package_name, file_name)
    out = request_pipe(cmd)

def grant_storage_permission(package):
    read_storage_cmd = "{0} shell pm grant {1} android.permission.READ_EXTERNAL_STORAGE".format(config.adb_path, package)
    subprocess.call(read_storage_cmd, shell=True)

    write_storage_cmd = "{0} shell pm grant {1} android.permission.WRITE_EXTERNAL_STORAGE".format(config.adb_path, package)
    subprocess.call(write_storage_cmd, shell=True)

def start_instrumenting(package, release_thread=False, onstop=None, timeout=None):
    grant_storage_permission(package)
    lock_thread = "" if release_thread else "-w"
    cmd = '{} shell am instrument -e coverage true {} {}/{}'.format(config.adb_path, lock_thread, package, config.INSTRUMENTING_NAME)

    if release_thread:
        os.system(cmd)
        return
    out = ''
    def run():
        out = request_pipe(cmd)
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
    
def coverage_is_locked(package_name):
    cmd = "{} shell \"test -e /sdcard/Download/{}.lock > /dev/null 2>&1 && echo \'1\' || echo \'0\'\"".format(config.adb_path, package_name)
    logging.debug('Command to check lock file:' + cmd)
    locked = subprocess.check_output(cmd, shell=True).replace("\n","").replace("\r", "")
    return locked == '1'

def stop_instrumenting(package_name, timeout=None):
    cmd = "{} shell am broadcast -a 'tool.acv.finishtesting'".format(config.adb_path)
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

@timeit
def instrument_apk(apk_path, result_dir, dbg_start=None, dbg_end=None, installation=False, granularity=Granularity.default, mem_stats=None):
    '''
    I assume that the result_dir is empty is checked.
    '''
    apktool = ApktoolInterface(javaPath = config.APKTOOL_JAVA_PATH,
                               javaOpts = config.APKTOOL_JAVA_OPTS,
                               pathApktool = Libs.APKTOOL_PATH,
                               jarApktool = Libs.APKTOOL_PATH)
    package = get_apk_properties(apk_path).package
    unpacked_data_path = decompile_apk(apktool, apk_path, package, result_dir)
    manifest_path = get_path_to_manifest(unpacked_data_path)
    logging.info("decompiled {0}".format(package))

    instrument_manifest(manifest_path)
    smali_code_path = get_path_to_smali_code(unpacked_data_path)
    pickle_path = get_pickle_path(apk_path, result_dir)
    instrument_smali_code(smali_code_path, pickle_path, package, granularity, dbg_start, dbg_end, mem_stats)
    logging.info("instrumented")
   
    instrumented_package_path = get_path_to_instrumented_package(apk_path, result_dir)
    remove_if_exits(instrumented_package_path)
    build_apk(apktool, unpacked_data_path, instrumented_package_path)
    Utils.rm_tree(unpacked_data_path)
    logging.info("built")

    instrumented_apk_path = get_path_to_insrumented_apk(instrumented_package_path, result_dir)
    sign_align_apk(instrumented_package_path, instrumented_apk_path)

    logging.info("apk instrumented: {0}".format(instrumented_apk_path))
    logging.info("package name: {0}".format(package))
    if installation:
        install(instrumented_apk_path)
    return (package, instrumented_apk_path, pickle_path)

def remove_if_exits(path):
    if os.path.exists(path):
        os.remove(path)

def build_dir(apktool_dir, result_dir, signature=False, installation=False):
    apktool = ApktoolInterface(javaPath = config.APKTOOL_JAVA_PATH,
                               javaOpts = config.APKTOOL_JAVA_OPTS,
                               pathApktool = Libs.APKTOOL_PATH,
                               jarApktool = Libs.APKTOOL_PATH)
    build_pkg_path = os.path.join(result_dir, "build_temp.apk")
    build_apk(apktool, apktool_dir, build_pkg_path)
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

def decompile_apk(apktool, apk_path, package, result_dir):
    unpacked_data_path = os.path.join(result_dir, "apktool", package)
    (run_successful, cmd_output) = apktool.decode(apkPath = apk_path,
                                        dirToDecompile = unpacked_data_path,
                                        quiet = True,
                                        noSrc = False,
                                        noRes = False,
                                        debug = False,
                                        noDebugInfo = False,
                                        force = True, #directory exist so without this this process finishes
                                        frameworkTag = "",
                                        frameworkDir = "",
                                        keepBrokenRes = False)

    if not run_successful:
        print("Run is not successful!")
    
    return unpacked_data_path

def get_path_to_manifest(unpacked_data_path):
    pth = os.path.join(unpacked_data_path, "AndroidManifest.xml")
    return pth

def get_path_to_smali_code(unpacked_data_path):
    pth = os.path.join(unpacked_data_path, "smali")
    return pth

def get_path_to_instrumentation_metadata_dir(result_dir):
    pth = os.path.join(result_dir, "metadata")
    return pth

def get_path_to_insrumented_apk(apk_path, result_dir):
    apk_dir, apk_fname = os.path.split(apk_path)
    new_apk_fname = "{}_{}".format("instr", apk_fname)
    pth = os.path.join(result_dir, new_apk_fname)
    return pth

def get_path_to_instrumented_package(apk_path, result_dir):
    apk_dir, apk_fname = os.path.split(apk_path)
    path = os.path.join(result_dir, apk_fname)
    return path

def get_pickle_path(apk_path, result_dir):
    apk_dir, apk_fname = os.path.split(apk_path)
    metadata_dir = get_path_to_instrumentation_metadata_dir(result_dir)
    return os.path.join(metadata_dir, "{}.pickle".format(apk_fname[:-4]))

def instrument_manifest(manifest_path):
    manifest_instrumenter.instrumentAndroidManifestFile(manifest_path, addSdCardPermission=True)

@timeit
def instrument_smali_code(input_smali_dir, pickle_path, package, granularity, dbg_start=None, dbg_end=None, mem_stats=None):
    smali_tree = SmaliTree(input_smali_dir)
    smali_instrumenter = Instrumenter(smali_tree, granularity, package, dbg_start, dbg_end, mem_stats)
    smali_instrumenter.save_instrumented_smali(input_smali_dir)
    smali_instrumenter.save_pickle(pickle_path)

def sign_align_apk(instrumented_package_path, output_apk):
    aligned_apk_path = instrumented_package_path.replace('.apk', '_signed_tmp.apk')
    align_cmd = '"{}" -f 4 "{}" "{}"'.format(config.zipalign, instrumented_package_path, aligned_apk_path)
    request_pipe(align_cmd)

    apksigner_cmd = '{} sign --ks {} --ks-pass pass:{} --out {} {}'\
        .format(config.apksigner_path, config.keystore_path, config.keystore_password, output_apk, aligned_apk_path)
    request_pipe(apksigner_cmd)
    os.remove(aligned_apk_path)

def build_apk(apktool, apkdata_dir, new_apk_path):
    apktool.build(srcPath=apkdata_dir, finalApk=new_apk_path, forceAll=True, 
                  debug=False)


class apkinfo(object):
    """Properties of the apk file."""
    def __init__(self, package=None, sdkversion=None, targetsdkverion=None):
        self.package = package
        self.sdkversion = sdkversion
        self.targetsdkversion = targetsdkverion

    def __repr__(self):
        return "%s %s %s" % (self.package, self.sdkversion, self.targetsdkversion)
