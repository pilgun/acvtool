import re
from .acv_classes import AcvReporter
from ...granularity import Granularity
from ...instrumenting.utils import Utils
from ..config import SINT16_MAX

class MethodInstrumenter(object):

    not_instr_regex = re.compile("^(move-result|move-exception).*$")

    def __init__(self, granularity):
        self.granularity = granularity

    def instrument(self):
        # Instrument the method
        pass

    @staticmethod
    def is_method_static(method):
        if 'static' in method.access:
            return True
        return False

    @staticmethod
    def map_registers_p_to_v(method, is_static):
        ''' Returns dictinary that maps px registers to vx.
        '''
        reg_map = []
        self_p0 = 1
        if is_static:
            self_p0 = 0
        for i in range(SmaliHelper.len_paras(method.paras) + self_p0):
            reg_map.append(('p%d' % i, 'v%d' % (method.registers + i)))

        reg_map = dict(reg_map)

        return reg_map
    
    @staticmethod
    def get_throw_safe_instr_labels(labels, regs, cover_index, instrument, goto_hack_i):
        safe_insns = []
        throwable_insns = []

        for l in labels:
            safe_insns.extend(l.get_lines())
            if instrument:
                l.cover_code = cover_index
        if instrument:
            goto, goto_lbl = MethodInstrumenter.get_goto_hack_line(goto_hack_i)
            goto_back, goto_back_lbl = MethodInstrumenter.get_goto_hack_back(goto_hack_i)
            safe_insns.append(goto)
            safe_insns.append(goto_back_lbl)
            throwable_insns.append(goto_lbl)
            throwable_insns.extend(MethodInstrumenter.get_tracking_insns(regs, cover_index))
            throwable_insns.append(goto_back)
            cover_index += 1
        return (safe_insns, throwable_insns, cover_index)

    @staticmethod
    def get_goto_hack_line(goto_hack_i):
        return "goto/32 :goto_hack_{0}".format(goto_hack_i), ":goto_hack_{0}".format(goto_hack_i)
    
    @staticmethod
    def get_goto_hack_back(goto_hack_i):
        return "goto/32 :goto_hack_back_{0}".format(goto_hack_i), ":goto_hack_back_{0}".format(goto_hack_i)

    @staticmethod
    def get_tracking_insns(regs, cover_index):
        const_ins = "const/16" if cover_index < SINT16_MAX else "const"
        line1 = "{} {}, {}".format(const_ins, regs.v2, hex(cover_index))
        line2 = "aput-boolean %s, %s, %s" % (regs.v1, regs.v0, regs.v2)
        return [line1, line2]
    
    @staticmethod
    def get_instrumented_labels(labels, regs, cover_index, instrument=True):
        insns = []
        is_try_end = False
        for l in labels:
            if instrument and not l.switch and not l.array_data:
                # Find the case when the new try_start goes immediatly after try_end 
                # and track this exceptional case.
                if is_try_end and l.name.startswith("try_start"):
                    insns.extend(MethodInstrumenter.get_tracking_insns(regs, cover_index))
                    cover_index += 1
                if l.name.startswith("try_end"):
                    is_try_end = True
                l.cover_code = cover_index
            insns.extend(l.get_lines())
        # Insert the only one track for a bunch of lables. We dont care to 
        # which of the labels the PC was navigated to. Handled in the report code.
            if instrument and not l.switch and not l.array_data:
                insns.extend(MethodInstrumenter.get_tracking_insns(regs, cover_index))
                cover_index += 1
        return (insns, cover_index)

    def get_instrumented_insns_and_labels(self, method, reg_map, regs, cover_index, instrument=True):
        lines = []
        block_move_insn = False
        labels = method.labels.values()
        labels_search = LabelReversedLoopSearch(labels)
        # The last insn is always goto, return or throw. We dont track them.
        last_insn_index = len(method.insns)-1
        labels = labels_search.find_reversed_by_index(last_insn_index + 1)
        if labels:
            insns, cover_index = MethodInstrumenter.get_instrumented_labels(
                labels, 
                regs, 
                cover_index,
                instrument and Granularity.is_instruction(self.granularity))
            lines[0:0] = insns
        goto_hack_i = 0
        throw_safe_indexes = []
        if method.synchronized:
            throw_safe_indexes = Utils.scan_synchronized_tries(method)
        # we start reading instructions from the end of the method in reversed loop
        for i in range(last_insn_index, -1, -1):
            insn = method.insns[i]
            insns = []
            if instrument:
                line = MethodInstrumenter.get_insn_change_registers(insn, reg_map)
            else:
                line = insn.get_line()
            is_throw_safe = Utils.is_in_ranges(i, throw_safe_indexes)
            # dont track 'return*'insns
            if insn.buf.startswith(".end packed-swi") or insn.buf.startswith(".end array"):
                print("OPCODE NAME: " + insn.opcode_name)
            if instrument and Granularity.is_instruction(self.granularity) and \
                not block_move_insn and \
                not insn.buf.startswith('return') and \
                not insn.buf.startswith('goto') and \
                not insn.buf.startswith('throw') and \
                insn.opcode_name != "packed-switch" and \
                insn.opcode_name != "nop":
                safe_insns, throwable_insns = MethodInstrumenter.get_throw_safe_tracking(line, regs, cover_index, goto_hack_i)
                lines[0:0] = safe_insns
                lines.extend(throwable_insns)
                if len(throwable_insns) > 0:
                    goto_hack_i += 1
                insn.cover_code = cover_index
                cover_index += 1
            lines.insert(0, line)
            # set this flag if instruction before current should not be instrumented
            block_move_insn = instrument and Granularity.is_instruction(self.granularity) and \
                self.not_instr_regex.match(insn.buf) is not None
            labels = labels_search.find_reversed_by_index(i)
            if labels:
                safe_insns, throwable_insns, cover_index = MethodInstrumenter.get_throw_safe_instr_labels(
                    labels, regs, cover_index, instrument and Granularity.is_instruction(self.granularity) and \
                    not block_move_insn, goto_hack_i)
                lines[0:0] = safe_insns
                lines.extend(throwable_insns)
                if len(throwable_insns) > 0:
                    goto_hack_i += 1
            # :try_end_x goes immediatly after monitor-enter
            if instrument and not block_move_insn and labels and method.insns[i-1].buf.startswith('monitor-enter') and any([any(l.tries) for l in labels]):
                block_move_insn = True
            #prev_insn = ins
        #first tracking statement in the method
        if instrument:
            insns = MethodInstrumenter.get_tracking_insns(regs, cover_index)
            lines[0:0] = insns
            method.cover_code = cover_index
            cover_index += 1

        return (lines, cover_index)

    @staticmethod
    def get_insn_change_registers(insn, reg_map):
        line = ''
        if insn.fmt:
            if insn.fmt == '35c':
                registers = []
                for r in range(len(insn.obj.registers)):
                    reg = insn.obj.registers[r]
                    if reg in reg_map:
                        reg = reg_map[reg]
                    registers.append(reg)
                line = insn.get_line(registers)
            else:# fmt == '3rc'
                reg_start = insn.obj.reg_start
                reg_end = insn.obj.reg_end
                if reg_start in reg_map:
                    reg_start = reg_map[reg_start]
                if reg_end in reg_map:
                    reg_end = reg_map[reg_end]
                line = insn.get_line([reg_start, reg_end])
        else:
            line = insn.get_line()
            if not line.startswith('.'):
                # regex examples: " p0", " p1", " p2"
                matched = re.findall(r'\s(p\d+)(?:,|$)', line)
                if len(matched) > 0:
                    line = MethodInstrumenter.replace_registers(line, matched, reg_map)
        return line

    @staticmethod
    def replace_registers(line, matched, reg_map):
        for reg in matched:
            line = re.sub('(%s)' % reg, reg_map[reg], line, 1) 
        return line

    @staticmethod
    def get_throw_safe_tracking(line, regs, cover_index, goto_hack_i):
        '''Operates goto insns to move track insns that can raise a VerifyChecker
        error in the end of method'''
        safe_insns = []
        throwable_insns = []
        goto_hack, goto_lbl = MethodInstrumenter.get_goto_hack_line(goto_hack_i)
        goto_back, goto_back_lbl = MethodInstrumenter.get_goto_hack_back(goto_hack_i)
        safe_insns.append(goto_hack)
        safe_insns.append(goto_back_lbl)
        throwable_insns.append(goto_lbl)
        throwable_insns.extend(MethodInstrumenter.get_tracking_insns(regs, cover_index))
        throwable_insns.append(goto_back)
        return safe_insns, throwable_insns
    
    def get_tracking_method_init_insns(self, treeId, method, reg_map, is_static, class_name, regs, class_number):
        ''' Returns init instructions for the beginnning of a method.
        The code does not track anything yet.
        '''
        insns = []
        if not is_static:
            move = "move-object/16 {}, {}".format(reg_map['p0'], 'p0')
            insns.append(move)
        sorted_keys = sorted(reg_map.keys(), key=lambda x: int(x[1:]))
        # p0 register is a link for self object if method is not static
        is_self_object = 1
        if is_static:
            is_self_object = 0
        reg_index = is_self_object

        i = 0
        move = ""
        for i in range(len(method.paras)):
            p = sorted_keys[reg_index]
            v = reg_map[p]
            if method.paras[i].basic and method.paras[i].dim == 0:
                if method.paras[i].words == 2:
                    move = "move-wide/16 %s, %s" % (v, p)
                    reg_index += 1
                else:
                    move = "move/16 %s, %s" % (v, p)
            else:
                move = "move-object/16 %s, %s" % (v, p)
            insns.append(move)
            reg_index += 1

        init0 = "sget-object {}, {}:[Z".format(regs.v0, AcvReporter.get_reporter_field(treeId, class_name, class_number))
        init1 = "const/16 {}, 0x1".format(regs.v1)
        insns.append(init0)
        insns.append(init1)
        return insns
    

    def instrument_method(self, treeId, method, cover_index, class_name, class_number, method_number=0, instrument=True):
        lines = []
        odd_regs = 0
        if instrument:
            odd_regs = 3
        is_not_abstract_or_native = 'abstract' not in method.access and 'native' not in method.access
        is_not_native = 'native' not in method.access
        if is_not_abstract_or_native:
            is_static = MethodInstrumenter.is_method_static(method)
            reg_map = MethodInstrumenter.map_registers_p_to_v(method, is_static)
            regs = InstrumentingRegisters(method.registers, method.paras, is_static)
            insns, cover_index= self.get_instrumented_insns_and_labels(method, reg_map, regs, cover_index, instrument)
            lines.extend(insns)
            if instrument:
                insns = self.get_tracking_method_init_insns(treeId, method, reg_map, is_static, class_name, regs, class_number)
                lines[0:0] = insns
            method_number += 1
        annotations = method.get_annotations()
        if annotations:
            lines[0:0] = annotations
        if is_not_native:
            parameters = method.get_parameters()
            if parameters:
                lines[0:0] = parameters
        if is_not_abstract_or_native:
            lines.insert(0, method.get_registers_line(odd_regs=odd_regs))
        lines.insert(0, method.get_method_line())
        lines.append(method.get_end_line())
        return (lines, cover_index, method_number, is_not_abstract_or_native)


class SmaliHelper(object):
    @staticmethod
    def len_paras(paras):
        # dalvik uses register pairs for J(long) and D(double) types
        count = sum([p.words for p in paras])
        return count
    
class InstrumentingRegisters(object):
    def __init__(self, registers, paras, is_static):
        self.regs_amt = 0
        self.v0 = ''
        self.v1 = ''
        self.v2 = ''
        self.init(registers, paras, is_static)

    def init(self, registers, paras, is_static):
        self.regs_amt = registers + 3
        self_p0 = 1
        if is_static:
            self_p0 = 0
        last_new_reg_amt = self.regs_amt + SmaliHelper.len_paras(paras) - 1 + self_p0
        self.v0 = 'v%s' % (last_new_reg_amt - 2)
        self.v1 = 'v%s' % (last_new_reg_amt - 1)
        self.v2 = 'v%s' % (last_new_reg_amt)


class LabelReversedLoopSearch(object):
    '''Allows to find an element in a list sequentially. Only usefull for reversed
    loops. We don't whant to check many times the same objects.'''

    def __init__(self, labels):
        self.is_not_empty = False
        if not labels:
            return
        self.is_not_empty = True
        self.labels = sorted(labels, key=lambda x: (x.lid, x.index))
        self.current_element_i = len(self.labels)-1
        self.next_label_index = self.labels[self.current_element_i].index

    def find_reversed_by_index(self, ins_index):
        if not self.is_not_empty or self.next_label_index < ins_index:
            # means there is no label for this instruction
            return None
        labels = []
        for i in range(self.current_element_i,-1,-1):
            if self.labels[i].index < ins_index:
                self.next_label_index = self.labels[i].index
                self.current_element_i = i
                break
            if self.labels[i].index == ins_index:
                labels.append(self.labels[i])
        return list(reversed(labels))

