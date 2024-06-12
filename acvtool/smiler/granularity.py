
class Granularity(object):
    INSTRUCTION = 1
    METHOD = 2
    CLASS = 4
    GRANULARITIES = {
        "instruction": INSTRUCTION,
        "method": METHOD, 
        "class": CLASS
    }
    reverseGranularityDict = {v: k for k, v in GRANULARITIES.items()}

    default = "instruction"
    
    def __init__(self, granularity="instruction"):
        self.granularity = Granularity.GRANULARITIES[granularity]
        
    
    @staticmethod
    def granularities():
        return Granularity.GRANULARITIES.keys()

    @staticmethod
    def is_class(granularity):
        return granularity <= Granularity.CLASS

    @staticmethod
    def is_method(granularity):
        return granularity <= Granularity.METHOD
    
    @staticmethod
    def is_instruction(granularity):
        return granularity == Granularity.INSTRUCTION

    @staticmethod
    def get(granularity_key):
        return Granularity.reverseGranularityDict[granularity_key]
    
class WrongGranularityValueException(Exception):
    pass