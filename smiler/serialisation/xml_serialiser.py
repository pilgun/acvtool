import lxml
from lxml import etree
from lxml.etree import Element, SubElement
from ..granularity import Granularity
from smiler.instrumenting.utils import Utils as Utils2

class XmlSerialiser(object):

    def __init__(self, smalitree, app_name, granularity):
        self.smalitree = smalitree
        self.app_name = app_name
        self.data = ""
        self.granularity = granularity

    def get_xml(self):
        report = Element("report")
        report.set("name", self.app_name)
        
        groups = Utils2.get_groupped_classes(self.smalitree)
        for g in groups:
            package = SubElement(report,"package")
            package.set("name", Utils2.get_package_name(g[0].name))
            for cl in g:
                if (cl.is_coverable()):
                    self.add_xml_class(package, cl)
        return etree.tostring(report, pretty_print=True)

    def add_xml_class(self, package, smali_class):
        class_insns_covered = 0
        class_insns_missed = 0
        xml_class = SubElement(package, "class")
        xml_class.set("name", smali_class.name[1:-1])
        class_instructions_added = 0
        for m in smali_class.methods:
            if (m.cover_code > -1): # not abstract and not native method
                xml_method = self.create_xml_method(xml_class, m)
                if Granularity.is_instruction(self.granularity):
                    lines_covered = m.covered()
                    lines_missed = m.not_covered()
                    self.add_xml_insn_counter(xml_method, lines_covered, lines_missed, "INSTRUCTION")
                    class_insns_covered += lines_covered
                    class_insns_missed += lines_missed
                    class_instructions_added += 1
                if Granularity.is_method(self.granularity):
                    self.add_xml_insn_counter(xml_method, int(m.called), 1-int(m.called), "METHOD")
        methods_covered = smali_class.mtds_covered()
        methods_missed = smali_class.mtds_coverable() - methods_covered
        if class_instructions_added:
            self.add_xml_insn_counter(xml_class, class_insns_covered, class_insns_missed, "INSTRUCTION")
        self.add_xml_insn_counter(xml_class, methods_covered, methods_missed, "METHOD")

    def create_xml_method(self, xml_class, smali_method):
        xml_method = SubElement(xml_class, "method")
        xml_method.set("name", smali_method.name)
        xml_method.set("desc", smali_method.get_method_argument_desc())
        return xml_method

    def add_xml_insn_counter(self, xml_method, covered, missed, cover_type):
        xml_counter = SubElement(xml_method, "counter")
        xml_counter.set("covered", str(covered))
        xml_counter.set("missed", str(missed))
        xml_counter.set("type", cover_type)