import re
import os


class Attribute:
    def __init__(self):
        pass


class MetrixPP:
    def __init__(self):
        self.magic = Attribute()
        self.size = Attribute()
        self.todo = Attribute()
        self.complexity = Attribute()
        self.lines = Attribute()

        self.lines.total = Attribute()
        self.lines.code = Attribute()
        self.lines.comments = Attribute()

    def parse(self, fn):
        with open(fn, 'r') as f:
            for l in f:
                if ':: ' and "'"in l:
                    param = l.split("'")[1]
                elif 'Average' in l:
                    avg = float(re.findall(r"[-+]?\d*\.\d+|\d+", l.split(':')[-1].strip())[0])
                elif 'Total' in l:
                    tot = float(re.findall(r"[-+]?\d*\.\d+|\d+", l.split(':')[-1].strip())[0])

                    if param == 'std.code.magic:numbers':
                        self.magic.average = avg
                        self.magic.total = tot
                    elif param == 'std.general:size':
                        self.size.average = avg
                        self.size.total = tot
                    elif param == 'std.code.todo:comments':
                        self.todo.average = avg
                        self.todo.total = tot
                    elif param == 'std.code.complexity:cyclomatic':
                        self.complexity.average = avg
                        self.complexity.total = tot
                    elif param == 'std.code.length:total':
                        self.lines.total.average = avg
                        self.lines.total.total = tot
                    elif param == 'std.code.lines:total':
                        self.lines.total.total = avg
                        self.lines.total.average = tot
                    elif param == 'std.code.lines:code':
                        self.lines.code.average = avg
                        self.lines.code.total = tot
                    elif param == 'std.code.lines:comments':
                        self.lines.comments.average = avg
                        self.lines.comments.total = tot


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