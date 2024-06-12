
import os
import time
from . import terminal

def install_multiple(apks):
    cmd = "adb install-multiple -r --no-incremental {}".format(" ".join(apks))
    out = terminal.request_pipe(cmd)
    return out

def input_text(text, sleep=0):
    os.system("adb shell input text {}".format(text))
    if sleep > 0:
        time.sleep(sleep)


def tap(x, y, sleep=0):
    os.system("adb shell input tap {} {}".format(x, y))
    if sleep > 0:
        time.sleep(sleep)


def clear_app_data(package):
    cmd = "adb shell pm clear {}".format(package)
    terminal.request_pipe(cmd)


def send_broadcast(action, package):
    #adb shell am broadcast -a 'tool.acv.snap' -n <package>/tool.acv.AcvReceiver
    #adb shell am broadcast -a 'tool.acv.snap' -p <package>
    cmd = "adb shell am broadcast -a '{}' -p '{}'".format(action, package)
    terminal.request_pipe(cmd)


def save_coverage(package):
    send_broadcast("tool.acv.snap", package)


def delete_app_sdcard_dir(package):
    cmd = "adb shell rm -rf '/sdcard/Download/{}'".format(package)
    terminal.request_pipe(cmd)


def create_app_sdcard_dir(package):
    cmd = "adb shell mkdir '/sdcard/Download/{}'".format(package)
    terminal.request_pipe(cmd)


def sd_dir_exists(package):
    cmd = "adb shell ls '/sdcard/Download/{}'".format(package)
    try:
        terminal.request_pipe(cmd)
        return True
    except Exception as ex:
        return False


def launch_app(package):
    cmd = "adb shell monkey -p '{}' 1".format(package)
    terminal.request_pipe(cmd)

