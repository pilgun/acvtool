import os
import time
from ..config import config
from . import terminal


def install_multiple(apks):
    cmd = "{} install-multiple -r --no-incremental {}".format(config.adb_path, " ".join(apks))
    out = terminal.request_pipe(cmd)
    return out


def input_text(text, sleep=0):
    os.system("{} shell input text {}".format(config.adb_path, text))
    if sleep > 0:
        time.sleep(sleep)


def tap(x, y, sleep=0):
    os.system("{} shell input tap {} {}".format(config.adb_path, x, y))
    if sleep > 0:
        time.sleep(sleep)


def clear_app_data(package):
    cmd = "{} shell pm clear {}".format(config.adb_path, package)
    terminal.request_pipe(cmd)


def send_broadcast(action, package):
    #adb shell am broadcast -a 'tool.acv.snap' -n <package>/tool.acv.AcvReceiver
    #adb shell am broadcast -a 'tool.acv.snap' -p <package>
    cmd = "{} shell am broadcast -a '{}' -p '{}'".format(config.adb_path, action, package)
    terminal.request_pipe(cmd)


def save_coverage(package):
    send_broadcast("tool.acv.snap", package)


def delete_app_sdcard_dir(package):
    if not package:
        raise Exception("Package name is empty!")
    cmd = "{} shell rm -rf '/sdcard/Download/{}'".format(config.adb_path, package)
    terminal.request_pipe(cmd)


def create_app_sdcard_dir(package):
    cmd = "{} shell mkdir '/sdcard/Download/{}'".format(config.adb_path, package)
    terminal.request_pipe(cmd)


def sd_dir_exists(package):
    cmd = "{} shell ls '/sdcard/Download/{}'".format(config.adb_path, package)
    try:
        terminal.request_pipe(cmd)
        return True
    except Exception as ex:
        return False
