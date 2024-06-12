import os
import logging
from . import smiler
from .config import config
from ..cutter import shrinker
from .operations import coverage
from .instrumenting import apktool
from .entities.wd import WorkingDirectory
from .reporting.reporter import Reporter



def instrument(args):
    if os.path.isdir(args.working_dir):
            if not args.force:
                print("The working directory exists and may contain data: {}".format(args.working_dir))
                user_choice = input("Overwrite (y/n)? ")
                if user_choice.lower() in ["y", "yes"]:
                    pass
                elif user_choice.lower() in ["n", "no"]:
                    print("Aborting operation!")
                    return
                else:
                    print("Your choice is not correct! Exiting!")
                    return
    package, apk_path, pickle_path = smiler.instrument_apk(
        apk_path=args.apk_path,
        result_dir=args.working_dir,
        dbg_start=args.dbg_start,
        dbg_end=args.dbg_end,
        installation=args.install or args.report,
        granularity=args.granularity,
        mem_stats=args.memstats, 
        keep_unpacked=args.keepsources,
        ignore_filter=args.stubs,
        target_cl=args.target_class,
        target_mtd=args.method,
        target_dexs=[] if not args.dex else args.dex.split(","))
    if args.report:
    # onstop is deprecated due to missing get_execution_results
        smiler.start_instrumenting(package,
            onstop=lambda: reporter.generate(
                package,
                pickle_path,
                output_dir=config.default_report_dir,
                granularity=args.granularity),
            timeout=int(args.timeout))

def install(args):
    smiler.install(args.apk_path)

def uninstall(args):
    smiler.uninstall(args.package_name)

def activate(args):
    smiler.activate(args.package)

def start(args):
    onstop_report = None
    if args.report:
    # onstop is deprecated due to missing get_execution_results
        onstop_report = lambda: reporter.generate(
            args.package_name,
            args.pickle_path,
            output_dir=config.default_report_dir,
            granularity=args.granularity)
    smiler.start_instrumenting(
        args.package_name, 
        args.q,
        onstop=onstop_report,
        timeout=int(args.timeout)) 

def stop(args):
    smiler.stop_instrumenting(args.package_name, int(args.timeout))

def snap(args):
    if args.repeat:
            smiler.save_ec_and_screen(args.package_name, int(args.throttle), args.output_dir)
    else:
        wd = WorkingDirectory(args.package_name, args.working_dir) if args.working_dir else ""
        output_dir = args.output_dir if args.output_dir else wd.ec_dir
        print("output_dir: {}".format(output_dir))
        smiler.snap(args.package_name, 1, output_dir)

def flush(args):
    smiler.flush(args.package_name)

def calculate(args):
    smiler.calculate(args.package_name)

def pull(args):
    wd = WorkingDirectory(args.package_name, args.working_dir)
    smiler.get_execution_results(args.package_name, wd.ec_dir, wd.images)

def cover_pickles(args):
    wd = WorkingDirectory(args.package_name, args.working_dir)
    coverage.cover_pickles(wd)

def report(args):
    wd = WorkingDirectory(args.package_name, args.working_dir)
    reporter = Reporter(args.package_name, wd.get_covered_pickles(), wd.images, wd.report)
    reporter.generate(html=args.html, xml=args.xml, 
        granularity=args.granularity, 
        ignore_filter=args.stubs, shrink=args.shrink)

def sign(args):
    smiler.patch_align_sign(args.apk_path, "{0}.signed.apk".format(args.apk_path))

def build(args):
    smiler.build_dir(args.apktool_dir, args.result_dir, signature=args.s, installation=args.i)

def shrink(args):
    wd = WorkingDirectory(args.package_name, args.working_dir)
    smiler.refresh_wd_no_smali(wd, args.apk_path)
    shrinker.shrink_smali(wd, wd.get_covered_pickles())
    apktool.build(wd.unpacked_apk, wd.instrumented_package_path)
    smiler.patch_align_sign(wd.instrumented_package_path, wd.short_apk_path)
    logging.info("shrinked apk was saved to {}".format(wd.short_apk_path))

