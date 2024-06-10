import os
import re
import zipfile

class ZipReader (object):

    def __init__(self, zip_path, unpacked_dir):
        self.zip_path = zip_path
        self.unpacked_dir = unpacked_dir
        self.names = self._readfiles()
        self.dex_filenames = [name for name in self.names if name.endswith('.dex')]
        self.is_multidex = len(self.dex_filenames) > 1
        self.max_dex_number = self._get_max_dex_number()
        self.acv_classes_dir_name = "classes{}".format(self.max_dex_number + 1)
        self.acv_classes_dir = os.path.join(self.unpacked_dir, self.acv_classes_dir_name)
        self.acv_extra_dirs = []
        self.extra_dirs = []


    def _get_max_dex_number(self):
        match = re.compile(r'classes(\d+).dex').match
        dex_numbers = []
        for dex_name in self.dex_filenames:
            res = match(dex_name)
            if res:
                dex_numbers.append(int(res.group(1)))
            else:
                dex_numbers.append(1)
        return max(dex_numbers)

    def _generate_next_classes_dir(self):     # 1-indexed: prime acv_classes_dir
        next_dex_number = self.max_dex_number + 1 + len(self.acv_extra_dirs) + len(self.extra_dirs) + 1
        next_classes_dir_name = "classes{}".format(next_dex_number)
        next_classes_dir = os.path.join(self.unpacked_dir, next_classes_dir_name)
        return next_classes_dir
    
    def add_next_acv_classes_dir(self):
        next_classes_dir = self._generate_next_classes_dir()
        self.acv_extra_dirs.append(next_classes_dir)
        return next_classes_dir
    
    def add_next_classes_dir(self):
        next_classes_dir = self._generate_next_classes_dir()
        self.extra_dirs.append(next_classes_dir)
        return next_classes_dir

    def _readfiles(self):
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            return zip_ref.namelist()

    def extract(self, output_dir, tgt_dexes=[]):
        extracted_files = []
        dex_names_to_extract = tgt_dexes if tgt_dexes else self.dex_filenames
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            for tgt_dex in dex_names_to_extract:
                extracted_file_path = os.path.join(output_dir, tgt_dex)
                zip_ref.extract(tgt_dex, output_dir)
                extracted_files.append(extracted_file_path)
        return extracted_files
    
    def get_acv_classes_dirs(self):
        return [self.acv_classes_dir] + self.acv_extra_dirs

    def get_extra_classes_dirs(self):
        return self.extra_dirs