#!/usr/bin/python

import csv, subprocess

sandbox_dir = 'sandbox'
subprocess.call(["mkdir", "-p", sandbox_dir])

class MModelTool:
    def __init__(self,Tool,langs,vcs,url,paths):
        self.Name = Tool
        self.Languages = langs
        self.VCS = vcs
        self.Repository = url
        self.Paths = paths

    def __init__(self,ToolDict):
        self.Name = ToolDict['Name']
        self.Languages = ToolDict['Languages']
        self.VCS = ToolDict['VCS']
        self.Repository = ToolDict['Repository']
        self.Paths = ToolDict['Paths'].split('/')

    def __str__(self):
        return "[ " + self.Name + " ] |VCS|: " + self.VCS + ", |Supported Languages|: " + self.Languages + ", |Repository|: " + self.Repository

SurveyTools = []
with open('data/mmodel-survey-tools.csv', 'rb') as csvfile:
    rowreader = csv.DictReader(csvfile)
    for row in rowreader:
        SurveyTools.append(row)
    #print SurveyTools

# Replace with a recursive parse of the CSV file to get the tool list
# tool = MModelTool('DTK','C++','Git','https://github.com/ORNL-CEES/DataTransferKit.git',[])
#tool = MModelTool('MOAB','C++','None','ftp://ftp.mcs.anl.gov/pub/fathom/moab-nightly.tar.gz',[])
tool = MModelTool(SurveyTools[0])
print tool

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def ExecCommand(shellCommand):
    import sys, subprocess
    p = subprocess.Popen(shellCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    #print "[CMD: ", shellCommand, "]:\n", output
    return output.rstrip('\n')

def ExecCommandStreaming(shellCommand):
    import sys, subprocess
    p = subprocess.Popen(shellCommand, shell=True, stderr=subprocess.PIPE)
    while True:
        out = p.stderr.read(64)
        if out == '' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()

def GetGitRepo(toolname, giturl):
    command = "git clone " + giturl + " " + sandbox_dir + "/" + toolname
    print '[',toolname,']','Cloning Git repository from URL:', giturl
    return ExecCommand(command)

def GetSVNRepo(toolname, svnurl):
    command = "svn checkout " + svnurl + " " + sandbox_dir + "/" + toolname
    print '[',toolname,']','Cloning Subversion repository from URL:', svnurl
    return ExecCommand(command)

def GetMercurialRepo(toolname, hgurl):
    command = "hg clone " + hgurl + " " + sandbox_dir + "/" + toolname
    print '[',toolname,']','Cloning Mercurial repository from URL:', hgurl
    return ExecCommand(command)

def GetTarball(toolname, url):
    filename = ExecCommand("basename " + url)
    print '[',toolname,']','Downloading tarball from URL:', url
    wgetcommand = ExecCommand("wget -O " + sandbox_dir + "/" + filename + " " + url)
    ExecCommand("mkdir -p " + sandbox_dir + "/" + toolname)
    print '[',toolname,']','Deflating the tarball into the directory:', sandbox_dir + "/" + toolname
    untarcommand = ExecCommand("tar -xf " + sandbox_dir + "/" + filename + " -C " + sandbox_dir + "/" + toolname + " --strip-components=1")
    return wgetcommand + "\n" + untarcommand

def CloneRepo(toolname, vcs, url):
    import os
    if not os.path.exists(sandbox_dir+"/"+toolname):
        if vcs == 'Git':
            return GetGitRepo(toolname, url)
        elif vcs == 'Mercurial':
            return GetMercurialRepo(toolname, url)
        elif vcs == 'Subversion':
            return GetSVNRepo(toolname, url)
        elif vcs == 'None':
            return GetTarball(toolname, url)
        else:
            raise ValueError('[' + toolname + ']' + 'Unhandled VCS type. Please check the key: ' + vcs + ' and URL:' + url)

def GetNSources(toolname):
    import os
    print '[',toolname,']','Computing source list (C, C++, Fortran, Python, Java)'
    command_base = "find " + sandbox_dir + "/" + toolname + " "
    # count number of source files
    command_end  = "| wc -l" # Use xargs wc -l, to count total lines in the sources
    extension_dict = {}
    extension_dict['C'] = ['c', 'h']
    extension_dict['C++'] = ['cpp', 'hpp', 'hh', 'C', 'cc']
    extension_dict['Fortran'] = ['h90', 'f90', 'F90', 'f', 'F']
    extension_dict['Python'] = ['py']
    extension_dict['Java'] = ['java']
    cppfiles = "-name '*.cpp' -o -name '*.hpp' -o -name '*.hh' -o -name '*.C' -o -name '*.cc'"
    cfiles = "-name '*.c' -o -name '*.h'"
    fortfiles = "-name '*.h90' -o -name '*.f90' -o -name '*.F90' -o -name '*.f' -o -name '*.F'"
    pyfiles = "-name '*.py'"
    javafiles = "-name '*.java'"
    source_count = {}
    for key, value in extension_dict.iteritems():
        srcexts = value
        command = command_base
        index = 0
        for srcext in srcexts:
            if index:
                command = command + " -o "
            command = command + "-name '*." + srcext + "' "
            index = index + 1
        command = command + command_end
        source_count[key] = int(ExecCommand(command))
    return source_count

# Real program starts here #
# For each of the tools, do the following actions
enable_metrixpp = False
enable_cppcheck = False
enable_pylint = True
enable_radon = False

# 1) First let us clone the repository
CloneOpOut = CloneRepo(tool.Name, tool.VCS, tool.Repository)

# 2) Find out the number of sources and types
Sourcelist = GetNSources(tool.Name)
print '[',tool.Name,']','Source type count:', Sourcelist

# 3) Run Metrix++ for C/C++/Java and PyLint for Python
if enable_metrixpp:
    ExecCommandStreaming("scripts/get_metrixpp_logs " + tool.Name + " " + sandbox_dir + "/" + tool.Name)

# 4) Launch static analyzer depending on languages supported

# 4.a)       C/C++: cppcheck (cppcheck.sourceforge.net)
if cmd_exists("cppcheck") and Sourcelist['C']+Sourcelist['C++'] > 0 and enable_cppcheck:
    ExecCommandStreaming("scripts/get_cppcheck_logs " + tool.Name + " " + sandbox_dir + "/" + tool.Name)

# 4.b)       Python: PyLint
if cmd_exists("pylint") and Sourcelist['Python'] > 0 and enable_pylint:
    ExecCommand("mkdir -p " + sandbox_dir + "/pylint")
    print '[',tool.Name,']','Performing static analysis on Python sources, with PyLint'
    if not tool.Paths:
        pysrc_dirs = sandbox_dir + "/" + tool.Name
    else:
        pysrc_dirs = " ".join([(sandbox_dir + "/" + tool.Name + "/" + s) for s in tool.Paths])
    print '[',tool.Name,']','Python source directories =', pysrc_dirs
    ExecCommandStreaming("pylint -E " + pysrc_dirs + " > " + sandbox_dir + "/pylint/" + tool.Name + ".txt")
    pylint_errors = ExecCommand("grep '^E:' " + sandbox_dir + "/pylint/" + tool.Name + ".txt | wc -l")
    print '[',tool.Name,']','Number of errors detected by PyLint:', pylint_errors

# 4.c)       Python: Radon
if cmd_exists("radon") and Sourcelist['Python'] > 0 and enable_radon:
    ExecCommand("mkdir -p " + sandbox_dir + "/radon")
    print '[',tool.Name,']','Running Radon to find "Cyclomatic Complexity"'
    ExecCommand("radon cc -a --total-average -s " + sandbox_dir + "/" + tool.Name + " > " + sandbox_dir + "/radon/" + tool.Name + ".txt")
    ExecCommandStreaming("grep 'Average complexity' " + sandbox_dir + "/radon/" + tool.Name + ".txt")
    print '[',tool.Name,']','Running Radon to find "Maintainability Index"'
    ExecCommand("radon mi -m -s " + sandbox_dir + "/" + tool.Name + " >> " + sandbox_dir + "/radon/" + tool.Name + ".txt")
    print '[',tool.Name,']','Running Radon to find "Raw SLOC metrics"'
    ExecCommand("radon raw -s " + sandbox_dir + "/" + tool.Name + " >> " + sandbox_dir + "/radon/" + tool.Name + ".txt")
    ExecCommandStreaming("tail -n8 " + sandbox_dir + "/radon/" + tool.Name + ".txt")


# 5) Aggregate static analyzer results
#        a) For cppcheck, parse XML to find number of "errors"
#        b) For PyLint, parse output to find "errors"
