'''
Author: your name
Date: 2021-10-04 09:12:37
LastEditTime: 2021-10-21 03:20:10
LastEditors: Please set LastEditors
Description: 统计覆盖信息之间的行数的差别，diff行有哪些
FilePath: /cfl/ODFL/gcc/study/coverage_line.py
'''
import os,sys,re
from configparser import ConfigParser
from collections import OrderedDict
sys.path.append('/root/cfl/ODFL/gcc/')
from collect_optioninfo import *

def collect_optimi_flags():
    O1_optimi = set()
    O2_optimi = set()
    O3_optimi = set()
    Os_optimi = set()
    O0_optimi = set()
    optLevels = ['-O0', '-O1', '-O2', '-O3', '-Os']
    for optLevel in optLevels:
        with open(exactoptimsDir + bugId + '/' + optLevel + '.txt', 'r') as f:
            optimilines = f.readlines()
        for line in optimilines:
            if line == '' or not '[enabled]' in line:
                continue
            if optLevel == '-O1':
                O1_optimi.add(line.strip().split(' ')[0].strip())
            elif optLevel == '-O2':
                O2_optimi.add(line.strip().split(' ')[0].strip())
            elif optLevel == '-O3':
                O3_optimi.add(line.strip().split(' ')[0].strip())
            elif optLevel == '-Os':
                Os_optimi.add(line.strip().split(' ')[0].strip())
            elif optLevel == '-O0':
                O0_optimi.add(line.strip().split(' ')[0].strip())

    return O1_optimi, O2_optimi, O3_optimi, Os_optimi, O0_optimi

def optionDict():
    with open(optioncovpath + '/wrong_exact_dict.txt', 'r') as f:
        wronglines = f.readlines()
    combinNum = OrderedDict()
    wrongoptExactdict = OrderedDict()
    for i in range(len(wronglines)):
        # print(wronglines[i])
        compilationOption = wronglines[i].strip().split('$')[0]
        wrongoptExactList = wronglines[i].strip().split('$')[1].split(',')
        wrongoptExactdict[compilationOption] = wrongoptExactList

    with open(optioncovpath + '/right_exact_dict.txt', 'r') as f:
        rightlines = f.readlines()
    combinNum = OrderedDict()
    rightoptExactdict = OrderedDict()
    for i in range(len(rightlines)):
        # print(rightlines[i])
        compilationOption = rightlines[i].strip().split('$')[0]
        rightoptExactList = rightlines[i].strip().split('$')[1].split(',')
        rightoptExactdict[compilationOption] = rightoptExactList
    
    return wrongoptExactdict, rightoptExactdict


revNum = sys.argv[1]
compilationOptionsRight = sys.argv[2].replace('+',' ')
compilationOptionsWrong = sys.argv[3].replace('+',' ')
checkpass = sys.argv[4]
configFile = sys.argv[5]
bugId = sys.argv[6]

cfg = ConfigParser()
cfg.read('/root/cfl/ODFL/conf/config.ini')
sumFile = cfg.get("gcc-workplace", 'buglist')
covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
compilerDir = cfg.get('gcc-workplace', 'compilersdir')
oracleDir = cfg.get('gcc-workplace', 'oracledir')
mianDir = cfg.get('gcc-workplace', 'maindir')
exactoptimsDir = cfg.get('gcc-workplace', 'exactoptimdir')
gcovpath = '/root/cfl/gccforme/r229639/r229639-build/bin/gcov'
# with open(sumFile, 'r') as f:
#     sumlines = f.readlines()
# for i in range(len(sumlines)):
#     bugId = sumlines[i].strip().split(',')[0]
#     revNum = sumlines[i].strip().split(',')[1]
#     compilationOptionsRight = sumlines[i].strip().split(',')[2].replace('+',' ')
#     compilationOptionsWrong = sumlines[i].strip().split(',')[3].replace('+',' ')
#     checkpasse = sumlines[i].strip().split(',')[4]

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

O1_optimi, O2_optimi, O3_optimi, Os_optimi, O0_optimi = collect_optimi_flags()
wrongoptExactdict, rightoptExactdict = optionDict()

optCovPath = optioncovpath + '/studyOptNumber'
if os.path.exists(optCovPath):
    os.system('rm -R ' + optCovPath)
    os.system('mkdir  ' + optCovPath)
else:
    os.system('mkdir  ' + optCovPath)

wrongLowestLevel = list(wrongoptExactdict.keys())[0]
wronglevel_cur = re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', wrongLowestLevel)
optList = []
for smallopt in eval(wronglevel_cur + '_optimi'):
    if smallopt.startswith('-fno'):
        smallopt = smallopt.replace('-fno-', '-f', 1)
    else:
        smallopt = smallopt.replace('-f', '-fno-', 1)
    if smallopt == '-fno-rtti' or smallopt == '-fthreadsafe-statics':
        continue
    optList.append(smallopt)
    optimOption = wrongLowestLevel + ' ' + ' '.join(optList)
    filename = wrongLowestLevel + '_' + str(len(optList)) + 'dis'
    get_cov(revNum, prefixpath,gcovpath, optCovPath, failfile, filename, optimOption)


