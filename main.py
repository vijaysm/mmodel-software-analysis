from mmsofttools import *

quit()
SurveyTools = []
with open('data/mmodel-survey-tools.csv', 'rb') as csvfile:
    rowreader = csv.DictReader(csvfile)
    for row in rowreader:
        SurveyTools.append(row)
    # print SurveyTools

# Replace with a recursive parse of the CSV file to get the tool list
# tool = MModelTool('DTK','C++','Git','https://github.com/ORNL-CEES/DataTransferKit.git')
# tool = MModelTool('DTK','C++','None','ftp://ftp.mcs.anl.gov/pub/fathom/moab-nightly.tar.gz')
tool = MModelTool(SurveyTools[3])
print tool

# For each of the tools, do the following actions

# 1) First let us clone the repository
CloneOpOut = CloneRepo(tool.Name, tool.VCS, tool.Repository)

# 2) Find out the number of sources and types
Sourcelist = GetNSources(tool.Name)

# 3) Run Metrix++ for C/C++/Java and PyLint for Python
ExecCommandStreaming("scripts/get_metrixpp_logs " + tool.Name + " " + sandbox_dir + "/" + tool.Name)

# 4) Launch static analyzer depending on languages supported

# 4.a)       C/C++: cppcheck (cppcheck.sourceforge.net)
if cmd_exists("cppcheck") and Sourcelist['C'] + Sourcelist['C++'] > 0:
    ExecCommandStreaming("scripts/get_cppcheck_logs " + tool.Name + " " + sandbox_dir + "/" + tool.Name)

# 4.b)       Python: PyLint
if cmd_exists("pylint") and Sourcelist['Python'] > 0:
    ExecCommand("mkdir -p " + sandbox_dir + "/pylint")
    ExecCommandStreaming("find " + sandbox_dir + "/" + tool.Name + "/ -name '*.py' | xargs pylint -E > " + sandbox_dir + "/pylint/" + tool.Name + ".txt")

# 4.c)       Python: Radon
if cmd_exists("radon") and Sourcelist['Python'] > 0:
    ExecCommand("mkdir -p " + sandbox_dir + "/radon")
    ExecCommandStreaming("radon cc -a --total-average -s " + sandbox_dir + "/" + tool.Name + " > " + sandbox_dir + "/radon/" + tool.Name + ".txt")


# 5) Aggregate static analyzer results
#        a) For cppcheck, parse XML to find number of "errors"
#        b) For PyLint, parse output to find "errors"