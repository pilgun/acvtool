from granularity import Granularity

class CoverageData(object):
    ''' Coverage data for method, class, package or app. '''
    def __init__(self, lines=0, lines_missed=0, lines_covered=0,
        methods_covered=0, methods_missed=0, methods=0, classes=0, 
        classes_missed=0, classes_covered=0):
        self.lines = lines
        self.lines_missed = lines_missed
        self.lines_covered = lines_covered
        self.methods_covered = methods_covered
        self.methods_missed = methods_missed
        self.methods = methods
        self.classes = classes
        self.classes_missed = classes_missed
        self.classes_covered = classes_covered

    @staticmethod
    def coverage(covered, coverable):
        if coverable == 0:
            return None
        return float(covered) / coverable

    def get_class_coverage(self):
        return CoverageData.coverage(self.classes_covered, self.classes)
    
    def get_method_coverage(self):
        return CoverageData.coverage(self.methods_covered, self.methods)
    
    def get_line_coverage(self):
        return CoverageData.coverage(self.lines_covered, self.lines)

    def get_coverage(self, granularity):
        if Granularity.is_instruction(granularity):
            return self.get_line_coverage()
        if Granularity.is_method(granularity):
            return self.get_method_coverage()
        return self.get_class_coverage()
    
    def update_coverage_for_single_class_from_methods(self):
        if self.methods > 0:
            self.classes = 1
            self.classes_missed = 1 if self.methods_missed == self.methods else 0
            self.classes_covered = self.classes - self.classes_missed
        else:
            self.classes = 0
            self.classes_covered = 0
            self.classes_missed = 0

    @staticmethod
    def format_coverage(result):
        return ("{:.5f}%".format(100 * result)) if result is not None else "-"
    
    def get_formatted_coverage(self, granularity):
        coverage = self.get_coverage(granularity)
        return CoverageData.format_coverage(coverage)

    def covered(self, granularity):
        if Granularity.is_instruction(granularity):
            return self.lines_covered
        if Granularity.is_method(granularity):
            return self.methods_covered
        return self.classes_covered
    
    def missed(self, granularity):
        if Granularity.is_instruction(granularity):
            return self.lines_missed
        if Granularity.is_method(granularity):
            return self.methods_missed
        return self.classes_missed

    def coverable(self, granularity):
        if Granularity.is_instruction(granularity):
            return self.lines
        if Granularity.is_method(granularity):
            return self.methods
        return self.classes

    def add_data(self, coverage_data):
        self.lines += coverage_data.lines
        self.lines_missed += coverage_data.lines_missed
        self.lines_covered += coverage_data.lines_covered
        self.methods_covered += coverage_data.methods_covered
        self.methods_missed += coverage_data.methods_missed
        self.methods += coverage_data.methods
        self.classes += coverage_data.classes
        self.classes_missed += coverage_data.classes_missed
        self.classes_covered += coverage_data.classes_covered
