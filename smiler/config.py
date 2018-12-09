import os
import sys
import shutil
import json
import logging

from pkg_resources import resource_filename
from os.path import expanduser


class config(object):

    dir_path = os.path.join(expanduser("~"), 'acvtool')
    if not os.path.exists(dir_path):
        logging.info('Creating acvtool directory in the user home directory')
        os.makedirs(dir_path)
    config_path = os.path.join(dir_path, 'config.json')
    if not os.path.exists(config_path):
        shutil.copy(resource_filename("smiler", "config.json"), config_path)
        logging.info("config.json config was created in the {}.".format(dir_path))
    with open(config_path) as json_file:
        config_data = json.load(json_file)

    APKTOOL_JAVA_PATH = "java" # it is possible that some tools will require different versions of java
    APKTOOL_JAVA_OPTS = "-Xms512m -Xmx1024m"
    APKTOOL_QUITE = "True"

    INSTRUMENTING_NAME = "tool.acv.AcvInstrumentation"
    
    instrumenting_class_dir_path = resource_filename('smiler.resources.instrumentation', 'smali')
    html_resources_dir_path = resource_filename('smiler.resources.html', '.resources')
    templates_path = resource_filename('smiler.resources.html', 'templates')
    keystore_path = resource_filename('smiler', 'keystore')
    keystore_password = '123456'
    
    apksigner_path = config_data["APKSIGNER"]
    adb_path = config_data["ADB"]
    aapt_path = config_data["AAPT"]
    zipalign = config_data["ZIPALIGN"]

    version = "0.2"
    logging_yaml = resource_filename('smiler.resources', 'logging.yaml')

    default_working_dir = os.path.join(dir_path, "acvtool_working_dir")
    default_report_dir = os.path.join(default_working_dir, "report")
    default_onstop_timeout = 240

    @staticmethod
    def get_ec_dir(output_dir, package):
        return os.path.join(output_dir, package, "ec_files")
    
    def check_tools(self):
        err = False
        if not os.path.exists(config.apksigner_path):
            err = True
            logging.error("apksigner was not found at {}".format(config.apksigner_path))
        if not os.path.exists(config.adb_path):
            err = True
            logging.error("adb tool was not found at {}".format(config.adb_path))
        if not os.path.exists(config.aapt_path):
            err = True
            logging.error("aapt tool was not found at {}".format(config.aapt_path))
        if not os.path.exists(config.zipalign):
            err = True
            logging.error("zipalign was not found at {}".format(config.zipalign))
        if err:
            logging.error("\nCONFIGURATION ERROR: Please check paths at {} or/and install required software.\n".format(self.config_path))
            sys.exit()

cf = config()
cf.check_tools()
