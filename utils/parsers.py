import re
import os


class MetrixPP:
    def __init__(self):
        pass

    def parse(self, fn):
        d = {}
        with open(fn, 'r') as f:
            for l in f:
                if ':: ' and "'"in l:
                    param = l.split("'")[1]
                elif 'Average' in l:
                    avg = float(re.findall(r"[-+]?\d*\.\d+|\d+", l.split(':')[-1].strip())[0])
                elif 'Total' in l:
                    tot = float(re.findall(r"[-+]?\d*\.\d+|\d+", l.split(':')[-1].strip())[0])

                    if param == 'std.code.magic:numbers':
                        key = 'std.code.magic:numbers'
                    elif param == 'std.general:size':
                        key = 'std.general:size'
                    elif param == 'std.code.todo:comments':
                        key = 'std.code.todo:comments'
                    elif param == 'std.code.complexity:cyclomatic':
                        key = 'std.code.complexity:cyclomatic'
                    elif param == 'std.code.length:total':
                        key = 'std.code.length:total'
                    elif param == 'std.code.lines:total':
                        key = 'std.code.lines:total'
                    elif param == 'std.code.lines:code':
                        key = 'std.code.lines:code'
                    elif param == 'std.code.lines:comments':
                        key = 'std.code.lines:comments'

                    d[key] = {}
                    d[key]['average'] = avg
                    d[key]['total'] = tot
        return d


class CPPcheck():
    def __init__(self):
        pass

    def parse(self, fn):
        # CPP check outputs in HTML. What do we want out of CPP check?
        # Is there an option to output in something other than HTML?
        # Skipping this parser for now...
        pass


class PyLint():
    def __init__(self, srcDir):
        self.files = []
        for dirpath, dirnames, filenames in os.walk(srcDir):
            for filename in [f for f in filenames if f.endswith(".py")]:
                self.files.append(os.path.join(dirpath, filename))

    def parse(self):
        with open(fn, 'r') as f:
            for l in f:
                print l


class Radon():
    def __init__(self):
        pass

    def parse(self, fn):
        d_tmp = {}
        d = {}
        file_key = None
        with open(fn, 'r') as f:
            for l in f:
                if ':' in l:
                    key, val = l.split(':')
                    key = key.strip().lower()
                    val = val.strip().lower()

                    try:
                        d_tmp[key] = int(val)
                    except:
                        pass

                    if key == 'blank':
                        d[file_key] = d_tmp
                        d_tmp = {}

                elif '.py\n' in l:
                    file_key = l[:-1]

                elif '** Total **' in l:
                    file_key = 'total'

        return d


# test/debug
if __name__ == '__main__':
    pl = PyLint()
    pl.parse('/home/sean/Desktop/temp.txt')