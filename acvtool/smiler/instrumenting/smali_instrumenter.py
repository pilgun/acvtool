import os
import re
import sys
import logging

from .apkil import constants
from pkg_resources import resource_filename
from ..operations import binaries
from .utils import Utils
from .core.acv_classes import AcvReporter
from ..granularity import Granularity

from .config import prefix_smdir_name_len
from .config import smalidir_name
from .core.method_instrumenter import MethodInstrumenter
from .core.class_instrumenter import ClassInstrumenter


class Instrumenter(object):
    ''' Instrumenter consists of instrumenting code to track smali instructions in
    smalitree.'''

    
    dir_path = sys.path[0]
    instrumentation_smali_path = resource_filename('acvtool.smiler.resources.instrumentation', 'smali')

    def __init__(self, smalitree, granularity, package, dbg_start=None, dbg_end=None, mem_stats=None, target_cl=None, target_mtd=None):
        self.smalitree = smalitree
        self.granularity = Granularity.GRANULARITIES[granularity]
        self.insns = []
        self.class_traces = []
        self.package = package
        self.dbg = dbg_start is not None
        self.dbg_start = dbg_start
        self.dbg_end = dbg_end
        self.mem_stats = mem_stats
        self.target_sm_cl = target_cl #Instrumenter.extract_target_sm_class(target_cl) if target_cl is not None else None
        self.target_sm_mtd = target_mtd #Instrumenter.extract_target_sm_mtd(target_cl, target_mtd) if target_mtd is not None and target_cl is not None else None
        self.class_info_list = []
        self.methodInstr = MethodInstrumenter(self.granularity)
        self.classInstr = ClassInstrumenter(self.methodInstr, self.target_sm_mtd)


    @staticmethod
    def extract_target_sm_class(target_cl):
        '''Converts java-ish class name to smali representation.'''
        "android.support.multidex.a -> Landroid/support/multidex/a;"
        return "L{};".format(target_cl.replace(".", "/"))
    
    @staticmethod
    def extract_target_sm_mtd(target_cl, target_mtd):
        '''Converts java-ish method name to smali representation.'''
        "void android.support.multidex.a.g(android.content.Context) -> g(Landroid/content/Context;)V"
        ret_type, method_name = target_mtd.split()
        if ret_type in constants.BASIC_TYPES_BY_JAVA:
            ret_type = constants.BASIC_TYPES_BY_JAVA[ret_type]
        else:
            ret_type = "L" + ret_type.replace(".", "/")
        method_name = method_name[len(target_cl)+1:-1].replace("(", "(L", 1).replace(".", "/") + ";)" + ret_type
        return method_name


    def save_instrumented_smalitrees(self):
        '''- Inserts tracking probes into smali code trees. 
        - Updates class_info_list for future covered code mapping. 
        - Adds AcvReporter classes.'''
        method_number = 0
        #last_class_info = None
        classes_info = self.save_instrumented_smalitree_by_class(self.smalitree, method_number, instrument=True)
        return classes_info


    def save_instrumented_smalitree_by_class(self, tree, method_number=0, instrument=True):
        '''Saves instrumented smali to the specified directory/'''
        output_dir = tree.foldername
        logging.info("saving instrumented smali: {}".format(output_dir))
        Utils.recreate_dir(output_dir)
        classes_info = []
        class_number = 0 # to make array name unique
        # Helps to find specific method that cased a fail after the instrumentation.
        # See '# Debug purposes' below
        #method_number = method_number
        # dbg_ means specific part of the code defined by dbg_start-dbg_end
        # numbers will be instrumented
        dbg_instrument = instrument
        # if last_class_info:
        #     cl_name, cover_index, class_number= last_class_info
        #     class_number += 1
        #temp_class = self.smalitree.classes[4]
        #print(temp_class.methods[2].insns[0].cover_code)
        for class_ in tree.classes:
            code, cover_index, method_number, is_instrumented = self.classInstr.instrument_class(
                tree.Id,
                class_, 
                class_number, 
                method_number=method_number,
                instrument=dbg_instrument and not class_.ignore and (self.target_sm_cl is None or self.target_sm_cl == class_.name),
                dbg_start=self.dbg_start, 
                dbg_end=self.dbg_end)
            tree.instrumented_method_number = method_number
            if dbg_instrument and class_.is_coverable(): # is_instrumented
                classes_info.append((class_.name, cover_index, class_number))
                class_number += 1
            class_path = os.path.join(output_dir, class_.folder, class_.file_name)
            Instrumenter.save_class(class_path, code)
            if self.dbg and dbg_instrument and method_number > self.dbg_end: # Now leave other code not instrumented.
                dbg_instrument = False
        if self.dbg:
            print("Number of methods instrumented: {0}-{1} from {2}".format(self.dbg_start, self.dbg_end, method_number))
        return classes_info


    def save_reporter_array_stats(self, classes_info, verbose=False):
        log_path = os.path.join("allocation_log.csv")
        csv_text = ""
        if self.mem_stats == "verbose":
            entries = ["{},{},{}".format(self.package, cl[0], cl[1]) for cl in classes_info]
            csv_text = "\n".join(entries)
        else:
            memory = sum(cl[1] for cl in classes_info)
            logging.info("{} bytes allocated in AcvReporter.smali".format(memory))
            csv_text = "{},{}".format(self.package, memory)
        Utils.log_entry(log_path, csv_text+'\n')
  

    @staticmethod
    def save_class(output_path, smali_code):
        '''Save instrumented Smali class file.'''
        file_dir = os.path.dirname(output_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(output_path, 'w') as f:
            f.write(smali_code)

    def save_pickle(self, pickle_dir):
        '''Saves source Smali code and links to the tracked instructions.'''
        if not os.path.exists(pickle_dir):
            os.makedirs(pickle_dir)
        pth = os.path.join(pickle_dir, "{}_{}.pickle".format(self.package, self.smalitree.Id))
        binaries.save_pickle(self.smalitree, pth)
