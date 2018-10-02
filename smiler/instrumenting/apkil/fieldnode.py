from logger import log

class FieldNode(object):

    def __init__(self, lines=None):
        self.buf = []
        self.name = ""
        self.access = []
        self.descriptor = ""
        self.value = None

        if lines:
            self.__parse(lines)

    def __repr__(self):
        return "    Field: %s %s %s%s\n" % \
                (' '.join(self.access), self.descriptor, self.name, \
                self.value and "=" + self.value or "")

    # .field <access-spec> <field-name>:<descriptor> [ = <value> ]
    def __parse(self, lines):
        #log("FieldNode: " + line + " parsing")
        self.buf = lines

        i = self.buf[0].find('=')
        segs = []
        if i > 0:
            segs = self.buf[0][:i].split()
            self.value = self.buf[0][i + 1:].strip()
        else:
            segs = self.buf[0].split()
        self.access = segs[1:-1]
        self.name, self.descriptor = segs[-1].split(':')
        log("FieldNode: " + self.name + " parsed!")

    def set_name(self, name):
        self.name = name

    def add_access(self, access):
        if type(access) == list:
            self.access.extend(access)
        else:
            self.access.append(access)

    def set_desc(self, desc):
        self.descriptor = desc

    def set_value(self, value):
        self.value = value
    
    def reload(self):
        self.buf[0] = "%s %s %s:%s" % \
                (".field", ' '.join(self.access), self.name, \
                self.descriptor)
        if self.value: self.buf[0] += " = %s" % self.value