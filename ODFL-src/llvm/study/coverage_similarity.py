'''
Author: your name
Date: 2021-10-04 09:12:24
LastEditTime: 2021-10-16 07:15:59
LastEditors: Please set LastEditors
Description: 统计覆盖信息的相似度
FilePath: /cfl/ODFL/gcc/study/similarity.py
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

def judge_dir():
    if not os.path.exists(optioncovpath + '/orifail'):
        os.system('mkdir ' + optioncovpath + '/orifail')
    if not os.path.exists(optioncovpath + '/rightOptionSmall'):
        os.system('mkdir ' + optioncovpath + '/rightOptionSmall')
    if not os.path.exists(optioncovpath + '/rightOptionBig'):
        os.system('mkdir ' + optioncovpath + '/rightOptionBig')
    if not os.path.exists(optioncovpath + '/wrongOptionBig'):
        os.system('mkdir ' + optioncovpath + '/wrongOptionBig')
    if not os.path.exists(optioncovpath + '/wrongOptionSmall'):
        os.system('mkdir ' + optioncovpath + '/wrongOptionSmall')
    if not os.path.exists(optioncovpath + '/covAnalysis'):
        os.system('mkdir ' + optioncovpath + '/covAnalysis')
    if not os.path.exists(optioncovpath + '/covAnalysis/wrongOptionSmall'):
        os.system('mkdir ' + optioncovpath + '/covAnalysis/wrongOptionSmall')
    if not os.path.exists(optioncovpath + '/covAnalysis/wrongOptionBig'):
        os.system('mkdir ' + optioncovpath + '/covAnalysis/wrongOptionBig')
    if not os.path.exists(optioncovpath + '/covAnalysis/rightOptionSmall'):
        os.system('mkdir ' + optioncovpath + '/covAnalysis/rightOptionSmall')
    if not os.path.exists(optioncovpath + '/covAnalysis/rightOptionBig'):
        os.system('mkdir ' + optioncovpath + '/covAnalysis/rightOptionBig')
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

def sameflagnum():
    wrongcovpath = wrongFlagCovPath
    key = 0
    # disable all bug-free and bug-related flags
    for compilationOption in wrongoptExactdict.keys():
        if key != 0:
            break
        flagOption = wrongoptExactdict[compilationOption]
        if len(flagOption) == 1:
            continue
        if len(flagOption) % 2 != 0:
            num = int((len(flagOption) - 1) / 2)
        else:
            num = int(len(flagOption) / 2)

        # print("wrong front " + str(len(flagOption[:num])) + ' in ' + str(len(flagOption)) + ':')
        covfilename = 'fail' + compilationOption.replace(' ', '+') + '_front' + str(len(flagOption[:num]))
        if not os.path.exists(wrongcovpath + '/stmt_info_' + covfilename +'.txt'):
            continue
        with open(wrongcovpath + '/stmt_info_' + covfilename +'.txt','r') as stmtfileFront:
            frontlines = stmtfileFront.readlines()

        # 后面一半的flag
        # print("wrong back " + str(len(flagOption[num:2*num])) + ' in ' + str(len(flagOption)) + ':')
        covfilename = 'fail' + compilationOption.replace(' ', '+') + '_back' + str(len(flagOption[num:2*num]))
        with open(wrongcovpath + '/stmt_info_' + covfilename +'.txt','r') as stmtfileBack:
            backlines = stmtfileBack.readlines()

        
        frontLineCnt = 0
        frontLineSet = set()
        for i in range(len(frontlines)):
            faillinesplit = frontlines[i].strip().split('$')  
            filename = faillinesplit[0]  # filename
            stmtlist = faillinesplit[1].split(',') # stmts
            frontLineCnt += len(stmtlist)
            for j in range(len(stmtlist)):
                frontLineSet.add(filename+':'+stmtlist[j])

        backLineCnt = 0
        backLineSet = set()
        for i in range(len(backlines)):
            faillinesplit = backlines[i].strip().split('$')  
            filename = faillinesplit[0]  # filename
            stmtlist = faillinesplit[1].split(',') # stmts
            backLineCnt += len(stmtlist)
            for j in range(len(stmtlist)):
                backLineSet.add(filename+':'+stmtlist[j])

        similarity = len(frontLineSet&backLineSet)/len(frontLineSet | backLineSet)
        print(bugId + ',' + revNum + ',' + str(similarity) + ',' + str(frontLineCnt) + ',' + str(backLineCnt) + ',' + str(frontLineCnt-backLineCnt))
        wrongflagNumFile.write(bugId + ',' + revNum + ',' + str(similarity) + ',' + str(frontLineCnt) + ',' + str(backLineCnt) + ',' + str(frontLineCnt-backLineCnt) + '\n')
        wrongflagNumFile.flush()

        key = 1

def diffflagnum():
    # 覆盖信息文件路径
    wrongSingleCovPath = optioncovpath + '/wrongOptionSmall/testfileCov'
    wrongMultiCovPath = optioncovpath + '/wrongOptionSmall/disallfreefileCov'
    files =  os.listdir(wrongMultiCovPath)
    if len(files) == 0:
        files = os.listdir(wrongFlagCovPath)
        files = sorted(files,key=lambda x: os.path.getmtime(os.path.join(wrongFlagCovPath, x)))
        covfilename = files[-1]
        optLevel = re.search('-O[0-9|s]+', covfilename).group()
        with open(wrongFlagCovPath + '/'+ covfilename,'r') as f:
            multilines = f.readlines()
    else:
        if len(files) > 1:
            files = sorted(files,key=lambda x: os.path.getmtime(os.path.join(wrongMultiCovPath, x)))
        covfilename = files[0]
        optLevel = re.search('-O[0-9|s]+', covfilename).group()

        with open(wrongMultiCovPath + '/' + covfilename,'r') as f:
            multilines = f.readlines()
    
    multiLineCnt = 0
    multiLineSet = set()
    for i in range(len(multilines)):
        faillinesplit = multilines[i].strip().split('$')  
        filename = faillinesplit[0]  # filename
        stmtlist = faillinesplit[1].split(',') # stmts
        multiLineCnt += len(stmtlist)
        for j in range(len(stmtlist)):
            multiLineSet.add(filename+':'+stmtlist[j])
    
    for file in os.listdir(wrongSingleCovPath):
        if not optLevel in file:
            continue
        with open(wrongSingleCovPath + '/' + file) as f:
            singlelines = f.readlines()
        
        singleLineCnt = 0
        singleLineCntList = []
        similarityList = []
        singleLineSet = set()
        for i in range(len(singlelines)):
            faillinesplit = singlelines[i].strip().split('$')  
            filename = faillinesplit[0]  # filename
            stmtlist = faillinesplit[1].split(',') # stmts
            singleLineCnt += len(stmtlist)
            singleLineCntList.append(singleLineCnt)
            for j in range(len(stmtlist)):
                singleLineSet.add(filename+':'+stmtlist[j])

        similarity = len(multiLineSet&singleLineSet)/len(multiLineSet | singleLineSet)
        similarityList.append(similarity)

    print(bugId + ',' + revNum + ',' + str(max(similarityList)) + ',' + str(multiLineCnt) + ',' + str(max(singleLineCntList)) + ',' + str(multiLineCnt-max(singleLineCntList)))
    singleMultiDiffFile.write(bugId + ',' + revNum + ',' + str(max(similarityList)) + ',' + str(multiLineCnt) + ',' + str(max(singleLineCntList)) + ',' + str(multiLineCnt-max(singleLineCntList)) + '\n')
    singleMultiDiffFile.flush()
        



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

# wrongflagNumFile = open(covinfoDir + '/flag_study_samenum.csv', 'w')
# wrongflagNumFile.write("bugId" + ',' + 'revNum' + ',similarity,frontLineCnt,backLineCnt,difference' + '\n')

singleMultiDiffFile = open(covinfoDir + '/flag_study_diffnum.csv', 'w')
singleMultiDiffFile.write("bugId" + ',' + 'revNum' + ',similarity,frontLineCnt,backLineCnt,difference' + '\n')

for i in range(len(sumlines)):
    bugId = sumlines[i].strip().split(',')[0]
    revNum = sumlines[i].strip().split(',')[1]
    compilationOptionsRight = sumlines[i].strip().split(',')[2].replace('+',' ')
    compilationOptionsWrong = sumlines[i].strip().split(',')[3].replace('+',' ')
    checkpasse = sumlines[i].strip().split(',')[4]

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

    optioncovpath = covinfoDir + bugId
    # if os.path.exists(optioncovpath):
    #     os.system('rm -r ' + optioncovpath)
    # os.system('mkdir ' + optioncovpath)
    if not os.path.exists(optioncovpath):
        os.system('mkdir ' + optioncovpath)

    os.chdir(optioncovpath)

    # 覆盖信息文件路径

    wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/flagTypefileCov'
    # wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/flagNumfileCov'

    # determine whether the folder exists
    judge_dir()

    # 获取每个optimization level对应的exact optimization option
    O1_optimi, O2_optimi, O3_optimi, Os_optimi, O0_optimi = collect_optimi_flags()

    # # The execution result of the program under right optimization
    # rightres = get_result(revNum, prefixpath, failfile, compilationOptionsRight, compilationOptionsWrong)
    # wrongres = get_result(revNum, prefixpath, failfile, compilationOptionsWrong, compilationOptionsWrong)
    # if rightres == wrongres:
    #     print('ERROR: the wrong option and right option has the same result')
    #     sys.exit(1)

    wrongoptExactdict, rightoptExactdict = optionDict()

    # sameflagnum()
    diffflagnum()
    

    

    

# wrongflagNumFile.close()
singleMultiDiffFile.close()
