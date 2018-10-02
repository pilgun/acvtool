class TryNode(object):

    def __init__(self, line, start, end, handler):
        self.buf = "" 
        self.exception = ""
        self.start = None
        self.end = None
        self.handler = None

        self.__parse(line, start, end, handler)

    def __repr__(self):
        return "Try: %s {%s .. %s} %s" % \
                (self.exception, start.index, end.index, handler.index)

    def __parse(self, line, start, end, handler):
        self.buf = line
        self.start = start
        self.end = end
        end.tries.append(self)
        self.handler = handler
        segs = self.buf.split()
        self.exception = segs[1]

    def reload(self):
        pass