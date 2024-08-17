'''
Author: your name
Date: 2021-10-09 06:57:56
LastEditTime: 2021-10-10 12:09:18
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/analysis/cmp_efficiency.py
'''
import os,sys,re
from configparser import ConfigParser
# sys.path.append('/root/cfl/innovation/Option/smalloptimoption/file_isolation')
from collect_optioninfo import *
from configparser import ConfigParser
from itertools import combinations, combinations_with_replacement
from collections import OrderedDict

def collect_orifail():
    print('#####compilationOptionWrong')
    print(compilationOptionsWrong)
    covpath = orifailCovPath
    option = compilationOptionsWrong.replace(' ', '+')
    # print(compilationOptionsWrong)
    if os.path.exists(covpath):
        os.system('rm -R ' + covpath)
        os.system('mkdir  ' + covpath)
    else:
        os.system('mkdir  ' + covpath)
    start = time.time()
    get_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, compilationOptionsWrong)
    end = time.time()
    spendTime = end - start

    return spendTime
    # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, compilationOptionsWrong)

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

def classify_optlevel():
    optionlist = ['-O0', '-O1', '-O2', '-Os', '-O3']
    optionlist_ = []
    rightoptionlist = []  # 为保证optimization level的顺序，使用list数据结构
    wrongoptionlist = []
    for opt in optionlist:
        # 出现-O2 -w -m32这样的多个编译选项，把其中-O的优化选项替换掉，例如替换成：-O0 -w -m32
        if ' ' in compilationOptionsWrong:
            opttmp_wrong = re.sub('-O([0-3]|s)', opt, compilationOptionsWrong)
            optionlist_.append(opttmp_wrong)
        else:
            optionlist_.append(opt) # 如果没有多个编译选项，直接把-On加入到集合中

        if ' ' in compilationOptionsRight:
            opttmp_right = re.sub('-O([0-3]|s)', opt, compilationOptionsRight)
            if opttmp_right == opttmp_wrong:  # 避免重复
                continue
            else:
                optionlist_.append(opttmp_right)

    for opt in optionlist_:
        tmpres = get_result(revNum, prefixpath, failfile, opt, compilationOptionsWrong)
        if tmpres == rightres:
            rightoptionlist.append(opt)
        else:
            wrongoptionlist.append(opt)
            if opt == compilationOptionsWrong: # 如果该编译选项与orifail编译选项相同，则跳转到下一个
                continue
    return rightoptionlist, wrongoptionlist

def collect_right_optimi(rightoptLevelist, wrongoptLevelist):
    # rightDictFile = open(optioncovpath + '/right_exact_dict.txt', 'w')
    # wrongDictFile = open(optioncovpath + '/wrong_exact_dict.txt', 'w')
    startTime = time.time()
    rightoptExactdict = OrderedDict()
    wrongoptExactdict = OrderedDict()
    wrongoptTmpdict = OrderedDict()
    wrongSequeNum = 0
    for compilationOption, i in zip(wrongoptLevelist, range(len(wrongoptLevelist))):
        # get right optimization options
        wrongoptExactSet = set()
        rightoptExactSet = set()
        tmpwrongOptSet = set()
        # 收集right optimization complication options
        for smallopt in eval(re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption) + '_optimi'):
            if smallopt.startswith('-fno'):
                smallopt = smallopt.replace('-fno-', '-f', 1)
            else:
                smallopt = smallopt.replace('-f', '-fno-', 1)
            smalloptimOption = compilationOption + ' ' + smallopt
            tmpres = get_result(revNum, prefixpath, failfile, smalloptimOption, compilationOptionsWrong)
            if tmpres == rightres: # 关闭small option后变成pass
                rightoptExactSet.add(smallopt)
                if smallopt.startswith('-fno'):
                    smallopt = smallopt.replace('-fno-', '-f', 1)
                else:
                    smallopt = smallopt.replace('-f', '-fno-', 1)
                # wrongOptimiSet.add(smallopt)
                tmpwrongOptSet.add(smallopt)
                # print(smalloptimOption)
        
        rightoptExactdict[compilationOption] = rightoptExactSet
        # rightDictFile.write(compilationOption + '$' + ','.join(rightoptExactSet) + '\n')
        # rightDictFile.flush()

        # get wrong optimization options
        if 'Os' in compilationOption:
            exact_set = Os_optimi - O1_optimi
        else:
            optimiOption_cur = re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption)
            
            exact_set = eval(optimiOption_cur + '_optimi') - eval(re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', rightoptLevelist[-1]) + '_optimi')
            if not exact_set:
                optimiOption_abo = 'O' + str(int(re.sub('O', '', optimiOption_cur)) - 1)
                exact_set = eval(optimiOption_cur + '_optimi') - eval(optimiOption_abo + '_optimi')
        for smallopt in exact_set - tmpwrongOptSet:
            if smallopt.startswith('-fno'):
                smallopt = smallopt.replace('-fno-', '-f', 1)
            else:
                smallopt = smallopt.replace('-f', '-fno-', 1)
            wrongoptExactSet.add(smallopt)
        wrongoptTmpdict[compilationOption] = wrongoptExactSet
        wrongoptExactdict[compilationOption] = wrongoptExactSet
    #     wrongDictFile.write(compilationOption + '$' + ','.join(wrongoptExactSet) + '\n')
    #     wrongDictFile.flush()
    endTime = time.time()
    # rightDictFile.close()
    # wrongDictFile.close()
    spendTime = endTime - startTime
    return rightoptExactdict, wrongoptExactdict, spendTime

def recursion(compilationOption, flagOption, num):
    if num == 0:
        return
    flagCombins = combinations(flagOption, num)
    flag = 0
    # 遍历上述组合
    for flagCombin in flagCombins:
        flagOption_ = list(flagCombin)
        optimOption = compilationOption + ' ' + ' '.join(flagOption_)
        res = get_result(revNum, prefixpath, failfile, optimOption, compilationOptionsWrong)
        if res == wrongres:
            flag = 1
            print('wrong-' + str(num) + ': ' + optimOption)
            # # 不关闭以下选项组合，编译结果正确
            bugTriggerSet = set(flagOption) - set(flagOption_)
            # print('use the: ' + str(bugTriggerSet).replace('-fno-', '-f') + ' from pass to fail')

            # 0: enable the flag; 1: disable the flag
            bugTriggerIndex = [1] * len(flagOption)
            for flag in flagOption_:
                bugTriggerIndex[flagOption.index(flag)] = 0
            print('wrong: ' + str(bugTriggerIndex))
            # covfilename = 'fail' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugTriggerIndex)
            # get_cov(revNum, prefixpath, gcovpath, wrongcovpath, failfile, covfilename, optimOption)
            
            # 从n个bugTriggerSet元素中筛选n-1个
            if len(bugTriggerSet) == 1:
                subbugTriggerSets = bugTriggerSet
            else:
                subbugTriggerSets = combinations(bugTriggerSet, len(bugTriggerSet) - 1)
            for subbugTriggerSet in subbugTriggerSets:
                # 在wrong集合optimOption的基础上加subbugTriggerSet
                rightoptimOption = optimOption + ' ' + ' '.join(subbugTriggerSet)
                res = get_result(revNum, prefixpath, failfile, rightoptimOption, compilationOptionsWrong)
                if res == rightres:
                    print('use the subset: ' + str(subbugTriggerSet) + ' from fail to pass')
                    # enableFlag = str(bugTriggerSet - set(subbugTriggerSet)).replace('-fno-', 'enable-f')
                    # covfilename = 'pass' + compilationOption.replace(' ', '+') + '_' + enableFlag
                    subbugTriggerIndex = bugTriggerIndex
                    for flag in subbugTriggerSet:
                        subbugTriggerIndex[flagOption.index(flag)] = 0
                    covfilename = 'pass' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in subbugTriggerIndex)
                    # get_cov(revNum, prefixpath, gcovpath, rightcovpath, failfile, covfilename, rightoptimOption)
                else:
                    print('##use the subset: ' + str(subbugTriggerSet) + ' not from fail to pass')
        elif res == rightres:
            # recursion(compilationOption, flagOption, num - 1)
            pass

    else:
        # 如果该组合下有bugtrigger configuration，则不再遍历下一次组合
        if flag != 0:
            return
        else:
            recursion(compilationOption, flagOption, num - 1)


if __name__ == '__main__':
    # revNum = sys.argv[1]
    # compilationOptionsRight = sys.argv[2].replace('+',' ')
    # compilationOptionsWrong = sys.argv[3].replace('+',' ')
    # checkpass = sys.argv[4]
    # configFile = sys.argv[5]
    # bugId = sys.argv[6]

    os.chdir(sys.path[0])
    cfg = ConfigParser()
    cfg.read('/root/cfl/ODFL/conf/config.ini')
    compilerDir = cfg.get('gcc-workplace', 'compilersdir')
    sumFile = cfg.get("gcc-workplace", 'buglist')
    configFile = cfg.get('gcc-workplace', 'configFile')
    oracleDir = cfg.get('gcc-workplace', 'oracledir')
    mianDir = cfg.get('gcc-workplace', 'maindir')
    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    exactoptimsDir = cfg.get('gcc-workplace', 'exactoptimdir')
    gcovpath = '/root/cfl/gccforme/r229639/r229639-build/bin/gcov'

    # debug执行时间
    debugTimeCnt = 0
    # search执行时间
    searchTimeCnt = 0
    # 收集一个覆盖信息的执行时间
    colcovTimeCnt = 0

    with open(sumFile, 'r') as f:
        sumlines = f.readlines()
    revisions = []
    bugIds = []
    rights = []
    wrongs = []
    checkpasses = []

    debugtimeFile = open(covinfoDir + '/debugtime.csv', 'w')

    for i in range(len(sumlines)):
        bugId = sumlines[i].strip().split(',')[0]
        revNum = sumlines[i].strip().split(',')[1]
        compilationOptionsRight = sumlines[i].strip().split(',')[2].replace('+', ' ')
        compilationOptionsWrong = sumlines[i].strip().split(',')[3].replace('+', ' ')
        # if bugId != '56478':
        #     continue

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

        optioncovpath = covinfoDir + 'test/' + bugId
        # if os.path.exists(optioncovpath):
        #     os.system('rm -r ' + optioncovpath)
        # os.system('mkdir ' + optioncovpath)
        if not os.path.exists(optioncovpath):
            os.system('mkdir -p ' + optioncovpath)

        os.chdir(optioncovpath)

        # 覆盖信息文件路径
        orifailCovPath = optioncovpath + '/orifail/testfileCov'
        rightLevelCovPath = optioncovpath + '/rightOptionBig/testfileCov'
        rightLevelCovAnalysis = optioncovpath + '/covAnalysis/rightOptionBig/testfileCov'
        wrongLevelCovPath = optioncovpath + '/wrongOptionBig/testfileCov'
        wrongLevelCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionBig/testfileCov'
        rightFlagCovPath = optioncovpath + '/rightOptionSmall/testfileCov'
        rightFlagCovAnalysis = optioncovpath + '/covAnalysis/rightOptionSmall/testfileCov'
        wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/testfileCov'
        wrongFlagCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionSmall/testfileCov'
        # determine whether the folder exists
        judge_dir()

        # 获取每个optimization level对应的exact optimization option
        O1_optimi, O2_optimi, O3_optimi, Os_optimi, O0_optimi = collect_optimi_flags()

        # The execution result of the program under right optimization
        rightres = get_result(revNum, prefixpath, failfile, compilationOptionsRight, compilationOptionsWrong)
        wrongres = get_result(revNum, prefixpath, failfile, compilationOptionsWrong, compilationOptionsWrong)
        if rightres == wrongres:
            print('ERROR: the wrong option and right option has the same result')
            sys.exit(1)

        # collect the info of compilation option
        rightoptLevelist, wrongoptLevelist = classify_optlevel()
        # print('rightoptLevelist : ' + str(rightoptLevelist))
        # print('wrongoptLevelist : ' + str(wrongoptLevelist))
        wrongOptimiSet = set()
        rightoptExactdict, wrongoptExactdict, spendTime = collect_right_optimi(rightoptLevelist, wrongoptLevelist)
        debugTimeCnt += spendTime
        print('debug time: ' + str(spendTime))
        debugtimeFile.write(bugId + ',' + revNum + ',' + str(spendTime) + '\n')
        debugtimeFile.flush()

        # for key in rightoptExactdict.keys():
        #     print(str(key) + ': ' + str(rightoptExactdict[key]))

        # get coverage of the program under wrong optimization
        # spendTime = collect_orifail()
        # colcovTimeCnt += spendTime

        # wrongcovpath = wrongFlagCovPath
        # for compilationOption in wrongoptExactdict.keys():
        #     flagOption = wrongoptExactdict[compilationOption] + rightoptExactdict[compilationOption]
        #     optimOption = compilationOption + ' ' + ' '.join(flagOption)
        #     res = get_result(revNum, prefixpath, failfile, optimOption, compilationOptionsWrong)
        #     if res == wrongres:
        #         pass
        #     elif res == rightres:
        #         # disable bug-free and enable bug-related flags
        #         wrongflagOption = wrongoptExactdict[compilationOption] # 所有的bugtrigger flags
        #         # wrongflagOption_ = wrongflagOption    # 初始化
        #         wrongoptimOption = compilationOption + ' ' + ' '.join(wrongflagOption)
        #         res = get_result(revNum, prefixpath, failfile, wrongoptimOption, compilationOptionsWrong)
        #         if res == wrongres:
        #             print(revNum + ' ' + bugId + ' disable all bug-free trigger and enable bug-related flags tigger the bug')
        #             bugTriggerIndex = [1] * len(flagOption)
        #             for flag in set(wrongflagOption):
        #                 bugTriggerIndex[flagOption.index(flag)] = 0
        #             print('wrong: ' + str(bugTriggerIndex))
        #             # covfilename = 'fail' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugTriggerIndex)
        #             # get_cov(revNum, prefixpath, gcovpath, wrongcovpath, failfile, covfilename, wrongoptimOption)
        #         elif res == rightres:
        #             print("******ERROR*******")
        #             # print(revNum + ' ' + bugId + ' disable all bug-free trigger and enable bug-related flags do not trigger the bug')
        #             # # 从多到少开始排列bugtrigger flags，知道能触发相同的bug
        #             # flagOption = wrongoptExactdict[compilationOption] + rightoptExactdict[compilationOption]
        #             # print('length of the flagOption is: ' + str(len(flagOption)))
        #             # recursion(compilationOption, flagOption, len(flagOption))
        #             # continue
                    
        #         # # disable bug-free and enable bug-related flags can trigger the bug, 
        #         # rightflagOption = rightoptExactdict[compilationOption]
        #         # rightcnt = 0
        #         # for i in range(len(rightflagOption)):
        #         #     flagCombins = combinations(rightflagOption, i + 1)
        #         #     if rightcnt > 30:
        #         #         break
        #         #     for flagCombin in flagCombins:
        #         #         flagOption_ = list(flagCombin)
        #         #         optimOption = wrongoptimOption + ' ' + ' '.join(flagOption_)
        #         #         res = get_result(revNum, prefixpath, failfile, optimOption, compilationOptionsWrong)
        #         #         if res == wrongres:
        #         #             print("wrong " + str(len(flagOption_)) + ' in ' + str(len(rightflagOption)) + ':')
        #         #             bugTriggerIndex = [1] * len(flagOption)
        #         #             for flag in set(wrongflagOption)|set(flagOption_):
        #         #                 bugTriggerIndex[flagOption.index(flag)] = 0
        #         #             print(str(bugTriggerIndex))
        #         #             covfilename = 'fail' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugTriggerIndex)
        #         #             # get_cov(revNum, prefixpath, gcovpath, wrongcovpath, failfile, covfilename, optimOption)
        #         #         elif res == rightres:
        #         #             print('right ' + str(len(flagOption_)) + ' in ' + str(len(rightflagOption)) + ':')
        #         #             bugFreeIndex = [1] * len(flagOption)
        #         #             for flag in set(wrongflagOption)|set(flagOption_):
        #         #                 bugFreeIndex[flagOption.index(flag)] = 0
        #         #             print(str(bugFreeIndex))
        #         #             covfilename = 'pass' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugFreeIndex)
        #         #             # get_cov(revNum, prefixpath, gcovpath, rightcovpath, failfile, covfilename, optimOption)
        #         #             rightcnt += 1

        # # collect the covinfo of orifail
        # for file in os.listdir(orifailCovPath):
        #     with open(orifailCovPath + '/' + file, 'r') as f:
        #         failcovlines = f.readlines()
        #     failset = set()
        #     for i in range(len(failcovlines)):
        #         filename = failcovlines[i].strip().split('$')[0]
        #         stmtlist = failcovlines[i].strip().split('$')[1].split(',')
        #         for j in range(len(stmtlist)):
        #             failset.add(filename + ':' + stmtlist[j])
        # existingcovset = dict()
        # unionCovwithFail = dict()

        # wrongoptExactdict, rightoptExactdict = optionDict()

        # collect_bigoption(rightoptLevelist, wrongoptLevelist)
        # # get coverage of small options
        # collect_smallrightoption(rightoptExactdict)
        
        # collect_smallwrongoption(wrongoptExactdict)
    # print('ave collcov time: ' + str(colcovTimeCnt/60))
        

