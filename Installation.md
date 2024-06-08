## Prerequisites
1. `Windows`/`OSX`/`Ubuntu`.
3. `Java` version `1.8`.
2. `Android SDK`.
4. `Python 3`.

## Installation
1. Run the `pip` command to install dependencies:

    ```shell
    $ cd acvtool
    $ pip install -e .
    $ acv -h
    ```

    When successfully installed, you will be able to execute `acv -h`. This command will create the working directory "\~/acvtool" and the configuration file "\~/acvtool/config.json". 

2. Download the [ACVPatcher](https://github.com/pilgun/acvpatcher/releases) binary for your system. ACVPatcher replaces usage of Apktool, zipalign, apksigner. ACVPatcher is a separated binary since it was implemented with .NET Core.

    ACVPatcher needs to be trusted to work:
    - (OSX/Linux) `chmod +x acvpatcher`
    - Call the Context Menu, Tap Open, Open the App From Not Trusted Developer

3. Specify absolute paths to the Android tools at "~/acvtool/config.json" (%userprofile%\acvtool\config.json in Windows) for the following variables.
    * AAPT
    * ZIPALIGN
    * ADB
    * APKSIGNER
    * ACVPATCHER

    3.1. Windows configuration example

    ```json
    {
        "AAPT": "[%userprofile%]\\appdata\\local\\android\\sdk\\build-tools\\25.0.1\\aapt2.exe",
        "ZIPALIGN": "[%userprofile%]\\appdata\\local\\android\\sdk\\build-tools\\25.0.1\\zipalign.exe",
        "ADB": "[%userprofile%]\\appdata\\local\\android\\sdk\\platform-tools\\adb.exe",
        "APKSIGNER": "[%userprofile%]\\appdata\\local\\android\\sdk\\build-tools\\24.0.3\\apksigner.bat",
        "ACVPATCHER": "D:\\distr\\acvpatcher.exe"
    }
    ```
    3.2. OSX, Linux configuration example

    ```json
    {
        "AAPT": "[$HOME]/Library/Android/sdk/build-tools/25.0.3/aapt2",
        "ZIPALIGN": "[$HOME]/Library/Android/sdk/build-tools/25.0.3/zipalign",
        "ADB": "[$HOME]/Library/Android/sdk/platform-tools/adb",
        "APKSIGNER": "[$HOME]/Library/Android/sdk/build-tools/24.0.3/apksigner",
        "ACVPATCHER": "~/distr/ACVPatcher-osx/acvpatcher"
    }
    ```