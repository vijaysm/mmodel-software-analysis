import os

from utils import commands
from utils import sandbox_dir


def getGitRepo(toolname, giturl):
    command = "git clone " + giturl + " " + sandbox_dir + "/" + toolname
    print '[', toolname, ']', 'Cloning Git repository from URL:', giturl
    return commands.execCommand(command)


def getSVNRepo(toolname, svnurl):
    command = "svn checkout " + svnurl + " " + sandbox_dir + "/" + toolname
    print '[', toolname, ']', 'Cloning Subversion repository from URL:', svnurl
    return commands.execCommand(command)


def getMercurialRepo(toolname, hgurl):
    command = "hg clone " + hgurl + " " + sandbox_dir + "/" + toolname
    print '[', toolname, ']', 'Cloning Mercurial repository from URL:', hgurl
    return commands.execCommand(command)


def getTarball(toolname, url):
    filename = commands.execCommand("basename " + url)
    print '[', toolname, ']', 'Downloading tarball from URL:', url
    wgetcommand = commands.execCommand("wget -O " + sandbox_dir + "/" + filename + " " + url)
    commands.execCommand("mkdir -p " + sandbox_dir + "/" + toolname)
    print '[', toolname, ']', 'Deflating the tarball into the directory:', sandbox_dir + "/" + toolname
    untarcommand = commands.execCommand("tar -xf " + sandbox_dir + "/" + filename + " -C " + sandbox_dir + "/" + toolname + " --strip-components=1")
    return wgetcommand + "\n" + untarcommand


def getZip(toolname, url):
    filename = commands.execCommand("basename " + url)
    print '[', toolname, ']', 'Downloading tarball from URL:', url
    wgetcommand = commands.execCommand("wget -O " + sandbox_dir + "/" + filename + " " + url)
    commands.execCommand("mkdir -p " + sandbox_dir + "/" + toolname)
    print '[', toolname, ']', 'Deflating the zip into the directory:', sandbox_dir + "/" + toolname
    unzipcommand = commands.execCommand("unzip " + sandbox_dir + "/" + filename + " -d " + sandbox_dir + "/" + toolname)
    return wgetcommand + "\n" + unzipcommand


def getCactusRepo(toolname, thornListURL, getComponentsURL):
    currentPath = os.getcwd()
    os.chdir(sandbox_dir)

    getComponentsName = commands.execCommand("basename " + getComponentsURL)
    print '[%s] Downloading %s script from URL: %s' % (toolname, getComponentsName, getComponentsURL)
    wgetComponentsCommand = commands.execCommand('wget --no-check-certificate %s' % getComponentsURL)

    print '[%s] Making GetComponents executable.' % toolname
    chmodcommand = commands.execCommand('chmod a+x %s' % getComponentsName)

    thornListName = commands.execCommand("basename " + thornListURL)
    print '[%s] Downloading thorn list from URL: %s' % (toolname, thornListURL)
    wgetThornsListCommand = commands.execCommand('wget --no-check-certificate %s' % thornListURL)

    print '[%s] Downloading source files...' % toolname
    getThornsCommand = commands.execCommand('./%s %s' % (getComponentsName, thornListName))

    print '[%s] Cleaning up directory...' % toolname
    if os.path.isfile(getComponentsName):
        os.remove(getComponentsName)
    if os.path.isfile(thornListName):
        os.remove(thornListName)

    os.chdir(currentPath)

    return '\n'.join([wgetComponentsCommand, chmodcommand, wgetThornsListCommand, getThornsCommand])
