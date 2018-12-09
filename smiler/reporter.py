import os
import sys
import cgi
import smiler
from config import config
import javaobj
import cPickle as pickle
import shutil
import logging
from operator import attrgetter
from granularity import Granularity
from coverage import CoverageData
from instrumenting.apkil.smalitree import SmaliTree
from chameleon import PageTemplateLoader
from chameleon.utils import Markup
from instrumenting.utils import Utils as Utils2
from serialisation.xml_serialiser import XmlSerialiser
import re

COV_CLASS = 'cov' #html class, ex: '<span class="%COV_CLASS%"/>'
EXEC_CLASS = 'exec'
not_instr_regex = re.compile("^(move-result|move-exception).*$")

def generate(package, pickle_path, output_dir, ec_dir=None, xml=True, html=True, granularity="instruction"):
    report_dir = os.path.join(output_dir, package, 'report')
    if ec_dir is None:
        ec_dir = config.get_ec_dir(output_dir, package)
        smiler.get_execution_results(package, ec_dir)
    recreate_dir(report_dir)
    logging.info("report generating...")
    ec_files = [os.path.join(ec_dir, f) for f in os.listdir(ec_dir) if os.path.isfile(os.path.join(ec_dir, f))]
    smalitree = get_covered_smalitree(ec_files, pickle_path)
    granularity = Granularity.GRANULARITIES[granularity]
    if html:
        save_html_report(report_dir, smalitree, package, granularity)
    if xml:
        save_xml_report(report_dir, smalitree, package, granularity)
    logging.info("report saved: {0}".format(report_dir))


def get_covered_smalitree(ec_files, pickle_path):
    st = None
    with open(pickle_path, 'rb') as f:
        st = pickle.load(f)
    for ec in ec_files:
        coverage = read_ec(ec)
        cover_smalitree(st, coverage)
    return st

def generate_xml(smalitree, app_name, granularity):
    serialiser = XmlSerialiser(smalitree, app_name, granularity)
    xml = serialiser.get_xml()
    return xml

def save_xml_report(output_dir, smalitree, app_name, granularity):
    xml = generate_xml(smalitree, app_name, granularity)
    path = os.path.join(output_dir, 'acvtool-report.xml')

    with open(path, 'w') as f:
        f.write(xml)

def save_html_report(output_dir, smalitree, app_name, granularity):
    templates = PageTemplateLoader(config.templates_path)
    resources_dir = os.path.join(output_dir, '.resources')
    Utils2.copytree(config.html_resources_dir_path, resources_dir)

    class_template = templates['class.pt']

    for cl in smalitree.classes:
        save_class(cl, class_template, output_dir, app_name, granularity)

    save_coverage(smalitree, templates, output_dir, app_name, granularity)

def save_coverage(tree, templates, output_dir, app_name, granularity):
    groups = Utils2.get_groupped_classes(tree)
    init_row = templates['init_row.pt']
    init_table = templates['init_table.pt']
    index_template = templates['index.pt']

    rows = []
    total_coverage_data = CoverageData()
    for g in groups:
        (package, path, coverage_data) = save_package_indexhtml(g, templates, output_dir, app_name, granularity)
        coverage = coverage_data.get_formatted_coverage(granularity)
        row = init_row(elementlink=path, type='package', elementname=package,
                  coverage=coverage,
                  respath='', coverage_data=coverage_data,
                  is_instruction_level=Granularity.is_instruction(granularity),
                  progress_covered=coverage_data.covered(granularity),
                  progress_missed=coverage_data.missed(granularity))
        rows.append(Markup(row))
        total_coverage_data.add_data(coverage_data)
    total_coverage = total_coverage_data.get_formatted_coverage(granularity)
    table = init_table(rows=Markup("\n".join(rows)),
                        total_coverage=total_coverage,
                        total_coverage_data=total_coverage_data,
                        is_instruction_level=Granularity.is_instruction(granularity),
                        progress_covered=total_coverage_data.covered(granularity),
                        progress_all=total_coverage_data.coverable(granularity))
    root_path = ''
    html = index_template(table=Markup(table), appname=app_name, title=app_name, package=None, 
                          respath=root_path, file_name=None, granularity=Granularity.get(granularity))
    path = os.path.join(output_dir, 'index.html')
    with open(path, 'w') as f:
        f.write(html)
    
def calculate_coverage(coveredlines, alllines):
    if alllines == 0:
        return None
    result = float(coveredlines) / alllines
    return ("%.5f" % (100 * result)) if result else None

def save_package_indexhtml(class_group, templates, output_dir, app_name, granularity):
    folder = class_group[0].folder.replace('\\', '/')
    class_name_with_pkg = class_group[0].name
    package_name = Utils2.get_standart_package_name(class_name_with_pkg)
    init_table = templates['init_table.pt']
    init_row = templates['init_row.pt']
    index_template = templates['index.pt']

    slash_num = class_name_with_pkg.count('/')
    root_path = ''
    for i in range(slash_num):
        root_path += '../'
    total_coverage_data = CoverageData()
    rows = []
    for cl in class_group:
        elementlink = os.path.join(root_path, folder, cl.file_name + '.html').replace('\\', '/')
        elementname = cl.file_name
        coverage_data = CoverageData(
            lines=cl.coverable(),
            lines_missed=cl.not_covered(),
            lines_covered=cl.covered(),
            methods_covered=cl.mtds_covered(),
            methods_missed=cl.mtds_not_covered(),
            methods=cl.mtds_coverable()
        )
        coverage_data.update_coverage_for_single_class_from_methods()
        coverage = coverage_data.get_coverage(granularity)
        row = init_row(elementlink=elementlink, type='class', elementname=elementname, 
                       coverage=coverage_data.format_coverage(coverage),
                       respath=root_path, coverage_data=coverage_data,
                       is_instruction_level=Granularity.is_instruction(granularity),
                       progress_missed=coverage_data.missed(granularity),
                       progress_covered=coverage_data.covered(granularity))
        rows.append(Markup(row))
        total_coverage_data.add_data(coverage_data)
    total_coverage = total_coverage_data.get_formatted_coverage(granularity)
    table = init_table(rows=Markup("\n".join(rows)),
                        total_coverage=total_coverage,
                        is_instruction_level=Granularity.is_instruction(granularity),
                        total_coverage_data=total_coverage_data,
                        progress_covered=total_coverage_data.covered(granularity),
                        progress_all=total_coverage_data.coverable(granularity))
    html = index_template(table=Markup(table), appname=app_name, title=folder, package=package_name, 
                          respath=root_path, file_name=None, granularity=Granularity.get(granularity))
    rel_path = os.path.join(folder, 'index.html').replace('\\', '/')
    path = os.path.join(output_dir, rel_path).replace('\\', '/')
    with open(path, 'w') as f:
        f.write(html)
    return (package_name, rel_path, total_coverage_data)

def LI_TAG(str):
    return '%s' % str

def span_tab_tag(txt, cl=''):
    return span_tag("\t{}".format(txt), cl)

def span_tag(txt, cl=""):
    return '<span class="{}">{}</span>'.format(cl, txt)

def get_first_lbl_by_index(lables, index):
    i = 0
    while i < len(lables) and lables[i].index < index:
        i += 1
    if i < len(lables) and lables[i].index == index:
        return lables[i]
    return None

def save_class(cl, class_template, output_dir, app_name, granularity):
    dir = os.path.join(output_dir, cl.folder)
    if not os.path.exists(dir):
        os.makedirs(dir)
    class_path = os.path.join(dir, cl.file_name + '.html')
    buf = [LI_TAG(d) for d in cl.get_class_description()]
    buf.append(LI_TAG(''))
    buf.extend([LI_TAG(a) for a in cl.get_annotations()])
    buf.append(LI_TAG(''))
    buf.extend([LI_TAG(f) for f in cl.get_fields()])
    buf.append(LI_TAG(''))
    for m in cl.methods:
        ins_buf = []
        labels = m.labels.values()
        labels = sorted(labels, key=attrgetter('index'))
        for i in range(len(m.insns)):
            ins = m.insns[i]
            if ins.covered:
                ins_buf.append(span_tab_tag(ins.buf, COV_CLASS))
            else:
                if ins.buf.startswith("return"):
                    lbl = get_first_lbl_by_index(labels, i)
                    if lbl is not None:
                        if lbl.covered:
                            ins_buf.append(span_tab_tag(ins.buf, EXEC_CLASS))
                    else:
                        if m.insns[i-1].covered:
                            ins_buf.append(span_tab_tag(ins.buf, EXEC_CLASS))
                else:
                    if i<len(m.insns)-1 and m.insns[i+1].covered and not_instr_regex.match(m.insns[i+1].buf):
                        ins_buf.append(span_tab_tag(ins.buf, EXEC_CLASS))
                    else:
                        ins_buf.append(span_tab_tag(ins.buf))
        # insert labels and tries
        # sort the labels by index
        count = 0
        for l in labels:
            if l.covered:
                ins_buf.insert(l.index + count, span_tab_tag(l.buf, COV_CLASS))
            else:
                ins_buf.insert(l.index + count, span_tab_tag(l.buf))
            count += 1
            for t in l.tries:
                ins_buf.insert(l.index + count, span_tab_tag(t.buf))
                count += 1
            if l.switch:
                for sl in l.switch.buf:
                    ins_buf.insert(l.index + count, span_tab_tag(sl))
                    count += 1
            if l.array_data:
                for sl in l.array_data.buf:
                    ins_buf.insert(l.index + count, span_tab_tag(sl))
                    count += 1
        ins_buf.insert(0, LI_TAG(''))
        for a in m.annotations:
            a.reload()
            ins_buf[0:0] = [span_tab_tag(d) for d in a.buf]
        for p in reversed(m.parameters):
            p.reload()
            ins_buf[0:0] = [span_tab_tag(d) for d in p.buf]
        ins_buf.insert(0, span_tab_tag(m.get_registers_line()))
        html_method_line = span_tag(cgi.escape(m.get_method_line()), COV_CLASS) if m.called else m.get_method_line()
        ins_buf.insert(0, html_method_line)
        ins_buf.append(LI_TAG(".end method"))
        buf.append(LI_TAG(''))
        buf.extend(ins_buf)
    slash_num = cl.name.count('/')
    respath = ''
    for i in range(slash_num):
        respath += '../'
    html = class_template(code=Markup("\n".join(buf)), appname=app_name, title=cl.file_name, 
                          package=Utils2.get_standart_package_name(cl.name), respath=respath,
                          granularity=Granularity.get(granularity))
    with open(class_path, 'w') as f:
        f.write(html)

def read_ec(ec_path):
    pobj = ''
    with open(ec_path, mode='rb') as f:
        marshaller = javaobj.JavaObjectUnmarshaller(f)
        pobj = marshaller.readObject()
    return pobj

def cover_smalitree(st, coverage):
    i = 0
    for c_i in range(len(st.classes)):
        cl = st.classes[c_i]
        if cl.is_coverable():
            cov_class = coverage[i]
            i += 1
            for m_i in range(len(cl.methods)):
                method = cl.methods[m_i]
                method.called = method.cover_code > -1 and cov_class[method.cover_code]
                for ins in method.insns:
                    ins.covered = ins.cover_code > -1 and cov_class[ins.cover_code]
                for k, lbl in method.labels.items():
                    lbl.covered = lbl.cover_code > -1 and cov_class[lbl.cover_code]

def recreate_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)
