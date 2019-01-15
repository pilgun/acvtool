import os
import re
import sys
import shutil
import logging
import cPickle as pickle
from apkil.smalitree import SmaliTree
from apkil.insnnode import InsnNode
from pkg_resources import resource_filename
from utils import Utils
from acv_reporter import AcvReporter
from ..granularity import Granularity

class Instrumenter(object):
    ''' Instrumenter consists of instrumenting code to track smali instructions in
    smalitree.'''

    not_instr_regex = re.compile("^(move-result|move-exception).*$")
    dir_path = sys.path[0]
    instrumentation_smali_path = resource_filename('smiler.resources.instrumentation', 'smali')

    def __init__(self, smalitree, granularity, package, dbg_start=None, dbg_end=None, mem_stats=None):
        self.smalitree = smalitree
        self.granularity = Granularity.GRANULARITIES[granularity]
        self.insns = []
        self.class_traces = []
        self.package = package
        self.dbg = dbg_start is not None
        self.dbg_start = dbg_start
        self.dbg_end = dbg_end
        self.mem_stats = mem_stats

    def instrument(self):
        '''Generates tracking code for evry smali instruction and label.'''
        print('instrumenting')

    def save_instrumented_smali(self, output_dir, instrument=True):
        '''Saves instrumented smali to the specified directory/'''
        print("saving instrumented smali:  %s..." % output_dir)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)
        classes_info = []
        class_number = 0 # to make array name unique
        # Helps to find specific method that cased a fail after the instrumentation.
        # See '# Debug purposes' below
        method_number = 0
        # dbg_ means specific part of the code defined by dbg_start-dbg_end
        # numbers will be instrumented
        dbg_instrument = instrument
        for class_ in self.smalitree.classes:
            class_path = os.path.join(output_dir, class_.folder, class_.file_name)
            code, cover_index, method_number, is_instrumented = self.instrument_class(
                class_, 
                class_number, 
                method_number=method_number,
                instrument=dbg_instrument,
                dbg_start=self.dbg_start, 
                dbg_end=self.dbg_end)
            if dbg_instrument and is_instrumented:
                classes_info.append((class_.name, cover_index, class_number))
                class_number += 1
            self.save_class(class_path, code)
            if self.dbg and dbg_instrument and method_number > self.dbg_end: # Now leave other code not instrumented.
                dbg_instrument = False
        if self.dbg:
            print("Number of methods instrumented: {0}-{1} from {2}".format(self.dbg_start, self.dbg_end, method_number))
        if instrument:
            self.generate_reporter_class(classes_info, output_dir)
            if self.mem_stats:
                self.save_reporter_array_stats(classes_info)
            Utils.copytree(self.instrumentation_smali_path, output_dir)
        
    def generate_reporter_class(self, classes_info, dir_path):
        acv_reporter = AcvReporter(classes_info)
        acv_reporter.save(dir_path)

    def save_reporter_array_stats(self, classes_info, verbose=False):
        log_path = os.path.join("allocation_log.csv")
        csv_text = ""
        if self.mem_stats == "verbose":
            entries = ["{},{},{}".format(self.package, cl[0], cl[1]) for cl in classes_info]
            csv_text = "\n".join(entries)
        else:
            memory = sum(cl[1] for cl in classes_info)
            logging.info("{} bytes allocated in AcvReporter.smali".format(memory))
            csv_text = "{},{}".format(self.package, memory)
        Utils.log_entry(log_path, csv_text+'\n')

    def instrument_class(self, smali_class, class_number, method_number=0, instrument=True, dbg_start=None, dbg_end=None):
        class_lines = []
        cover_index = 0
        entry_lines = []
        entry_lines.extend(smali_class.get_class_description())
        entry_lines.extend(smali_class.get_annotations())
        entry_lines.extend(smali_class.get_fields())

        method_lines = []
        is_instrumented = False
        for meth in smali_class.methods:
            dbg_instrument = self.get_dbg_instrument(
                instrument,
                method_number,
                dbg_start,
                dbg_end)
            method_lines, cover_index, method_number, m_instrumented = self.instrument_method(
                meth,
                cover_index, smali_class.name,
                class_number,
                method_number,
                dbg_instrument)
            is_instrumented |= m_instrumented
            class_lines.extend(method_lines)
        class_lines[0:0] = entry_lines
        return ('\n'.join(class_lines), cover_index, method_number, is_instrumented)

    def get_dbg_instrument(self, instrument, method_number, dbg_start,  dbg_end):
        return (instrument and dbg_start is None) \
            or (instrument and dbg_start is not None and method_number >= dbg_start and method_number <= dbg_end)

    def instrument_method(self, method, cover_index, class_name, class_number, method_number=0, instrument=True):
        lines = []
        odd_regs = 0
        if instrument:
            odd_regs = 3
        is_not_abstract_or_native = 'abstract' not in method.access and 'native' not in method.access
        is_not_native = 'native' not in method.access
        if is_not_abstract_or_native:
            is_static = self.is_method_static(method)
            reg_map = self.map_registers_p_to_v(method, is_static)
            regs = InstrumentingRegisters(method.registers, method.paras, is_static)
            insns, cover_index= self.get_instrumented_insns_and_labels(method, reg_map, regs, cover_index, instrument)
            lines.extend(insns)
            if instrument:
                insns = self.get_tracking_method_init_insns(method, reg_map, is_static, class_name, regs, class_number)
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
    
    def map_registers_p_to_v(self, method, is_static):
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

    def is_method_static(self, method):
        if 'static' in method.access:
            return True
        return False
    
    def get_instrumented_insns_and_labels(self, method, reg_map, regs, cover_index, instrument=True):
        lines = []
        block_move_insn = False
        labels = method.labels.values()
        labels_search = LabelReversedLoopSearch(labels)
        # The last insn is always goto, return or throw. We dont track them.
        last_insn_index = len(method.insns)-1
        labels = labels_search.find_reversed_by_index(last_insn_index + 1)
        if labels:
            insns, cover_index = self.get_instrumented_labels(
                labels, 
                regs, 
                cover_index,
                instrument and Granularity.is_instruction(self.granularity))
            lines[0:0] = insns
        goto_hack_i = 0
        throw_safe_indexes = []
        if method.synchronized:
            throw_safe_indexes = Utils.scan_synchronized_tries(method)
        # we start reading the instructions from the end of the method in reversed loop
        for i in range(last_insn_index, -1, -1):
            insns = []
            if instrument:
                line = self.get_insn_change_registers(method.insns[i], reg_map)
            else:
                line = method.insns[i].get_line()
            is_throw_safe = Utils.is_in_ranges(i, throw_safe_indexes)
            # dont track 'return*'insns
            if instrument and Granularity.is_instruction(self.granularity) and \
                not block_move_insn and \
                not method.insns[i].buf.startswith('return') and \
                not method.insns[i].buf.startswith('goto') and \
                not method.insns[i].buf.startswith('throw'):
                safe_insns, throwable_insns = self.get_throw_safe_tracking(line, regs, cover_index, goto_hack_i)
                lines[0:0] = safe_insns
                lines.extend(throwable_insns)
                if len(throwable_insns) > 0:
                    goto_hack_i += 1
                method.insns[i].cover_code = cover_index
                cover_index += 1
            lines.insert(0, line)
            # set this flag if instruction before current should not be instrumented
            block_move_insn = instrument and Granularity.is_instruction(self.granularity) and \
                self.not_instr_regex.match(method.insns[i].buf) is not None
            labels = labels_search.find_reversed_by_index(i)
            if labels:
                safe_insns, throwable_insns, cover_index = self.get_throw_safe_instr_labels(
                    labels, regs, cover_index, instrument and Granularity.is_instruction(self.granularity) and \
                    not block_move_insn, goto_hack_i)
                lines[0:0] = safe_insns
                lines.extend(throwable_insns)
                if len(throwable_insns) > 0:
                    goto_hack_i += 1
            # :try_end_x goes immediatly after monitor-enter
            if instrument and not block_move_insn and labels and method.insns[i-1].buf.startswith('monitor-enter') and any([any(l.tries) for l in labels]):
                block_move_insn = True
        #first tracking statement in the method
        if instrument:
            insns = self.get_tracking_insns(regs, cover_index)
            lines[0:0] = insns
            method.cover_code = cover_index
            cover_index += 1

        return (lines, cover_index)

    def get_goto_hack_line(self, goto_hack_i):
        return "goto/32 :goto_hack_{0}".format(goto_hack_i), ":goto_hack_{0}".format(goto_hack_i)

    def get_goto_hack_back(self, goto_hack_i):
        return "goto/32 :goto_hack_back_{0}".format(goto_hack_i), ":goto_hack_back_{0}".format(goto_hack_i)

    def get_throw_safe_tracking(self, line, regs, cover_index, goto_hack_i):
        '''Operates goto insns to move track insns that can raise a VerifyChecker
        error in the end of method'''
        safe_insns = []
        throwable_insns = []
        goto_hack, goto_lbl = self.get_goto_hack_line(goto_hack_i)
        goto_back, goto_back_lbl = self.get_goto_hack_back(goto_hack_i)
        safe_insns.append(goto_hack)
        safe_insns.append(goto_back_lbl)
        throwable_insns.append(goto_lbl)
        throwable_insns.extend(self.get_tracking_insns(regs, cover_index))
        throwable_insns.append(goto_back)
        return safe_insns, throwable_insns

    def get_throw_safe_instr_labels(self, labels, regs, cover_index, instrument, goto_hack_i):
        safe_insns = []
        throwable_insns = []

        for l in labels:
            safe_insns.extend(l.get_lines())
            if instrument:
                l.cover_code = cover_index
        if instrument:
            goto, goto_lbl = self.get_goto_hack_line(goto_hack_i)
            goto_back, goto_back_lbl = self.get_goto_hack_back(goto_hack_i)
            safe_insns.append(goto)
            safe_insns.append(goto_back_lbl)
            throwable_insns.append(goto_lbl)
            throwable_insns.extend(self.get_tracking_insns(regs, cover_index))
            throwable_insns.append(goto_back)
            cover_index += 1
        return (safe_insns, throwable_insns, cover_index)

    def get_instrumented_labels(self, labels, regs, cover_index, instrument=True):
        insns = []
        is_try_end = False
        for l in labels:
            if instrument:
                # Find the case when the new try_start goes immediatly after try_end 
                # and track this exceptional case.
                if is_try_end and l.name.startswith("try_start"):
                    insns.extend(self.get_tracking_insns(regs, cover_index))
                    cover_index += 1
                if l.name.startswith("try_end"):
                    is_try_end = True
                l.cover_code = cover_index
            insns.extend(l.get_lines())
        # Insert the only one track for a bunch of lables. We dont care to 
        # which of the labels the PC was navigated to. Handled in the report code.
            if instrument:
                insns.extend(self.get_tracking_insns(regs, cover_index))
                cover_index += 1
        return (insns, cover_index)

    def get_tracking_method_init_insns(self, method, reg_map, is_static, class_name, regs, class_number):
        ''' Returns init instructions for the beginnning of a method.
        The code does not track anything yet.
        '''
        insns = []
        if not is_static:
            move = "move-object/16 %s, %s" % (reg_map['p0'], 'p0')
            insns.append(move)
        sorted_keys = sorted(reg_map.iterkeys(), key=lambda x: int(x[1:]))
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
            if method.paras[i].basic and method.paras[i].dim is 0:
                if method.paras[i].words == 2:
                    move = "move-wide/16 %s, %s" % (v, p)
                    reg_index += 1
                else:
                    move = "move/16 %s, %s" % (v, p)
            else:
                move = "move-object/16 %s, %s" % (v, p)
            insns.append(move)
            reg_index += 1

        init0 = "sget-object {}, {}:[Z".format(regs.v0, AcvReporter.get_reporter_field(class_name, class_number))
        init1 = "const/16 {}, 0x1".format(regs.v1)
        insns.append(init0)
        insns.append(init1)
        return insns

    def get_tracking_insns(self, regs, cover_index):
        line1 = "const/16 %s, %s" % (regs.v2, hex(cover_index))
        line2 = "aput-boolean %s, %s, %s" % (regs.v1, regs.v0, regs.v2)
        return [line1, line2]
    
    def get_insn_change_registers(self, insn, reg_map):
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
                matched = re.findall('\s(p\d+)(?:,|$)', line)
                if len(matched) > 0:
                    line = self.replace_registers(line, matched, reg_map)
        return line

    def replace_registers(self, line, matched, reg_map):
        for reg in matched:
            line = re.sub('(%s)' % reg, reg_map[reg], line, 1) 
        return line

    def save_class(self, output_path, smali_code):
        '''Save instrumented Smali class file.'''
        file_dir, filename = os.path.split(output_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(output_path, 'w') as f:
            f.write(smali_code)

    def save_pickle(self, pickle_path):
        '''Saves source Smali code and links to the tracked instructions.'''
        output_dir, file_name = os.path.split(pickle_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(pickle_path, 'wb') as f:
            pickle.dump(self.smalitree, f, pickle.HIGHEST_PROTOCOL)
        print('pickle file saved: {0}'.format(pickle_path))

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

        self.labels = sorted(labels, key=lambda x: x.lid)
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

class SmaliHelper(object):
    @staticmethod
    def len_paras(paras):
        # dalvik uses register pairs for J(long) and D(double) types
        count = sum([p.words for p in paras])
        return count
