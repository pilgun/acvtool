import re


def remove_not_covered(smalitree):
    references = get_references(smalitree)
    i = 0
    for cl in smalitree.classes:
        if "abstract" not in cl.access and "interface" not in cl.access and not methods_called(cl) and cl.name not in references:
            smalitree.classes.remove(cl)
            i += 1
    print("{} classes removed".format(i))


def methods_called(klass):
    return sum(m.called for m in klass.methods)

check_cast_rx = r"^check-cast\s(v|p)\d+, (?P<invoke>.*)"

def get_references(smalitree):
    references = set()
    i = 0
    for cl in smalitree.classes:
        for m in cl.methods:
            for insn in m.insns:
                res = re.search(check_cast_rx, insn.buf)
                if res:
                    references.add(res.group("invoke"))
                    i += 1
    print("{} check-cast insns found".format(i))
    print("{} references found".format(len(references)))
    return references

ref_only = r"^(?:const-class|check-cast|instance-of|new-instance|new-array|filled-new-array|(?:iget|iput|sget|sput)(:?-[a-z]+)?|invoke-[a-z]+(?:/range)?)\s[\s{},vp0-9.]+,\s(?P<ref>.*)$"
ref_ins_regex = r"^(?:const-class|check-cast|instance-of|new-instance|new-array|filled-new-array|(?:iget|iput|sget|sput)(:?-[a-z]+)?|invoke-[a-z]+(?:/range)?)\s[\s{},vp0-9.]+,\s(?P<ref>\[?(?P<cl_ref>[^-]+)(:?->(?:(?P<meth>[\w<>]+\((?P<arg>[^-]*)\)[^-]+)|(?P<field>\w+:.*)))?)$" #|
#(?P<cl_ref>.*;)(?:->(?P<meth_ref>[a-zA-Z_$0-9]+\(.*\).*)|(?P<field_ref>[a-zA-Z_$0-9]+:.*))?$

def get_mentioned(smalitree, ins_name):
    classes = set()
    for cl in smalitree.classes:
        for m in cl.methods:
            for ins in m.insns:
                if ins.buf.startswith(ins_name):
                    print(ins.buf)

# todo: add @proto
ref_ins_rx = r"^iget|iput|sget|sput|invoke"

def get_all_refs(smalitree):
    refs = dict()
    for cl in smalitree.classes:
        for m in cl.methods:
            for ins in m.insns:
                if ins.buf.startswith(ins_name):
                    print(ins.buf)


#-instructions having references to fields/classes
# const-string vAA, string@BBBB
# const-string/jumbo vAA, string@BBBBBBBB
# const-class vAA, type@BBBB
# check-cast vAA, type@BBBB
# instance-of vA, vB, type@CCCC
# new-instance vAA, type@BBBB
# new-array vA, vB, type@CCCC
# filled-new-array {vC, vD, vE, vF, vG}, type@BBBB
# filled-new-array/range {vCCCC .. vNNNN}, type@BBBB
# iget* #iinstanceop vA, vB, field@CCCC
# sget* #sstaticop vAA, field@BBBB
# invoke-kind {vC, vD, vE, vF, vG}, meth@BBBB
# invoke-kind/range {vCCCC .. vNNNN}, meth@BBBB
# invoke-polymorphic {vC, vD, vE, vF, vG}, meth@BBBB, proto@HHHH
# invoke-polymorphic/range {vCCCC .. vNNNN}, meth@BBBB, proto@HHHH	
# invoke-custom {vC, vD, vE, vF, vG}, call_site@BBBB
# invoke-custom/range {vCCCC .. vNNNN}, call_site@BBBB
# const-method-handle vAA, method_handle@BBBB
# const-method-type vAA, proto@BBBB