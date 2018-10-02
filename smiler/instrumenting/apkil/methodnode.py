import constants
import insnnode
from logger import log
from labelnode import LabelNode
from arraydatanode import ArrayDataNode
from typenode import TypeNode
from trynode import TryNode
from switchnode import SwitchNode
from codeblocknode import CodeBlockNode
from operator import attrgetter

class MethodNode(object):

    def __init__(self, lines=None):
        self.name = ""
        self.buf = []
        self.access = []
        self.descriptor = ""
        self.paras = []
        self.parameters = []
        self.annotations = []
        self.ret = ""
        self.registers = 0
        self.insns = []
        self.labels = {}
        self.tries = []
        self.is_constructor = False
        self.cover_code = -1
        self.called = False
        # monitor-enter/monitor-exit instructions are in use
        self.synchronized = False 

        if lines:
            self.__parse(lines)


    def __repr__(self):
        return "    Method: %s %s\n        locals: %d\n%s" % \
                (' '.join(self.access), self.descriptor, self.registers, \
                ''.join(["%13d %s" % \
                (self.insns.index(i), repr(i)) for i in self.insns]))

    # .method <access-spec> <method-spec>
    #     <statements>
    # .end method
    def __parse(self, lines):
        self.buf = lines
        segs = self.buf[0].split()
        self.access = segs[1:-1]
        self.descriptor = segs[-1]
        self.name = self.descriptor.split('(', 1)[0]
        self.__parse_desc()

        start = 1
        # .registers <register-num>
        segs = self.buf[1].split()
        if segs[0] == ".locals":
            self.registers = int(segs[1])
            start = 2

        index = 0
        lid = 0
        try_node_cache = []
        k = start
        while k < len(self.buf) - 1:
            line = self.buf[k]
            segs = line.split()
            if not self.synchronized and line.startswith("monitor"):
                self.synchronized = True
            # :<label-name>
            if segs[0][0] == ":":
                label = LabelNode(line, index, lid)
                self.labels[label.name] = label
                lid += 1
            elif line.startswith('.line') or segs[0] == ".prologue" or \
                line.startswith(".end local") or segs[0] == ".local" or \
                segs[0] == ".restart":
                pass
            # .catch <classname> {<label1> ..  <label2>} <label3>
            # .catchall {<label1> ..  <label2>} <label3>
            elif segs[0] == ".catch" or segs[0] == ".catchall": 
                try_node_cache.append(line)
            elif segs[0] == ".packed-switch" or segs[0] == ".sparse-switch":
                lb = self.labels[self.buf[k - 1][1:]]
                lines = [line]
                k += 1
                line = self.buf[k]
                lines.append(line)
                segs = line.split()
                while segs[0] != ".end":
                    k += 1
                    line = self.buf[k]
                    lines.append(line)
                    segs = line.split()
                SwitchNode(lines, lb)
            elif segs[0] == ".param":
                ''' Annotations added with parameters'''
                lines = [line]
                next_line = self.buf[k + 1]
                next_segs = next_line.split()
                if next_line.startswith(".annotation"):
                    # is possible that .annotation is not closed by '.end annotation'?
                    while next_line.startswith(".annotation"):
                        k += 1
                        while not next_line.startswith(".end annotation") or \
                        next_line.startswith(".end param"): # != ".end param":
                            lines.append(next_line)
                            k += 1
                            next_line = self.buf[k]
                        lines.append(next_line)
                        if next_line == ".end annotation":
                            next_line = self.buf[k + 1]
                            if next_line == ".end param":
                                lines.append(next_line)
                                k += 1
                self.parameters.append(CodeBlockNode(lines))
            elif segs[0] == ".array-data":
                lb = self.labels[self.buf[k - 1][1:]]
                lines = [line]
                k += 1
                line = self.buf[k]
                lines.append(line)
                segs = line.split()
                while segs[0] != ".end":
                    k += 1
                    line = self.buf[k]
                    lines.append(line)
                    segs = line.split()
                ArrayDataNode(lines, lb)
            elif segs[0] == ".annotation":
                k += 1
                lines = [line]
                line = self.buf[k]
                lines.append(line)
                segs = line.split()
                while (segs[0] != ".end" or segs[1] != "annotation"):
                    k += 1
                    line = self.buf[k]
                    lines.append(line)
                    segs = line.split()
                self.annotations.append(CodeBlockNode(lines))
            else:
                self.insns.append(insnnode.InsnNode(line))
                index += 1
            k += 1
        
        for line in try_node_cache:
            segs = line.split()
            start = self.labels[segs[-4][2:]]
            end = self.labels[segs[-2][1:-1]]
            handler = self.labels[segs[-1][1:]]
            self.tries.append(TryNode(line, start, end, handler))
        try_node_cache = []

        if self.name == "<init>":
            self.is_constructor = True
        log("MethodNode: " + self.name + " parsed!")

    def __parse_desc(self):
        self.name = self.descriptor.split('(', 1)[0]
        p1 = self.descriptor.find('(')
        p2 = self.descriptor.find(')')
        self.ret = TypeNode(self.descriptor[p2 + 1:])
        self.paras = []
        paras = self.descriptor[p1 + 1:p2]
        index = 0
        dim = 0
        while index < len(paras):
            c = paras[index]
            if c == '[':
                dim += 1
                index += 1
            elif constants.BASIC_TYPES.has_key(c):
                self.paras.append(TypeNode(paras[index - dim:index + 1]))
                index += 1
                dim = 0
            else:
                tmp = paras.find(';', index)
                self.paras.append(TypeNode(paras[index - dim:tmp + 1]))
                index = tmp + 1
                dim = 0

    def reload(self):
        self.__parse_desc()

        self.buf = []
        for i in self.insns:
            i.reload()
            self.buf.append(i.buf)
        # insert labels and tries
        # sort the labels by index
        count = 0
        labels = self.labels.values()
        labels = sorted(labels, key=attrgetter('index'))
        for l in labels:
            self.buf.insert(l.index + count, l.buf)
            count += 1
            for t in l.tries:
                self.buf.insert(l.index + count, t.buf)
                count += 1
            if l.switch:
                for sl in l.switch.buf:
                    self.buf.insert(l.index + count, sl)
                    count += 1
            if l.array_data:
                for sl in l.array_data.buf:
                    self.buf.insert(l.index + count, sl)
                    count += 1
        
        for a in self.annotations:
            a.reload()
            self.buf[0:0] = a.buf
        for p in reversed(self.parameters):
            p.reload()
            self.buf[0:0] = p.buf

        self.buf.insert(0, self.get_registers_line())
        
        self.buf.insert(0, self.get_method_line())
        self.buf.append(".end method")

    def get_end_line(self):
        return ".end method"

    def get_parameters(self):
        insns = []
        for p in self.parameters:
            insns.extend(p.get_lines())
        return insns

    def get_annotations(self):
        insns = []
        for a in self.annotations:
            insns.extend(a.get_lines())
        return insns


    def get_method_line(self):
        return ".method %s %s" % \
                (' '.join(self.access), self.descriptor)

    def get_registers_line(self, odd_regs=0):
        line = ''
        if self.registers+odd_regs > 0:
            line = ".locals %d" % (self.registers+odd_regs)
        elif (not "abstract" in self.access) and \
                (not "native" in self.access):
            line = ".locals 0"

        return line

    def get_insn_by_index(self, index):
        if index < 0 or index >= len(self.insns): return None
        return self.insns[index]

    def get_insn35c(self, opcode_name, method_desc):
        result = []
        for i in self.insns:
            if i.fmt == "35c" and i.opcode_name == opcode_name and \
                    i.obj.method_desc == method_desc:
                result.append(i)
        return result

    def get_desc(self):
        return self.descriptor

    def get_paras_reg_num(self):
        reg_num = 0
        for p in self.paras:
            reg_num += p.words
        return reg_num

    def set_name(self, name):
        self.name = name

    def set_desc(self, desc):
        self.descriptor = desc
        self.__parse_desc()

    def add_para(self, para, index=0):
        self.paras.insert(index, para)
        self.descriptor = self.name + '('
        for p in self.paras:
            self.descriptor += p.get_desc()
        self.descriptor += ')'
        self.descriptor += self.ret.get_desc()

    def insert_insn(self, insn, index=0, direction=0):
        self.insns.insert(index, insn)
        for l in self.labels.values():
            if l.index >= index + direction: 
                l.index += 1

    def insert_insn_bundle(self, insns, index=0, direction=0):
        i = index
        for ins in insns:
            self.insns.insert(i, ins)
            i += 1
        for l in self.labels.values():
            if l.index >= index + direction:
                l.index += len(insns)

    def add_access(self, access):
        if type(access) == list:
            self.access.extend(access)
        else:
            self.access.append(access)

    def add_label(self, label):
        if type(label) == list:
            for l in label:
                self.labels[l.name] = l
        else:
            self.labels[label.name] = label

    def set_registers(self, registers):
        self.registers = registers

    def add_insn(self, insn):
        if type(insn) == list:
            self.insns.extend(insn)
        else:
            self.insns.append(insn)

    def replace_insn35c(self):
        for i in self.insns:
            i.replace()

    def coverable(self):
        '''Number of objects that could be tracked in the method'''
        return sum(insn.cover_code > -1 for insn in self.insns) + \
            sum(lbl.cover_code > -1 for k, lbl in self.labels.items())

    def covered(self):
        '''Number of really executed statements including labels'''
        return sum(insn.covered for insn in self.insns) + sum(lbl.covered for k, lbl in self.labels.items())

    def not_covered(self):
        return self.coverable() - self.covered()
        
    def coverage(self):
        coverable = self.coverable()
        if coverable == 0:
            return None
        return float(self.covered()) / self.coverable()

    def get_method_argument_desc(self):
        return self.descriptor[self.descriptor.find('('):]
