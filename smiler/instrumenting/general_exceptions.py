class MsgException(Exception):
    '''
    Generic exception with an optional string msg.
    '''
    def __init__(self, msg=""):
        self.msg = msg
    