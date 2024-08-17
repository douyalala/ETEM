'''
Author: your name
Date: 2021-07-22 09:17:40
LastEditTime: 2021-08-22 11:49:37
LastEditors: Please set LastEditors
Description: 查看gcc版本
FilePath: /cfl/ODFL/gcc/check/version.py
'''
import os
import subprocess
from configparser import ConfigParser

if __name__ == '__main__':
    
    cfg = ConfigParser()
    cfg.read('/root/cfl/ODFL/conf/config.ini')
    configFile = cfg.get('gcc-workplace', 'configFile')
    mianDir = cfg.get('gcc-workplace', 'maindir')
    compilerDir = cfg.get('gcc-workplace', 'compilersdir')
    oracleDir = cfg.get('gcc-workplace', 'oracledir')
    sumFile = cfg.get("gcc-workplace", 'buglist')
    configFile = cfg.get('gcc-workplace', 'configFile')
    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    with open(sumFile, 'r') as f:
        lines = f.readlines()
    
    

    for i in range(len(lines)):
        bugId = lines[i].strip().split(',')[0]
        revNum = lines[i].strip().split(',')[1]
        compilationOptionsRight = lines[i].strip().split(',')[2]
        compilationOptionsWrong = lines[i].strip().split(',')[3]
        checkpass = lines[i].strip().split(',')[4]

        optioncovpath = covinfoDir + bugId
        prefixpath = compilerDir + revNum + '/' + revNum
        oraclepath = oracleDir + bugId
        failfile = oraclepath + '/fail.c'
        curpath = mianDir + '/gcc'
        
        failcovpath = optioncovpath + '/wrongOptionSmall/fileGene'
        for (dirpath, dirnames, filenames) in os.walk(failcovpath):
            for subdir in dirnames:
                abspath = os.path.join(dirpath, subdir)
                if not os.listdir(abspath):
                    print(bugId + ' ' + revNum)                   
