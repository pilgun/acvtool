import logging
from ..smiler.instrumenting.smali_instrumenter import Instrumenter
from ..smiler.instrumenting.utils import Utils
from ..smiler.operations import binaries
from . import basic_block


def shrink_smali(wd, pickle_files):
    '''Saves shrunk version of smali files.
       This implementation only removes not executed classes, methods and instructions in a dull way.
       The resulting code may not compile because some instructions still reference removed classes.
       ACVCut implementation was more sophisticated targeting to keep the shrunk app executable.
    '''
    smali_dirs = Utils.get_smali_dirs(wd.unpacked_apk)
    if smali_dirs:
        for sd in smali_dirs:
            Utils.rm_if_exists(sd)
    min_pickle = min(pickle_files.keys())
    max_pickle = max(pickle_files.keys())
    for treeId in range(min_pickle, max_pickle+1):
        if treeId not in pickle_files:
            continue
        smalitree = binaries.load_smalitree(pickle_files[treeId])
        shrink_smalitree(smalitree)
        smali_instrumenter = Instrumenter(smalitree, "", "instruction", wd.package)
        smali_instrumenter.save_instrumented_smalitree_by_class(smalitree, 0, instrument=False)
    logging.info("smali saved: {}".format(wd.unpacked_apk))


def shrink_smalitree(smalitree):
    remove_not_executed_methods_and_classes(smalitree)
    basic_block.remove_blocks_from_selected_method(smalitree)


def remove_not_executed_methods_and_classes(smalitree):
    '''Remove not executed methods and classes (for visualisation only).'''
    for cl in smalitree.classes[:]:
        if cl.covered() == 0:
            print(cl.name)
            smalitree.classes.remove(cl)
        else:
            for m in cl.methods[:]:
                if m.covered() == 0:
                    cl.methods.remove(m)