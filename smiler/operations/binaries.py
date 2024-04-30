import os
import logging
import javaobj
import pickle


def read_ec(ec_path):
    pobj = ''
    with open(ec_path, mode='rb') as f:
        marshaller = javaobj.JavaObjectUnmarshaller(f)
        pobj = marshaller.readObject()
    return pobj


def read_multiple_ec_per_tree(ec_pths):
    total_bin_coverage = []
    for p in ec_pths:
        single_bin_coverage = read_ec(p)
        #logging.info(p)
        total_bin_coverage = sum_ec_bin_arrays(total_bin_coverage, single_bin_coverage)
        #coverage.calculate(total_bin_coverage)
    return total_bin_coverage



def sum_ec_bin_arrays(total_bin_coverage, single_bin_coverage):
    if not total_bin_coverage:
        return single_bin_coverage
    for i in range(len(total_bin_coverage)):
        for j in range(len(total_bin_coverage[i])):
            total_bin_coverage[i][j] |= single_bin_coverage[i][j]
    return total_bin_coverage


def save_pickle(smalitree, path):
    if os.path.exists(path):
        os.remove(path)
    dir_path = os.path.dirname(path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    if not os.path.exists(path):
        #clean_smalitree_buf(smalitree)
        with open(path, 'wb') as f:
                pickle.dump(smalitree, f, pickle.HIGHEST_PROTOCOL)
        logging.info('pickle file saved: {0}'.format(path))


def clean_smalitree_buf(smalitree):
    for cl in smalitree.classes:
        cl.buf = []
        for m in cl.methods:
            m.buf = []


def load_smalitree(pickle_path):
    logging.info("deserialise: {}".format(pickle_path))
    with open(pickle_path, 'rb') as f:
        st = pickle.load(f)
        return st


def read_file(path):
    with open(path, 'r') as file:
        data = file.read()
        return data

def save_list(path, entities_list):
    str_list = "\n".join(entities_list)
    with open(path, 'w') as f:
        f.write(str_list)
