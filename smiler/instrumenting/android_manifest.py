import codecs
from xml.dom import minidom
from general_exceptions import MsgException


class AndroidManifest:
    def __init__(self, pathAndroidManifest):
        self.pathAndroidManifest = pathAndroidManifest
        self.xml = minidom.parse(pathAndroidManifest)
        self.packageName = self.getElement("manifest", "package")
    
    def getUsesPermissions(self):
        return self.getElements("uses-permission", "android:name")
    
    def addUsesPermission(self, permName):
        if permName not in self.getUsesPermissions():
            self.createElement("manifest", "uses-permission", {"android:name" : permName})

    def addInstrumentation(self, instrumentationClassName, targetPackage):
        instr = self.getElements("instrumentation", "android:name")
        #TODO: Check if several instrumentations are possible
        if len(instr) > 0:
            raise ManifestAlreadyInstrumentedException()
        
        self.createElement("manifest", "instrumentation", 
                           {"android:name" : instrumentationClassName,
                            "android:targetPackage" : targetPackage})
    
    def removeExistingInstrumentation(self):
        instr = self.getElements("instrumentation", "android:name")
        if len(instr) <= 0:
            raise NoInstrumentationTagFound()
        for elem in self.xml.getElementsByTagName("instrumentation"):
            self.xml._get_childNodes()[0].removeChild(elem)
    
        
    def getPackageName(self):
        return self.packageName

    def getElement(self, tag_name, attribute):
        """
            Return element in xml files which matches with the tag name and the specific attribute

            :param tag_name: specify the tag name
            :type tag_name: string
            :param attribute: specify the attribute
            :type attribute: string

            :rtype: string
        """
        for item in self.xml.getElementsByTagName(tag_name) :
            value = item.getAttribute(attribute)

            if len(value) > 0 :
                return value
            
        return None
    
    def getElements(self, tag_name, attribute):
        """
            Return values of elements in xml files which match with the tag name and the specific attribute.

            :param tag_name: a string which specify the tag name
            :param attribute: a string which specify the attribute
        """
        l = []
        for item in self.xml.getElementsByTagName(tag_name) :
            value = item.getAttribute(attribute)
            value = self.formatValue(value)
            l.append(str(value))

        return l

    def formatValue(self, value) :
        if len(value) > 0 :
            if value[0] == "." : 
                value = self.packageName + value
            else :
                v_dot = value.find(".")
                if v_dot == 0 :
                    value = self.packageName + "." + value
                elif v_dot == -1 :
                    value = self.packageName + "." + value
        return value
    
    def createElement(self, under_tag, tag, attributes):
        where = self.xml.getElementsByTagName(under_tag) #adding after the first occurrence
        if len(where) <= 0:
            raise NoTagException("Cannot find tag: %s" % under_tag)
        elem = self.xml.createElement(tag)
        if attributes:
            for entry in attributes.iteritems():
                elem.setAttribute(entry[0], entry[1])
        where[0].appendChild(elem)
    
    def getAndroidManifestXml(self):
        return self.xml.toprettyxml()
    
    def exportManifest(self, path=None):
        if not path:
            path = self.pathAndroidManifest
        with codecs.open(path, "w", "utf-8") as f:
            self.xml.writexml(f)



# Exception classes
class NoTagException(MsgException):
    '''
    No tag found in the manifest file.
    '''

class ManifestAlreadyInstrumentedException(MsgException):
    '''
    Manifest already contains instrumentation tag.
    '''

class NoInstrumentationTagFound(MsgException):
    '''
    No instrumentation tag found.
    '''
