import yaml
import argparse
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
    if args.subcmd in ["instrument", "install", "uninstall", "activate", "start", "stop", "snap", "flush", "calculate", "pull", "cover-pickles", "report", "shrink"] and args.device:
        config.adb_path = "{} -s {}".format(config.adb_path, args.device)
    if args.subcmd == "instrument":
        acv.instrument(args)
    elif args.subcmd == "install":
        acv.install(args)
    elif args.subcmd == "uninstall":
        acv.uninstall(args)
    elif args.subcmd == "activate":
        acv.activate(args)
    elif args.subcmd == "start":
        acv.start(args)
    elif args.subcmd == "stop":
        acv.stop(args)
    elif args.subcmd == "snap":
        acv.snap(args)
    elif args.subcmd == "flush":
        acv.flush(args)
    elif args.subcmd == "calculate":
        acv.calculate(args)
    elif args.subcmd == "pull":
        acv.pull(args)
    elif args.subcmd == "cover-pickles":
        acv.cover_pickles(args)
    elif args.subcmd == "report":
        acv.report(args)
    elif args.subcmd == "sign":
        acv.sign(args)
    elif args.subcmd == "build":
        acv.build(args)
    elif args.subcmd == "shrink":
        acv.shrink(args)
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
    return parser

def main():
    setup_logging()
    parser = get_parser()
    args = parser.parse_args()
    run_actions(parser, args)

if __name__ == "__main__":
    main()
