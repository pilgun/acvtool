import logging
import os
from ..operations import terminal
from ..libs.libs import Libs

def decode(unpacked_apk, dex_filenames, remove_dex=False):
    smali_dirpaths = []
    for dex in dex_filenames:
        smali_dir = dex.replace(".dex", "")
        smali_dirpaths.append(smali_dir)
        decode_single_dex(dex, smali_dir)
        if remove_dex:
            os.remove(dex)
    return smali_dirpaths

def decode_single_dex(dex_path, smali_dir):
    os.makedirs(smali_dir, exist_ok=True)
    cmd = 'java -jar "{}" disassemble "{}" -o "{}" -l'.format(Libs.BAKSMALI_PATH, dex_path, smali_dir)
    terminal.request_pipe(cmd)
    return smali_dir

def build(smali_dirs):
    dex_filepaths = []
    for smali_dir_path in smali_dirs:
        dex_path = smali_dir_path + ".dex"
        if os.path.exists(dex_path):
            os.remove(dex_path)
        cmd = 'java -jar "{}" assemble "{}" -o "{}"'.format(Libs.SMALI_PATH, smali_dir_path, dex_path)
        terminal.request_pipe(cmd)
        logging.info("built dex file: {}".format(dex_path))
        dex_filepaths.append(dex_path)
    return dex_filepaths