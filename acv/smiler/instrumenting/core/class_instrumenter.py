import logging

from .method_instrumenter import SmaliHelper

class ClassInstrumenter:
    def __init__(self, methodInstr, target_sm_mtd=None):
        self.methodInstr = methodInstr
        self.target_sm_mtd = target_sm_mtd


    @staticmethod
    def get_dbg_instrument(instrument, method_number, dbg_start,  dbg_end):
        return (instrument and dbg_start is None) \
            or (instrument and dbg_start is not None and method_number >= dbg_start and method_number <= dbg_end)


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
            to_instrument = instrument and not meth.ignore and meth.registers < 253 and (SmaliHelper.len_paras(meth.paras)+meth.registers)<253 and (self.target_sm_mtd is None or self.target_sm_mtd == meth.descriptor)
            if instrument and not meth.ignore and SmaliHelper.len_paras(meth.paras) + meth.registers > 252:
                logging.info(f"Skipping method: {smali_class.name}->{meth.name}... Too many registers occupied: {meth.registers} registers + {SmaliHelper.len_paras(meth.paras)} parameter regs > 252")
            dbg_instrument = ClassInstrumenter.get_dbg_instrument(to_instrument, method_number, dbg_start, dbg_end)
            method_lines, cover_index, method_number, m_instrumented = self.methodInstr.instrument_method(
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