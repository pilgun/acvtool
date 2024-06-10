import codecs
from xml.dom import minidom


class XMLManifest(object):


    def __init__(self, manifest_path):
        self.manifest_path = manifest_path
        self.xml = minidom.parse(manifest_path)
        self.package = self.get_package_name()
    

    def add_instrumentation_tag(self):
        instrumentation = self.create_element(
            under_tag="manifest", 
            tag="instrumentation", 
            attributes={
                "android:name" : "tool.acv.AcvInstrumentation", 
                "android:targetPackage" : self.package
            }
        )
        manifest = self.xml.getElementsByTagName("manifest")[0]
        manifest.appendChild(instrumentation)


    def add_broadcast_receiver(self):
        receiver = self.create_element(
            under_tag="application",
            tag="receiver",
            attributes={
                "android:name": "tool.acv.AcvReceiver",
                "android:enabled": "true",
                "android:exported": "true"
            }
        )
        intent_filter = self.create_element(
            under_tag="receiver",
            tag="intent-filter",
            attributes={}
        )
        action1 = self.create_element(
            under_tag="intent-filter",
            tag="action",
            attributes={
                "android:name": "tool.acv.calculate"
            }
        )
        action2 = self.create_element(
            under_tag="intent-filter",
            tag="action",
            attributes={
                "android:name": "tool.acv.snap"
            }
        )
        action3 = self.create_element(
            under_tag="intent-filter",
            tag="action",
            attributes={
                "android:name": "tool.acv.flush"
            }
        )
        
        application = self.xml.getElementsByTagName("application")[0]
        application.appendChild(receiver)
        receiver.appendChild(intent_filter)
        intent_filter.appendChild(action3)
        intent_filter.appendChild(action2)
        intent_filter.appendChild(action1)


    def add_write_permission(self):
        write_permission = "android.permission.WRITE_EXTERNAL_STORAGE"
        permissions = self.xml.getElementsByTagName("uses-permission")
        for p in permissions:
            if p.getAttribute("android:name") == write_permission:
                return
        uses_write_permission = self.create_element(
            under_tag="manifest",
            tag="uses-permission",
            attributes={
                "android:name": write_permission
            }
        )
        manifest = self.xml.getElementsByTagName("manifest")[0]
        manifest.appendChild(uses_write_permission)
        

    def addUsesPermission(self, permName):
        if permName not in self.getUsesPermissions():
            self.createElement("manifest", "uses-permission", {"android:name" : permName})


    def save_xml(self):
        with codecs.open(self.manifest_path, "w", "utf-8") as f:
            self.xml.writexml(f)


    def get_package_name(self):
        return self.xml.getElementsByTagName("manifest")[0].getAttribute("package")


    def create_element(self, under_tag, tag, attributes):
        elem = self.xml.createElement(tag)
        if attributes:
            for entry in attributes.items():
                elem.setAttribute(entry[0], entry[1])
        return elem
