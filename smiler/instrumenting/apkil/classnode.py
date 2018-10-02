import methodnode
import sys
import os
from logger import log
from fieldnode import FieldNode
from codeblocknode import CodeBlockNode

class ClassNode(object):

    def __init__(self, filename=None, buf=None, folder=None):
        self.buf = []
        self.file_path = "" 
        self.folder = ""
        self.file_name = ""
        self.name = ''
        self.super_name = ''
        self.source = ''
        self.implements = []
        self.access = []
        self.interfaces = []
        self.fields_comment = ''
        self.fields = []
        self.methods_comment = ''
        self.methods = []
        self.inner_classes = []
        self.annotations_comment = ''
        self.annotations = []
        self.debugs = []

        if filename or buf:
            self.__parse(filename, buf, folder)

    def __repr__(self):
        return  "Class: %s %s << %s\n%s%s" % \
                (' '.join(self.access), self.name, self.super_name, \
                ''.join([repr(f) for f in self.fields]), \
                ''.join([repr(m) for m in self.methods]))

    def __parse(self, file_path, buf, folder):
        if file_path:
            self.file_path = file_path
            f = open(self.file_path, 'r')
        elif buf:
            f = StringIO.StringIO(buf)
        else:
            return

        self.folder = folder
        full_folder, self.file_name = os.path.split(file_path)
        

        line = f.readline()
        while line:
            if line.isspace():
                line = f.readline()
                continue
            line = line.strip()
            segs = line.split()
            # .source <source-file>
            if segs[0] == ".source":
                self.source = segs[1]
            # .class <access-spec> <class-name>
            elif segs[0] == ".class":
                self.name = segs[-1]
                # <access-spec>: public, final, super, interface, abstract
                self.access = segs[1:-1]
            # .super <class-name>
            elif segs[0] == ".super":
                self.super_name = segs[1]
            elif segs[0] == ".interface":
                print("can't parse .interface")
                sys.exit(1)
            elif segs[0] == ".implements":
                self.implements.append(segs[1])
            elif segs[0] == ".field":
                lines = [line]
                line = f.readline()
                if not line.isspace():
                    line = line.strip()
                    annotation_lines = []
                    if line.startswith(".annotation"):
                        while not line.startswith(".end field"):
                            annotation_lines.append(line)
                            line = f.readline()
                            if line.isspace():
                                line = f.readline()
                            line = line.strip()

                    if line == ".end field":
                        # annotations is inside a field
                        lines.extend(annotation_lines)
                        lines.append(line)
                    else:
                        # when annotations are not included inside the field
                        self.annotations.append(CodeBlockNode(annotation_lines))
                self.fields.append(FieldNode(lines))
                continue
            elif segs[0] == ".method":
                lines = [line]
                line = f.readline()
                while line:
                    if line.isspace():
                        line = f.readline()
                        continue
                    line = line.strip()
                    lines.append(line)
                    segs = line.split(None, 2)
                    if segs[0] == ".end" and segs[1] == "method":
                        break
                    line = f.readline()
                self.methods.append(methodnode.MethodNode(lines))
            elif segs[0] == ".annotation":
                # there may be subannotations
                lines = [line]
                line = f.readline()
                while line:
                    if line.isspace():
                        line = f.readline()
                        continue
                    line = line.strip()
                    lines.append(line)
                    segs = line.split(None, 2)
                    if segs[0] == ".end" and segs[1] == "annotation":
                        break
                    line = f.readline()
                self.annotations.append(CodeBlockNode(lines))
            elif segs[0] == '#':
                if len(segs) > 1 and segs[1] == 'annotations':
                    self.annotations_comment = line
                if len(segs) > 2 and segs[2] == 'fields':
                    self.fields_comment = line
                if len(segs) > 2 and segs[2] == 'methods':
                    self.methods_comment = line
                pass
            line = f.readline()
        f.close()
        log("ClassNode: " + self.name + " parsed!")

    def get_class_description(self):
        buf = []
        # .class
        buf.append(".class %s %s" % (' '.join(self.access), self.name))
        # .super
        buf.append(".super %s" % (self.super_name,))
        # .source
        if self.source:
            buf.append(".source %s" % (self.source,))
        # .implements
        if self.implements:
            for imp in self.implements:
                buf.append(".implements %s" % (imp,))
        # .interfaces

        return buf

    def get_annotations(self):
        buf = []
        # .annotations
        if self.annotations:
            #buf.append(self.annotations_comment)
            for a in self.annotations:
                a.reload()
                buf.extend(a.buf)

        return buf

    def get_fields(self):
        buf = []
        # .field
        if self.fields:
            #buf.append(self.fields_comment)
            for f in self.fields:
                f.reload()
                buf.extend(f.buf)

        return buf

    def reload(self):
        self.buf = []

        # .class, .super, .source, .implements, .interfaces, .annotations,
        # .field
        self.buf.extend(self.get_class_description())
        self.buf.extend(self.get_annotations())
        self.buf.extend(self.get_fields())

        # .method
        #self.buf.append(self.methods_comment)
        for m in self.methods:
            m.reload()
            self.buf.extend(m.buf)

    def set_name(self, name):
        self.name = name
    
    def add_access(self, access):
        if type(access) == list:
            self.access.extend(access)
        else:
            self.access.append(access)

    def set_super_name(self, super_name):
        self.super_name = super_name
    
    def add_field(self, field):
        self.fields.append(field)

    def add_method(self, method):
        if type(method) == list:
            self.methods.extend(method)
        else:
            self.methods.append(method)

    def save(self, new_foldername):
        self.reload()
        path, filename = os.path.split(self.name[1:-1])
        filename += ".smali"
        path = os.path.join(new_foldername, path)
        if not os.path.exists(path):
            os.makedirs(path)
        filename = os.path.join(path, filename)
        f = open(filename, 'w')
        f.write('\n'.join(self.buf))
        f.close()

    def coverable(self):
        return sum(m.coverable() for m in self.methods)

    def covered(self):
        return sum(m.covered() for m in self.methods)

    def not_covered(self):
        return sum(m.not_covered() for m in self.methods)
    
    def coverage(self):
        coverable = self.coverable()
        if coverable == 0:
            return None
        return float(self.covered()) / coverable

    def missed_methods(self):
        return sum(m.covered() == 0 for m in self.methods)

    def mtds_coverable(self):
        return sum(m.cover_code > -1 for m in self.methods)

    def is_coverable(self):
        return any(m.cover_code > -1 for m in self.methods)

    def mtds_covered(self):
        return sum(m.called for m in self.methods)

    def mtds_not_covered(self):
        return self.mtds_coverable() - self.mtds_covered()

    def mtds_coverage(self):
        coverable = self.mtds_coverable()
        if coverable == 0:
            return None
        return float(self.mtds_covered()) / coverable
        