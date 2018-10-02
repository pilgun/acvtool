from logger import log

class LabelNode(object):
    '''Consists of label line including tries, switches and array data if any.'''
    
    def __init__(self, line, index, lid):
        self.name = ""
        self.buf = ""
        self.index = -1 # id of the insn which is next to the label
        self.lid = None # number of the label in method
        self.tries = []
        self.switch = None
        self.array_data = None
        self.cover_code = -1
        self.covered = False

        self.__parse(line, index, lid)

    def __repr__(self):
        return "Lable: %s\n" % \
                (self.name, )

    def __parse(self, line, index, lid):
        self.buf = line
        self.index = index
        self.name = self.buf[1:]
        self.lid = lid

        log("LabelNode: " + self.name + " parsed!")

    def reload(self):
        self.buf = self.get_line()
    
    def get_line(self):
        '''Returns single label line.'''
        return ":%s" % self.name
    
    def get_lines(self):
        ''' Returns labels including tries, switches, and arrays.'''
        lines = [":%s" % self.name]
        for t in self.tries:
            lines.append(t.buf)
        if self.switch:
            for sl in self.switch.buf:
                lines.append(sl)
        if self.array_data:
            for sl in self.array_data.buf:
                lines.append(sl)
        return lines
