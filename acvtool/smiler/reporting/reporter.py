import os

from .. import smiler
import logging
from ..operations import binaries
from ..granularity import Granularity
from ..serialisation.html_serialiser import HtmlSerialiser
from ..serialisation.xml_serialiser import XmlSerialiser
from ..serialisation.json_serialiser import JsonSerialiser
from ...cutter import shrinker


class Reporter(object):

    def __init__(self, package, pickle_files, images_dir, report_dir):
        self.package = package
        self.pickle_files = pickle_files # covered pickle files
        self.images_dir = images_dir
        self.report_dir = report_dir


    def generate(self, html=True, xml=True, json=False, granularity="instruction", ignore_filter=None, shrink=False):
        report_dir = self.report_dir
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        logging.info("report generating...")
        self.save_reports(self.pickle_files, xml, html, json, granularity, ignore_filter, to_shrink=shrink)
        logging.info("reports saved to: {0}".format(report_dir))


    def save_reports(self,pickle_files, xml, html, json, granularity, ignore_filter, to_shrink):
        dex_coverages = {}
        granularity_index = Granularity.GRANULARITIES[granularity]
        if html:
            htmlSerialiser = HtmlSerialiser(self.package, granularity_index, self.report_dir)
        min_pickle = min(pickle_files.keys())
        max_pickle = max(pickle_files.keys())
        if json:
            logging.info("saving json...")
            jsonSerialiser = JsonSerialiser(self.package, granularity)
            classes_data = dict()
        for treeId in range(min_pickle, max_pickle+1):
            if treeId not in pickle_files:
                continue
            smalitree = binaries.load_smalitree(pickle_files[treeId])
            if to_shrink:
                shrinker.remove_not_executed_methods_and_classes(smalitree)
            if ignore_filter:
                smiler.apply_ignore_filter(smalitree, ignore_filter)
            if html:
                dex_coverage_data = htmlSerialiser.save_html(smalitree)
                dex_coverages[treeId] = dex_coverage_data
            if xml:
                logging.info("saving xml...")
                self.save_xml_report(treeId, smalitree, granularity_index)
            if json:
                dex_classes_data = jsonSerialiser.get_executed_methods_by_class(smalitree)
                classes_data.update(dex_classes_data)
        if json:
            logging.info("saving json...")
            json_data = jsonSerialiser.get_json_data(classes_data)
            self.save_json_report(json_data)
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


    def save_json_report(self, json_data):
        path = os.path.join(self.report_dir, 'methods.json')
        logging.info("saving json report to {}".format(path))
        with open(path, 'w') as f:
            f.write(json_data)
