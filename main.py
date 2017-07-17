import mmodel_software_analysis as mmsa
import csv
import numpy as np

surveyTools = []
with open('data/mmodel-survey-tools.csv', 'rb') as csvfile:
    rowreader = csv.DictReader(csvfile)
    for row in rowreader:
        # convert key values to lowercase to enable dictionary passing
        row = {k.lower(): v for k, v in row.items()}
        surveyTools.append(row)

d = {}
for toolInfo in surveyTools:
    tool = mmsa.MModelTool(**toolInfo)
    print tool.name

    result = tool.analyze()
    d[tool.name] = tool.parse()

np.save('mmodel_dictionary.npy', d)
