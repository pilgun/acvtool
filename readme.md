# ACVTool

`acvtool.py` instruments Android apk and produces its code coverage without original source code. Code coverage is based on Smali representation of the bytecode.

## Prerequisites
1. `Windows`/`OSX`/`Ubuntu`.
3. `Java` version `1.8`.
2. `Android SDK`.
4. `Python` version  `2.7`.

## Installation
1. Run the `pip` command to install dependencies:

    ```shell
    $ cd acvtool
    $ pip install -e .
    $ acv -h
    ```

When successfully installed, you will be able to execute `acv -h`. This command will create the working directory "~/acvtool" and the configuration file "~/acvtool/config.json". 

2. Specify absolute paths to the Android tools at "~/acvtool/config.json" (%userprofile%\acvtool\config.json in Windows) for the following variables.
    * AAPT
    * ZIPALIGN
    * ADB
    * APKSIGNER

2.1. Windows configuration example

    ```json
    {
        "AAPT": "[%userprofile%]\\appdata\\local\\android\\sdk\\build-tools\\25.0.1\\aapt.exe",
        "ZIPALIGN": "[%userprofile%]\\appdata\\local\\android\\sdk\\build-tools\\25.0.1\\zipalign.exe",
        "ADB": "[%userprofile%]\\appdata\\local\\android\\sdk\\platform-tools\\adb.exe",
        "APKSIGNER": "[%userprofile%]\\appdata\\local\\android\\sdk\\build-tools\\24.0.3\\apksigner.bat",
    }
    ```
2.2. OSX, Linux configuration example

    ```json
    {
        "AAPT": "[$HOME]/Library/Android/sdk/build-tools/25.0.3/aapt",
        "ZIPALIGN": "[$HOME]/Library/Android/sdk/build-tools/25.0.3/zipalign",
        "ADB": "[$HOME]/Library/Android/sdk/platform-tools/adb",
        "APKSIGNER": "[$HOME]/Library/Android/sdk/build-tools/24.0.3/apksigner",
    }
    ```



### Workflow

Steps:
1. Instrument the original APK with ACVTool. [instrument <path>]
2. Install the instrumented APK in the Android emulator or device. [install <path>]
3. Initiate instrumentation process in the emulator. [start <package>]
4. Test the application. (just click the installed app)
5. Finish instrumention process in the emulator. [Press Ctrl+C]
6. Generate coverage report. [report <package> -p <pickle_path>]

Instrument an apk:

    ```shell
    $ acv instrument <path>
    ```

An APK file and \<package_name>.pickle file will be created.

Install/uninstall the app in emulator/device:

    ```shell
    $ acv install <path>
    $ acv uninstall <path>
    ```

Initiate instrumentation process of the APK:

    ```shell
    $ acv start <package.name>
    ```

Now the application must be tested manually or automatically. Acvtool itself does not provide the strategies for testing. Finish instrumentation process to generate coverage file by Ctrl+C.
Generate coverage report after tesing of apk:

    ```shell
    $ acv report <package.name> -p <path>
    ```

### Example

1. Instrument the original APK with ACVTool, and run the emulator:

    ```shell
    $ acv instrument test_apks/snake.apk
    ```

    ```shell
    $ emulator -avd [device-name] &
    ```

2. Install the instrumented APK in the Android emulator or device:

    ```shell
    $ acv install ~/acvtool/acvtool_working_dir/instr_snake.apk
    ```

3. Initiate instrumentation process in the emulator:

    ```shell
    $ acv start com.gnsdm.snake
    ```

4. Test the application. 

    Interact with the application a little bit.

5. Finish instrumention process in the emulator. 
    
    Press "Ctrl+c" in the console where the acvtool has been launched with "acv start".

6. Generate the coverage report. 

    ```shell
    $ acv report com.gnsdm.snake -p  ~/acvtool/acvtool_working_dir/metadata/com.gnsdm.snake.pickle
    ```

The coverage report will be located at "~/acvtool/acvtool_working_dir/report/com.gnsdm.snake/report"

###

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
| start        | package.name | Starts runtime coverage data collection. |                                      |
| stop         | -            | Stops runtime coverage data collection.  |                                      |
| report       | package_name | Produces a report.                       | -p(required), -o, -ec                |
| sign         | apk_path     | Signs and alignes an apk.                |                                      |

  optional arguments:
  
| option     | argument            | description                                                                                                                                 |
| :--------- | :------------------ | :------------------------------------------------------------------------------------------------------------------------------------------ |
| -h, --help | -                   | Shows this help message and exit.                                                                                                           |
| --version  | -                   | Shows program's version number and exits.                                                                                                   |
| --wd       | \<result_directory> | Path to the directory where the working data is stored. Default: .\smiler\acvtool_working_dir.                                              |
| --dbgstart | \<methods_number>   | For troubleshooting purposes. The number of the first method to be instrumented. Only methods from DBGSTART to DBGEND will be instrumented. |
| -r, --r    | -                   | Working directory (--wd) will be overwritten without asking.                                                                                |
| -i, --i    | -                   | Installs the application immidiately after instrumenting.                                                                                   |
| -p         | \<pickle_file>      | Path to the Pickle file, that was generated during the instrumentation process (required).                                                  |
| -o         | <output_dir>        | Output directory.                                                                                                                           |
| -ec        | <ec_dir>            | The directory with the code coverage binary files pre-loaded from the emulator.                                                             |

## Dependencies

* [apkil](https://github.com/kelwin/apkil)
* [Apktool](https://ibotpeaches.github.io/Apktool/)

## Reference

ACVTool will be demonstrated at ACM Conference on Computer and Communications Security 2018, Toronto, October 15-19.
Link to the paper and bibtex reference will soon appear here.

The citation of the paper is highly appreciated.

## License

Copyright © 2018 SnT, University of Luxembourg

Licensed under the Apache License, Version 2.0 (the "License");
you may not use the files under this repository except in compliance with 
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
