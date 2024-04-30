import os
import re
import sys
import logging
from .apkil import constants
from pkg_resources import resource_filename
from smiler.operations import binaries
from .utils import Utils
from .acv_classes import AcvReporter
from ..granularity import Granularity
from .config import SINT16_MAX

class Instrumenter(object):
    ''' Instrumenter consists of instrumenting code to track smali instructions in
    smalitree.'''

    not_instr_regex = re.compile("^(move-result|move-exception).*$")
    dir_path = sys.path[0]
    instrumentation_smali_path = resource_filename('smiler.resources.instrumentation', 'smali')

    def __init__(self, smalitree, acv_files_smali_dir, granularity, package, dbg_start=None, dbg_end=None, mem_stats=None, target_cl=None, target_mtd=None):
        self.smalitree = smalitree
        self.granularity = Granularity.GRANULARITIES[granularity]
        self.insns = []
        self.class_traces = []
        self.package = package
        self.dbg = dbg_start is not None
        self.dbg_start = dbg_start
        self.dbg_end = dbg_end
        self.mem_stats = mem_stats
        self.target_sm_cl = target_cl #Instrumenter.extract_target_sm_class(target_cl) if target_cl is not None else None
        self.target_sm_mtd = target_mtd #Instrumenter.extract_target_sm_mtd(target_cl, target_mtd) if target_mtd is not None and target_cl is not None else None
        self.class_info_list = []
        self.acv_files_smali_dir = acv_files_smali_dir


    @staticmethod
    def extract_target_sm_class(target_cl):
        '''Converts java-ish class name to smali representation.'''
        "android.support.multidex.a -> Landroid/support/multidex/a;"
        return "L{};".format(target_cl.replace(".", "/"))
    
    @staticmethod
    def extract_target_sm_mtd(target_cl, target_mtd):
        '''Converts java-ish method name to smali representation.'''
        "void android.support.multidex.a.g(android.content.Context) -> g(Landroid/content/Context;)V"
        ret_type, method_name = target_mtd.split()
        if ret_type in constants.BASIC_TYPES_BY_JAVA:
            ret_type = constants.BASIC_TYPES_BY_JAVA[ret_type]
        else:
            ret_type = "L" + ret_type.replace(".", "/")
        method_name = method_name[len(target_cl)+1:-1].replace("(", "(L", 1).replace(".", "/") + ";)" + ret_type
        return method_name

    @staticmethod
    def choose_acv_files_smali_dir(input_smali_dirs):
        '''Returns the name of the new smali_classes directory for ACV files.'''
        prime_smali_dir = input_smali_dirs[0]
        acvfiles_smali_dir = prime_smali_dir
        unpacked_apk = os.path.dirname(prime_smali_dir)
        all_smali_dirs = Utils.get_smali_dirs(unpacked_apk)
        if len(all_smali_dirs) > 1:
            # loop smali_classes dirs and calculate the new dir for ACV files
            if any(os.path.basename(d).startswith("smali_classes") for d in all_smali_dirs):
                max_dex = max([int(os.path.basename(d)[13:] if len(os.path.basename(d))>13 else 0) for d in all_smali_dirs])
                acvfiles_smali_dir = os.path.join(unpacked_apk, "smali_classes" + str(max_dex+1))
        # if len(all_smali_dirs) == 1 and self.smalitree.smalitrees[0].instrumented_method_number < config.METHOD_LIMIT:
        #     acvfiles_smali_dir = os.path.join(source_basepath, "smali_classes2")
        if not os.path.exists(acvfiles_smali_dir):
            os.mkdir(acvfiles_smali_dir)
        return acvfiles_smali_dir

        # if self.mem_stats:
        #     self.save_reporter_array_stats(classes_info)
        
    def save_instrumented_smalitrees(self):
        '''- Inserts tracking probes into smali code trees. 
        - Updates class_info_list for future covered code mapping. 
        - Adds AcvReporter classes.'''
        method_number = 0
        #last_class_info = None
        classes_info = self.save_instrumented_smalitree_by_class(self.smalitree, method_number, instrument=True)
        return classes_info


    def save_instrumented_smalitree_by_class(self, tree, method_number=0, instrument=True):
        '''Saves instrumented smali to the specified directory/'''
        output_dir = tree.foldername
        logging.info("saving instrumented smali: {}".format(output_dir))
        Utils.recreate_dir(output_dir)
        classes_info = []
        class_number = 0 # to make array name unique
        # Helps to find specific method that cased a fail after the instrumentation.
        # See '# Debug purposes' below
        #method_number = method_number
        # dbg_ means specific part of the code defined by dbg_start-dbg_end
        # numbers will be instrumented
        dbg_instrument = instrument
        # if last_class_info:
        #     cl_name, cover_index, class_number= last_class_info
        #     class_number += 1
        #temp_class = self.smalitree.classes[4]
        #print(temp_class.methods[2].insns[0].cover_code)
        for class_ in tree.classes:
            # if class_.name != "Landroidx/profileinstaller/d;":
            #     continue
            code, cover_index, method_number, is_instrumented = self.instrument_class(
                tree.Id,
                class_, 
                class_number, 
                method_number=method_number,
                instrument=dbg_instrument and not class_.ignore and (self.target_sm_cl is None or self.target_sm_cl == class_.name),
                dbg_start=self.dbg_start, 
                dbg_end=self.dbg_end)
            tree.instrumented_method_number = method_number
            if dbg_instrument and class_.is_coverable(): # is_instrumented
                classes_info.append((class_.name, cover_index, class_number))
                class_number += 1
            class_path = os.path.join(output_dir, class_.folder, class_.file_name)
            self.save_class(class_path, code)
            if self.dbg and dbg_instrument and method_number > self.dbg_end: # Now leave other code not instrumented.
                dbg_instrument = False
            #print(self.smalitree.classes[4].methods[2].insns[0].cover_code)
            #print(temp_class.methods[2].insns[0].cover_code)
        if self.dbg:
            print("Number of methods instrumented: {0}-{1} from {2}".format(self.dbg_start, self.dbg_end, method_number))
        return classes_info


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


    def instrument_class(self, treeId, smali_class, class_number, method_number=0, instrument=True, dbg_start=None, dbg_end=None):
        # method_number is app through counter
        class_lines = []
        cover_index = 0
        entry_lines = []
        entry_lines.extend(smali_class.get_class_description())
        entry_lines.extend(smali_class.get_annotations())
        entry_lines.extend(smali_class.get_fields())

        method_lines = []
        is_instrumented = False
        for meth in smali_class.methods:
            # if meth.descriptor != "i(Landroid/content/Context;Ljava/util/concurrent/Executor;Landroidx/profileinstaller/d$c;Z)V":
            #     continue
            to_instrument = instrument and not meth.ignore and meth.registers < 253 and (self.target_sm_mtd is None or self.target_sm_mtd == meth.descriptor)
            dbg_instrument = self.get_dbg_instrument(to_instrument, method_number, dbg_start, dbg_end)
            method_lines, cover_index, method_number, m_instrumented = self.instrument_method(
                treeId,
                meth,
                cover_index, smali_class.name,
                class_number,
                method_number,
                dbg_instrument)
            is_instrumented |= m_instrumented
            class_lines.extend(method_lines)
        class_lines[0:0] = entry_lines
        return ('\n'.join(class_lines), cover_index, method_number, is_instrumented)

    @staticmethod
    def get_dbg_instrument(instrument, method_number, dbg_start,  dbg_end):
        return (instrument and dbg_start is None) \
            or (instrument and dbg_start is not None and method_number >= dbg_start and method_number <= dbg_end)

    def instrument_method(self, treeId, method, cover_index, class_name, class_number, method_number=0, instrument=True):
        lines = []
        odd_regs = 0
        if instrument:
            odd_regs = 3
        is_not_abstract_or_native = 'abstract' not in method.access and 'native' not in method.access
        is_not_native = 'native' not in method.access
        if is_not_abstract_or_native:
            is_static = Instrumenter.is_method_static(method)
            reg_map = Instrumenter.map_registers_p_to_v(method, is_static)
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
    def is_method_static(method):
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
            insns, cover_index = Instrumenter.get_instrumented_labels(
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
                line = Instrumenter.get_insn_change_registers(insn, reg_map)
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
                safe_insns, throwable_insns = self.get_throw_safe_tracking(line, regs, cover_index, goto_hack_i)
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
            #prev_insn = ins
        #first tracking statement in the method
        if instrument:
            insns = Instrumenter.get_tracking_insns(regs, cover_index)
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
        throwable_insns.extend(Instrumenter.get_tracking_insns(regs, cover_index))
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
            throwable_insns.extend(Instrumenter.get_tracking_insns(regs, cover_index))
            throwable_insns.append(goto_back)
            cover_index += 1
        return (safe_insns, throwable_insns, cover_index)

    @staticmethod
    def get_instrumented_labels(labels, regs, cover_index, instrument=True):
        insns = []
        is_try_end = False
        for l in labels:
            if instrument and not l.switch and not l.array_data:
                # Find the case when the new try_start goes immediatly after try_end 
                # and track this exceptional case.
                if is_try_end and l.name.startswith("try_start"):
                    insns.extend(Instrumenter.get_tracking_insns(regs, cover_index))
                    cover_index += 1
                if l.name.startswith("try_end"):
                    is_try_end = True
                l.cover_code = cover_index
            insns.extend(l.get_lines())
        # Insert the only one track for a bunch of lables. We dont care to 
        # which of the labels the PC was navigated to. Handled in the report code.
            if instrument and not l.switch and not l.array_data:
                insns.extend(Instrumenter.get_tracking_insns(regs, cover_index))
                cover_index += 1
        return (insns, cover_index)

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

    @staticmethod
    def get_tracking_insns(regs, cover_index):
        const_ins = "const/16" if cover_index < SINT16_MAX else "const"
        line1 = "{} {}, {}".format(const_ins, regs.v2, hex(cover_index))
        line2 = "aput-boolean %s, %s, %s" % (regs.v1, regs.v0, regs.v2)
        return [line1, line2]
    
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
                matched = re.findall('\s(p\d+)(?:,|$)', line)
                if len(matched) > 0:
                    line = Instrumenter.replace_registers(line, matched, reg_map)
        return line

    @staticmethod
    def replace_registers(line, matched, reg_map):
        for reg in matched:
            line = re.sub('(%s)' % reg, reg_map[reg], line, 1) 
        return line

    def save_class(self, output_path, smali_code):
        '''Save instrumented Smali class file.'''
        file_dir = os.path.dirname(output_path)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(output_path, 'w') as f:
            f.write(smali_code)

    def save_pickle(self, pickle_dir):
        '''Saves source Smali code and links to the tracked instructions.'''
        if not os.path.exists(pickle_dir):
            os.makedirs(pickle_dir)
        pth = os.path.join(pickle_dir, "{}_{}.pickle".format(self.package, self.smalitree.Id))
        binaries.save_pickle(self.smalitree, pth)


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

class SmaliHelper(object):
    @staticmethod
    def len_paras(paras):
        # dalvik uses register pairs for J(long) and D(double) types
        count = sum([p.words for p in paras])
        return count
