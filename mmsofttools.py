#!/usr/bin/python

import csv
import subprocess
import sys
import os

sandbox_dir = 'sandbox'
subprocess.call(["mkdir", "-p", sandbox_dir])


class MModelTool:
    def __init__(self, Tool, langs, vcs, url):
        self.Name = Tool
        self.Languages = langs
        self.VCS = vcs
        self.Repository = url

    def __init__(self, ToolDict):
        self.Name = ToolDict['Name']
        self.Languages = ToolDict['Languages']
        self.VCS = ToolDict['VCS']
        self.Repository = ToolDict['Repository']

    def __str__(self):
        return "[ " + self.Name + " ] |VCS|: " + self.VCS + ", |Supported Languages|: " + self.Languages + ", |Repository|: " + self.Repository


def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


def ExecCommand(shellCommand):
    p = subprocess.Popen(shellCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    # print "[CMD: ", shellCommand, "]:\n", output
    return output.rstrip('\n')


def ExecCommandStreaming(shellCommand):
    p = subprocess.Popen(shellCommand, shell=True, stderr=subprocess.PIPE)
    while True:
        out = p.stderr.read(64)
        if out == '' and p.poll() is not None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()


def GetGitRepo(toolname, giturl):
    command = "git clone " + giturl + " " + sandbox_dir + "/" + toolname
    print '[', toolname, ']', 'Cloning Git repository from URL:', giturl
    return ExecCommand(command)


def GetSVNRepo(toolname, svnurl):
    command = "svn checkout " + svnurl + " " + sandbox_dir + "/" + toolname
    print '[', toolname, ']', 'Cloning Subversion repository from URL:', svnurl
    return ExecCommand(command)


def GetMercurialRepo(toolname, hgurl):
    command = "hg clone " + hgurl + " " + sandbox_dir + "/" + toolname
    print '[', toolname, ']', 'Cloning Mercurial repository from URL:', hgurl
    return ExecCommand(command)


def GetTarball(toolname, url):
    filename = ExecCommand("basename " + url)
    print '[', toolname, ']', 'Downloading tarball from URL:', url
    wgetcommand = ExecCommand("wget -O " + sandbox_dir + "/" + filename + " " + url)
    ExecCommand("mkdir -p " + sandbox_dir + "/" + toolname)
    print '[', toolname, ']', 'Deflating the tarball into the directory:', sandbox_dir + "/" + toolname
    untarcommand = ExecCommand("tar -xf " + sandbox_dir + "/" + filename + " -C " + sandbox_dir + "/" + toolname + " --strip-components=1")
    return wgetcommand + "\n" + untarcommand


def CloneRepo(toolname, vcs, url):
    if not os.path.exists(sandbox_dir + "/" + toolname):
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
    print '[', toolname, ']', 'Computing source list (C, C++, Fortran, Python, Java)'
    command_base = "find " + sandbox_dir + "/" + toolname + " "
    # count number of source files
    command_end = "| wc -l"  # Use xargs wc -l, to count total lines in the sources
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
    print source_count
    return source_count
