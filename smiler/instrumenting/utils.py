import os
import shutil
from time import time
from datetime import datetime

class Utils(object):
    ''' Static Helpers.'''

    @staticmethod
    def rm_tree(path):
        '''Removes all the files.'''
        if os.path.isdir(path):
            if os.name == 'nt':
                #Hack for Windows. Shutil can't remove files with a path longer than 260.
                cmd = "rd {0} /s /q".format(path)
                os.system(cmd)
            else:
                shutil.rmtree(path) 

    @staticmethod
    def get_groupped_classes(tree):
        # Group classes by relative path to generate index.html.
        groups = []
        classes = []
        key = tree.classes[0].folder
        classes.append(tree.classes[0])
        for i in range(1, len(tree.classes)):
            if tree.classes[i].folder == key:
                classes.append(tree.classes[i])
            else:
                groups.append(classes)
                key = tree.classes[i].folder
                classes = [tree.classes[i]]
        groups.append(classes)

        return groups

    @staticmethod
    def get_package_name(smali_class_name):
        '''Returns the package name by given smali class name.
        Format: org/android/rock.'''
        package_name, f = os.path.split(smali_class_name)
        return package_name[1:]

    @staticmethod
    def get_standart_package_name(smali_class_name):
        '''Returns the package name by given smali class name.
        Format: org.android.rock.'''
        return Utils.get_package_name(smali_class_name).replace('/', '.')
    
    @staticmethod
    def is_in_ranges(i, ranges):
        '''Returns if i is in the intervals ranges.
        Ranges variable contains list of indexes intervals.'''
        for r in ranges:
            if i >= r[0]:
                if i < r[1]:
                    return True
            return False
        return False

    @staticmethod
    def scan_synchronized_tries(method):
        '''Returns list of intervals of indexes where the insnsmust be throw safe.
        Otherwise, VerifyChecker recognizes the code as invalid.'''
        ranges = []
        for tr in method.tries:
            if tr.handler.name.startswith("catchall"):
                start = tr.start.index
                end = tr.end.index
                if tr.handler.index < tr.end.index and tr.handler.index >= tr.start.index:
                    end = tr.handler.index
                for i in range(start, end):
                    if method.insns[i].opcode_name.startswith("monitor-exit"):
                        ranges.append([i, end])
                        break
        return ranges

    @staticmethod
    def copytree(src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                Utils.copytree(s, d, symlinks, ignore)
            else:
                if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                    shutil.copy2(s, d)

    @staticmethod
    def log_entry(log_path, entry, sep=','):
        if not os.path.exists(log_path):
            with open(log_path, 'w') as log_file:
                log_file.write("sep={}\n".format(sep))
                log_file.flush()
        with open(log_path, 'a+') as log_file:
            log_file.write(entry)
            log_file.flush()


def timeit(method):
    '''Measures the working time of the method.'''
    def wrapper(*args, **kwargs):
        start = time()
        result = method(*args, **kwargs)
        end = time()
        time_log_path = os.path.join("times_log.csv")
        args_str = ";".join(map(str,args))
        entry = "{0};{1};{2};{3}\n".format(datetime.now(), end - start, method.__name__.lower(), args_str)
        Utils.log_entry(time_log_path, entry, sep=";")
        return result
    return wrapper
