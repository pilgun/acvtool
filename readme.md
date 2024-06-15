# ACVTool 2.3.2 Multidex

[![Software license](https://img.shields.io/github/license/pilgun/acvcut)](https://github.com/pilgun/acvcut/blob/master/LICENSE)
[![Python version](https://img.shields.io/badge/Python-3)]()
[![versions](https://img.shields.io/pypi/pyversions/pybadges.svg)]()
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4060443.svg)](https://doi.org/10.5281/zenodo.4060443)

`acvtool.py` instruments an Android app and produces its code coverage without original source code. Code coverage is based on Smali representation of the bytecode.

[Demonstration video of ACVTool](https://www.youtube.com/watch?v=xyaR4Ivrij0).

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
        "AAPT": "C:/users/ME/appdata/local/android/sdk/build-tools/25.0.1/aapt2.exe",
        "ZIPALIGN": "C:/users/ME/appdata/local/android/sdk/build-tools/25.0.1/zipalign.exe",
        "ADB": "C:/users/ME/appdata/local/android/sdk/platform-tools/adb.exe",
        "APKSIGNER": "C:/users/ME/appdata/local/android/sdk/build-tools/24.0.3/apksigner.bat",
        "ACVPATCHER": "D:/distr/acvpatcher.exe"
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

### Workflow

Steps:
1. Instrument the original APK with ACVTool [instrument <path> --wd <working_dir>]
2. Install the instrumented APK in the Android emulator or device. [install <path>]
3. Activate the app for coverage measurement [activate <package_name>] (alternatively, [start <package_name>])
4. Test the application (launch it!)
5. Make a snap [snap <package_name>]
6. Apply the extracted coverage data onto the smali code tree [cover-pickles <package_name> --wd <working_dir>]
6. Generate the code coverage report [report <package_name> --wd <working_dir>]

### Example: instruction coverage measurement

1. Instrument the original APK with ACVTool, and run the emulator:

    ```shell
    $ acv instrument test_apks/snake.apk --wd wd
    ```

    ```shell
    $ ANDROID_HOME/tools/emulator -avd [device-name] 
    ```

2. Install the instrumented APK in the Android emulator or device:

    ```shell
    $ acv install ./wd/instr_snake.apk
    ```

3. Activate the app:

    ```shell
    $ acv activate com.gnsdm.snake
    ```

4. Test the application. 

    Interact with the application.

5. Do the first coverage snapshot:

    ```shell
    $ acv snap com.gnsdm.snake --wd wd
    ```

6. Apply coverage data to the Smali code tree:

    ```shell
    $ acv cover-pickles com.gnsdm.snake --wd wd
    ```

7. Generate the code coverage report. 

    ```shell
    $ acv report com.gnsdm.snake --wd wd
    ```

The code coverage report is available at "./wd/report/main_index.html"

### Example: App Shrinking

- Make sure you got the `covered_pickles` files generated in previous steps.

- Generate the shrunk smali coverage report.

    ```shell
    $ acv report com.gnsdm.snake --wd wd --shrink
    ```

- Generate the shrunk app.

    ```shell
    $ acv shrink --wd wd com.gnsdm.snake test_apks/snake.apk
    ```

The shrunk version is here ./wd/shrunk.apk.

### Full list of commands
```shell
$ acv <command> <path> [-/--options]
```

  positional arguments:
  
| command      | argument     | description                              | options                              |
| :----------- | :----------- | :--------------------------------------- | :----------------------------------- |
| instrument   | path_to_apk  | Instruments an apk                       | --wd, --dbgstart, --dbgend, --r, --i |
| install      | path_to_apk  | Installs an apk.                         |                                      |
| uninstall    | path_to_apk  | Uninstalls an apk.                       |                                      |
| activate     | package_name | Prepared the app for measurements.       |                                      |
| start        | package_name | Starts runtime coverage data collection. |                                      |
| stop         | -            | Stops runtime coverage data collection.  |                                      |
| snap         | package_name | Saves coverage data.                     | --wd                                 |
| flush        | package_name | Flushes runtime coverage information.    |                                      |
| calculate    | package_name | Logs current coverage into logcat.       |                                      |
| report       | package_name | Produces a report.                       | --wd, --shrink                       |
| sign         | apk_path     | Signs and alignes an apk.                |                                      |
| shrink       | pkg, apk_pth | Generates shrunk code.                   | --wd                                 |

  optional arguments:
  
| option     | argument            | description                                                                                                                                 |
| :--------- | :------------------ | :------------------------------------------------------------------------------------------------------------------------------------------ |
| -h, --help | -                   | Shows this help message and exit.                                                                                                           |
| --version  | -                   | Shows program's version number and exits.                                                                                                   |
| --wd       | \<result_directory> | Path to the directory where the working data is stored. Default: .\smiler\acvtool_working_dir.                                              |
| --dbgstart | \<methods_number>   | For troubleshooting purposes. The number of the first method to be instrumented. Only methods from DBGSTART to DBGEND will be instrumented. |
| -r, --r    | -                   | Working directory (--wd) will be overwritten without asking.                                                                                |
| -i, --i    | -                   | Installs the application immidiately after instrumenting.                                                                                   |


## References

Please cite our paper:
```
@article{pilgun2020acvtool,
  title={Fine-grained code coverage measurement in automated black-box Android testing},
  author={Pilgun, Aleksandr and Gadyatskaya, Olga and Zhauniarovich, Yury and Dashevskyi, Stanislav and Kushniarou, Artsiom and Mauw, Sjouke},
  journal={ACM Transactions on Software Engineering and Methodology (TOSEM)},
  volume={29},
  number={4},
  pages={1--35},
  year={2020},
  publisher={ACM New York, NY, USA}
}
```
```
@inproceedings{pilgun2020acvcut,
  title={Don't Trust Me, Test Me: 100\% Code Coverage for a 3rd-party Android App},
  author={Pilgun, Aleksandr},
  booktitle={2020 27th Asia-Pacific Software Engineering Conference (APSEC)},
  pages={375--384},
  year={2020},
  organization={IEEE}
}
```

## Contributions

Contributions to ACVTool is a subject to Contributer License Agreement (to be defined).

## License

Copyright (c) 2024 Aleksandr Pilgun

Licensed under the Apache License, Version 2.0 (the "License"); you may not use ACVTool files from this repository except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

By sharing this code, the author of ACVTool does not grant or waive any patent rights beyond the scope of this ACVTool repository.

## Aknowledgement

The initial development of ACVTool took place at the University of Luxembourg as part of the FNR DroidMod 2016-2020 research project. This project would not have been possible without the invaluable support of my coauthors: Dr. Olga Gadyatskaya, Dr. Yury Zhauniarovich, and Prof. Dr. Sjouke Mauw.
