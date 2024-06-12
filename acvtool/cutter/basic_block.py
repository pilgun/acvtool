import logging
import re
from operator import attrgetter
from . import returns
from .label_block import LBlock
from ..smiler.instrumenting.apkil.insnnode import InsnNode
from ..smiler.instrumenting.apkil.labelnode import LabelNode

# matched examples
#.catch Landroid/content/res/Resources$NotFoundException; {:try_start_0 .. :try_end_0} :catch_0
#if-ne v4, v5, :cond_5
#goto/16 :goto_a
labels_rx = r'^(?:goto[/1632]{0,3}|if-[a-z]*|\.catch)\s(?:(?:.*\s{:(?P<trystart>\w+)\s\.\.\s:(?P<tryend>\w+)}\s)|(?:(?:[vp]\d+,\s?)+))?:(?P<label>\w+)$'

def remove_blocks_from_selected_method(smalitree):
    for cl in smalitree.classes:#[518:519]
        #print("----------" + cl.name)
        # if cl.name != "L-;": #"Lme;":
        #     continue
        for m in cl.methods:
            # if m.descriptor != "initialize()V":
            #     continue
            if m.called:# and not (cl.name == "Lprd$c;") \
                #and not (cl.name == "Landroidx/emoji2/text/d;" and m.descriptor == "i()Z"):# and m.descriptor == "<init>(Landroid/content/Context;Landroid/util/AttributeSet;)V":
                #print_monitor_chunks(m)
                #print_catchall(m)
                # if not m.synchronized:
                #if m.descriptor == "d(Landroid/content/Intent;)V":#"onStartCommand(Landroid/content/Intent;II)I":
                #if m.synchronized:
                #print("----------"+m.descriptor)
                remove_blocks(m, cl.name)
                # if m.synchronized and not is_monitor_enter_covered(m):
                #     remove_blocks(m)
                #     m.tries = []

def clean_classes(smalitree, start, end):
    for i in range(start, end):
        cl =  smalitree.classes[i]
        for m in cl.methods:
            if m.called:# and not (cl.name == "Lprd$c;") \
                #and not (cl.name == "Landroidx/emoji2/text/d;" and m.descriptor == "i()Z"):
                remove_blocks(m, cl.name)


def clean_class_by_name(smalitree, cl_name, mtd_descriptor=None):
    for cl in smalitree.classes:
        if cl.name == cl_name:
            for m in cl.methods:
                if m.called and not mtd_descriptor or (mtd_descriptor and m.descriptor==mtd_descriptor):
                    remove_blocks(m, cl.name)


def print_catchall(method):
    lbl_by_ins_ind = {}
    for lk, lbl in method.labels.items():
        if lbl.index in lbl_by_ins_ind:
            lbl_by_ins_ind[lbl.index].append(lk)
        else:
            lbl_by_ins_ind[lbl.index] = [lk]
    for lk, lbl in method.labels.items():
        if lk.startswith("catchall"):
            print("----------" + method.descriptor)
            i = lbl.index
            if i > 0:
                if i-1 in lbl_by_ins_ind:
                    s = ",".join(lbl_by_ins_ind[i-1])
                    print(":"+s)
                print("{}: {}".format(i-1, method.insns[i].buf))
            for j in range(i, min(i+5, len(method.insns))):
                if j in lbl_by_ins_ind:
                    s = ",".join(lbl_by_ins_ind[j])
                    print(":"+s)
                print("{}: {}".format(j, method.insns[j].buf))


def print_monitor_chunks(method):
    for i, ins in enumerate(method.insns):
        if ins.buf.startswith("monitor-exit"):
            print("----------" + method.descriptor)
            for j in range(i-1 if i > 0 else i, min(i+5, len(method.insns))):
                print("{}: {}".format(j, method.insns[j].buf))


def remove_blocks(method, cl_name):
    if len(method.insns) == 1: # keep empty methods without processing
        return
    #print(method.descriptor)
    #if method.descriptor == "a(I[B)Z":
    # if method.synchronized:
    #     remove_single_not_called_try(method)
    #remove_not_called_tries(method)
    align_monitor_enter(method)
    cover_catch_labels(method)
    align_tries2(method)
    #check_insn_followed_by_trycatch(method) # to remove?
    lblocks = get_label_blocks(method)
    collapse_lblocks_to_correct_catchall(method, lblocks)
    lblocks_catchall_goto_monitor_exit_check(method, lblocks)
    mark_not_exec_catchall_monitor_exit(method, lblocks, cl_name)
    #remove_not_called_tries(method, lblocks)
    excluded_lbls = select_covered_l_blocks(method, lblocks)
    if excluded_lbls:
        remove_not_referenced_label_calls(method, excluded_lbls) # new
    remove_ifs(method)
    update_tries(method)
    remove_extra_tries(method)
    ##remove_catchs(method)
    remove_array_data(method)
    lblocks = get_label_blocks(method)
    check_not_referenced_goto_endings(method, lblocks, excluded_lbls, cl_name)
    merge_goto(method)
    clean_switch(method)
    check_pre_move_exception_insn(method)
    check_return_throw_in_the_end(method)
    # todo: to check now the move-exception,monitor-exit,throw sequence
    # merge_handlers(method)
    # check_if_labels_referenced(method)
    #remove_empty_switch_data(method)

def check_return_throw_in_the_end(method):
    last_ins = method.insns[-1].opcode_name
    if not (last_ins.startswith("return") or last_ins.startswith("throw")):
        ret_type = returns.get_return_type(method.descriptor)
        ret_insns = returns.get_return_insns(ret_type)
        method.insns.extend(ret_insns)



def lblocks_catchall_goto_monitor_exit_check(method, lblocks):
    '''
    Verifier workaround for move-exception, [goto], monitor-exit, return/throw sequence.
    :catchall_0
	move-exception v1
	goto :goto_2
	[other instructions]
	:goto_2
	monitor-exit v0
	throw v1
    '''
    if method.synchronized and any(lb.is_goto_monitor_exit for lb in lblocks):
        goto_blocks = {}
        for lb in lblocks:
            if lb.is_goto_monitor_exit:
                goto_lname = next(ln for ln in lb.labels if ln.startswith("goto"))
                goto_blocks[goto_lname] = lb
        if goto_blocks:
            for lb in lblocks:
                if lb.is_move_exception:
                    #a: move-exc, goto
                    #b: move-exc, move-obj, goto
                    goto_ins = method.insns[lb.end_i-1]
                    if goto_ins.buf.startswith("goto") and lb.end_i-lb.start_i<3:
                        goto_ins = method.insns[lb.end_i-1]
                        goto_lname = goto_ins.buf.split()[-1][1:]
                        if goto_lname in goto_blocks:
                            lb.is_goto_monitor_exit = True
                            goto_blocks[goto_lname].is_catchall = True
            for lname, lb in goto_blocks.items():
                ''' additinal case for move-exception, monitor-exit, throw/return
                :catchall
                move-exception v1
            	goto :goto_3
                [other insns]
                :goto_3
                monitor-exit v0
                :try_end_2
                .catchall {:try_start_2 .. :try_end_2} :catchall_0
                throw v1
                '''
                if lb.is_catchall and not lb.covered and lb.end_i-lb.start_i==1 \
                    and method.insns[lb.end_i].buf.startswith(".catch") \
                    and not method.insns[lb.end_i].covered:
                    i = lb.end_i
                    while i<len(method.insns) and method.insns[i].buf.startswith(".catch"):
                        i+=1
                    if i<len(method.insns) and re.match("^goto|return|throw", method.insns[i].buf):
                        method.insns.insert(lb.end_i, InsnNode(method.insns[i].buf))
                        recalculate_label_indexes_after_insert(method.labels, lb.end_i, 1)
                        recalculate_lblocks_after_insert(lblocks, lb.end_i, 1)


def collapse_lblocks_to_correct_catchall(method, lblocks):
    '''
    this method is to save the not covered :chatchall_* instructions 
    including the throw to satisfy the Verifier. Example:
    :catchall_0
    move-exception p1
    :try_start_1
    monitor-exit v0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0
    throw p1
    '''
    #pattern: ["move-exc", "monitor-exit", ".catchall", "throw"]

    if method.synchronized:
        for i, lb in enumerate(lblocks):
            if lb.is_catchall and not lb.covered and lb.end_i-lb.start_i<=2 \
                and method.insns[lb.start_i].buf.startswith("move-exc") \
                and lb.start_i+1<len(method.insns) \
                and method.insns[lb.start_i+1].buf.startswith("monitor-exit") \
                and not method.insns[lb.start_i+2].buf.startswith(".catch"):
                ending_lblock_start = lb.start_i+2
                if ending_lblock_start < len(method.insns) and i+1 < len(lblocks):
                    next_lb = lblocks[i+1]
                    if next_lb.start_i <= ending_lblock_start:
                        lb.end_i = next_lb.end_i
                        if i+2 < len(lblocks):
                            next_next_lb = lblocks[i+2]
                            if next_next_lb.start_i <= ending_lblock_start:
                                lb.end_i = next_next_lb.end_i
                                lblocks.remove(next_next_lb)
                        lblocks.remove(next_lb)


def mark_not_exec_catchall_monitor_exit(method, lblocks, cl_name):
    '''For this example we mark catchall_0 as is_monitor_exit so it stays in the code.
    We don't care here about monitor consistancy because we don't expect that code to work.
    It is only to satisfy the Runtime Verifier.'''
    '''
    Lcom/facebook/appevents/eventdeactivation/EventDeactivationManager

	:catchall_0
	move-exception v1
	:try_start_3
	invoke-static {v1, v0}, Lcom/facebook/internal/instrument/crashshield/CrashShieldHandler;->handleThrowable(Ljava/lang/Throwable;Ljava/lang/Object;)V
	:try_end_3
	.catchall {:try_start_3 .. :try_end_3} :catchall_1
	monitor-exit v0
    return-void
    '''
    # pattern: ["move-exc", "invoke-stat", (".catchall"), "monitor-exit", "return"]
    # .catchall and try/end here were removed by previous functions
    if method.synchronized:
        for i, lb in enumerate(lblocks):
            if lb.is_catchall and not lb.covered and lb.end_i-lb.start_i<=2 \
                and method.insns[lb.start_i].buf.startswith("move-exc") \
                and lb.start_i+2<len(method.insns) \
                and method.insns[lb.start_i+1].buf.startswith("invoke-stat") \
                and method.insns[lb.start_i+2].buf.startswith("monitor-exit"):
                lb.is_goto_monitor_exit = True # to keep the catchall block
                logging.info("catchall preserved {}->{}".format(cl_name, method.descriptor))


# removed goto before move-exception? -> get a runtime error
# this method checks that finalizing ins is before the move-exception
def check_pre_move_exception_insn(method):
    for ln, lbl in method.labels.items():
        if ln.startswith("catch") \
            and method.insns[lbl.index].buf.startswith("move-exc") \
            and lbl.index-1>0:
            i = lbl.index-1
            while i>0 and method.insns[i].buf.startswith(".catch"):
                i -= 1
            ins = method.insns[i]
            if not re.match("^goto|return|throw", ins.buf):
                ret_type = returns.get_return_type(method.descriptor)
                ret_insns = returns.get_return_insns(ret_type)
                method.insns[lbl.index:lbl.index] = ret_insns
                recalculate_label_indexes_after_insert(method.labels, lbl.index, len(ret_insns))


def check_not_referenced_goto_endings(method, lblocks, excluded_lbls, cl_name):
    for lb in lblocks:
        if lb.is_try_end:
            last_ins = method.insns[lb.end_i-1]
            if last_ins.buf.startswith("goto"):
                goto, lbl = last_ins.buf.split()
                if lbl[1:] in excluded_lbls:
                    method.insns.remove(last_ins)
                    ret_type = returns.get_return_type(method.descriptor)
                    ret_insns = returns.get_return_insns(ret_type)
                    method.insns[lb.end_i-1:lb.end_i-1] = ret_insns
                    recalculate_label_indexes_after_insert(method.labels, lb.end_i, len(ret_insns)-1)
                    recalculate_lblocks_after_insert(lblocks, lb.end_i, len(ret_insns)-1)
                    # = InsnNode("{} :{}".format(goto, method.labels.keys()[0]))
                    logging.warning("possible odd {}: {}->{}".format(method.insns[lb.end_i-1], cl_name, method.descriptor))
                    print(method.insns[lb.end_i-1])

def recalculate_label_indexes_after_insert(labels, start_, d):
    if d==0:
        return
    for (k, v) in labels.items():
        if v.index >= start_:
            v.index += d


def recalculate_lblocks_after_insert(lblocks, start_, d):
    if d==0:
        return
    for lb in lblocks:
        if lb.start_i >= start_:
            lb.start_i += d
        if lb.end_i >= start_:
            lb.end_i += d


def check_insn_followed_by_trycatch(method):
    '''This method seems does not do anything.'''
    #ind_to_lbl_dict = index_to_label(method)
    checked_insn_inds = set()
    for tr in method.tries:
        i = tr.end.index
        if checked_insn_inds and i < max(checked_insn_inds):
            continue
        while i < len(method.insns) and method.insns[i].buf.startswith(".catch"):
            i += 1
        if i >= len(method.insns):
            return
        ins = method.insns[i]
        if ins.buf.startswith("goto") or ins.buf.startswith("return") or ins.buf.startswith("throw"):
            # return ins after .catch probably is there to finalizes the basic block
            checked_insn_inds.add(i)
            # if method.insns[i-1].covered:
            #     method.insns[i].covered = True
            continue
            
        # if i not in ind_to_lbl_dict and i not in checked_insn_inds:
        #     checked_insn_inds.append(i)
        #     if not ins.covered and not \
        #         (i+1<len(method.insns) and ins.buf.startswith("invoke-") and \
        #         method.insns[i+1].buf.startswith("move-r") and method.insns[i+1].covered) \
        #         and not (ins.buf.startswith("goto") and i+1<len(method.insns) and method.insns[i+1].buf.startswith("move-exc")):
        #         new_name = "lbl_{}".format(i)
        #         method.labels[new_name] = LabelNode(":"+new_name, i, tr.end.lid+1)


def align_monitor_enter(method):
    '''This is a hack due to a bug/feature of acvtool when it does not 
    instrument monitor-enter instruction that stays just before the try_end_ label.'''
    if method.synchronized:
        for lname, lnode in method.labels.items():
            if lname.startswith("try_end") and lnode.covered and \
                lnode.index > 0 and method.insns[lnode.index-1].opcode_name.startswith("monitor-ent"):
                    method.insns[lnode.index-1].covered = True


def cover_catch_labels(method):
    '''Mark :catch* label as covered if it is followed 
    by the covered move-exception instruction.'''
    for lb in method.labels:
        ins_ind = method.labels[lb].index
        if not method.labels[lb].covered and ins_ind < len(method.insns) \
            and method.insns[ins_ind].opcode_name.startswith("move-exc") \
            and method.insns[ins_ind].covered:
            method.labels[lb].covered = True

LABELS_REG = "^(?:\.catch|if|go|pack|spar|fill).+ \:(\w+\_*\d*)$"

def check_if_labels_referenced(method):
    lbl_set = set()
    for ins in method.insns:
        if ins.buf.startswith(".catchall"):
            segs = ins.buf.split()
            start = segs[-4][2:]
            end = segs[-2][1:-1]
            handler = segs[-1][1:]
            lbl_set.add(start)
            lbl_set.add(end)
            lbl_set.add(handler)
        else:
            search_res = re.search(LABELS_REG, ins.buf)
            if search_res:
                lbl = search_res.groups()[0]
                lbl_set.add(lbl)

    for lbl in lbl_set:
        if lbl not in method.labels:
            print(lbl)
    print("-----------")
    for lbl in method.labels:
        if lbl not in lbl_set:
            print(lbl)


def merge_handlers(method):
    update_tries(method)
    handlers = get_try_handlers(method)
    sorted_handlers = sorted(handlers, key=lambda h: method.labels[h].lid)
    if len(sorted_handlers) > 1:
        to_remove_labels = set()
        to_remove_insns = set()
        change_labels = {}
        for i, current in enumerate(sorted_handlers):
            if i+1 < len(sorted_handlers):
                cur_l_ins_ind = method.labels[current].index
                next_l_ins_ind = method.labels[sorted_handlers[i+1]].index
                cur_ins = method.insns[cur_l_ins_ind]
                next_l_ins = method.insns[next_l_ins_ind]
                if cur_l_ins_ind + 2 == next_l_ins_ind \
                    and cur_ins.opcode_name.startswith("move-exception") \
                    and cur_ins.buf == next_l_ins.buf \
                    and method.insns[cur_l_ins_ind+1].buf == method.insns[next_l_ins_ind+1].buf:
                    to_remove_insns.add(next_l_ins_ind)
                    to_remove_insns.add(next_l_ins_ind+1)
                    to_remove_labels.add(sorted_handlers[i+1])
                    change_labels[sorted_handlers[i+1]] = sorted_handlers[i]
        if to_remove_labels:
            remove_labels(method, to_remove_labels)

        if to_remove_insns:
            remove_insns(method, to_remove_insns)
            recalculate_labels_by_array(method.labels, to_remove_insns)
            for ins in method.insns:
                if ins.buf.startswith(".catch"):
                    segs = ins.buf.split()
                    if segs[-1][1:] in change_labels:
                        line = ins.buf.replace(segs[-1][1:], change_labels[segs[-1][1:]])
                        method.insns[method.insns.index(ins)] = InsnNode(line)



def remove_not_referenced_label_calls(method, excluded_lbls):
    for insn in method.insns[:]:
        if insn.buf.startswith("if-"):
            # l_index = insn.buf.rfind(':') + 1
            # label = insn.buf[l_index:]
            label = insn.buf.split()[-1][1:]
            if label in excluded_lbls:
                ind = method.insns.index(insn)
                method.insns.remove(insn)
                recalculate_label_indexes(method.labels, ind, ind+1)

def align_tries2(method):
    ''' Puts try_start towards first executed instruction if the label appeared in
    not covered block, but try_end was executed'''
    lbls_candidates_to_rm = set()
    for tr in method.tries[:]:
        if tr.start.index == tr.end.index:
            lbls_candidates_to_rm.add(tr.start.name)
            lbls_candidates_to_rm.add(tr.end.name)
            ind = tr.end.index
            method.tries.remove(tr)
            method.insns.remove(method.insns[ind])
            recalculate_label_indexes(method.labels, ind, ind+1)
            continue
        if not tr.start.covered:
            i = tr.start.index
            while not method.insns[i].covered and i < tr.end.index:
                i += 1
            ind = method.tries.index(tr)
            newlbl_name = "old_try_{}".format(tr.start.index)
            method.labels[newlbl_name] = LabelNode(":"+newlbl_name, tr.start.index, tr.start.lid)
            method.tries[ind].start.index = i-1 if method.insns[i].opcode_name.startswith("move-res") else i
            if method.insns[i].covered or (i+1 < len(method.insns) and method.insns[i].buf.startswith("invoke") and method.insns[i+1].buf.startswith("move-r") and method.insns[i+1].covered):
                method.tries[ind].start.covered = True
            if tr.start.index == tr.end.index:
                lbls_candidates_to_rm.add(tr.start.name)
                lbls_candidates_to_rm.add(tr.end.name)
                ind = tr.end.index
                method.tries.remove(tr)
                method.insns.remove(method.insns[ind])
                recalculate_label_indexes(method.labels, ind, ind+1)
    if lbls_candidates_to_rm:
        all_try_lbls = set([tr.start.name for tr in method.tries])
        all_try_lbls |= set([tr.end.name for tr in method.tries])
        lbls = lbls_candidates_to_rm.difference(all_try_lbls)
        for l in lbls:
            method.labels.pop(l)
                # if i < tr.end.index:
                #   while i < tr.end.index:
                #       i += 1
                #   new_lbl_name = "del_"+tr.name 
                #   method.labels[new_lbl_name] = LabelNode(":"+new_lbl_name, i, i+100)

def align_tries(method):
    ''' Puts try_start towards first executed instruction if the label appeared in
    not covered block, but try_end was executed'''
    removed_try_starts = set()
    to_remove_ins_inds = []
    for tr in method.tries[:]:
        if tr in method.tries and tr.start.name in removed_try_starts:
            method.tries.remove(tr)
            continue
        if not tr.start.covered:
            if tr.start.name =="try_start_11":
                print("debug")
            i = tr.start.index
            while not method.insns[i].covered and i < tr.end.index:
                i += 1
            print("aligned: {}".format(method.name))
            if i == tr.end.index:
                removed_try_starts.add(tr.start.name)
                lbl = LabelNode(":del"+tr.end.name.split("_")[-1], tr.end.index, tr.end.lid)
                method.labels.pop(tr.start.name)
                method.labels.pop(tr.end.name)
                method.labels[lbl.name] = lbl
                method.tries.remove(tr)
            else:
                ind = method.tries.index(tr)
                method.tries[ind].start.index = i-1 if method.insns[i].opcode_name.startswith("move-r") else i
                if method.insns[i].covered:
                    method.tries[ind].start.covered = True


def remove_single_catch_ins(catch_line, label_index, label_name, insns, labels):
    '''Removes single catch instruction under try_end_n label.'''
    for c_ins in insns[label_index:label_index+len(labels[label_name].tries)]:
        if c_ins.buf == catch_line:
            insns.remove(c_ins)
            break

def remove_single_not_called_try(method): #this is only for sync method
    # remove the whole try if no catches executed. Otherwise leave as it is.
    for tr in method.tries[:]:
        if not tr.handler.covered and tr.end.name in method.labels:
            keep_tr = any([tr_.handler.covered for tr_ in method.labels[tr.end.name].tries])
            if not keep_tr:
                tr_index = tr.end.index
                remove_single_catch_ins(tr.buf, tr.end.index, tr.end.name, method.insns, method.labels)
                method.labels[tr.end.name].tries.remove(tr)
                if len(method.labels[tr.end.name].tries) == 0:
                    method.labels.pop(tr.end.name)
                    method.labels.pop(tr.start.name)
                method.tries.remove(tr)
                recalculate_label_indexes(method.labels, tr_index, tr_index+1)


def remove_not_called_tries(method):
    #if method.descriptor == "doInBackground()Ljava/lang/Void;":
    for tr in method.tries[:]:
        if not tr.handler.covered:
            tr_index = tr.end.index
            remove_single_catch_ins(tr.buf, tr.end.index, tr.end.name, method.insns, method.labels)
            method.labels[tr.end.name].tries.remove(tr)
            if len(method.labels[tr.end.name].tries) == 0:
                if tr.end.name in method.labels:
                    method.labels.pop(tr.end.name)
                if tr.start.name in method.labels:
                    method.labels.pop(tr.start.name)
            method.tries.remove(tr)
            recalculate_label_indexes(method.labels, tr_index, tr_index+1)
    

def remove_extra_tries(method):
    #if method.descriptor == "doInBackground()Ljava/lang/Void;":
    for tr in method.tries[:]:
        if tr.handler.name not in method.labels:
            tr_index = tr.end.index
            remove_single_catch_ins(tr.buf, tr.end.index, tr.end.name, method.insns, method.labels)
            method.labels[tr.end.name].tries.remove(tr)
            if len(method.labels[tr.end.name].tries) == 0:
                if tr.end.name in method.labels:
                    method.labels.pop(tr.end.name)
                if tr.start.name in method.labels:
                    method.labels.pop(tr.start.name)
            method.tries.remove(tr)
            recalculate_label_indexes(method.labels, tr_index, tr_index+1)
    

def update_tries(method):
    '''Synchronizing method tries with labels.tries.'''
    #if method.descriptor == "doInBackground()Ljava/lang/Void;":
    for tr in method.tries[:]:
        if tr.end.name not in method.labels:
            if tr.start.name in method.labels:
                method.labels.pop(tr.start.name)
            method.tries.remove(tr)
        elif tr.start.name not in method.labels:
            method.labels.pop(tr.end.name)
            method.tries.remove(tr)


def remove_empty_switch_data(method):
    if method.labels and any(l.switch for l in method.labels.values()):
        for k, lbl in method.labels.items():
            if lbl.switch and (not lbl.switch.packed_labels and not lbl.switch.sparse_dict or (lbl.switch.packed_labels and not any(lbl.switch.packed_labels))):
                method.labels.pop(k)
        for ins in method.insns[:]:
            if ins.opcode_name.startswith("packed-switch") or ins.opcode_name.startswith("sparse-switch"):
                lbl = ins.buf.split()[-1][1:]
                if lbl not in method.labels:
                    ind = method.insns.index(ins)
                    method.insns.remove(ins)
                    recalculate_label_indexes(method.labels, ind, ind+1)



def clean_switch(method):
    if is_switch_in(method):
        for i, ins in enumerate(method.insns[:]):
            if ins.opcode_name.startswith("packed-switch"):
                if ins not in method.insns:
                    continue
                j_start = method.insns.index(ins)+1
                if j_start < len(method.insns):
                    current = method.insns[j_start]
                    if has_label_by_index(method.labels, j_start):
                        continue
                    if current.covered:
                        continue
                    if current.cover_code > -1 and not current.covered:
                        if current.opcode_name.startswith("invoke") and method.insns[j_start+1].covered:
                            continue
                        j_end = j_start

                        while j_end < len(method.insns) and \
                            not has_label_by_index(method.labels, j_end):# and \
                            # not method.insns[j_end].opcode_name.startswith("goto") and \
                            # not method.insns[j_end].opcode_name.startswith("return"):
                                j_end += 1
                        del method.insns[j_start:j_end]
                        recalculate_label_indexes(method.labels, j_start, j_end)


def is_switch_in(method):
    for l in method.labels.values():
        if l.switch != None and l.switch.type_ == ".packed-switch":
            return True
    return False


class GotoLabel(object):
    def __init__(self, label):
        self.label = ""
        self.indexes = []


def scan_gotos(method):
    references = {}
    for i, insn in enumerate(method.insns):
        if insn.buf.startswith("goto") or insn.buf.startswith("if-"):
            l_index = insn.buf.rfind(':') + 1
            label = insn.buf[l_index:]
            #label = insn.buf.split()[1][1:]
            if label not in references:
                references[label] = []
            references[label].append(i)
    return references


def merge_goto(method):
    gotos = scan_gotos(method)
    rm_labels = []
    rm_insns = set()

    for lb, indexes in gotos.items():
        if lb not in method.labels:
            for ind in indexes:
                rm_insns.add(ind)
        if lb in method.labels and method.labels[lb].index-1 in indexes:
            rm_insns.add(method.labels[lb].index-1)
            if len(indexes) == 1:
                rm_labels.append(lb)
    remove_labels(method, rm_labels)
    remove_insns(method, rm_insns)
    recalculate_labels_by_array(method.labels, rm_insns)

def remove_insns(method, rm_insns):
    for i in sorted(list(rm_insns), reverse=True):
        del method.insns[i]

def remove_labels(method, rm_labels):
    for lb in rm_labels:
        del method.labels[lb]

def recalculate_labels_by_array(m_labels, rm_insns_set):
    labels = sorted(m_labels.values(), key=attrgetter('lid'))
    i = 0
    rm_insns = sorted(list(rm_insns_set))
    for l in labels:
        while i < len(rm_insns) and rm_insns[i] < l.index:
            i += 1
        m_labels[l.name].index -= i


def get_referenced_array_labels(method):
    labels = set()
    for ins in method.insns:
        if ins.opcode_name == "fill-array-data":
            index = ins.buf.rfind(':')
            label = ins.buf[index+1:]
            labels.add(label)
    return labels


def remove_array_data(method):
    referenced_array_labels = get_referenced_array_labels(method)
    array_labels = set([l.name for l in method.labels.values() if l.array_data])
    to_remove = array_labels - referenced_array_labels
    for l_name in to_remove:
        method.labels.pop(l_name)


def first_insn_is_covered(insns):
    if insns[0].covered:
        return True
    if insns[0].buf.startswith('invoke'):
        return insns[1].covered
    return False


def get_try_handlers(method):
    handlers = set()
    for t in method.tries:
        handlers.add(t.handler.name)
    return handlers


def get_label_blocks(method):
    #try_handlers = get_try_handlers(method)
    label_blocks = []
    # this function runs only on executed methods, first instruciton is always called
    block = LBlock(0, True, [])
    for label in sorted(method.labels.values(), key=attrgetter('lid')):
        if label.index != block.start_i:
            # this is the label for the next LBlock, so we finalize adding the previous one
            block.end_i = label.index 
            label_blocks.append(block)
            # the new Labeled Block starts here
            is_switch = label.switch != None
            is_array = label.array_data != None
            #is_try_handler = label.name in try_handlers
            block = LBlock(label.index, 
                label.covered,
                [label.name],
                is_switch=is_switch,
                is_array=is_array)
        else: # the new label belongs to the same LBlock
            block.labels.append(label.name)
        if label.name.startswith("try_start_"):
            handlers = get_handlers_by_try_end_label(method, method.labels[label.name.replace("start", "end")])
            if handlers and any(h in method.labels and method.labels[h].covered for h in handlers):
                block.is_try_start = True
        if label.name.startswith("try_end_"):
            handlers = get_handlers_by_try_end_label(method, label)
            if handlers and any(h in method.labels and method.labels[h].covered for h in handlers):
                block.is_try_end = True
        if label.name.startswith("catch") and label.covered:
            block.is_catch = True
        if not label.covered and label.name.startswith("catchall"):
            #if method.synchronized and label.index < len(method.insns) and method.insns[label.index].buf.startswith("monitor-ex"):
            block.is_catchall = True
            if method.synchronized \
                and method.insns[label.index].buf.startswith("move-exc"):
                block.is_move_exception = True
        if method.synchronized and label.name.startswith("goto") \
            and method.insns[label.index].buf.startswith("monitor-exit"):
            # case: move-exception, [goto], monitor-exit, return/throw
            block.is_goto_monitor_exit = True
    block.end_i = len(method.insns)
    label_blocks.append(block)
    return label_blocks

def get_handlers_by_try_end_label(method, label):
    i = label.index
    handlers = set()
    while  i < len(method.insns) and method.insns[i].buf.startswith(".catch"):
        handlers.add(method.insns[i].buf.split()[-1][1:])
        i+=1
    return handlers

def mark_synchronized_not_covered_lblocks(lblocks, method):
    throw_counter = 0
    for lb in lblocks:
        if not lb.covered and not lb.is_array and not lb.is_switch and lb.is_catchall:
            cur_ins = method.insns[lb.start_i]
            next_ins = method.insns[lb.start_i+1]
            if cur_ins.buf.startswith("move-exc"):
                if next_ins.buf.startswith("monitor-ex"):
                    lb.monitor_exit = True
                    if lb.start_i+3<len(method.insns) \
                        and method.insns[lb.start_i+2].buf.startswith(".catchall") \
                        and method.insns[lb.start_i+3].buf.startswith("throw") \
                        and not method.insns[lb.start_i+2].covered:
                            lb_index = lblocks.index(lb)
                            lbl_name = "throw{}".format(throw_counter)
                            throw_counter += 1
                            new_lblock = LBlock(lb.start_i+3, True, [lbl_name], lb.start_i+4)
                            throw_containing_lb = next(x for x in lblocks if lb.start_i+3 < x.end_i)
                            throw_containing_lb.end_i -= 1
                            throw_lb_ind = lblocks.index(throw_containing_lb)
                            lid = method.labels[lb.labels[0]].lid
                            method.labels[lbl_name] = LabelNode(":"+lbl_name, lb.start_i+3,lid+1)
                            method.labels[lbl_name].covered = True
                            if throw_lb_ind+1 < len(lblocks):
                                lblocks.insert(throw_lb_ind+1, new_lblock)
                            else:
                                lblocks.append(new_lblock)


def select_covered_l_blocks(method, lblocks):
    if method.synchronized:
        mark_synchronized_not_covered_lblocks(lblocks, method)
    insns = []
    labels = {}
    excluded_lbls = set()
    for lb in lblocks:
        if lb.covered or lb.is_switch \
            or lb.is_array or lb.is_try_start or lb.is_try_end \
            or lb.is_catch or lb.monitor_exit \
            or (lb.is_goto_monitor_exit and lb.is_catchall):
            for ln in lb.labels:
                method.labels[ln].index = len(insns)
                labels[ln] = method.labels[ln]
                if lb.is_switch:
                    adjust_switch(labels, ln)
            insns.extend(method.insns[lb.start_i:lb.end_i])
        else:
            if lb.labels:
                excluded_lbls.update(lb.labels)
    if len(insns) == 0 and len(method.insns) > 0:
        print(method)
        last_insn = method.insns[-1]
        if last_insn.buf.startswith("return"):
            insns.append(last_insn)
        else:
            for insn in reversed(method.insns):
                if insn.buf.startswith("return"):
                    insns.append(insn)
    method.insns = insns
    method.labels = labels
    return excluded_lbls


def adjust_switch(labels, ln):
    if not labels[ln].switch:
        return
    sw = labels[ln].switch
    if sw.type_ == ".packed-switch":
        packed_labels = []
        last_pl = ""
        for pl in sw.packed_labels:
            if pl[1:] in labels:
                packed_labels.append(pl)
                last_pl = pl
            else: #copy the last found labels instead of removing (impacts execution logic)
                packed_labels.append(last_pl)
        # if labels in the begining were removed, find the first existing and copy
        for i, pl in enumerate(packed_labels):
            if pl:
                break
        for j in range(0, i):
            packed_labels[j] = packed_labels[i]
        sw.packed_labels = packed_labels
        # if not any(sw.packed_labels):
        #     labels.pop(ln)
    else:
        sparse_dict = {}
        for k, v in sw.sparse_dict.items():
            if v in labels:
                sparse_dict[k] = v
        sw.sparse_dict = sparse_dict
    sw.reload()


def remove_ifs(method):
    lock = False
    start_ = 0
    end_ = 0
    i = 0
    while i < len(method.insns):
        insn = method.insns[i]
        if lock and has_label_by_index(method.labels, i):
            end_ = i
            del method.insns[start_+1:end_]
            recalculate_label_indexes(method.labels, start_+1, end_)
            i -= end_ - start_ + 1
            lock = False
            continue
        if not lock and insn.opcode_name.startswith('if-'):
            lbl_name = insn.buf[insn.buf.rfind(':')+1:]
            if insn.covered:
                if lbl_name not in method.labels:
                    del method.insns[i:i+1]
                    recalculate_label_indexes(method.labels, i, i+1)
                    continue
            else:
                method.insns[i] = InsnNode("goto/32 :{}".format(lbl_name))
                start_ = i
                lock = True
        i += 1


def get_tryend_labels(method):
    tryends = []
    i = 0
    tryend_lmd = lambda x: "try_end_{}".format(hex(i)[2:])
    tryend_name = tryend_lmd(i)
    while tryend_name in method.labels:
        tryends.append(tryend_name)
        i += 1
        tryend_name = tryend_lmd(i)
    return tryends


def get_sequential_catches(insns, i):
    catches_indexes = []
    while insns[i].buf.startswith(".catch"):
        catches_indexes.append(i)
        i += 1
    return catches_indexes

# def catchs_groupby_tryend(to_remove):
#     tryend_dict = {}
#     for tr in to_remove:
#         tryend_dict[tr.]


# #def sync

# def remove_catchs2(method):
#     sync_method_n_label_tries(method)
#     to_remove = []
#     for tr in method.tries:
#         if tr.handler.name not in method.labels:
#             to_remove.append(tr)
#     groupped = catchs_groupby_tryend(to_remove)


def remove_catchs(method):
    # when code in the method is executed without exceptions, then remove .catch
    # instruction together with :try_start_ and :try_end_ labels
    tryends = get_tryend_labels(method)
    for tr in tryends:
        try_lbl = method.labels[tr]
        if try_lbl.covered:
            catch_indexes = get_sequential_catches(method.insns, try_lbl.index)
            rm_indexes = []
            try_start = method.insns[catch_indexes[0]].buf.split()[-4][2:]
            for ci in catch_indexes:
                catch_str_index = method.insns[ci].buf.rfind(':')
                catch_name = method.insns[ci].buf[catch_str_index+1:]
                if catch_name not in method.labels:
                    rm_indexes.append(ci)
            if len(rm_indexes) == len(catch_indexes):
                del method.labels[try_start]
                del method.labels[tr]
            for i in reversed(rm_indexes):
                del method.insns[i]
            recalculate_label_indexes(method.labels, catch_indexes[0], catch_indexes[0]+len(rm_indexes))


def recalculate_label_indexes(labels, start_, end_):
    d = end_ - start_
    if d == 0:
        return
    for (k, v) in labels.items():
        if v.index >= end_:
            v.index -= d


def get_referenced_labels(method):
    labels = set()
    for i, ins in enumerate(method.insns):
        if (ins.buf.startswith("goto") or ins.buf.startswith("if")
                or ins.buf.startswith(".catch")) and branch_ins_executed(
                    method, i):
            lbl_match = re.match(labels_rx, ins.buf)
            if lbl_match:
                labels.add(lbl_match.group("label"))
                if lbl_match.group("trystart"):
                    labels.add(lbl_match.group("trystart"))
                    labels.add(lbl_match.group("tryend"))
    return labels


def branch_ins_executed(method, i):
    if i == 0 and method.covered:
        return True
    if method.insns[i].covered:
        return True
    lbls = get_labels_by_index(method.labels, i)
    if lbls and lbls[0].covered:  #both labels covered
        return True
    if not lbls and method.insns[i - 1].covered:
        return True
    return False


def has_covered_lbl(labels, index):
    for (k, v) in labels.items():
        if v.index == index:
            return v.covered
    return False


def has_label_by_index(labels, index):
    for (k, v) in labels.items():
        if v.index == index:
            return True
    return False


def get_labels_by_index(labels, index):
    found_labels = []
    for k, l in labels.items():
        if l.index == index:
            found_labels.append(l)
    return found_labels


def is_monitor_enter_covered(method):
    for ins in method.insns:
        if ins.opcode_name.startswith("monitor-enter") and ins.covered:
            return True
    return False


def index_to_label(method):
    labels_dict = {}
    for name, lbl in method.labels.items():
        if lbl.index in labels_dict:
            labels_dict[lbl.index].append(name)
        else:
            labels_dict[lbl.index] = [name]
    return labels_dict
 