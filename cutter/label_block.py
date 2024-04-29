
class LBlock(object):

    def __init__(self, start_i, covered, labels, end_i=0, is_switch=False, is_array=False):
        self.start_i = start_i
        self.covered = covered
        self.labels = labels
        self.end_i = end_i
        self.is_switch = is_switch
        self.is_array = is_array
        #self.is_try_handler = is_try_handler
        self.monitor_exit = False
        self.is_try_start = False
        self.is_try_end = False
        self.is_catch = False
        self.is_catchall = False
        self.is_move_exception = False
        self.is_goto_monitor_exit = False
        #self.is_to_cut = False

    def __repr__(self):
        return "{}-{}: covered:{}, labels:{}, switch:{}, array:{}, monitor_exit:{}, try_start:{}, try_end:{}, catch:{}" \
        .format(self.start_i, self.end_i, self.covered, ",".join(self.labels),self.is_switch, self.is_array, self.monitor_exit, self.is_try_start, self.is_try_end, self.is_catch)