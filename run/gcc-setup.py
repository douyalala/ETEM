import os
from configparser import ConfigParser

# --------------modify maindir--------------

cfg = ConfigParser()
cfg.read('config/config.ini')

path = os.getcwd()
cfg.set('llvm-locations', 'maindir', path)
f = open('config/config.ini', 'w')
cfg.write(f)
f.close()

cfg.set('gcc-locations', 'maindir', path)
f = open('config/config.ini', 'w')
cfg.write(f)
f.close()

# --------------build gcc directory--------------

compilersdir = cfg.get('gcc-locations', 'compilersdir')
if not os.path.exists(compilersdir):
    print('\033[1;35m Now build directory: ', compilersdir,'\033[0m')
    os.system('mkdir -p ' + compilersdir)
else: print('\033[1;35m Already has directory: ', compilersdir,'\033[0m')

infodir = cfg.get('gcc-locations', 'infodir')
if not os.path.exists(infodir):
    print('\033[1;35m Now build directory: ', infodir, '\033[0m')
    os.system('mkdir -p ' + infodir)
else: print('\033[1;35m Already has directory: ', infodir,'\033[0m')

logdir = cfg.get('gcc-locations', 'logdir')
if not os.path.exists(logdir):
    print('\033[1;35m Now build directory: ', logdir, '\033[0m')
    os.system('mkdir -p ' + logdir)
else: print('\033[1;35m Already has directory: ', logdir,'\033[0m')

passdir = cfg.get('gcc-locations', 'passdir')
if not os.path.exists(passdir):
    print('\033[1;35m Now build directory: ', passdir, '\033[0m')
    os.system('mkdir -p ' + passdir)
else: print('\033[1;35m Already has directory: ', passdir,'\033[0m')

# --------------check gcc bug config in benchmark repository--------------

gccRepo = cfg.get('gcc-locations', 'benchmark')
gccbugsname = os.listdir(gccRepo)

bugList = cfg.get('gcc-locations', 'bugList')
revfile = open(bugList)
revlines = revfile.readlines()
revfile.close()

for i in range(len(revlines)):
    bugId = revlines[i].strip().split(',')[0]
    if bugId not in gccbugsname:
        print('\033[1;35m GCC bug ', bugId,' does not exist in existing repository.\033[0m')
        print('\033[1;35m Please configure it by yourself\033[0m')
    else:
        os.system('cp -r ' + gccRepo + bugId + ' ' + infodir)

# --------------install gcc compilers and collect info--------------
configFile = cfg.get('gcc-locations', 'configFile')
bugList = cfg.get('gcc-locations', 'bugList')
compilersdir = cfg.get('gcc-locations', 'compilersdir')
infodir = cfg.get('gcc-locations', 'infodir')

revisions = []
bugIds = []
whether_installs = []
wrongs = []

revfile = open(bugList)
revlines = revfile.readlines()
revfile.close()

for i in range(len(revlines)):
    bugIds.append(revlines[i].strip().split(',')[0])
    revisions.append(revlines[i].strip().split(',')[1])
    whether_installs.append(revlines[i].strip().split(',')[5])
    wrongs.append(revlines[i].strip().split(',')[3])
    
print('\033[1;35m Begin gcc - install\033[0m')
from src.gcc import install
install(revisions, configFile, whether_installs, bugIds)
print('\033[1;35m Begin gcc - search simp opt and collect\033[0m')
os.system(f'python3 src/gcc/get_min_opt.py {configFile}')

# --------------config permission--------------

maindir = cfg.get('llvm-locations', 'maindir')
alldir = maindir + '/../'
os.system('chmod -R 777 ' + alldir)