
from ..config import config
from ..operations import terminal

def patch_apk(apk_path, dex_filepaths):
    classes_dex = ' '.join([f'"{d}"' for d in dex_filepaths])
    cmd = '"{}" -c {} -p {} -i {} -r {} -a "{}"'.format(config.acvpatcher,
        classes_dex,
        "android.permission.WRITE_EXTERNAL_STORAGE",
        "tool.acv.AcvInstrumentation",
        "tool.acv.AcvReceiver:tool.acv.calculate tool.acv.AcvReceiver:tool.acv.snap tool.acv.AcvReceiver:tool.acv.flush",
        apk_path)
    terminal.request_pipe(cmd)