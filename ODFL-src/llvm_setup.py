import os,sys
from configparser import ConfigParser

# --------------modify maindir--------------

os.chdir(sys.path[0])
cfg = ConfigParser()
cfg.read('conf/config.ini')

path = sys.path[0]
cfg.set('llvm-workplace', 'maindir', path)
with open('conf/config.ini', 'w') as f:
    cfg.write(f)


# --------------build llvm directory--------------

compilersdir = cfg.get('llvm-workplace', 'compilersdir')
if not os.path.exists(compilersdir):
    print('\033[1;35m Now build directory: ', compilersdir,'\033[0m')
    os.system('mkdir -p ' + compilersdir)
else: print('\033[1;35m Already has directory: ', compilersdir,'\033[0m')

oracleDir = cfg.get('llvm-workplace', 'oracledir')
if not os.path.exists(oracleDir):
    print('\033[1;35m Now build directory: ', oracleDir, '\033[0m')
    os.system('mkdir -p ' + oracleDir)
else: print('\033[1;35m Already has directory: ', oracleDir,'\033[0m')

covInfoDir = cfg.get('llvm-workplace', 'covInfodir')
if not os.path.exists(covInfoDir):
    print('\033[1;35m Now build directory: ', covInfoDir, '\033[0m')
    os.system('mkdir -p ' + covInfoDir)
else: print('\033[1;35m Already has directory: ', covInfoDir,'\033[0m')

# --------------check llvm bug config in benchmark repository--------------

llvmRepo = cfg.get('llvm-workplace', 'benchmark')
llvmbugsname = os.listdir(llvmRepo)

bugList = cfg.get('llvm-workplace', 'bugList')
revfile = open(bugList)
revlines = revfile.readlines()
revfile.close()

for i in range(len(revlines)):
    bugId = revlines[i].strip().split(',')[0]
    if bugId not in llvmbugsname:
        print('\033[1;35m llvm bug ', bugId,' does not exist in existing repository.\033[0m')
        print('\033[1;35m Please configure it by yourself\033[0m')
    else:
        os.system('cp -r ' + llvmRepo + bugId + ' ' + oracleDir)

# --------------install llvm compilers and collect info--------------
configFile = cfg.get('llvm-workplace', 'configFile')
bugList = cfg.get('llvm-workplace', 'bugList')
compilersdir = cfg.get('llvm-workplace', 'compilersdir')
oracleDir = cfg.get('llvm-workplace', 'oracledir')

revisions = []
bugIds = []
whether_installs = []
wrongs = []

revfile = open(bugList)
revlines = revfile.readlines()
revfile.close()

for i in range(len(revlines)):
    if i < 5:
        continue
    bugIds.append(revlines[i].strip().split(',')[0])
    revisions.append(revlines[i].strip().split(',')[1])
    whether_installs.append(revlines[i].strip().split(',')[5])
    wrongs.append(revlines[i].strip().split(',')[3])
from llvm import collect
print('\033[1;35m Begin llvm - install\033[0m')
install(configFile)
print('\033[1;35m Begin llvm - collect\033[0m')
collect(configFile)

