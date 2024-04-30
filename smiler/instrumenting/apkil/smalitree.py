import os
import copy
from .classnode import ClassNode

class SmaliTree(object):

    def __init__(self, treeId, foldername):
        self.foldername = ""
        self.classes = []
        self.class_ref_dict = None
        self.instrumented = False
        self.instrumented_method_number = None # go through method counter among all smali trees
        self.Id = treeId # smali dir number starting from 1

        self.__parse(foldername)

    def __repr__(self):
        return "Foldername: %s\n%s" % \
                (self.foldername, \
                "".join([repr(class_) for class_ in self.classes]))

    def __parse(self, foldername):
        print("parsing {}...".format(foldername))
        self.foldername = foldername
        for (path, dirs, files) in os.walk(self.foldername):
            for f in files:
                name = os.path.join(path, f)
                rel_path = os.path.relpath(name, self.foldername)
                if rel_path.find("annotation") == 0:
                    continue
                ext = os.path.splitext(name)[1]
                if ext != '.smali': continue
                folder, fn = os.path.split(rel_path)
                self.classes.append(ClassNode(filename=name, folder=folder))

    def get_class(self, class_name):
        result = [c for c in self.classes if c.name == class_name]
        if result:
            return result[0]
        else:
            return None
    
    def add_class(self, class_node):
        if [c for c in self.classes if c.name == class_node.name]:
            print("Class {} alreasy exsits!".format(class_node.name))
            return False
        else:
            self.classes.append(copy.deepcopy(class_node))
            return True

    def remove_class(self, class_node):
        # self.classes.del()
        pass

    def update_class_ref_dict(self):
        self.class_ref_dict = {}
        for cl in self.classes:
            cl.update_meth_ref_dict()
            self.class_ref_dict[cl.name] = cl
