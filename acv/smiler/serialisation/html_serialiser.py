import os
import re
import html
from operator import attrgetter
from chameleon import PageTemplateLoader
from chameleon.utils import Markup
from ..instrumenting.utils import Utils
from ..config import config
from ..granularity import Granularity
from ..entities.coverage import CoverageData


class HtmlSerialiser(object):
    
    not_instr_regex = re.compile("^(move-result|move-exception).*$")

    def __init__(self, package, granularity, output_dir):
        self.package = package
        self.granularity = granularity
        self.output_dir = output_dir
        self.templates = PageTemplateLoader(config.templates_path)
        self.class_template = self.templates["class.pt"]
        self.resources_dir = os.path.join(output_dir, '.resources')
        self.init_row = self.templates['init_row.pt']
        self.init_table = self.templates['init_table.pt']
        self.index_template = self.templates['index.pt']


    @staticmethod
    def get_first_lbl_by_index(lables, index):
        i = 0
        while i < len(lables) and lables[i].index < index:
            i += 1
        if i < len(lables) and lables[i].index == index:
            return lables[i]
        return None

    def get_init_row(self, path, type, elementname, coverage_data, respath):
        coverage = coverage_data.get_formatted_coverage(self.granularity)
        return self.init_row(elementlink=path, type=type, elementname=elementname,
                    coverage=coverage,
                    respath=respath, coverage_data=coverage_data,
                    is_instruction_level=Granularity.is_instruction(self.granularity),
                    progress_covered=coverage_data.covered(self.granularity),
                    progress_missed=coverage_data.missed(self.granularity))

    def get_init_table(self, rows, coverage_data):
        total_coverage = coverage_data.get_formatted_coverage(self.granularity)
        table = self.init_table(rows=Markup("\n".join(rows)),
                total_coverage=total_coverage,
                total_coverage_data=coverage_data,
                is_instruction_level=Granularity.is_instruction(self.granularity),
                progress_covered=coverage_data.covered(self.granularity),
                progress_all=coverage_data.coverable(self.granularity))
        return table

    def get_index_html(self, table, appname, title, package, respath, file_name):
        htmlpage = self.index_template(table=Markup(table), appname=appname, title=title, 
        package=package, respath=respath, file_name=file_name, 
        granularity=Granularity.get(self.granularity), version=config.version)
        return htmlpage

    def save_dex_report(self, dex_coverages):
        Utils.copytree(config.html_resources_dir_path, self.resources_dir)
        total_coverage_data = CoverageData()
        rows = []
        for id, coverage_data in dex_coverages.items():
            pth = os.path.join(str(id), "main_index.html")
            row = self.get_init_row(pth, "dex", str(id), coverage_data, "")
            rows.append(Markup(row))
            total_coverage_data.add_data(coverage_data)
        table = self.get_init_table(rows, total_coverage_data)
        htmlpage = self.get_index_html(table, self.package, self.package, self.package, '', None)
        path = os.path.join(self.output_dir, "main_index.html")
        with open(path, 'w') as f:
            f.write(htmlpage)

    def save_html(self, smalitree):
        report_dir = os.path.join(self.output_dir, str(smalitree.Id))
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        for cl in smalitree.classes:
            self.save_class(cl, report_dir)
        dex_coverage_data = self.save_packaged_coverage(report_dir, smalitree)
        return dex_coverage_data

    def save_multidex_report(coverage_data):
        pass

    def save_class(self, cl, report_dir):
        dir = os.path.join(report_dir, cl.folder)
        if not os.path.exists(dir):
            os.makedirs(dir)
        class_path = os.path.join(dir, cl.file_name + '.html')
        buf = [Tag.Li(d) for d in cl.get_class_description()]
        buf.append(Tag.Li(''))
        buf.extend([Tag.Li(html.escape(a)) for a in cl.get_annotations()])
        buf.append(Tag.Li(''))
        buf.extend([Tag.Li(f) for f in cl.get_fields()])
        buf.append(Tag.Li(''))
        for m in cl.methods:
            ins_buf = []
            labels = m.labels.values()
            labels = sorted(labels, key=attrgetter('index'))
            for i in range(len(m.insns)):
                ins = m.insns[i]
                if ins.covered:
                    ins_buf.append(Tag.span_tab(html.escape(ins.buf), Tag.COV_CLASS))
                else:
                    if ins.buf.startswith("return"):
                        lbl = HtmlSerialiser.get_first_lbl_by_index(labels, i)
                        if lbl and lbl.covered or (not lbl and m.insns[i-1].covered):
                            ins_buf.append(Tag.span_tab(ins.buf, Tag.EXEC_CLASS))
                        else:
                            ins_buf.append(Tag.span_tab(ins.buf))
                    else:
                        if m.insns[i].cover_code > -1 and not m.insns[i].covered:
                            ins_buf.append(Tag.span_tab(html.escape(ins.buf), Tag.MISSED))
                            continue
                        if i<len(m.insns)-1 and m.insns[i+1].covered and \
                            ( HtmlSerialiser.not_instr_regex.match(m.insns[i+1].buf) or \
                                m.insns[i].buf.startswith("goto") or \
                                m.insns[i].opcode_name == "packed-switch" ):
                            ins_buf.append(Tag.span_tab(html.escape(ins.buf), Tag.EXEC_CLASS))
                        else:
                            ins_buf.append(Tag.span_tab(html.escape(ins.buf)))
            # insert labels and tries
            # sort the labels by index
            count = 0
            for l in labels:
                if l.covered:
                    ins_buf.insert(l.index + count, Tag.span_tab(l.buf, Tag.COV_CLASS))
                else:
                    ins_buf.insert(l.index + count, Tag.span_tab(l.buf))
                count += 1
                # for t in l.tries:
                #     ins_buf.insert(l.index + count, Tag.span_tab(t.buf))
                #     count += 1
                if l.switch:
                    for sl in l.switch.buf:
                        ins_buf.insert(l.index + count, Tag.span_tab(sl))
                        count += 1
                if l.array_data:
                    for sl in l.array_data.buf:
                        ins_buf.insert(l.index + count, Tag.span_tab(sl))
                        count += 1
            ins_buf.insert(0, Tag.Li(''))
            for a in m.annotations:
                a.reload()
                ins_buf[0:0] = [Tag.span_tab(html.escape(d)) for d in a.buf]
            for p in reversed(m.parameters):
                p.reload()
                ins_buf[0:0] = [Tag.span_tab(d) for d in p.buf]
            ins_buf.insert(0, Tag.span_tab(m.get_registers_line()))
            html_method_line = html.escape(m.get_method_line())
            if m.ignore:
                html_method_line = Tag.span(html_method_line, Tag.IGNORE_TAG)
            elif m.called:
                html_method_line = Tag.span(html_method_line, Tag.COV_CLASS)
            ins_buf.insert(0, html_method_line)
            ins_buf.append(Tag.Li(".end method"))
            buf.append(Tag.Li(''))
            buf.extend(ins_buf)
        slash_num = cl.name.count('/')
        respath = '../'
        for i in range(slash_num):
            respath += '../'
        htmlpage = self.class_template(code=Markup("\n".join(buf)), 
                    appname=self.package, title=cl.file_name, 
                    package=Utils.get_standart_package_name(cl.name), 
                    respath=respath,
                    granularity=Granularity.get(self.granularity),
                    version=config.version)
        with open(class_path, 'w') as f:
            f.write(htmlpage)


    def save_packaged_coverage(self, report_dir, smalitree):
        groups = Utils.get_groupped_classes(smalitree)
        rows = []
        total_coverage_data = CoverageData()
        for g in groups:
            (package, path, coverage_data) = self.save_package_indexhtml(g, report_dir)
            if not package:
                package = "."
            row = self.get_init_row(path, 'package', package, coverage_data, '../')
            rows.append(Markup(row))
            total_coverage_data.add_data(coverage_data)
        table = self.get_init_table(rows, total_coverage_data)
        htmlpage = self.get_index_html(table, self.package, self.package, self.package, '../', None)
        path = os.path.join(report_dir, "main_index.html")
        with open(path, 'w') as f:
            f.write(htmlpage)
        return total_coverage_data


    def save_package_indexhtml(self, class_group, report_dir):
        folder = class_group[0].folder.replace('\\', '/')
        class_name_with_pkg = class_group[0].name
        package_name = Utils.get_standart_package_name(class_name_with_pkg)
        slash_num = class_name_with_pkg.count('/')
        root_path = ''
        for i in range(slash_num):
            root_path += '../'
        respath = root_path + '../'
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
            row = self.get_init_row(elementlink, "class", elementname, coverage_data, respath)
            rows.append(Markup(row))
            total_coverage_data.add_data(coverage_data)
        table = self.get_init_table(rows, total_coverage_data)
        htmlpage = self.get_index_html(table, self.package, folder, package_name, respath, None)
        rel_path = os.path.join(folder, 'index.html').replace('\\', '/')
        path = os.path.join(report_dir, rel_path).replace('\\', '/')
        with open(path, 'w') as f:
            f.write(htmlpage)
        return (package_name, rel_path, total_coverage_data)


class Tag(object):
    @staticmethod
    def Li(str):
        return '{}'.format(str)
    
    @staticmethod
    def span(txt, cl=""):
        return '<span class="{}">{}</span>'.format(cl, txt)

    @staticmethod
    def span_tab(txt, cl=''):
        return Tag.span("\t{}".format(txt), cl)
    
    COV_CLASS = 'cov' #html class, ex: '<span class="%COV_CLASS%"/>'
    EXEC_CLASS = 'exec'
    IGNORE_TAG = 'ignore'
    MISSED = "missed"