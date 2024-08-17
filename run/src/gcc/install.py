import os, sys
from configparser import ConfigParser

def rewrite_installs(new_installs, configFile):

    cfg = ConfigParser()
    cfg.read(configFile)
    bugList = cfg.get('gcc-locations', 'bugList')
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
    compilersdir = cfg.get('gcc-locations', 'compilersdir')
    src_dir = cfg.get('gcc-locations', 'gcc_src_dir')
    new_installs = []

    for i in range(len(revisions)):

        whether_install = whether_installs[i]
        if whether_install == 'install_yes':
            continue
        bugId = bugIds[i]
        rev = revisions[i]
        srcpath = f'{src_dir}/{rev}'
        revpath = f'{compilersdir}/{rev}-build'

        if os.path.exists(revpath):
            os.system('rm -rf '+revpath)
        if os.path.exists(srcpath):
            os.system('rm -rf '+srcpath)
        try:
            os.system('mkdir -p '+srcpath)
            os.system('mkdir -p '+revpath)
            print('\033[1;35m downloading src..\033[0m')
            os.system('svn co svn://gcc.gnu.org/svn/gcc/trunk -' + rev + ' ' + srcpath)
            os.chdir(revpath)

            print('\033[1;35m gcc configuring ..\033[0m')
            os.system(
                srcpath + '/configure --enable-languages=c,c++ --disable-werror --enable-checking=release --prefix=' + revpath + ' --enable-coverage')

            print('\033[1;35m making..\033[0m')
            os.system('make -j ' + str(install_thread))
            os.system('make install')
            os.chdir(compilersdir)
            new_installs.append(bugId)
        except:
            print('\033[1;35m Failed to install GCC revision ', str(rev),'\033[0m')

    rewrite_installs(new_installs, configFile)