'''
`Cover`, `calculate`, `log` operations on SmaliTree. 

Input files: .pickle & .ec
'''

import logging
import os
from ..entities.coverage import CoverageData
from . import coverage
from . import binaries


def cover_pickles(wd):
    ecs = wd.get_ecs()
    if not ecs:
        logging.info("No coverage files found")
        return
    pkls = wd.get_pickles()
    covered_pkls = wd.get_covered_pickles() if os.path.exists(wd.covered_pickle_dir) else None
    total_cov_diff = CoverageData()
    for dex in ecs.keys():
        pkl_path = covered_pkls[dex] if covered_pkls else pkls[dex]
        smalitree = binaries.load_smalitree(pkl_path)
        st_cov = get_coverage_data(smalitree)
        bin_coverage = binaries.read_multiple_ec_per_tree(ecs[dex])
        prob_cov = calculate(bin_coverage)
        logging.info("ec files: {}({}), probes: {} out of {} total; {}% coverage".format(dex, len(ecs[dex]), prob_cov.covered, prob_cov.total, prob_cov.coverage()))
        log_coverage("", dex, st_cov.lines_covered, st_cov.lines, st_cov.get_line_coverage())
        coverage.cover_tree(smalitree, bin_coverage)
        new_st_cov = get_coverage_data(smalitree)
        log_coverage("new", dex, new_st_cov.lines_covered, new_st_cov.lines, new_st_cov.get_line_coverage())
        cov_diff = CoverageData.log_coverage_difference(dex, st_cov, new_st_cov)
        total_cov_diff.add_data(cov_diff, st_cov.lines, st_cov.methods, st_cov.classes)
        covered_pkl_pth = os.path.join(wd.covered_pickle_dir, os.path.basename(pkl_path))
        if cov_diff.lines_covered > 0 or not os.path.exists(covered_pkl_pth):
            binaries.save_pickle(smalitree, covered_pkl_pth)
    CoverageData.log_diff(total_cov_diff)


def log_coverage(prefix, i, lines_covered, lines, coverage):
    logging.info("{}\tst {}: {} out of {}, {}%".format(
        prefix, i, lines_covered, lines, 100*coverage)
    )


def get_coverage_data(smalitree):
    total_cd = CoverageData()
    for cl in smalitree.classes:
        coverage_data = CoverageData(
                lines=cl.coverable(),
                lines_missed=cl.not_covered(),
                lines_covered=cl.covered(),
                methods_covered=cl.mtds_covered(),
                methods_missed=cl.mtds_not_covered(),
                methods=cl.mtds_coverable()
            )
        coverage_data.update_coverage_for_single_class_from_methods()
        total_cd.add_data(coverage_data)
    return total_cd

def cover_tree(st, ec_coverage):
    cov_iterator = enumerate(ec_coverage)
    for cl in st.classes:
        if cl.is_coverable():
            cov_class = next(cov_iterator)[1]
            for m in cl.methods:
                # print not executed methods
                # if m.cover_code > -1 and not m.called and cov_class[m.cover_code]:
                #     print("{}->{}".format(cl.name, m.descriptor))
                m.called = m.cover_code > -1 and (m.called or cov_class[m.cover_code])
                for ins in m.insns:
                    ins.covered = ins.cover_code > -1 and (ins.covered or cov_class[ins.cover_code])
                for lbl in m.labels.values():
                    lbl.covered = lbl.cover_code > -1 and (lbl.covered or cov_class[lbl.cover_code])


def nullify_smalitree_coverage(st):
    for cl in st.classes:
        for m in cl.methods:
            m.called = False
            for ins in m.insns:
                ins.covered = False
            for lbl in m.labels.values():
                lbl.covered = False
    

def calculate(bin_coverage):
    covered_insns = 0
    total_insns = 0
    for cl in bin_coverage:
        class_covered_insns = sum(cl)
        class_insns = len(cl)
        covered_insns += class_covered_insns
        total_insns += class_insns
    return ProbesCoverage(covered_insns, total_insns)


class ProbesCoverage(object):
    def __init__(self, covered=0, total=0):
        self.covered = covered
        self.total = total

    def coverage(self):
        return 100*float(self.covered)/self.total
