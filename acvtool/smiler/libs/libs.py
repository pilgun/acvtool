import os
import sys

from pkg_resources import resource_filename

class Libs:
    APKTOOL_PATH = resource_filename("acv.smiler.libs.jars", "apktool_2.9.3.jar")
    SMALI_PATH = resource_filename("acv.smiler.libs.jars", "smali-3.0.7-1c13925b-dirty-fat.jar")
    BAKSMALI_PATH = resource_filename("acv.smiler.libs.jars", "baksmali-3.0.7-1c13925b-dirty-fat.jar")
