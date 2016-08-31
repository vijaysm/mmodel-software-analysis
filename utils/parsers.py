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
    def __init__(self):
        pass

    def parse(self, logDir):
        d = {}
        self.files = []
        for dirpath, dirnames, filenames in os.walk(logDir):
            for filename in [f for f in filenames if f.endswith(".txt")]:
                self.files.append(os.path.join(dirpath, filename))

        for fn in self.files:
            key = os.path.basename(fn)
            d[key] = {}
            d[key]['errors'] = []
            d[key]['duplication'] = []
            d[key]['regions'] = []
            d[key]['messagesByCategory'] = []
            d[key]['messages'] = []
            d[key]['global'] = []
            d[key]['metrics'] = []
            tableKey = None
            print fn
            with open(fn, 'r') as f:
                for l in f:
                    if l is None or '':
                        pass
                    elif l.startswith(' ') or l.startswith('\n'):
                        pass
                    elif re.match(r"[A-Z]: ", l) is not None:
                        d[key]['errors'].append(l.strip())
                    elif 'Duplication' in l:
                        tableKey = 'duplication'
                    elif 'Statistics by type' in l:
                        tableKey = 'regions'
                    elif 'Messages by category' in l:
                        tableKey = 'messagesByCategory'
                    elif l.strip() == 'Messages':
                        tableKey = 'messages'
                    elif 'Global evaluation' in l:
                        tableKey = 'global'
                    elif 'Raw metrics' in l:
                        tableKey = 'metrics'
                    elif 'External dependencies' in l:
                        tableKey = 'dependencies'
                    elif tableKey is not None and re.search(r"[a-z]", l) is not None:
                        if tableKey is not 'errors' and tableKey is not 'global' and tableKey is not 'dependencies':
                            tmp = l.strip()
                            d[key][tableKey].append([s.strip() for s in tmp.split('|')][1:-1])
                        else:
                            d[key][tableKey].append(l.strip())

            for table in d[key].keys():
                if table is not 'errors' and table is not 'global' and table is not 'dependencies':
                    # colnames = d[key][table][0]
                    d_tmp = {}
                    for i in range(1, len(d[key][table])):
                        row = d[key][table][i]
                        name = row[0]
                        values = row[1:]

                        if table == 'messages':
                            d_tmp[name] = int(values[0])
                        elif table == 'regions':
                            d_tmp[name] = {}
                            d_tmp[name]['number'] = int(values[0])
                            d_tmp[name]['documented'] = float(values[3])
                        elif table == 'metrics':
                            d_tmp[name] = {}
                            d_tmp[name]['number'] = int(values[0])
                            d_tmp[name]['percent'] = float(values[1])
                        elif table == 'messagesByCategory':
                            d_tmp[name] = int(values[0])
                        elif table == 'duplication':
                            try:
                                d_tmp[name] = int(values[0])
                            except:
                                d_tmp[name] = float(values[0])

                    d[key][table] = d_tmp

    def parse_debug(self, fn):
        d = {}
        tableKey = None
        with open(fn, 'r') as f:
            key = os.path.basename(fn)
            d[key] = {}
            d[key]['errors'] = []
            d[key]['duplication'] = []
            d[key]['regions'] = []
            d[key]['messagesByCategory'] = []
            d[key]['messages'] = []
            d[key]['global'] = []
            d[key]['metrics'] = []
            for l in f:
                if l is None or '':
                    pass
                elif l.startswith(' ') or l.startswith('\n'):
                    pass
                elif re.match(r"[A-Z]: ", l) is not None:
                    d[key]['errors'].append(l.strip())
                elif 'Duplication' in l:
                    tableKey = 'duplication'
                elif 'Statistics by type' in l:
                    tableKey = 'regions'
                elif 'Messages by category' in l:
                    tableKey = 'messagesByCategory'
                elif l.strip() == 'Messages':
                    tableKey = 'messages'
                elif 'Global evaluation' in l:
                    tableKey = 'global'
                elif 'Raw metrics' in l:
                    tableKey = 'metrics'
                elif 'External dependencies' in l:
                    tableKey = 'dependencies'
                elif tableKey is not None and re.search(r"[a-z]", l) is not None:
                    if tableKey is not 'errors' and tableKey is not 'global' and tableKey is not 'dependencies':
                        tmp = l.strip()
                        d[key][tableKey].append([s.strip() for s in tmp.split('|')][1:-1])
                    else:
                        d[key][tableKey].append(l.strip())

        for table in d[key].keys():
            if table is not 'errors' and table is not 'global' and table is not 'dependencies':
                # colnames = d[key][table][0]
                d_tmp = {}
                for i in range(1, len(d[key][table])):
                    row = d[key][table][i]
                    name = row[0]
                    values = row[1:]

                    if table == 'messages':
                        d_tmp[name] = int(values[0])
                    elif table == 'regions':
                        d_tmp[name] = {}
                        d_tmp[name]['number'] = int(values[0])
                        d_tmp[name]['documented'] = float(values[3])
                    elif table == 'metrics':
                        d_tmp[name] = {}
                        d_tmp[name]['number'] = int(values[0])
                        d_tmp[name]['percent'] = float(values[1])
                    elif table == 'messagesByCategory':
                        d_tmp[name] = int(values[0])
                    elif table == 'duplication':
                        try:
                            d_tmp[name] = int(values[0])
                        except:
                            d_tmp[name] = float(values[0])

                d[key][table] = d_tmp
                print d_tmp


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
    pl.parse_debug('../sandbox/pylint/Amuse/ez_setup.txt')