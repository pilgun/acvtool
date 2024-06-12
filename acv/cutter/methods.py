import returns

def clean_not_executed_methods(smalitree):
    stub_methods = set()
    for cl in smalitree.classes:
        for m in cl.methods:
            full_name = "{}->{}".format(cl.name, m.descriptor)
            if m.is_constructor and not m.called:
                stub(full_name, m)
                stub_methods.add(full_name)
            if not m.is_constructor and not m.called:# and not m.synchronized:
                ret_type = returns.get_return_type(m.descriptor)
                stub(full_name, m, ret_type)
                full_name = "{}->{}".format(cl.name, m.descriptor)
                stub_methods.add(full_name)
    return stub_methods


def clean_not_exec_methods_range(smalitree, start, end):
    for i in range(start, end):
        cl =  smalitree.classes[i]
        for m in cl.methods:
            full_name = "{}->{}".format(cl.name, m.descriptor)
            if m.is_constructor and not m.called:
                stub(full_name, m)
            if not m.is_constructor and not m.called:# and not m.synchronized:
                ret_type = returns.get_return_type(m.descriptor)
                stub(full_name, m, ret_type)


def remove_static(smalitree):
    i = 0
    for cl in smalitree.classes:
        for m in cl.methods[:]:
            if not m.called and "static" in m.access:
                cl.methods.remove(m)
                i += 1
    print("{} static methods removed".format(i))


def stub(full_name, method, ret_type=None):
    method.labels = {}
    method.tries = []
    method.insns = []

    if ret_type:
        method.insns.extend(returns.get_return_insns(ret_type))
        #returns.set_defaults(method, ret_type)
    else:
        method.insns.extend(returns.default_constructor_insns)
        #returns.set_default_constructor_for(method)
    method.ignore = True
