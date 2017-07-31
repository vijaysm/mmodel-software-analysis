import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


# path to saved dictionary
fp = './mmodel_dictionary.npy'

# load the dictionary
d = np.load(fp).item()

final = {'tool': [], 'lines': [], 'comments': [], 'errors': [], 'docs': [], 'size': []}
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
    final['lines'].append(lines)
    final['comments'].append(comments)
    final['errors'].append(errors)
    final['docs'].append(docs)
    final['size'].append(size)

final = pd.DataFrame(final)
final['cpl'] = final['comments'] / final['lines']
final['epl'] = final['errors'] / final['lines']
final['dpl'] = final['docs'] / final['lines']

ax = sns.barplot(x='tool', y='lines', data=final)
plt.xticks(rotation=90)
plt.ylabel('LOC')
plt.show()

ax = sns.barplot(x='tool', y='cpl', data=final)
plt.xticks(rotation=90)
plt.ylabel('Comments per LOC')
plt.show()

ax = sns.barplot(x='tool', y='epl', data=final)
plt.xticks(rotation=90)
plt.ylabel('Errors per LOC')
plt.show()

ax = sns.barplot(x='tool', y='dpl', data=final)
plt.xticks(rotation=90)
plt.ylabel('Docstrings per LOC')
plt.show()
