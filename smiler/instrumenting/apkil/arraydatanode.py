class ArrayDataNode(object):

    def __init__(self, lines, label):
        self.buf = [] 
        self.label = None

        self.__parse(lines, label)

    def __repr__(self):
        pass

    def __parse(self, lines, label):
        self.buf = lines
        self.label = label
        label.array_data = self 

    def reload(self):
        pass

