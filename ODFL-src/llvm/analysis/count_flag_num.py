'''
Author: your name
Date: 2021-09-08 07:13:55
LastEditTime: 2021-10-16 09:05:36
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/analysis/count_flag_num.py
'''
from configparser import ConfigParser
from collections import OrderedDict
import re

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

# def collect_flag_num(bugId, revNum, rightflagNumFile, wrongflagNumFile):
def collect_flag_num(bugId, revNum, rightflagNumList, wrongflagNumList):
    # with open(optioncovpath + '/wrong_exact_dict.txt', 'r') as f:
    #     wronglines = f.readlines()

    combinNum = OrderedDict()
    # wrongoptExactdict = OrderedDict()
    # wrongLevelNum = 0
    # for i in range(len(wronglines)):
    #     # print(wronglines[i])
    #     compilationOption = wronglines[i].strip().split('$')[0]
    #     compilationOption = re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption)
    #     wrongoptExactList = wronglines[i].strip().split('$')[1].split(',')
    #     wrongoptExactdict[compilationOption] = wrongoptExactList
    #     wrongflagNumList[compilationOption] = len(wrongoptExactList)
    #     wrongLevelNum += 1
    
    # wrongflagNumFile.write(bugId + ',' + revNum + ',' + ','.join(wrongflagNumList) + '\n')
    
    with open(optioncovpath + '/right_exact_dict.txt', 'r') as f:
        rightlines = f.readlines()
    combinNum = OrderedDict()
    rightoptExactdict = OrderedDict()
    rightLevelNum = 0 # 优化级别的数量
    for i in range(len(rightlines)):
        # print(rightlines[i])
        compilationOption = rightlines[i].strip().split('$')[0]
        compilationOption = re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption)
        rightoptExactList = rightlines[i].strip().split('$')[1].split(',')
        rightoptExactdict[compilationOption] = rightoptExactList
        rightflagNumList[compilationOption] = len(rightoptExactList)
        rightLevelNum += 1
    # rightflagNumFile.write(bugId + ',' + revNum + ',' + ','.join(rightflagNumList) + '\n')
    
    wrongoptExactdict = OrderedDict()
    wrongLevelNum = 0 # 编译器优化级别的数量
    for compilationOption in rightoptExactdict.keys():
        alloptset = set()
        for smallopt in eval(re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption) + '_optimi'):
            if smallopt.startswith('-fno'):
                smallopt = smallopt.replace('-fno-', '-f', 1)
            else:
                smallopt = smallopt.replace('-f', '-fno-', 1)
            if smallopt == '-fno-rtti' or smallopt == '-fthreadsafe-statics':
                continue
            alloptset.add(smallopt)
        wrongoptExactdict[compilationOption] = list(alloptset - set(rightoptExactdict[compilationOption]))
        wrongflagNumList[compilationOption] = len(alloptset - set(rightoptExactdict[compilationOption]))
        wrongLevelNum += 1
    
    return wrongLevelNum, rightLevelNum


cfg = ConfigParser()
cfg.read('/root/cfl/ODFL/conf/config.ini')
sumFile = cfg.get("gcc-workplace", 'buglist')
covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
with open(sumFile, 'r') as f:
    sumlines = f.readlines()
rightflagNumFile = open(covinfoDir + '/right_flag_num.csv', 'w')
wrongflagNumFile = open(covinfoDir + '/wrong_flag_num.csv', 'w')
optionlist = ['O0', 'O1', 'O2', 'Os', 'O3']
wrongflagNumFile.write("bugId" + ',' + 'revNum' + ',' + ','.join(optionlist) + ',levelCnt,sum,lowestCnt,higestCnt' + '\n')
rightflagNumFile.write('bugId' + ',' + 'revNum' + ',' + ','.join(optionlist) + ',levelCnt,sum,lowestCnt,higestCnt' + '\n')

for i in range(len(sumlines)):
    bugId = sumlines[i].strip().split(',')[0]
    revNum = sumlines[i].strip().split(',')[1]
    right = sumlines[i].strip().split(',')[2]
    wrong = sumlines[i].strip().split(',')[3]
    checkpasse = sumlines[i].strip().split(',')[4]
    # if bugId == '58418':
    #     print(1)
    #     pass
    optioncovpath = covinfoDir + bugId
    exactoptimsDir = cfg.get('gcc-workplace', 'exactoptimdir')

    O1_optimi, O2_optimi, O3_optimi, Os_optimi, O0_optimi = collect_optimi_flags()
    
    # 每个优化级别的option的数量
    wrongflagNumList = OrderedDict()
    rightflagNumList = OrderedDict()
    for level in optionlist:
        wrongflagNumList[level] = 0
        rightflagNumList[level] = 0
    wrongLevelNum, rightLevelNum = collect_flag_num(bugId, revNum, rightflagNumList, wrongflagNumList) # 不同优化级别对应的优化option的数量
    # wrongoptExactdict, rightoptExactdict = collect_flag_num(bugId, revNum, rightflagNumFile, wrongflagNumFile)
    wrongCntList = list(wrongflagNumList.values()) #获取option数量的值
    rightCntList = list(rightflagNumList.values())
    wrongNonzeroList = [e for i, e in enumerate(wrongCntList) if e != 0]
    # wrongLastList = [e for i, e in enumerate(wrongCntList)]
    rightNonzeroList = [e for i, e in enumerate(rightCntList) if e != 0]
    # for cnt in wrongCntList:
    #     if cnt != '0':

    wrongflagNumFile.write(bugId + ',' + revNum + ',' + ','.join([str(x) for x in wrongCntList]) + ',' + str(wrongLevelNum) + ',' + str(sum(wrongCntList)) + ',' + str(wrongNonzeroList[0]) + ',' + str(wrongNonzeroList[-1]) + '\n')
    rightflagNumFile.write(bugId + ',' + revNum + ',' + ','.join([str(x) for x in rightCntList]) + ',' + str(rightLevelNum) + ',' + str(sum(rightCntList)) +  ',' + str(rightNonzeroList[0]) + ',' + str(rightNonzeroList[-1]) + '\n')
    wrongflagNumFile.flush()
    rightflagNumFile.flush()



rightflagNumFile.close()
wrongflagNumFile.close()
    
