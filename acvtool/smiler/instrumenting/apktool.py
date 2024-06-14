import logging
import shutil
import os
from ..operations import terminal
from ..libs.libs import Libs

def decode(apk_path, result_dir):
    # javaOpts = "-Xms512m -Xmx1024m"
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    cmd = 'java -jar "{}" d "{}" -o "{}"'.format(Libs.APKTOOL_PATH, apk_path, result_dir)
    terminal.request_pipe(cmd)

def decode_no_res(apk_path, result_dir):
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    cmd = f'java -jar "{Libs.APKTOOL_PATH}" d --no-res "{apk_path}" -o "{result_dir}"'
    terminal.request_pipe(cmd)

def unpack(apk_path, result_dir):
    cmd = 'java -jar "{}" -r -s d "{}" -o "{}"'.format(Libs.APKTOOL_PATH, apk_path, result_dir)
    terminal.request_pipe(cmd)

def build(dir_path, output_apk):
    logging.info("building")
    cmd = 'java -jar "{}" --use-aapt2 b "{}" -o "{}"'.format(Libs.APKTOOL_PATH, dir_path, output_apk)
    terminal.request_pipe(cmd)
