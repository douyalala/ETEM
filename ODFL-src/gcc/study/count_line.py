'''
Author: your name
Date: 2021-10-21 03:20:18
LastEditTime: 2021-10-23 07:48:37
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/study/count_line.py
'''
import os,sys,re
from configparser import ConfigParser
from collections import OrderedDict
sys.path.append('/root/cfl/ODFL/gcc/')
from collect_optioninfo import *
cfg = ConfigParser()
cfg.read('/root/cfl/ODFL/conf/config.ini')
sumFile = cfg.get("gcc-workplace", 'buglist')
covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
compilerDir = cfg.get('gcc-workplace', 'compilersdir')
oracleDir = cfg.get('gcc-workplace', 'oracledir')
mianDir = cfg.get('gcc-workplace', 'maindir')
exactoptimsDir = cfg.get('gcc-workplace', 'exactoptimdir')
gcovpath = '/root/cfl/gccforme/r229639/r229639-build/bin/gcov'
with open(sumFile, 'r') as f:
    sumlines = f.readlines()
for i in range(len(sumlines)):
    bugId = sumlines[i].strip().split(',')[0]
    revNum = sumlines[i].strip().split(',')[1]
    compilationOptionsRight = sumlines[i].strip().split(',')[2].replace('+',' ')
    compilationOptionsWrong = sumlines[i].strip().split(',')[3].replace('+',' ')
    checkpasse = sumlines[i].strip().split(',')[4]

    if bugId != '57488':
        continue

    # r237156
    
    print(revNum + ' ' + bugId)

    prefixpath = compilerDir + revNum + '/' + revNum
    clangpath = prefixpath + '-build/bin/clang'
    # clangbuildpath = prefixpath + '-build/clang'
    covdir = prefixpath + '-build'
    oraclepath = oracleDir + bugId
    curpath = mianDir + '/gcc'
    failfile = oraclepath + '/fail.c'
    gccpath = prefixpath + '-build/bin/gcc'
    gccbuildpath = prefixpath+'-build/gcc'
    covdir = prefixpath+'-build'
    failfile = oraclepath + '/fail.c'

    optioncovpath = covinfoDir + bugId
    # if os.path.exists(optioncovpath):
    #     os.system('rm -r ' + optioncovpath)
    # os.system('mkdir ' + optioncovpath)
    if not os.path.exists(optioncovpath):
        os.system('mkdir ' + optioncovpath)

    os.chdir(optioncovpath)

    cntToFile = open(optioncovpath + '/covFileLine.csv', 'w')
    cntToFile.write('bugid,revNum,Number of finer-grained options disabled,Number of code lines covered in compiler,Number of files covered in compiler\n')
    cntToFile.flush()

    optCovPath = optioncovpath + '/studyOptNumber/'
    dir_list = os.listdir(optCovPath)
    dir_list = sorted(dir_list,  key=lambda x: os.path.getmtime(os.path.join(optCovPath, x)))
    for file,i in zip(dir_list, range(1, len(dir_list)+1)):
        with open(optCovPath + file, 'r') as f:
            lines = f.readlines()
        cntLine = 0
        cntFile = 0
        for j in range(len(lines)):
            linesplit = lines[j].strip().split('$')
            # filename=passlinesplit[0].strip().split('.gcda')[0].strip()
            filename = linesplit[0]
            stmtlist = linesplit[1].split(',')
            cntLine += len(stmtlist)
            cntFile += 1
        cntToFile.write(bugId + ',' + revNum + ',' + str(i) + ',' + str(cntLine) + ',' + str(cntFile) + '\n')
        cntToFile.flush()