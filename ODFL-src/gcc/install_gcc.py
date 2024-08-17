'''
Author: your name
Date: 2021-07-21 07:11:52
LastEditTime: 2021-10-24 10:59:05
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/install_gcc.py
'''

import os
import sys
from configparser import ConfigParser
import subprocess
# if __name__ == '__main__':
def install(configFile):
    cfg = ConfigParser()
    cfg.read(configFile)
    compilersDir = cfg.get('gcc-workplace', 'compilersdir')
    bugList = cfg.get('gcc-workplace', 'buglist')
    with open(bugList, 'r') as f:
        sumlines = f.readlines()
    for i in range(len(sumlines)):
        rev = sumlines[i].strip().split(',')[1]
        print(rev)
        srcdir = compilersDir
        revpath = srcdir + rev
        if os.path.exists(revpath):
            os.system('rm -rf '+revpath)
        os.system('mkdir -p '+revpath)
        os.system('svn co svn://gcc.gnu.org/svn/gcc/trunk -'+rev.split('-')[0] +' '+revpath+'/'+rev)
        if not os.path.exists(revpath + '/' + rev):
            exit(1)
        os.chdir(revpath + '/'+rev)
        os.system('./contrib/download_prerequisites')

        os.system('mkdir ' + revpath + '/' + rev + '-build')
        os.chdir(revpath + '/' + rev + '-build')
        os.system('rm * -rf')
        os.system('../'+rev+'/configure --enable-languages=c,c++ --enable-checking=release --enable-coverage --prefix='+revpath+'/'+rev+'-build')

        subprocess.run('make -j 64', shell=True)
        subprocess.run('make install', shell=True)
        os.chdir(srcdir)