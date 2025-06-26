import os
import sys
import shutil
import json
import logging
from pathlib import Path

from importlib import resources
from os.path import expanduser


class config(object):
    @staticmethod
    def get_resource(folder, filename):
        with resources.path(folder, filename) as file_path:
            return str(file_path)

    dir_path = os.path.join(expanduser("~"), 'acvtool')
    if not os.path.exists(dir_path):
        logging.info('Creating acvtool directory in the user home directory')
        os.makedirs(dir_path)
    config_path = os.path.join(dir_path, 'config.json')
    if not os.path.exists(config_path):
        shutil.copy(get_resource('acvtool.smiler', 'config.json'), config_path)
        logging.info("config.json config was created in the {}.".format(dir_path))
    with open(config_path) as json_file:
        config_data = json.load(json_file)

    INSTRUMENTING_NAME = "tool.acv.AcvInstrumentation"
    
    instrumenting_class_dir_path = get_resource('acvtool.smiler.resources.instrumentation', 'smali')
    html_resources_dir_path = get_resource('acvtool.smiler.resources.html', '.resources')
    templates_path = get_resource('acvtool.smiler.resources.html', 'templates')
    keystore_path = get_resource('acvtool.smiler', 'keystore')
    keystore_password = '123456'
    
    adb_path = Path(config_data["ADB"])
    aapt_path = Path(config_data["AAPT"])
    acvpatcher = Path(config_data["ACVPATCHER"])

    version = "2.3.4"
    logging_yaml = resources.path('acvtool.smiler.resources', 'logging.yaml')

    default_working_dir = os.path.join(dir_path, "acvtool_working_dir")
    default_report_dir = os.path.join(default_working_dir, "report")
    default_onstop_timeout = 240

    throttle = 10
    
    # 65535 is the max number of methods in DEX, 11 is the number of methods acvtool adds to the app
    METHOD_LIMIT = 50000 # 65535-11

    @staticmethod
    def get_logging_yaml():
        with resources.path("acvtool.smiler.resources", "logging.yaml") as yaml_path:
            return str(yaml_path)

    @staticmethod
    def get_ec_dir(output_dir, package):
        return os.path.join(output_dir, package, "ec_files")
    

    @staticmethod
    def get_images_dir(output_dir, package):
        return os.path.join(output_dir, package, "images")
    
    @staticmethod
    def check_tools():
        err = False
        if not os.path.exists(config.adb_path):
            err = True
            logging.error("adb tool was not found at {}".format(config.adb_path))
        if not os.path.exists(config.aapt_path):
            err = True
            logging.error("aapt tool was not found at {}".format(config.aapt_path))
        if not os.path.exists(config.acvpatcher):
            err = True
            if config.acvpatcher == "acvpatcher":
                logging.error("acvpatcher path is not set in the config.json")
            else:
                logging.error("acvpatcher was not found at {}".format(config.acvpatcher))
        if err:
            logging.error("\nCONFIGURATION ERROR: Please check paths at {} or/and install required software (consult README.md for details).\n".format(config.config_path))
            sys.exit()

config.check_tools()
