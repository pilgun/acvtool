from .constants import BASIC_TYPES, BASIC_TYPES_BY_JAVA

class TypeNode(object):

    def __init__(self, desc=None):
        self.type_ = ""
        self.dim = 0
        self.basic = None
        self.void = None
        self.words = 1

        if desc:
            self.__parse(desc)

    def __parse(self, desc):
        self.dim = desc.rfind('[') + 1
        desc = desc[self.dim:]

        if desc[0] in BASIC_TYPES:
            self.type_ = desc[0]
            self.basic = True
            if self.type_ == 'V':
                self.void = True
            else:
                self.void = False
            if (self.type_ == 'J' or self.type_ == 'D') and self.dim == 0:
                self.words = 2
        elif desc[0] == 'L':
            self.type_ = desc
            self.basic = False

    def __repr__(self):
        return self.dim * '[' + self.type_

    def load_java(self, java):
        self.dim = java.count("[]")
        java = java.replace("[]", '')
        if java in BASIC_TYPES_BY_JAVA:
            self.type_ = BASIC_TYPES_BY_JAVA[java]
            self.basic = True
            if self.type_ == 'V':
                self.void = True
            else:
                self.void = False
            if self.type_ == 'J' or self.type_ == 'D':
                self.words = 2
        else:
            self.type_ = 'L' + java.replace('.', '/') + ';'

    def get_desc(self):
        return self.dim * '[' + self.type_

    def get_java(self):
        if self.basic:
            if self.void:
                return ""
            else:
                return BASIC_TYPES[self.type_] + self.dim * "[]"
        else:
            return self.type_[1:-1].replace('/', '.') + self.dim * "[]"
