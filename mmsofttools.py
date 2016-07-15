import subprocess
import sys
import os

sandbox_dir = './sandbox'
subprocess.call(["mkdir", "-p", sandbox_dir])


class MModelTool:
    def __init__(self, name, languages, vcs, repository):
        self.name = name
        self.languages = languages
        self.vcs = vcs
        self.repository = repository

        self.c = False
        self.python = False
        self.java = False

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

    def checkSource(self):
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

        # are the following lines needed?
        cppfiles = "-name '*.cpp' -o -name '*.hpp' -o -name '*.hh' -o -name '*.C' -o -name '*.cc'"
        cfiles = "-name '*.c' -o -name '*.h'"
        fortfiles = "-name '*.h90' -o -name '*.f90' -o -name '*.F90' -o -name '*.f' -o -name '*.F'"
        pyfiles = "-name '*.py'"
        javafiles = "-name '*.java'"
        #

        sourceCount = {}
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
            sourceCount[key] = int(execCommand(command))

        # store booleans for each code type if source files present
        if sourceCount['C'] + sourceCount['C++'] > 0:
            self.c = True
        if sourceCount['Python'] > 0:
            self.python = True
        if sourceCount['Java'] > 0:
            self.java = True
        if sourceCount['Fortran'] > 0:
            self.fortran = True

        print sourceCount
        return sourceCount

    def analyzeJavaC(self):
        # run metrix++
        # runs regardless of source contents right now.  do we want to check for Java/C/C++?
        execCommandStreaming("./scripts/get_metrixpp_logs " + self.name + " " + sandbox_dir + "/" + self.name)

        # run cppcheck in installed and source contains C/C++ code
        if cmd_exists("cppcheck") and self.c is True:
            execCommandStreaming("scripts/get_cppcheck_logs " + self.name + " " + sandbox_dir + "/" + self.name)

        # TODO: parse output and return stats

    def analyzePython(self):
        # run pylint if installed and source contains Python code
        if cmd_exists("pylint") and self.python is True:
            execCommand("mkdir -p " + sandbox_dir + "/pylint")
            execCommandStreaming("find " + sandbox_dir + "/" + self.name + "/ -name '*.py' | xargs pylint -E > " + sandbox_dir + "/pylint/" + self.name + ".txt")

        # run radon if installed and source contains Python code
        if cmd_exists("radon") and self.python is True:
            execCommand("mkdir -p " + sandbox_dir + "/radon")
            execCommandStreaming("radon cc -a --total-average -s " + sandbox_dir + "/" + self.name + " > " + sandbox_dir + "/radon/" + self.name + ".txt")

        # TODO: parse output and return stats

    def analyzeFortran(self):
        # TODO: add commands used for assessing Fortran source
        # TODO: parse output and return stats
        pass

    def analyze(self):
        result = Result()

        # 1) First let us clone the repository
        result.repoOutput = self.cloneRepo()  # what is this outputting? goes from getGitRepo() -> execCommand()

        # 2) Find out the number of sources and types
        result.sourceCounts = self.checkSource()

        # 3) Run Metrix++ for C/C++/Java and cppcheck for C/C++
        self.analyzeJavaC()

        # 4) Run PyLint and Radon for Python
        self.analyzePython()

        # TODO: 5) Run * for Fortran
        # self.analyzeFortran()

        # TODO: 5) Aggregate static analyzer results
        # TODO: a) For cppcheck, parse XML to find number of "errors"
        # TODO: b) For PyLint, parse output to find "errors"

        return result


class Result:
    '''A container object to store relevant results from the tool analysis
            Returns
            -------
            self.sourceCounts : ...
            self.repoOutput : ...
    '''

    def __init__(self):
        pass


def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


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
