import re
from ..smiler.instrumenting.apkil.constants import BASIC_TYPES

rx = r"^invoke-(direct|super)"

def get_invoke_non_virt_methods(smalitree):
    invokes = set()
    for cl in smalitree.classes:
        for m in cl.methods:
            for insn in m.insns:
                res = re.search(rx, insn.opcode_name)
                if res:
                    segs = insn.buf.split()
                    invokes.add(segs[-1])
    return invokes


def get_invoke_direct_methods(smalitree):
    invokes = set()
    for cl in smalitree.classes:
        for m in cl.methods:
            for insn in m.insns:
                if insn.buf.startswith("invoke-direct"):
                    segs = insn.buf.split()
                    invokes.add(segs[-1])
    return invokes

def get_invoke_static_methods(smalitree):
    invokes = set()
    for cl in smalitree.classes:
        for m in cl.methods:
            for insn in m.insns:
                if insn.buf.startswith("invoke-static"):
                    segs = insn.buf.split()
                    invokes.add(segs[-1])
    return invokes                

def get_invoke_super_methods(smalitree):
    invokes = set()
    for cl in smalitree.classes:
        for m in cl.methods:
            for insn in m.insns:
                if insn.buf.startswith("invoke-super"):
                    segs = insn.buf.split()
                    invokes.add(segs[-1])
    return invokes                



def get_method_descriptions(smalitree):
    descriptions = set()
    for cl in smalitree.classes:
        for m in cl.methods:
            full_name = "{}->{}".format(cl.name, m.descriptor)
            descriptions.add(full_name)
    return descriptions


def get_class_method_dict(invokes):
    invokes_dict = {}
    for cm in invokes:
        c, m = cm.split('->')
        if c not in invokes_dict:
            invokes_dict[c] = []
        invokes_dict[c].append(m)
    return invokes_dict

def count_methods(smalitree):
    basics = 0
    objects_count = 0
    for cl in smalitree.classes:
        for m in cl.methods:
            if not m.called:
                index = m.descriptor.rfind(')')+1
                rtype = m.descriptor[index:]
                if rtype in BASIC_TYPES:
                    basics += 1
                else:
                    objects_count += 1
                    print(cl.name+"->"+ m.descriptor)
    print("methods with basic types: {}".format(basics))
    print("methods with object types: {}".format(objects_count))

def remove_methods_by_invokes(smalitree, to_remove_invokes):
    invokes_dict = get_class_method_dict(to_remove_invokes)
    i = 0
    for c in smalitree.classes:
        if c.name in invokes_dict:
            for m in c.methods[:]:
                if not m.is_constructor and m.descriptor in invokes_dict[c.name]:
                    c.methods.remove(m)
                    i += 1
    print("{} methods not anymore mentioned in invoke instructions removed".format(i))
