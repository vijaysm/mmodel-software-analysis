import numpy as np
import json


# path to saved dictionary
fp = './mmodel_dictionary.npy'

# load the dictionary
d = np.load(fp).item()

d_amuse = d['Amuse']
j = json.dumps(d_amuse)

with open('data.txt', 'w') as outfile:
    json.dump(d_amuse, outfile)