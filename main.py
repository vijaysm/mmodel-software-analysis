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
print tool

# For each of the tools, do the following actions

# 1) First let us clone the repository
cloneOpOut = tool.cloneRepo()

# 2) Find out the number of sources and types
sourceList = tool.getNSources()

# 3) Run Metrix++ for C/C++/Java and PyLint for Python
mmst.execCommandStreaming("scripts/get_metrixpp_logs " + tool.name + " " + mmst.sandbox_dir + "/" + tool.name)

# 4) Launch static analyzer depending on languages supported

# 4.a)       C/C++: cppcheck (cppcheck.sourceforge.net)
if mmst.cmd_exists("cppcheck") and sourceList['C'] + sourceList['C++'] > 0:
    mmst.execCommandStreaming("scripts/get_cppcheck_logs " + tool.Name + " " + mmst.sandbox_dir + "/" + tool.Name)

# 4.b)       Python: PyLint
if mmst.cmd_exists("pylint") and sourceList['Python'] > 0:
    mmst.execCommand("mkdir -p " + mmst.sandbox_dir + "/pylint")
    mmst.execCommandStreaming("find " + mmst.sandbox_dir + "/" + tool.name + "/ -name '*.py' | xargs pylint -E > " + mmst.sandbox_dir + "/pylint/" + tool.name + ".txt")

# 4.c)       Python: Radon
if mmst.cmd_exists("radon") and sourceList['Python'] > 0:
    mmst.execCommand("mkdir -p " + mmst.sandbox_dir + "/radon")
    mmst.execCommandStreaming("radon cc -a --total-average -s " + mmst.sandbox_dir + "/" + tool.name + " > " + mmst.sandbox_dir + "/radon/" + tool.name + ".txt")


# 5) Aggregate static analyzer results
#        a) For cppcheck, parse XML to find number of "errors"
#        b) For PyLint, parse output to find "errors"
