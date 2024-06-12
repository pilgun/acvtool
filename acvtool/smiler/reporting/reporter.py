import os

from .. import smiler
import logging
from ..operations import binaries
from ..granularity import Granularity
from ..serialisation.html_serialiser import HtmlSerialiser
from ..serialisation.xml_serialiser import XmlSerialiser
from ...cutter import shrinker


class Reporter(object):

    def __init__(self, package, pickle_files, images_dir, report_dir):
        self.package = package
        self.pickle_files = pickle_files # covered pickle files
        self.images_dir = images_dir
        self.report_dir = report_dir


    def generate(self, html=True, xml=True, granularity="instruction", ignore_filter=None, shrink=False):
        report_dir = self.report_dir
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        logging.info("report generating...")
        self.save_reports(self.pickle_files, xml, html, granularity, ignore_filter, to_shrink=shrink)
        logging.info("reports saved to: {0}".format(report_dir))


    def save_reports(self,pickle_files, xml, html, granularity, ignore_filter, to_shrink):
        dex_coverages = {}
        granularity = Granularity.GRANULARITIES[granularity]
        if html:
            htmlSerialiser = HtmlSerialiser(self.package, granularity, self.report_dir)
        min_pickle = min(pickle_files.keys())
        max_pickle = max(pickle_files.keys())
        for treeId in range(min_pickle, max_pickle+1):
            if treeId not in pickle_files:
                continue
            smalitree = binaries.load_smalitree(pickle_files[treeId])
            if to_shrink:
                shrinker.shrink_smalitree(smalitree)
            if ignore_filter:
                smiler.apply_ignore_filter(smalitree, ignore_filter)
            if html:
                dex_coverage_data = htmlSerialiser.save_html(smalitree)
                dex_coverages[treeId] = dex_coverage_data
            if xml:
                logging.info("saving xml...")
                self.save_xml_report(treeId, smalitree, granularity)
        if dex_coverages:
            htmlSerialiser.save_dex_report(dex_coverages)


    def generate_xml(self, smalitree, app_name, granularity):
        serialiser = XmlSerialiser(smalitree, app_name, granularity)
        xml = serialiser.get_xml()
        return xml


    def save_xml_report(self, treeId, smalitree, granularity):
        xml = self.generate_xml(smalitree, self.package, granularity)
        path = os.path.join(self.report_dir, 'report_{}.xml'.format(treeId))
        with open(path, 'w') as f:
            f.write(xml)
