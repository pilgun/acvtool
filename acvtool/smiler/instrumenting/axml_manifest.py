import pyaxml
from typing import Set
from lxml.etree import Element, SubElement
from androguard.core import axml
from androguard import util
util.set_log("INFO")

ANDROID_NAMESPACE_URI = "{http://schemas.android.com/apk/res/android}"

class AxmlBinManifest(object):
    
    def __init__(self, manifest_path) -> None:
        self.manifest_path = manifest_path
        self.manifest = self._read_axml()
        self.package = self.manifest.get("package")

    def _read_axml(self):
        with open(self.manifest_path, "rb") as f:
            data = f.read()
        ap = axml.AXMLPrinter(data)
        return ap.root

    def _get_existing_children(self, child_tag: str) -> Set[str]:
        result = set()
        for element in self.manifest:
            if element.tag != child_tag:
                continue
            name_attributes = [attr for attr in element.attrib if attr == f"{ANDROID_NAMESPACE_URI}name"]
            # only adds permission identifier into the set
            if name_attributes:
                result.add(element.get(name_attributes[0]))
        return result

    @staticmethod
    def _add_attribute(element: SubElement, name: str, value: str):
        element.set(f"{ANDROID_NAMESPACE_URI}{name}", value)
    
    def add_instrumentation_tag(self):
        instr_element = SubElement(self.manifest, "instrumentation")
        self._add_attribute(instr_element, "name", "tool.acv.AcvInstrumentation")
        self._add_attribute(instr_element, "targetPackage", self.package)

    def add_broadcast_receiver(self):
        application_element = self.manifest.find("application")
        receiver = SubElement(application_element, "receiver")
        self._add_attribute(receiver, "name", "tool.acv.AcvReceiver")
        self._add_attribute(receiver, "enabled", "true")
        self._add_attribute(receiver, "exported", "true")
        intent_filter = SubElement(receiver, "intent-filter")
        actions = ["tool.acv.flush", "tool.acv.snap", "tool.acv.calculate"]
        for action in actions:
            action_element = SubElement(intent_filter, "action")
            self._add_attribute(action_element, "name", action)

    def add_write_permission(self):
        write_permission = "android.permission.WRITE_EXTERNAL_STORAGE"
        existing_permissions = self._get_existing_children("uses-permission")
        if write_permission in existing_permissions:
            return
        print(f"adding permission {write_permission}")
        perm_element = SubElement(self.manifest, "uses-permission")
        perm_element.set(f"{ANDROID_NAMESPACE_URI}name", write_permission)

    def save_xml(self):
        # Reencode XML to AXML
        axml_object = pyaxml.axml.AXML()
        axml_object.from_xml(self.manifest)
        # Rewrite the file
        with open(self.manifest_path, "wb") as f:
            f.write(axml_object.pack())

