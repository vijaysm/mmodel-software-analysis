import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from stacked_bar import *
from colour import *


tools = pd.read_csv('data/mmodel-survey-tools.csv')

# path to saved dictionary
fp = './mmodel_dictionary.npy'

# load the dictionary
data = np.load(fp).item()

pylint = []
metrix = []
radon = []
for t in data.keys():
    languages = [x.lower() for x in tools.loc[tools['Name'] == t]['Languages'].values[0].split('/')]

    for a in data[t]:
        if 'c' in languages or 'c++' in languages or 'java' in languages:
            if a == 'metrix' and bool(data[t][a]):
                d = {}
                d['Tool'] = t
                d['Comments'] = data[t][a]['std.code.lines:comments']['total']
                d['Code'] = data[t][a]['std.code.lines:code']['total']
                d['Complexity'] = data[t][a]['std.code.complexity:cyclomatic']['total']
                # d['Errors'] = data[t][a]['std.general.procerrors']   
                metrix.append(d)

        if 'python' in languages:
            if a == 'pylint' and bool(data[t][a]):
                d = {}
                lines = 0
                comments = 0
                docs = 0
                errors = 0
                for f in data[t][a].keys():
                    try:
                        # print(d[t][a][f]['messages'].keys())
                        lines += data[t][a][f]['metrics']['code']['number']
                        comments += data[t][a][f]['metrics']['comment']['number']
                        docs += data[t][a][f]['metrics']['docstring']['number']
                        errors += len(data[t][a][f]['errors'])
                    except:
                        pass

                d['Tool'] = t
                d['Code'] = lines
                d['Comments'] = comments
                d['Docstrings'] = docs
                d['Errors'] = errors
                pylint.append(d)
            elif a == 'radon' and bool(data[t][a]):
                d = {}
                d['Tool'] = t
                d['Complexity'] = data[t][a]['Complexity']
                radon.append(d)

# pylint prep
pylint = pd.DataFrame(pylint)
pylint.sort_values(by='Tool', inplace=True)
pylint.index = pylint['Tool']
pylint['cpl'] = (pylint['Comments'] + pylint['Docstrings']) / pylint['Code']
pylint['epl'] = pylint['Errors'] / pylint['Code']

# metrix prep
metrix = pd.DataFrame(metrix)
metrix.sort_values(by='Tool', inplace=True)
metrix.index = metrix['Tool']
metrix['cpl'] = metrix['Comments'] / metrix['Code']

# radon prep
radon = pd.DataFrame(radon)
radon.sort_values(by='Tool', inplace=True)
radon.index = radon['Tool']

# # stacked plots
stacked_bar_chart(pylint, ['Code', 'Comments', 'Docstrings'], 'Tool', 'Lines', 'figs/python_stacked.png', Color('lightgray'), Color('gray'))
stacked_bar_chart(metrix, ['Code', 'Comments'], 'Tool', 'Lines', 'figs/cpp_stacked.png', Color('lightgray'), Color('gray'))

# comments per line code
ax = sns.barplot(x='Tool', y='cpl', data=pylint, color='gray')
plt.xticks(rotation=90)
ax.set(xlabel='', ylabel='Comments per LOC')
ax.tick_params(bottom='off')
plt.tight_layout()
# plt.show()
plt.savefig('figs/python_cploc.png')
plt.close()

ax = sns.barplot(x='Tool', y='cpl', data=metrix, color='gray')
plt.xticks(rotation=90)
ax.set(xlabel='', ylabel='Comments per LOC')
ax.tick_params(bottom='off')
plt.tight_layout()
# plt.show()
plt.savefig('figs/cpp_cploc.png')
plt.close()

# errors per line code
ax = sns.barplot(x='Tool', y='epl', data=pylint, color='gray')
plt.xticks(rotation=90)
ax.set(xlabel='', ylabel='Errors per LOC')
ax.tick_params(bottom='off')
plt.tight_layout()
# plt.show()
plt.savefig('figs/python_eplc.png')
plt.close()

# cyclomatic complexity
ax = sns.barplot(x='Tool', y='Complexity', data=metrix, color='gray')
plt.xticks(rotation=90)
ax.set(xlabel='', ylabel='Cyclomatic Complexity')
ax.tick_params(bottom='off')
ax.set_yscale("log")
plt.tight_layout()
plt.savefig('figs/cpp_cc.png')
plt.close()

ax = sns.barplot(x='Tool', y='Complexity', data=radon, color='gray')
plt.xticks(rotation=90)
ax.set(xlabel='', ylabel='Cyclomatic Complexity')
ax.tick_params(bottom='off')
ax.set_yscale("log")
plt.tight_layout()
plt.savefig('figs/python_cc.png')
plt.close()