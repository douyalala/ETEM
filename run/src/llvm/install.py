import os, sys
from configparser import ConfigParser

def rewrite_installs(new_installs, configFile):

    cfg = ConfigParser()
    cfg.read(configFile)
    bugList = cfg.get('llvm-locations', 'bugList')
    f = open(bugList)
    lines = f.readlines()
    f.close()
    downi = 0
    downj = 0
    for i in range(downi, len(new_installs)):
        bugId1 = new_installs[i]
        for j in range(downj, len(lines)):
            bugId2 = lines[j].strip().split(',')[0]
            if bugId1 == bugId2:
                lines[j] = lines[j].split('\n')[0][:-10] + 'install_yes\n'
                downi = i + 1
                downj = j + 1
                break
    f = open(bugList, 'w')
    for line in lines:
        f.write(line)
    f.close()

def install(revisions, configFile, whether_installs, bugIds):

    cfg = ConfigParser()
    cfg.read(configFile)
    install_thread = cfg.get('params', 'install_thread')
    compilersdir = cfg.get('llvm-locations', 'compilersdir')
    maindir = cfg.get('llvm-locations', 'maindir')
    maindir=cfg.get('llvm-locations', 'maindir')

    new_installs = []
    
    print('\033[1;35m github clone llvm..\033[0m')
    os.chdir(compilersdir)
    os.system('git clone https://github.com/llvm/llvm-project.git')

    for i in range(len(revisions)):

        whether_install = whether_installs[i]
        if whether_install == 'install_yes':
            continue

        rev = revisions[i]
        srcpath = f'{compilersdir}/{rev}-src'
        revpath = f'{compilersdir}/{rev}-build'

        bugId = bugIds[i]

        try:
            print('\033[1;35m github checkout and copy..\033[0m')
            os.chdir(f'{compilersdir}/llvm-project')
            os.system('git checkout -f main')
            os.system(f'git checkout -f {rev}')
            os.system(f'cp -r {compilersdir}/llvm-project/ {srcpath}/')
            
            print('\033[1;35m llvm building...\033[0m')
            os.system('mkdir -p '+revpath)
            os.chdir(revpath)
            os.system(f'cmake -DLLVM_ENABLE_PROJECTS=clang -DCMAKE_INSTALL_PREFIX="{revpath}" -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="-g -O0 -fprofile-arcs -ftest-coverage" -DCMAKE_CXX_FLAGS="-g -O0 -fprofile-arcs -ftest-coverage" -DCMAKE_EXE_LINKER_FLAGS="-g -fprofile-arcs -ftest-coverage -lgcov" {srcpath}/llvm')
            
            print('\033[1;35m llvm making..\033[0m')
            os.system('make -j ' + str(install_thread))
            os.system('make install')
            new_installs.append(bugId)
        except:
            print('\033[1;35m Failed to install LLVM revision ', str(rev),'\033[0m')
        
    rewrite_installs(new_installs, configFile)
    os.chdir(maindir)