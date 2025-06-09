import os
import sys

from pkg_resources import resource_filename

class Libs:
    SMALI_PATH = resource_filename("acvtool.smiler.libs.jars", "smali-3.0.9-dev-fat.jar")
    BAKSMALI_PATH = resource_filename("acvtool.smiler.libs.jars", "baksmali-3.0.9-dev-fat.jar")
