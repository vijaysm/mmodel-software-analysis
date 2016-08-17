import re


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
            lines = f.readlines()
            for l in lines:
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
    def __init__(self):
        pass

    def parse(self, fn):
        pass


class Radon():
    def __init__(self):
        pass

    def parse(self, fn):
        d = {}
        with open(fn, 'r') as f:
            lines = f.readlines()
            for l in lines:
                if ':' in l:
                    key, val = l.split(':')
                    key = key.strip().lower()
                    val = val.strip().lower()
                    try:
                        d[key] = int(val)
                    except:
                        pass
        return d


# test/debug
if __name__ == '__main__':
    # mpp = MetrixPP()
    # mpp.parse('./sandbox/metrixpp/mpp-DTK.txt')
    # print mpp.lines.comments.total

    r = Radon()
    print r.parse('../sandbox/radon/DTK.txt')
