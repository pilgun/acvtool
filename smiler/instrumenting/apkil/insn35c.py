class Insn35c(object):

    def __init__(self, line):
        self.buf = ""
        self.opcode_name = ""
        self.registers = []
        self.method_descriptor = ""

        self.__parse(line)

    def __repr__(self):
        return "%s\n" % self.buf

    def __parse(self, line):
        self.buf = line
        tmp = self.buf
        tmp = tmp.replace('{', '')
        tmp = tmp.replace('}', '')
        tmp = tmp.replace(',', '')
        segs = tmp.split()
        self.opcode_name = segs[0]
        self.registers = segs[1:-1]
        self.method_desc = segs[-1]

    def reload(self):
        self.buf = "%s {%s}, %s" % \
                (self.opcode_name, ", ".join(self.registers), \
                self.method_desc)

    def get_line(self, registers = None):
        if not registers:
            registers = self.registers
        return Insn35c.create_line(self.opcode_name, registers, self.method_desc)

    @staticmethod
    def create_line(opcode_name, registers, method_desc):
        return "%s {%s}, %s" % (opcode_name, ", ".join(registers), method_desc)

    def replace(self, opcode_name, method_desc):
        self.opcode_name = opcode_name
        self.method_desc = method_desc

    def set_regs(self, registers):
        self.registers = registers

