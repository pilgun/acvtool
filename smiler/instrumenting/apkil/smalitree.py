import os
import copy
import sys
import shutil
import StringIO
import classnode 
from logger import log

class SmaliTree(object):

    def __init__(self, foldername):
        self.foldername = ""
        self.smali_files = []
        self.classes = []

        self.__parse(foldername)

    def __repr__(self):
        return "Foldername: %s\n%s" % \
                (self.foldername, \
                "".join([repr(class_) for class_ in self.classes]))

    def __parse(self, foldername):
        print "parsing %s..." % foldername
        self.foldername = foldername
        for (path, dirs, files) in os.walk(self.foldername):
            for f in files:
                name = os.path.join(path, f)
                rel_path = os.path.relpath(name, self.foldername)
                if rel_path.find("annotation") == 0:
                    continue
                ext = os.path.splitext(name)[1]
                if ext != '.smali': continue
                self.smali_files.append(name)
                folder, fn = os.path.split(rel_path)
                self.classes.append(classnode.ClassNode(filename=name, folder=folder))
        # print repr(self.smali_files)
        log("SmaliTree parsed!")

    def get_class(self, class_name):
        result = [c for c in self.classes if c.name == class_name]
        if result:
            return result[0]
        else:
            return None
    
    def add_class(self, class_node):
        if [c for c in self.classes if c.name == class_node.name]:
            print "Class %s alreasy exsits!" % class_node.name
            return False
        else:
            self.classes.append(copy.deepcopy(class_node))
            return True

    def remove_class(self, class_node):
        # self.classes.del()
        pass

    def save(self, new_foldername):
        print "Saving %s..." % new_foldername
        if os.path.exists(new_foldername):
            shutil.rmtree(new_foldername)
        os.makedirs(new_foldername)
        for c in self.classes:
            c.save(new_foldername)
