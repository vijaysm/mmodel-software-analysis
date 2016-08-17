import mmodel_software_analysis as mmsa
import csv

surveyTools = []
with open('data/mmodel-survey-tools.csv', 'rb') as csvfile:
    rowreader = csv.DictReader(csvfile)
    for row in rowreader:
        # convert key values to lowercase to enable dictionary passing
        row = {k.lower(): v for k, v in row.items()}
        surveyTools.append(row)

tool = mmsa.MModelTool(**surveyTools[3])

result = tool.analyze()