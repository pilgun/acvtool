from importlib import resources

class Libs:
    @staticmethod
    def smali_path():
        return resources.files("acvtool.smiler.libs.jars").joinpath("smali-3.0.9-dev-fat.jar")

    @staticmethod
    def baksmali_path():
        return resources.files("acvtool.smiler.libs.jars").joinpath("baksmali-3.0.9-dev-fat.jar")

    @staticmethod
    def smali():
        with resources.as_file(Libs.smali_path()) as path:
            return str(path)

    @staticmethod
    def baksmali():
        with resources.as_file(Libs.baksmali_path()) as path:
            return str(path)