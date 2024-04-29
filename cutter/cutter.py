from smiler.instrumenting.apkil.insnnode import InsnNode


def remove_not_covered_instructions(smalitree):
    i = 0
    j = 0
    insns_amount = lambda classes: sum([sum([len(m.insns) for m in cl.methods]) for cl in classes])
    insns_orig = insns_amount(smalitree.classes)
    print("insns: {}".format(insns_orig))
    for cl in smalitree.classes:
        for m in cl.methods:
            for insn in m.insns:
                if insn.covered:
                    m.insns.remove(insn)
    insns_new = insns_amount(smalitree.classes)
    print("insns: {}".format(insns_new))

    print("left classes: {}".format(len(smalitree.classes)))
    print("removed {} classes".format(i))
    print("removed {} methods, left {}".format(j, sum([len(cl.methods) for cl in smalitree.classes])))


def remove_methods_in_not_covered_classes(smalitree):
    i = 0
    j = 0

    for cl in smalitree.classes:
        if cl.not_covered():
            print("{} {}".format(cl.name, cl.covered()))
            for m in cl.methods:
                if m.not_covered():
                    cl.methods.remove(m)
                    j+=1
            #smalitree.classes.remove(cl)
            i += 1
    print("left classes: {}".format(len(smalitree.classes)))
    print("removed {} classes".format(i))
    print("removed {} methods, left {}".format(j, sum([len(cl.methods) for cl in smalitree.classes])))


def get_all_method_invokes(smalitree):
    invokes = set()
    for cl in smalitree.classes:
        for m in cl.methods:
            for insn in m.insns:
                if insn.opcode_name.startswith("invoke"):
                    invokes.add(insn.obj.method_desc)
    return invokes

def get_all_methods_desc(smalitree):
    signatures = set()
    for cl in smalitree.classes:
        for m in cl.methods:
            signatures.add("{}->{}".format(cl.name, m.descriptor))
    return signatures


def remove_not_covered_if(smalitree):
    for cl in smalitree.classes:
        #if cl.name == "Landroid/support/v7/app/AppCompatDelegateImplBase;":
        if cl.name != "Landroid/support/constraint/ConstraintLayout;":
            continue
        # m = cl.methods[4]
        # print("method name: {}".format(m.descriptor))
        for m in cl.methods[7:8]:
            print(m.descriptor)
            # if m.name != "setChildrenConstraints":
            #     continue
            if not m.synchronized:
                start_ = 0
                block = False
                blocks = 0
                for i, insn in enumerate(m.insns):
                    # if i == 18:
                    #     print(i)
                    if not block and insn.opcode_name.startswith("if") and not insn.covered: # and insn.cover_code > -1 and not has_label_by_index(m.labels, i):
                        lbl_index = insn.buf.rfind(':')
                        m.insns[i] = InsnNode("goto {}".format(insn.buf[lbl_index:]))
                        start_ = i
                        block = True
                        continue
                    if block and has_label_by_index(m.labels, i): #(insn.covered or has_covered_lbl(m.labels, i)):
                        end_ = i
                        #print("\n".join([ins.buf for ins in m.insns[start_:end_]]))
                        del m.insns[start_+1:end_]
                        recalculate_label_indexes(m.labels, start_+1, end_)
                        block = False
                        blocks += 1
                        if blocks == 6:
                            break
                        #break
                #break
        #    break
        #for m in cl.methods:

def recalculate_label_indexes(labels, start_, end_):
    d = end_ - start_
    for (k, v) in labels.items():
        if v.index >= end_:
            v.index -= d


def has_label_by_index(labels, index):
    for (k, v) in labels.items():
        if v.index == index:
            return True
    return False

def has_covered_lbl(labels, index):
    for (k, v) in labels.items():
        if v.index == index:
            return v.covered
    return False
