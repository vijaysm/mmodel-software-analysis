import subprocess
import os

import utils.repository
import utils.commands
from utils import sandbox_dir

subprocess.call(["mkdir", "-p", sandbox_dir])


class MModelTool:
    def __init__(self, name, languages, vcs, repository, paths):
        self.name = name
        self.languages = languages
        self.vcs = vcs
        self.repository = repository
        self.paths = paths

        self.c = False
        self.python = False
        self.java = False
        self.fortran = False

    def __str__(self):
        return "[ " + self.name + " ] |VCS|: " + self.vcs + ", |Supported Languages|: " + self.languages + ", |Repository|: " + self.repository

    def cloneRepo(self):
        if not os.path.exists(sandbox_dir + "/" + self.name):
            if self.vcs == 'Git':
                if self.name == 'Cactus':
                    # special edge-case for cactus
                    return utils.repository.getCactusRepo(self.name, self.repository, self.paths)
                else:
                    return utils.repository.getGitRepo(self.name, self.repository)
            elif self.vcs == 'Mercurial':
                return utils.repository.getMercurialRepo(self.name, self.repository)
            elif self.vcs == 'Subversion':
                return utils.repository.getSVNRepo(self.name, self.repository)
            elif self.vcs == 'None':
                return utils.repository.getTarball(self.name, self.repository)
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
            sourceCount[key] = int(utils.commands.execCommand(command))

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

    def analyzeMetrixPP(self):
        # run metrix++ if source contains C/C++ or Java code
        if self.c is True or self.java is True:
            utils.commands.execCommandStreaming("./scripts/get_metrixpp_logs " + self.name + " " + sandbox_dir + "/" + self.name)

        # TODO: parse output and return stats

    def analyzeCPPcheck(self):
        # run cppcheck in installed and source contains C/C++ code
        if utils.commands.cmd_exists("cppcheck") and self.c is True:
            utils.commands.execCommandStreaming("scripts/get_cppcheck_logs " + self.name + " " + sandbox_dir + "/" + self.name)

        # TODO: parse output and return stats

    def analyzeRadon(self):
        # run radon if installed and source contains Python code
        if utils.commands.cmd_exists("radon") and self.python is True:
            # execCommand("mkdir -p " + sandbox_dir + "/radon")
            # execCommandStreaming("radon cc -a --total-average -s " + sandbox_dir + "/" + self.name + " > " + sandbox_dir + "/radon/" + self.name + ".txt")
            utils.commands.execCommand("mkdir -p " + sandbox_dir + "/radon")

            print '[', self.name, ']', 'Running Radon to find "Cyclomatic Complexity"'
            utils.commands.execCommand("radon cc -a --total-average -s " + sandbox_dir + "/" + self.name + " > " + sandbox_dir + "/radon/" + self.name + ".txt")
            utils.commands.execCommandStreaming("grep 'Average complexity' " + sandbox_dir + "/radon/" + self.name + ".txt")

            print '[', self.name, ']', 'Running Radon to find "Maintainability Index"'
            utils.commands.execCommand("radon mi -m -s " + sandbox_dir + "/" + self.name + " >> " + sandbox_dir + "/radon/" + self.name + ".txt")

            print '[', self.name, ']', 'Running Radon to find "Raw SLOC metrics"'
            utils.commands.execCommand("radon raw -s " + sandbox_dir + "/" + self.name + " >> " + sandbox_dir + "/radon/" + self.name + ".txt")
            utils.commands.execCommandStreaming("tail -n8 " + sandbox_dir + "/radon/" + self.name + ".txt")

        # TODO: parse output and return stats

    def analyzePyLint(self):
        # run pylint if installed and source contains Python code
        if utils.commands.cmd_exists("pylint") and self.python is True:

            utils.commands.execCommand("mkdir -p " + sandbox_dir + "/pylint")
            utils.commands.execCommand("mkdir -p " + sandbox_dir + "/pylint/" + self.name)

            print '[', self.name, ']', 'Performing static analysis on Python sources, with PyLint'
            if not self.paths:
                pysrc_dirs = sandbox_dir + "/" + self.name
            else:
                pysrc_dirs = " ".join([(sandbox_dir + "/" + self.name + "/" + s) for s in self.paths])
            print '[', self.name, ']', 'Python source directories =', pysrc_dirs

            files = []
            for dirpath, dirnames, filenames in os.walk(pysrc_dirs):
                for filename in [f for f in filenames if f.endswith(".py")]:
                    files.append(os.path.join(dirpath, filename))

            for f in files:
                utils.commands.execCommandStreaming('pylint -f parseable %s > %s/pylint/%s/%s.txt' % (f, sandbox_dir, self.name, os.path.basename(f)[:-3]))

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
        self.analyzeMetrixPP()
        self.analyzeCPPcheck()

        # 4) Run PyLint and Radon for Python
        self.analyzeRadon()
        self.analyzePyLint()

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
