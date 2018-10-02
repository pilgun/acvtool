class CodeBlockNode(object):

    def __init__(self, lines):
        self.buf = []

        self.__parse(lines)

    def __repr__(self):
        pass

    def __parse(self, lines):
        self.buf = lines

    def reload(self):
        pass

    def get_lines(self):
        return self.buf