class Insn3rc(object):

    def __init__(self, line=None, opcode_name='', reg_start='', reg_end='', method_desc=''):
        self.buf = ""
        self.opcode_name = opcode_name
        self.reg_start = reg_start
        self.reg_end = reg_end
        # self.reg_num = 0
        self.method_desc = method_desc

        if line:
            self.__parse(line)
        else:
            self.reload()
    
    def __repr__(self):
        return "%s\n" % self.buf

    def __parse(self, line):
        self.buf = line
        tmp = self.buf
        tmp = tmp.replace('{', '')
        tmp = tmp.replace('}', '')
        tmp = tmp.replace(',', '')
        tmp = tmp.replace("..", '')
        segs = tmp.split()
        self.opcode_name = segs[0]
        self.reg_start = segs[1]
        self.reg_end = segs[2]
        self.method_desc = segs[-1]

    def reload(self):
        self.buf = self.get_line()
    
    def get_line(self, registers=None):
        if not registers:
            reg_start = self.reg_start
            reg_end = self.reg_end
        else:
            reg_start = registers[0]
            reg_end = registers[1]
        
        return Insn3rc.create_line(self.opcode_name, reg_start, reg_end,
                                   self.method_desc)

    @staticmethod
    def create_line(opcode_name, reg_start, reg_end, method_desc):
        return "%s {%s .. %s}, %s" % (opcode_name,reg_start,reg_end, method_desc)
    
    def replace(self, opcode_name, method_desc):
        self.opcode_name = opcode_name
        self.method_desc = method_desc

    def set_reg_start(self, register):
        self.reg_start = register

    def set_reg_end(self, register):
        self.reg_end = register