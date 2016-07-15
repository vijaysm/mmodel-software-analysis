import subprocess
import sys
import os

sandbox_dir = 'sandbox'
subprocess.call(["mkdir", "-p", sandbox_dir])


class MModelTool:
    def __init__(self, toolDict):
        self.name = toolDict['Name']
        self.languages = toolDict['Languages']
        self.vcs = toolDict['VCS']
        self.repository = toolDict['Repository']

    def __str__(self):
        return "[ " + self.name + " ] |VCS|: " + self.vcs + ", |Supported Languages|: " + self.languages + ", |Repository|: " + self.repository

    def cloneRepo(self):
        if not os.path.exists(sandbox_dir + "/" + self.name):
            if self.vcs == 'Git':
                return getGitRepo(self.name, self.repository)
            elif self.vcs == 'Mercurial':
                return getMercurialRepo(self.name, self.repository)
            elif self.vcs == 'Subversion':
                return getSVNRepo(self.name, self.repository)
            elif self.vcs == 'None':
                return getTarball(self.name, self.repository)
            else:
                raise ValueError('[' + self.name + ']' + 'Unhandled VCS type. Please check the key: ' + self.vcs + ' and URL:' + self.repository)

    def getNSources(self):
        print '[', self.name, ']', 'Computing source list (C, C++, Fortran, Python, Java)'
        command_base = "find " + sandbox_dir + "/" + self.name + " "
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
            source_count[key] = int(execCommand(command))
        print source_count
        return source_count


def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


def execCommand(shellCommand):
    p = subprocess.Popen(shellCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    # print "[CMD: ", shellCommand, "]:\n", output
    return output.rstrip('\n')


def execCommandStreaming(shellCommand):
    p = subprocess.Popen(shellCommand, shell=True, stderr=subprocess.PIPE)
    while True:
        out = p.stderr.read(64)
        if out == '' and p.poll() is not None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()


def getGitRepo(toolname, giturl):
    command = "git clone " + giturl + " " + sandbox_dir + "/" + toolname
    print '[', toolname, ']', 'Cloning Git repository from URL:', giturl
    return execCommand(command)


def getSVNRepo(toolname, svnurl):
    command = "svn checkout " + svnurl + " " + sandbox_dir + "/" + toolname
    print '[', toolname, ']', 'Cloning Subversion repository from URL:', svnurl
    return execCommand(command)


def getMercurialRepo(toolname, hgurl):
    command = "hg clone " + hgurl + " " + sandbox_dir + "/" + toolname
    print '[', toolname, ']', 'Cloning Mercurial repository from URL:', hgurl
    return execCommand(command)


def getTarball(toolname, url):
    filename = execCommand("basename " + url)
    print '[', toolname, ']', 'Downloading tarball from URL:', url
    wgetcommand = execCommand("wget -O " + sandbox_dir + "/" + filename + " " + url)
    execCommand("mkdir -p " + sandbox_dir + "/" + toolname)
    print '[', toolname, ']', 'Deflating the tarball into the directory:', sandbox_dir + "/" + toolname
    untarcommand = execCommand("tar -xf " + sandbox_dir + "/" + filename + " -C " + sandbox_dir + "/" + toolname + " --strip-components=1")
    return wgetcommand + "\n" + untarcommand
