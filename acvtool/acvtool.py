import yaml
import argparse
import logging
from logging import config as logging_config
from .smiler import acv, cliparser
from .smiler.cliparser import AcvCommandParsers
from .smiler.config import config


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
    if args.debug:
        logging.info("Debug logging is on")
        logging.getLogger().setLevel(logging.DEBUG)
    command_map = {
        "instrument": acv.instrument,
        "install": acv.install,
        "uninstall": acv.uninstall,
        "activate": acv.activate,
        "start": acv.start,
        "stop": acv.stop,
        "snap": acv.snap,
        "flush": acv.flush,
        "calculate": acv.calculate,
        "pull": acv.pull,
        "cover-pickles": acv.cover_pickles,
        "report": acv.report,
        "sign": acv.sign,
        "build": acv.build,
        "shrink": acv.shrink,
        "smali": acv.smali,
    }

    if args.subcmd in command_map and getattr(args, "device", None):
        config.adb_path = "{} -s {}".format(config.adb_path, args.device)

    func = command_map.get(args.subcmd)
    if func:
        func(args)
    else:
        parser.print_usage()
        return

def get_parser():
    parser = argparse.ArgumentParser(prog='acvtool.py', 
        description='This tool is designed to measure code coverage of \
        Android applications when its sources are not available.')
    parser.add_argument('--version', action='version', version=str(config.version))
    parser.add_argument('--debug', help='Print verbose output', action='store_true')
    subparsers = parser.add_subparsers(dest='subcmd', metavar="<command>", 
        help="acvtool commands")
    cli_cmd = AcvCommandParsers(subparsers)
    cli_cmd.instrument()
    cli_cmd.install()  
    cli_cmd.uninstall()
    cli_cmd.activate()
    cli_cmd.start()
    cli_cmd.stop()
    cli_cmd.snap()
    cli_cmd.flush()
    cli_cmd.calculate()  
    cli_cmd.pull()
    cli_cmd.cover_pickles()
    cli_cmd.report()
    cli_cmd.sign()
    cli_cmd.build()
    cli_cmd.shrink()
    cli_cmd.smali()
    return parser

def main():
    setup_logging()
    parser = get_parser()
    args = parser.parse_args()
    run_actions(parser, args)

if __name__ == "__main__":
    main()
    
