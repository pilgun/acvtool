class SwitchNode(object):

    def __init__(self, lines, label):
        self.buf = [] 
        self.type_ = ""
        self.packed_value = ""
        self.packed_labels = []
        self.sparse_dict = {}
        self.label = None

        self.__parse(lines, label)

    def __repr__(self):
        return "Switch: %s" % ("".join(self.buf))

    def __parse(self, lines, label):
        self.buf = lines
        self.label = label
        segs = self.buf[0].split()
        self.type_ = segs[0]
        # TODO:parse more
        label.switch = self 

    def reload(self):
        self.buf = []
        if self.type_ == ".packed-switch":
            self.buf.append("%s %s" % (self.type_, self.packed_value))
            for l in self.packed_labels:
                #l.reload()
                self.buf.append(l.buf)
            self.buf.append(".end packed-switch")
        elif self.type_ == ".sparse-switch":
            self.buf.append(".sparse-switch")
            for value in self.sparse_dict.keys():
                label = self.sparse_dict[value]
                #label.reload()
                self.buf.append("%s -> %s" % (value, label.buf))
            self.buf.append(".end sparse-switch")
