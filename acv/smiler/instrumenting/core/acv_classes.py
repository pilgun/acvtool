import os
from ..config import SINT16_MAX


class AcvCalculator(object):
    
    @staticmethod
    def add_reporter_calls(tree_number, smali_dir, package):
        code = AcvCalculator.get_smali_addons(tree_number)
        AcvCalculator.save(code, smali_dir, package)
    
    @staticmethod
    def get_smali_addons(tree_number):
        codes = []
        for i in range(2, tree_number+1):
            codes.append(AcvCalculator.PRINTSUM_ADDON.format(i, i))
        codes.append(AcvCalculator.PRINTSUM_ENDING)
        return "\n".join(codes)
    
    @staticmethod
    def save(code, smali_dir, package):
        path = os.path.join(smali_dir, "tool", "acv", "AcvCalculator.smali")
        with open(path, 'a') as f:
            f.write(code)
    
    PRINTSUM_ADDON = r'''
    const-class v0, Ltool/acv/AcvReporter{};
    invoke-virtual {{v0}}, Ljava/lang/Class;->getFields()[Ljava/lang/reflect/Field;
    move-result-object v0
    const-string v1, "{}"
    invoke-static {{v0, v1}}, Ltool/acv/AcvCalculator;->printSum([Ljava/lang/reflect/Field;Ljava/lang/String;)V
    '''
    PRINTSUM_ENDING = r'''
# end of additional generation code
    return-void
.end method
    '''

class AcvStoring(object):

    @staticmethod
    def add_reporter_calls(tree_number, smali_dir, package):
        code = AcvStoring.get_onreceive_smali_addons(tree_number)
        AcvStoring.save(code, smali_dir, package)

    @staticmethod
    def get_onreceive_smali_addons(tree_number):
        codes = []
        for i in range(2, tree_number+1):
            codes.append(AcvStoring.ONRECEIVE_SMALI_ADDON.format(i))
        codes.append(AcvStoring.ONRECEIVE_METHOD_ENDING)
        return "\n".join(codes)

    @staticmethod
    def save(code, smali_dir, package):
        path = os.path.join(smali_dir, "tool", "acv", "AcvStoring.smali")
        content = ""
        with open(path, 'r') as f:
            content = f.read().replace("app.debloat.instrapp", package)
        with open(path, 'w') as f:
            f.write(content)
        with open(path, 'a') as f:
            f.write(code)

    ONRECEIVE_SMALI_ADDON = r'''
    const-class v0, Ltool/acv/AcvReporter{};
    invoke-virtual {{v0}}, Ljava/lang/Class;->getFields()[Ljava/lang/reflect/Field;
    move-result-object v0
    invoke-direct {{p0, v0}}, Ltool/acv/AcvStoring;->saveExternalPublicFile([Ljava/lang/reflect/Field;)V
    '''

    ONRECEIVE_METHOD_ENDING = r'''
# end of additional generation code
    return-void
.end method
    '''

class AcvFlushing(object):

    @staticmethod
    def add_reporter_calls(tree_number, smali_dir, package):
        code = AcvFlushing.get_flush_smali_addons(tree_number)
        AcvFlushing.save(code, smali_dir, package)

    @staticmethod
    def get_flush_smali_addons(tree_number):
        codes = []
        for i in range(2, tree_number+1):
            codes.append(AcvFlushing.FLUSH_SMALI_ADDON.format(i))
        codes.append(AcvFlushing.FLUSH_METHOD_ENDING)
        return "\n".join(codes)

    @staticmethod
    def save(code, smali_dir, package):
        path = os.path.join(smali_dir, "tool", "acv", "AcvFlushing.smali")
        with open(path, 'a') as f:
            f.write(code)

    FLUSH_SMALI_ADDON = r'''
    const-class v0, Ltool/acv/AcvReporter{};
    invoke-virtual {{v0}}, Ljava/lang/Class;->getFields()[Ljava/lang/reflect/Field;
    move-result-object v0
    invoke-static {{v0}}, Ltool/acv/AcvFlushing;->flushArrays([Ljava/lang/reflect/Field;)V
    '''
    FLUSH_METHOD_ENDING = r'''
# end of additional generation code
    return-void
.end method
    '''


class AcvInstrumentation(object):

    @staticmethod
    def change_package(package, smali_dir):
        path = os.path.join(smali_dir, "tool", "acv", "AcvInstrumentation.smali")
        content = ""
        with open(path, 'r') as f:
            content = f.read().replace("app.debloat.instr", package)
        with open(path, 'w') as f:
            f.write(content)


class AcvReporter(object):
    ''' Generates AcvReporter.smali classes.
    '''

    def __init__(self, treeId, classes_info):
        self.treeId = treeId
        self.classes_info = classes_info
        self.number_of_fields = len(self.classes_info)
        return
    
    @staticmethod
    def get_reporter_field(treeId, class_name, class_number):
        field_name = Smali.get_reporting_field_name(class_name, class_number)
        return "Ltool/acv/AcvReporter{};->{}".format(treeId, field_name)
    
    @staticmethod
    def get_reporting_class(classes_info, treeId):
        fields = []
        init_arrays = []
        for name, length, number in classes_info:
            field_name = Smali.get_reporting_field_name(name, number)
            fields.append(Smali.get_acv_static_field(name, number))
            init_block = Smali.get_clinit_array(length, treeId, field_name)
            init_arrays.append(init_block)
        reporter_fields = "\n".join(fields)
        init_arrays = "\n".join(init_arrays)
        reporter = Smali.get_reporter_smali(treeId, reporter_fields, init_arrays)
        # outdated getArray() (we use reflection now)
        # array_puts = AcvReporter.get_array_puts(classes_info)
        # reporter += Smali.get_array_method_smali(len(classes_info), array_puts)
        return reporter

    @staticmethod
    def get_array_puts(classes_info, treeId):
        arrays = []
        i = 0
        for name, length, number in classes_info:
            arrays.append(Smali.get_array_put_smali(treeId, i, name, number))
            i+=1
        all_arrays = "\n".join(arrays)
        return all_arrays
        
    @staticmethod
    def save_file(treeId, dir_path, reporter):
        reporter_dir = os.path.join(dir_path, 'tool', 'acv')
        reporter_path = os.path.join(reporter_dir, Smali.get_acvreporter_name(treeId))
        if not os.path.isdir(reporter_dir):
            os.makedirs(reporter_dir)
        with open(reporter_path, 'w') as f_writer:
            f_writer.write(reporter)

    # (acv_classes_dir, tree_id, classes_info)
    @staticmethod
    def save(dir_path, treeId, classes_info):
        acv_reporter_code = AcvReporter.get_reporting_class(classes_info, treeId)
        AcvReporter.save_file(treeId, dir_path, acv_reporter_code)


class Smali(object):
    ''' AcvReport specific smali manipulations.
    '''

    ACVREPORTER_FILENAME = "AcvReporter{}.smali"
    
    @staticmethod
    def get_acvreporter_name(treeId):
        return Smali.ACVREPORTER_FILENAME.format(treeId)

    @staticmethod
    def get_reporting_field_name(class_name, class_number):
        return "{}_{}".format(''.join(class_name[:-1].split('/')), class_number)

    @staticmethod
    def get_array_put_smali(treeId, ind, class_name, class_number):
        field = Smali.get_reporting_field_name(class_name, class_number)
        if ind < SINT16_MAX:
            return Smali.PUT16_ARRAY_SMALI.format(index=hex(ind), treeId=treeId, field=field)
        return Smali.PUT_ARRAY_SMALI.format(index=hex(ind), treeId=treeId, field=field)

    @staticmethod
    def get_acv_static_field(class_name, class_number):
        field_name = Smali.get_reporting_field_name(class_name, class_number)
        return ".field public static {}:[Z".format(field_name)

    @staticmethod
    def get_clinit_array(array_len, treeId, field_name):
        if array_len < SINT16_MAX:
            return Smali.CLINIT16_SMALI.format(hex(array_len), treeId, field_name)
        return Smali.CLINIT_SMALI.format(hex(array_len), treeId, field_name)

    @staticmethod
    def get_reporter_smali(treeId, fields, field_inits):
        return Smali.REPORTER_SMALI.format(treeId=treeId, fields=fields, field_inits=field_inits)

    @staticmethod
    def get_array_method_smali(number_of_fields, arrays):
        return Smali.GET_ARRAY_SMALI.format(number=hex(number_of_fields), arrays=arrays)


    #const/4 v2, 0x0
    PUT_ARRAY_SMALI = r'''
sget-object v1, Ltool/acv/AcvReporter{treeId};->{field}:[Z
const v2, {index}
aput-object v1, v0, v2
'''

    PUT16_ARRAY_SMALI = r'''
sget-object v1, Ltool/acv/AcvReporter{treeId};->{field}:[Z
const/16 v2, {index}
aput-object v1, v0, v2
'''

    CLINIT_SMALI = r'''
const v0, {}
new-array v0, v0, [Z
sput-object v0, Ltool/acv/AcvReporter{};->{}:[Z
'''
    CLINIT16_SMALI = r'''
const/16 v0, {}
new-array v0, v0, [Z
sput-object v0, Ltool/acv/AcvReporter{};->{}:[Z
'''

    REPORTER_SMALI = r'''.class public Ltool/acv/AcvReporter{treeId};
.super Ljava/lang/Object;
.source "AcvReporter{treeId}.java"
# static fields
{fields}

# direct methods
.method static constructor <clinit>()V
    .locals 1
    {field_inits}
    return-void
.end method

.method private constructor <init>()V
    .locals 1

    invoke-direct {{p0}}, Ljava/lang/Object;-><init>()V

    return-void
.end method

'''

    GET_ARRAY_SMALI = r'''

.method public static getArray()[[Z
    .locals 3

# array of arrays declaration
    const/16 v0, {number}

    new-array v0, v0, [[Z

# start of putting arrays into the total array
{arrays}
# end of putting arrays into the total array

    return-object v0
.end method

'''