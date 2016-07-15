import mmsofttools as mmst
import csv

surveyTools = []
with open('data/mmodel-survey-tools.csv', 'rb') as csvfile:
    rowreader = csv.DictReader(csvfile)
    for row in rowreader:
        surveyTools.append(row)

# Replace with a recursive parse of the CSV file to get the tool list
# tool = MModelTool('DTK','C++','Git','https://github.com/ORNL-CEES/DataTransferKit.git')
# tool = MModelTool('DTK','C++','None','ftp://ftp.mcs.anl.gov/pub/fathom/moab-nightly.tar.gz')
tool = mmst.MModelTool(surveyTools[3])

result = tool.analyze()