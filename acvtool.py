import os
import sys
import yaml
import logging
import argparse
from logging import config as logging_config
from six.moves import input
from smiler import smiler
from smiler import reporter
from smiler.config import config
from pkg_resources import resource_stream
from smiler.granularity import Granularity


def setup_logging():
    with open(config.logging_yaml) as f:
        logging_config.dictConfig(yaml.safe_load(f.read()))

def run_actions(parser, args=None):
    """
    This function parses the arguments using the provided parser and run
    corresponding acvtool actions.

    Args:
        parser(argparse.ArgumentParser): ArgumentParser for this code
    """

    if args is None:
        args = parser.parse_args()
    if args.subcmd in ["instrument", "install", "uninstall", "start", "stop", "report"] and args.device:
            config.adb_path = "{} -s {}".format(config.adb_path, args.device)
    if args.subcmd == "instrument":
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
            mem_stats=args.memstats)
        if args.report:
            smiler.start_instrumenting(package,
                onstop=lambda: reporter.generate(
                    package,
                    pickle_path,
                    output_dir=config.default_report_dir,
                    granularity=args.granularity),
                timeout=int(args.timeout))
    elif args.subcmd == "install":
        smiler.install(args.apk_path)
    elif args.subcmd == "uninstall":
        smiler.uninstall(args.package_name)
    elif args.subcmd == "start":
        onstop_report = None
        if args.report:
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
    elif args.subcmd == "stop":
        smiler.stop_instrumenting(args.package_name, int(args.timeout))
    elif args.subcmd == "report":
        xml_html = not (args.xml or args.html) # generate both xml and html by default
        reporter.generate(
            args.package_name,
            args.pickle_path,
            args.output_dir,
            args.ec_dir,
            xml=args.xml or xml_html, html=args.html or xml_html,
            granularity=args.granularity)
    elif args.subcmd == "sign":
        smiler.sign_align_apk(args.apk_path, "{0}.signed.apk".format(args.apk_path))
    elif args.subcmd == "build":
        smiler.build_dir(args.apktool_dir, args.result_dir, signature=args.s, installation=args.i)
    else:
        parser.print_usage()
        return

def get_parser():
    parser = argparse.ArgumentParser(prog='acvtool.py', 
        description='This tool is designed to measure code coverage of \
        Android applications when its sources are not available.')
    parser.add_argument('--version', action='version', version=str(config.version))

    subparsers = parser.add_subparsers(dest='subcmd', metavar="<command>", 
        help="acvtool commands")
    
    parser_instrument = subparsers.add_parser("instrument", help="Instruments an apk")
    parser_instrument.add_argument("apk_path", metavar="<path_to_apk>", 
            help="Path to apk file")
    parser_instrument.add_argument("--wd", metavar="<result_directory>", 
            default=config.default_working_dir,
            dest="working_dir", required=False, 
            help="Path to the directory where the working data is stored")
    parser_instrument.add_argument("--dbgstart", metavar="<methods_number>",
            help="Troubleshooting purposes. The number of the first method to be \
            instrumented. Only methods from DBGSTART to DBGEND will be instrumented.",
            required=False, dest="dbg_start", type=int)
    parser_instrument.add_argument("--dbgend", metavar="<methods_number>",
            help="Troubleshooting purposes. The number of the last method to be \
            instrumented. Only methods from DBGSTART to DBGEND will be instrumented.",
            required=False, dest="dbg_end", type=int)
    parser_instrument.add_argument("-f", "--force", action="store_true", 
            help="Working directory will be overwritten without asking.",
            required=False)
    parser_instrument.add_argument("-i", "--install", action="store_true",
            help="Installs the application immidiately after instrumenting.")
    parser_instrument.add_argument("-r", "--report", action="store_true",
            help="Performs the whole testing cycle in a single session: \
            instrument, start, report.")
    parser_instrument.add_argument("-g", "--granularity", metavar="<granularity>", 
            help="Code coverage granularity [instruction or method].", choices=Granularity.granularities(),
            default=Granularity.default)
    parser_instrument.add_argument("-t", "--timeout", metavar="<timeout>", required=False,
            help="Waiting time for coverage file preparing.",
            default=config.default_onstop_timeout)
    parser_instrument.add_argument("-ms", "--memstats", metavar="<memstats>", required=False,
            help="How many bytes acvtool allocated for tracking.['single', 'verbose']", 
            choices=["single", "verbose"], default=None)
    parser_instrument.add_argument("-d", "--device", metavar="<device>", required=False,
            help="The name of adb device/emulator.", default=None, dest="device")
    
    parser_install = subparsers.add_parser("install", help="Installs an apk")
    parser_install.add_argument("apk_path", metavar="<path_to_apk>",
            help="Path to apk file")
    parser_install.add_argument("-d", "--device", metavar="<device>", required=False,
            help="The name of adb device/emulator.", default=None, dest="device")
    parser_uninstall = subparsers.add_parser("uninstall", help="Uninstalls an apk")
    parser_uninstall.add_argument("package_name", metavar="<package>",
            help="Package name")
    parser_uninstall.add_argument("-d", "--device", metavar="<device>", required=False,
            help="The name of adb device/emulator.", default=None, dest="device")

    parser_start = subparsers.add_parser("start", help="Starts runtime coverage data collection")
    parser_start.add_argument("package_name", metavar="<package.name>")
    parser_start.add_argument("-q", "--q", action="store_true", required=False,
            help="Releases the thread. Requires to call 'stop' command after the tests were completed.")
    parser_start.add_argument("-r", "--report", action="store_true",
            help="Generates a report immediately after the test is finished.")
    parser_start.add_argument("-p", metavar="<pickle_file>", required=False,
            dest="pickle_path", help="Path to pickle file")
    parser_start.add_argument("-g", "--granularity", metavar="<granularity>",
            help="Code coverage granularity [instruction or method].", choices=Granularity.granularities(),
            default=Granularity.default)
    parser_start.add_argument("-t", "--timeout", metavar="<timeout>", required=False,
            help="Waiting time for coverage file preparing.",
            default=config.default_onstop_timeout)
    parser_start.add_argument("-d", "--device", metavar="<device>", required=False,
            help="The name of adb device/emulator.", default=None, dest="device")

            
    parser_stop = subparsers.add_parser("stop", help="Stops runtime coverage data collection")
    parser_stop.add_argument("package_name", metavar="<package.name>")
    parser_stop.add_argument("-t", "--timeout", metavar="<timeout>", required=False,
           help="Waiting time for coverage file preparing.",
           default=config.default_onstop_timeout)
    parser_stop.add_argument("-d", "--device", metavar="<device>", required=False,
            help="The name of adb device/emulator.", default=None, dest="device")

    parser_report = subparsers.add_parser("report", help="Produces a report")
    parser_report.add_argument("package_name", metavar="<package_name>",
            help="Package name")
    parser_report.add_argument("-p", metavar="<pickle_file>", required=True,
            dest="pickle_path", help="Path to pickle file")
    parser_report.add_argument("-o", metavar="<output_dir>", required=False,
            dest="output_dir", help="Output directory",
            default=config.default_report_dir)
    parser_report.add_argument("-ec", metavar="<ec_dir>", required=False,
            dest="ec_dir", help="The directory with the code coverage binary files preloaded from the emulator.")
    parser_report.add_argument("-xml", "--xml", action="store_true",
            help="Generate XML report.")
    parser_report.add_argument("-html", "--html", action="store_true",
            help="Generate HTML report.")
    parser_report.add_argument("-g", "--granularity", metavar="<granularity>", dest="granularity",
            help="Code coverage granularity [instruction or method].", choices=Granularity.granularities(),
            default=Granularity.default)
    parser_report.add_argument("-d", "--device", metavar="<device>", required=False,
            help="The name of adb device/emulator.", default=None, dest="device")
    
    parser_sign = subparsers.add_parser("sign", help="Signs and alignes an apk.")
    parser_sign.add_argument("apk_path", metavar="<apk_path>", help="An application's path")

    parser_build = subparsers.add_parser("build", help="Builds a folder with an unpacked by apktool apk.")
    parser_build.add_argument("apktool_dir", metavar="<apktool_dir>", help="The path to an unpacked apk.")
    parser_build.add_argument("--rd", metavar="<result_dir>", required=False,
            dest="result_dir",
            default=config.default_working_dir,
            help="Path to the directory where the working data is stored")
    parser_build.add_argument("-s", "--s", action="store_true", help="Signs the apk produced.")
    parser_build.add_argument("-i", "--i", action="store_true",
            help="Installs the application immidiately after instrumenting.")

    return parser

def main():
    setup_logging()
    parser = get_parser()
    args = parser.parse_args()
    run_actions(parser, args)

if __name__ == "__main__":
    main()
