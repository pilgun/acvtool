import os

from ..instrumenting.utils import Utils
from ..instrumenting import config


class WorkingDirectory(object):
    '''Describes the default working directory structure.'''

    def __init__(self, package, wd_path):
        if not wd_path:
            raise Exception("no working directory path given") 
        self.wd_path = wd_path
        self.package = package
        self.unpacked_apk = os.path.join(wd_path, "apktool") # sources to be processed in this dir
        self.pickle_dir = os.path.join(wd_path, "pickles")
        self.instrumented_package_path =  os.path.join(wd_path, self.package + ".apk")
        self.instrumented_apk_path = os.path.join(wd_path, "instr_{}.apk".format(self.package))
        self.manifest_path = os.path.join(self.unpacked_apk, "AndroidManifest.xml")
        self.decompiled_apk = os.path.join(self.wd_path, "dec_apk") # sources to stay original in this dir
        self.ec_dir = os.path.join(wd_path, "ec_files")
        self.images = os.path.join(wd_path, "images")
        self.report = os.path.join(wd_path, "report")
        self.short_apk_path = os.path.join(wd_path, "short.apk")
        self.stub_dir = os.path.join(wd_path, "stubs")
        self.covered_pickle_dir = os.path.join(wd_path, "covered_pickles")
        self.shrunk_pickle_dir = os.path.join(wd_path, "shrunk_pickles")
        self.cha_pickle_dir = os.path.join(wd_path, "cha_pickles")
        self.cha_apk_path = os.path.join(wd_path, "cha.apk")

    @staticmethod
    def get_manifest_path(unpacked_path):
        return os.path.join(unpacked_path, "AndroidManifest.xml")


    def get_ecs(self):
        if not os.path.exists(self.ec_dir):
            raise Exception("No such directory: {}\nConsider: $ acv snap <package> - to generate coverage .ec files".format(self.ec_dir))
        ecs = {}
        for f in os.listdir(self.ec_dir):
            id = int(f.split("_")[2][:-3])
            ec_path = os.path.join(self.ec_dir, f)
            if os.path.isfile(ec_path):
                if id not in ecs:
                    ecs[id] = []
                ecs[id].append(ec_path)
        return ecs
        #return {int(f.split("_")[1]): os.path.join(self.ec_dir, f) for f in os.listdir(self.ec_dir) if os.path.isfile(os.path.join(self.ec_dir, f))}

    def get_ecs_by_ts(self):
        ecs = {}
        for f in sorted(os.listdir(self.ec_dir)):
            ts, id = (lambda s: (int(s[1]), int(s[2][:-3])))(f.split("_"))
            ec_path = os.path.join(self.ec_dir, f)
            if os.path.isfile(ec_path):
                if ts not in ecs:
                    ecs[ts] = []
                ecs[ts].append(ec_path)
        return ecs
    

    def get_ecs_by_ts_by_dex(self):
        '''
        Grupping ec files into ec[ts][dn] by timestamp (ts),
        then by dex number (dn)
        '''
        ecs = {}
        for f in sorted(os.listdir(self.ec_dir)):
            ts, dn = (lambda s: (int(s[1]), int(s[2][:-3])))(f.split("_"))
            ec_path = os.path.join(self.ec_dir, f)
            if os.path.isfile(ec_path):
                if ts not in ecs:
                    ecs[ts] = {}
                if dn not in ecs[ts]:
                    ecs[ts][dn] = ec_path
        return ecs


    def __get_pickles(self, dir_path):
        if not os.path.exists(dir_path):
            raise Exception("No such directory: {}".format(dir_path))
        return {int(f.split("_")[1][:-7]): os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))}

    def get_pickles(self):
        return self.__get_pickles(self.pickle_dir)
    
    def get_covered_pickles(self):
        if not os.path.exists(self.covered_pickle_dir):
            raise Exception("No such directory: {}\nConsider: $ acv cover-pickles <package>".format(self.covered_pickle_dir))
        return self.__get_pickles(self.covered_pickle_dir)

    def get_shrunk_pickles(self):
        return self.__get_pickles(self.shrunk_pickle_dir)
    
    def get_smali_dirs(self, apk_dir):
        all_smali_dirs = Utils.get_smali_dirs(apk_dir)
        smali_dirs = {}
        smali_dirs[1] = os.path.join(apk_dir, config.smalidir_name)
        for i in range(2, len(all_smali_dirs)+1):
            smali_dirs[i] = os.path.join(apk_dir, config.smalidir_name + str(i))
        return smali_dirs

