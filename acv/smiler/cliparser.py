from .config import config
from .granularity import Granularity


class AcvCommandParsers(object):

    def __init__(self, subparsers):
        self.subparsers = subparsers

    def instrument(self):
        parser_instrument = self.subparsers.add_parser("instrument", help="Instruments an apk")
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
        parser_instrument.add_argument("-k", "--keepsources", action="store_true",
                help="Keep instrumented smali dir.")
        parser_instrument.add_argument("-s", "--stubs", metavar="<stubs>", required=False,
                help="Ignores list of stub methods. List methods signatures in txt files", default=None)
        parser_instrument.add_argument("-cl", "--class", metavar="<target_class>", required=False,
                help="Instrument specific class, e.g. 'android.support.multidex.a'.",
                default=None, dest="target_class")
        parser_instrument.add_argument("-m", "--method", metavar="<method>", required=False,
                help="Instrument specific method, e.g. 'void android.support.multidex.a.g(android.content.Context)'.",
                default=None)
        parser_instrument.add_argument("-dex", "--dex", metavar="<dex>", required=False,
                help="Instrument specific dex file, e.g. 'classes2.dex'.",
                default=None)

    def install(self):
        parser_install = self.subparsers.add_parser("install", help="Installs an apk")
        parser_install.add_argument("apk_path", metavar="<path_to_apk>",
                help="Path to apk file")
        parser_install.add_argument("-d", "--device", metavar="<device>", required=False,
                help="The name of adb device/emulator.", default=None, dest="device")
    
    def uninstall(self):
        parser_uninstall = self.subparsers.add_parser("uninstall", help="Uninstalls an apk")
        parser_uninstall.add_argument("package_name", metavar="<package>",
                help="Package name")
        parser_uninstall.add_argument("-d", "--device", metavar="<device>", required=False,
                help="The name of adb device/emulator.", default=None, dest="device")

    def activate(self):
        parser_activate = self.subparsers.add_parser("activate", help="Prepares the app for coverage measurement.")
        parser_activate.add_argument("package", metavar="<package.name>")
        parser_activate.add_argument("-d", "--device", metavar="<device>", required=False,
                help="The name of adb device/emulator.", default=None, dest="device")

    def start(self):
        parser_start = self.subparsers.add_parser("start", help="Starts the instrumentation process for the app")
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

    def stop(self):
        parser_stop = self.subparsers.add_parser("stop", help="Stops the instrumentation process")
        parser_stop.add_argument("package_name", metavar="<package.name>")
        parser_stop.add_argument("-t", "--timeout", metavar="<timeout>", required=False,
            help="Waiting time for coverage file preparing.",
            default=config.default_onstop_timeout)
        parser_stop.add_argument("-d", "--device", metavar="<device>", required=False,
                help="The name of adb device/emulator.", default=None, dest="device")

    def flush(self):
        parser_flush = self.subparsers.add_parser("flush", help="Resets instruction tracking")
        parser_flush.add_argument("package_name", metavar="<package.name>")
        parser_flush.add_argument("-d", "--device", metavar="<device>", required=False,
            help="The name of adb device/emulator.", default=None, dest="device")

    def calculate(self):
        parser_calculate = self.subparsers.add_parser("calculate", help='Calculates current probes coverage (adb logcat ACV:V "*:S")')
        parser_calculate.add_argument("package_name", metavar="<package.name>")
        parser_calculate.add_argument("-d", "--device", metavar="<device>", required=False,
            help="The name of adb device/emulator.", default=None, dest="device")

    def pull(self):
        parser_pull = self.subparsers.add_parser("pull", help="Pull execution results.")
        parser_pull.add_argument("package_name", metavar="<package.name>")
        parser_pull.add_argument("-d", "--device", metavar="<device>", required=False,
                help="The name of adb device/emulator.", default=None, dest="device")
        parser_pull.add_argument("--wd", metavar="<result_directory>", 
                default=config.default_working_dir,
                dest="working_dir", required=True, 
                help="Path to the directory where the working data is stored")
    
    def cover_pickles(self):
        cover_parser = self.subparsers.add_parser("cover-pickles", help="Apply coverage information (.ec) onto pickle files (code trees). We process files from the working directory.")
        cover_parser.add_argument("package_name", metavar="<package.name>")
        cover_parser.add_argument("-d", "--device", metavar="<device>", required=False,
                help="The name of adb device/emulator.", default=None, dest="device")
        cover_parser.add_argument("--wd", metavar="<result_directory>", 
                default=config.default_working_dir,
                dest="working_dir", required=False, 
                help="Path to the directory where the working data is stored")
                
        cover_parser.add_argument("-ts", "--timestamp", metavar="<timestamp>", required=False,
                help="choose only specified timestamp (specified in .ec file name)")
    
    def snap(self):
        parser_snap = self.subparsers.add_parser("snap", help="Saves runtime current coverage data and screen")
        parser_snap.add_argument("package_name", metavar="<package.name>")
        parser_snap.add_argument("--wd", metavar="<working_dir>", 
                default=config.default_working_dir,
                dest="working_dir", required=False, 
                help="Path to the directory where the working data is stored")
        parser_snap.add_argument("-d", "--device", metavar="<device>", required=False,
                help="The name of adb device/emulator.", default=None, dest="device")
        parser_snap.add_argument("-r", "--repeat", action="store_true", 
                help="Repeats coverage saving every 5 seconds.")
        parser_snap.add_argument("-o", metavar="<output_dir>", required=False,
                dest="output_dir", help="Output directory")
        parser_snap.add_argument("-t", "--throttle", metavar="<throttle>", required=False,
                dest="throttle", help="Delay between snaps.", default=config.throttle)

    def report(self):
        parser = self.subparsers.add_parser("report", help="Produces a report html/xml reports from covered code trees saved in 'covered_pickles' directory. Make sure to run 'cover-pickles' command.")
        parser.add_argument("package_name", metavar="<package_name>",
                help="Package name")
        parser.add_argument("-d", "--device", metavar="<device>", required=False,
                help="The name of adb device/emulator.", default=None, dest="device")
        parser.add_argument("--wd", metavar="<working_dir>", 
                default=config.default_working_dir,
                dest="working_dir", required=False, 
                help="Path to the directory where the necessary working files are organised.")
        parser.add_argument("-xml", "--xml", action="store_true", default=False,
                help="Generate XML report.")
        parser.add_argument("-html", "--html", action="store_true", default=True,
                help="Generate HTML report.")
        parser.add_argument("-g", "--granularity", metavar="<granularity>", dest="granularity",
                help="Code coverage granularity [instruction or method].", choices=Granularity.granularities(),
                default=Granularity.default)
        parser.add_argument("-s", "--stubs", metavar="<stubs>", required=False,
                help="Ignores list of stub methods. List methods signatures in txt files", default=None)
        parser.add_argument("-shrink", "--shrink", required=False, action="store_true", default=False,
                help="Keeps only executed methods in the report to ease navigation through executed code")
       
        
    def sign(self):
        parser_sign = self.subparsers.add_parser("sign", help="Signs and alignes an apk.")
        parser_sign.add_argument("apk_path", metavar="<apk_path>", help="An application's path")

    def build(self):
        parser_build = self.subparsers.add_parser("build", help="Builds a folder with an unpacked by apktool apk.")
        parser_build.add_argument("apktool_dir", metavar="<apktool_dir>", help="The path to an unpacked apk.")
        parser_build.add_argument("--rd", metavar="<result_dir>", required=False,
                dest="result_dir",
                default=config.default_working_dir,
                help="Path to the directory where the working data is stored")
        parser_build.add_argument("-s", "--s", action="store_true", help="Signs the apk produced.")
        parser_build.add_argument("-i", "--i", action="store_true",
                help="Installs the application immidiately after instrumenting.")

    def shrink(self):
        parser = self.subparsers.add_parser("shrink", help="Generates shrunk smali code from covered_pickle files. Only for analysis (would not compile).")
        parser.add_argument("--wd", metavar="<working_dir>", 
                default=config.default_working_dir,
                dest="working_dir", required=False, 
                help="Path to the directory where the working data is stored")
        parser.add_argument("package_name", metavar="<package>",
                help="Package name")
        parser.add_argument("apk_path", metavar="<path_to_original_apk>", 
                help="Path to apk file")
        parser.add_argument("-d", "--device", metavar="<device>", required=False,
                help="The name of adb device/emulator.", default=None, dest="device")
