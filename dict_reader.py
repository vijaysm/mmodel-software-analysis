import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from stacked_bar import *
from colour import *


# path to saved dictionary
fp = './mmodel_dictionary.npy'

# load the dictionary
d = np.load(fp).item()

final = {'tool': [], 'Code': [], 'Comments': [], 'Errors': [], 'Docstrings': [], 'Size': []}
for t in d.keys():
    comments = 0
    lines = 0
    size = 0
    errors = 0
    docs = 0
    for a in d[t]:
        if a == 'metrix' and bool(d[t][a]):

            comments += d[t][a]['std.code.lines:comments']['total']
            lines += d[t][a]['std.code.lines:code']['total']
            size += d[t][a]['std.general:size']['total']

        elif a == 'radon' and bool(d[t][a]):
            try:
                comments += d[t][a]['total']['comments']
                lines += d[t][a]['total']['loc']
            except:
                pass

        elif a == 'pylint' and bool(d[t][a]):
            llines = 0
            lcomments = 0
            lsize = 0
            ldocs = 0
            nerrors = 0
            for f in d[t][a].keys():
                try:
                    # print(d[t][a][f]['messages'].keys())
                    llines += d[t][a][f]['metrics']['code']['number']
                    lcomments += d[t][a][f]['metrics']['comment']['number']
                    ldocs += d[t][a][f]['metrics']['docstring']['number']
                    nerrors += len(d[t][a][f]['errors'])
                except:
                    pass

            comments += lcomments
            lines += llines
            errors += nerrors
            docs += ldocs

    final['tool'].append(t)
    final['Code'].append(lines)
    final['Comments'].append(comments)
    final['Errors'].append(errors)
    final['Docstrings'].append(docs)
    final['Size'].append(size)

final = pd.DataFrame(final)
final['cpl'] = final['Comments'] / final['Code']
final['epl'] = final['Errors'] / final['Code']
final['dpl'] = final['Docstrings'] / final['Code']

final.sort_values(by='tool', inplace=True)
final.index = final['tool']

# stacked_bar_chart(final, ['Code', 'Comments', 'Docstrings'], 'tool', 'Lines', 'stacked.png', Color('lightgray'), Color('gray'))

# ax = sns.barplot(x='tool', y='Code', data=final, color='gray')
# plt.xticks(rotation=90)
# ax.set_yscale("log")
# plt.ylabel('LOC')
# plt.show()

# ax = sns.barplot(x='tool', y='cpl', data=final, color='gray')
# plt.xticks(rotation=90)
# ax.set(xlabel='', ylabel='Comments per LOC')
# ax.tick_params(bottom='off')
# plt.tight_layout()
# plt.savefig('cploc.png')
# plt.close()

ax = sns.barplot(x='tool', y='epl', data=final, color='gray')
plt.xticks(rotation=90)
ax.set(xlabel='', ylabel='Errors per LOC')
ax.tick_params(bottom='off')
plt.tight_layout()
plt.savefig('eplc.png')
plt.close()

ax = sns.barplot(x='tool', y='dpl', data=final, color='gray')
plt.xticks(rotation=90)
ax.set(xlabel='', ylabel='Docstrings per LOC')
ax.tick_params(bottom='off')
plt.tight_layout()
plt.savefig('dplc.png')
plt.close()
