from .constants import INSN_FMT
from .insn35c import Insn35c
from .insn3rc import Insn3rc

class InsnNode(object):

    def __init__(self, line=None):
        self.buf = ""
        self.opcode_name = ""
        self.fmt = ""
        self.obj = None
        self.cover_code = -1
        self.covered = False

        if line:
            self.__parse(line)

    def __repr__(self, line_number=""):
        return "%s\n" % \
                (self.buf, )

    def __parse(self, line):
        self.buf = line
        segs = self.buf.split()
        self.opcode_name = segs[0] 
        if self.opcode_name in INSN_FMT:
            self.fmt = INSN_FMT[self.opcode_name]

        if self.fmt == "35c":
            self.obj = Insn35c(line)
        elif self.fmt == "3rc":
            self.obj = Insn3rc(line)

    def reload(self):
        if self.obj:
            self.obj.reload()
            self.buf = self.obj.buf
        else:
            pass

    def get_line(self, registers = None):
        if self.obj:
            return self.obj.get_line(registers)
        return self.buf
