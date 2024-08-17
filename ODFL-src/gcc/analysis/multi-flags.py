# 关闭On优化选项对应的小的优化选项，若关闭小的优化选项后程序从fail变成pass，比较关闭优化选项后的函数覆盖信息和之前的覆盖信息，保存具有相同覆盖信息的函数，可以用于排除。

# from Option.smalloptimoption.collect_optioninfo import *
import os
from random import choice
import time
import subprocess
import sys
import collections
import re
sys.path.append('/root/cfl/innovation/Option/smalloptimoption/file_isolation')
from collect_optioninfo import *
from configparser import ConfigParser
from itertools import combinations, combinations_with_replacement
from collections import OrderedDict

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

def collect_smallwrongoption(wrongoptExactdict):
    print('########collect small wrong option')
    covpath = wrongFlagCovPath
    cov_analysis = wrongFlagCovAnalysis
    if os.path.exists(covpath):
        os.system('rm -R ' + covpath)
        os.system('mkdir ' + covpath)
    else:
        os.system('mkdir ' + covpath)
    if os.path.exists(cov_analysis):
        os.system('rm -R ' + cov_analysis)
        os.system('mkdir ' + cov_analysis)
    else:
        os.system('mkdir ' + cov_analysis)
    for optlevel in wrongoptExactdict.keys():
        # compilationOption = optlevel[0]
        compilationOption = optlevel
        wrongoptExactSet = wrongoptExactdict[optlevel]
        if len(wrongoptExactSet) == 0:
            continue
        # for wrongopt in wrongoptExactSet:

        #     smalloptimOption = compilationOption + ' ' + wrongopt

        #     option = smalloptimOption.replace(' ', '+')
        #     print(smalloptimOption)
        #     # if len(option) > 150:
        #     #     optiontmp = option[0:3] + ''.join(random.sample(option, 20))
        #     # else:
        #     optiontmp = option
        #     # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, optiontmp, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
        #     get_cov(revNum, prefixpath, gcovpath, covpath, failfile, optiontmp, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
        #     diff_cov_wrong(cov_analysis, revNum, optioncovpath, covpath, compilationOptionsWrong, optiontmp)   # 比较fail和pass对应的覆盖信息完全一致的method，用于排除
        #     judge_buggymethods_in_diffmethods(cov_analysis, revNum, curpath, optiontmp) # 判断fail执行过而pass没有执行过的method信息
        if len(wrongoptExactSet) == 1:
            for smallopt in wrongoptExactSet:
                smalloptimOption = compilationOption + ' ' + smallopt

                option = smalloptimOption.replace(' ', '+')
                print(smalloptimOption)
                # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                get_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                # flagCovIsRepetitive = diff_pass_existing_cov(covpath, '/stmt_info_' + option +'.txt', failset, existingcovset, unionCovwithFail)
                # if flagCovIsRepetitive == 1:
                #     os.system('rm -rf ' + covpath + '/stmt_info_' + option +'.txt')
                #     print('flagCovIsRepetitive ##wrong cov ' + covpath + '/stmt_info_' + option +'.txt')
                #     continue
                # else:
                #     print('wrong small cov collect')
                #     diff_cov_wrong(cov_analysis, revNum, optioncovpath, covpath, compilationOptionsWrong, smalloptimOption)   # 比较fail和pass对应的覆盖信息完全一致的method，用于排除
                #     judge_buggymethods_in_diffmethods(cov_analysis, revNum, curpath, option) # 判断fail执行过而pass没有执行过的method信息
        elif len(wrongoptExactSet) <= 10:
            for combiNum in range(2, len(wrongoptExactSet) + 1):
                for flagCom in combinations(wrongoptExactSet, combiNum):
                    smalloptimOption = compilationOption + ' ' + ' '.join(flagCom)

                    option = smalloptimOption.replace(' ', '+')
                    if len(option) > 150:
                        option = option[0:3] + ''.join(random.sample(option, 20))
                    # else:
                    #     option = option
                    print(smalloptimOption)
                    # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                    get_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                    # flagCovIsRepetitive = diff_pass_existing_cov(covpath, '/stmt_info_' + option +'.txt', failset, existingcovset, unionCovwithFail)
                    # if flagCovIsRepetitive == 1:
                    #     os.system('rm -rf ' + covpath + '/stmt_info_' + option +'.txt')
                    #     print('flagCovIsRepetitive ##wrong cov ' + covpath + '/stmt_info_' + option +'.txt')
                    #     continue
                    # else:
                    #     print('wrong small cov collect')
                    #     diff_cov_wrong(cov_analysis, revNum, optioncovpath, covpath, compilationOptionsWrong, smalloptimOption)   # 比较fail和pass对应的覆盖信息完全一致的method，用于排除
                    #     judge_buggymethods_in_diffmethods(cov_analysis, revNum, curpath, option) # 判断fail执行过而pass没有执行过的method信息
        else:
            for combiNum in range(2, len(wrongoptExactSet) + 1):
                combiList = list(combinations(wrongoptExactSet, combiNum))
                if len(combiList) <= 10:
                    sampleCombi = combiList
                else:
                    sampleCombi = random.sample(combiList, 10)
                sampleCombi = random.sample(combiList, 10)
                for flagCom in sampleCombi:
                    smalloptimOption = compilationOption + ' ' + ' '.join(flagCom)

                    option = smalloptimOption.replace(' ', '+')
                    if len(option) > 150:
                        option = option[0:3] + ''.join(random.sample(option, 20))
                    # else:
                    #     option = option
                    print(smalloptimOption)
                    # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                    get_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)
       
        # smalloptimOption = compilationOption + ' ' + ' '.join(wrongoptExactSet)
        # option = smalloptimOption.replace(' ', '+')
        # print(smalloptimOption)
        # if len(option) > 150:
        #     optiontmp = option[0:3] + ''.join(random.sample(option, 20))
        # else:
        #     optiontmp = option
        # get_cov(revNum, prefixpath, gcovpath, covpath, failfile, optiontmp, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
        # diff_cov_wrong(cov_analysis, revNum, optioncovpath, covpath, compilationOptionsWrong, smalloptimOption, optiontmp)   # 比较fail和pass对应的覆盖信息完全一致的method，用于排除
        # judge_buggymethods_in_diffmethods(cov_analysis, revNum, curpath, optiontmp) # 判断fail执行过而pass没有执行过的method信息
        
        # flagCovIsRepetitive = diff_pass_existing_cov(covpath, '/stmt_info_' + option +'.txt', failset, existingcovset, unionCovwithFail)
        # if flagCovIsRepetitive == 1:
        #     os.system('rm -rf ' + covpath + '/stmt_info_' + option +'.txt')
        #     print('flagCovIsRepetitive ##wrong cov ' + covpath + '/stmt_info_' + option +'.txt')
        #     continue
        # else:
        #     print('wrong small cov collect')
        #     diff_cov_wrong(cov_analysis, revNum, optioncovpath, covpath, compilationOptionsWrong, smalloptimOption)   # 比较fail和pass对应的覆盖信息完全一致的method，用于排除
        #     judge_buggymethods_in_diffmethods(cov_analysis, revNum, curpath, option) # 判断fail执行过而pass没有执行过的method信息
    
    # if not wrongoptExactSet:# 该optlevel没有对应的wrong option
    #     continue
        

def collect_smallrightoption(rightoptExactdict):
    print("########collect small right option")
    covpath = rightFlagCovPath
    cov_analysis = rightFlagCovAnalysis
    if os.path.exists(covpath):
        os.system('rm -R ' + covpath)
        os.system('mkdir ' + covpath)
    else:
        os.system('mkdir ' + covpath)
    if os.path.exists(cov_analysis):
        os.system('rm -R ' + cov_analysis)
        os.system('mkdir ' + cov_analysis)
    else:
        os.system('mkdir ' + cov_analysis)

    for optlevel in rightoptExactdict.keys():
        compilationOption = optlevel
        rightoptExactSet = rightoptExactdict[optlevel]
        if len(rightoptExactSet) == 1:
            for smallopt in rightoptExactSet:
                smalloptimOption = compilationOption + ' ' + smallopt

                option = smalloptimOption.replace(' ', '+')
                print(smalloptimOption)
                # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                get_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                # flagCovIsRepetitive = diff_pass_existing_cov(covpath, '/stmt_info_' + option +'.txt', failset, existingcovset, unionCovwithFail)
                # if flagCovIsRepetitive == 1:
                #     os.system('rm -rf ' + covpath + '/stmt_info_' + option +'.txt')
                #     print('flagCovIsRepetitive ##right cov ' + covpath + '/stmt_info_' + option +'.txt')
                #     continue
                # else:
                #     print('right small cov collect')
                #     diff_cov_right(cov_analysis, revNum, optioncovpath, covpath, compilationOptionsWrong, smalloptimOption)   # 比较fail和pass对应的覆盖信息完全一致的method，用于排除
                #     judge_buggymethods_in_diffmethods(cov_analysis, revNum, curpath, option) # 判断fail执行过而pass没有执行过的method信息
        elif len(rightoptExactSet) <= 10:
            for combiNum in range(2, len(rightoptExactSet) + 1):
                for flagCom in combinations(rightoptExactSet, combiNum):
                    smalloptimOption = compilationOption + ' ' + ' '.join(flagCom)

                    option = smalloptimOption.replace(' ', '+')
                    if len(option) > 150:
                        option = option[0:3] + ''.join(random.sample(option, 20))
                    # else:
                    #     option = option
                    print(smalloptimOption)
                    # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                    get_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                    # flagCovIsRepetitive = diff_pass_existing_cov(covpath, '/stmt_info_' + option +'.txt', failset, existingcovset, unionCovwithFail)
                    # if flagCovIsRepetitive == 1:
                    #     os.system('rm -rf ' + covpath + '/stmt_info_' + option +'.txt')
                    #     print('flagCovIsRepetitive ##right cov ' + covpath + '/stmt_info_' + option +'.txt')
                    #     continue
                    # else:
                    #     print('right small cov collect')
                    #     diff_cov_right(cov_analysis, revNum, optioncovpath, covpath, compilationOptionsWrong, smalloptimOption)   # 比较fail和pass对应的覆盖信息完全一致的method，用于排除
                    #     judge_buggymethods_in_diffmethods(cov_analysis, revNum, curpath, option) # 判断fail执行过而pass没有执行过的method信息
        else:
            for combiNum in range(2, len(rightoptExactSet) + 1):
                combiList = list(combinations(rightoptExactSet, combiNum))
                if len(combiList) < 50:
                    sampleCombi = combiList
                else:
                    sampleCombi = random.sample(combiList, 50)
                for flagCom in sampleCombi:
                    smalloptimOption = compilationOption + ' ' + ' '.join(flagCom)

                    option = smalloptimOption.replace(' ', '+')
                    if len(option) > 150:
                        option = option[0:3] + ''.join(random.sample(option, 20))
                    # else:
                    #     option = option
                    print(smalloptimOption)
                    # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
                    get_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对
        if not rightoptExactSet:# 该optlevel没有对应的right option
            continue
              
            
def collect_bigoption(rightoptLevelist, wrongoptLevelist):
    # right option
    right_covpath = rightLevelCovPath
    right_cov_analysis = rightLevelCovAnalysis
    if os.path.exists(right_covpath):
        os.system('rm -R ' + right_covpath)
        os.system('mkdir  ' + right_covpath)
    else:
        os.system('mkdir  ' + right_covpath)
    if os.path.exists(right_cov_analysis):
        os.system('rm -R ' + right_cov_analysis)
        os.system('mkdir  ' + right_cov_analysis)
    else:
        os.system('mkdir  ' + right_cov_analysis)

    # wrong option
    wrong_covpath = wrongLevelCovPath
    wrong_cov_analysis = wrongLevelCovAnalysis
    if os.path.exists(wrong_covpath):
        os.system('rm -R ' + wrong_covpath)
        os.system('mkdir  ' + wrong_covpath)
    else:
        os.system('mkdir  ' + wrong_covpath)
    if os.path.exists(wrong_cov_analysis):
        os.system('rm -R ' + wrong_cov_analysis)
        os.system('mkdir  ' + wrong_cov_analysis)
    else:
        os.system('mkdir  ' + wrong_cov_analysis)

    for opt in rightoptLevelist:
        print("########collect big right option")
        print(opt)
        option = opt.replace(' ', '+')
        # get_block_cov(revNum, prefixpath, gcovpath, right_covpath, failfile, option, opt)
        get_cov(revNum, prefixpath, gcovpath, right_covpath, failfile, option, opt)
        flagCovIsRepetitive = diff_pass_existing_cov(right_covpath, '/stmt_info_' + option +'.txt', failset, existingcovset, unionCovwithFail)
        if flagCovIsRepetitive == 1:
            os.system('rm -rf ' + right_covpath + '/stmt_info_' + option +'.txt')
            print('flagCovIsRepetitive ##right cov ' + right_covpath + '/stmt_info_' + option +'.txt')
            continue
        else:
            print('right small cov collect')
            diff_cov_right(right_cov_analysis, revNum, optioncovpath, right_covpath, compilationOptionsWrong, option)
            judge_buggymethods_in_diffmethods(right_cov_analysis, revNum, curpath, option)
    for opt in wrongoptLevelist:
        print("########collect big wrong option")
        print(opt)
        if opt == compilationOptionsWrong: # 如果该编译选项与orifail编译选项相同，则跳转到下一个
            continue
        option = opt.replace(' ', '+')
        # get_block_cov(revNum, prefixpath, gcovpath, wrong_covpath, failfile, option, opt)
        get_cov(revNum, prefixpath, gcovpath, wrong_covpath, failfile, option, opt)
        flagCovIsRepetitive = diff_pass_existing_cov(wrong_covpath, '/stmt_info_' + option +'.txt', failset, existingcovset, unionCovwithFail)
        if flagCovIsRepetitive == 1:
            print('flagCovIsRepetitive ##wrong cov ' + wrong_covpath + '/stmt_info_' + option +'.txt')
            os.system('rm -rf ' + wrong_covpath + '/stmt_info_' + option +'.txt')
            continue
        else:
            print('wrong big cov collect')
            diff_cov_wrong(wrong_cov_analysis, revNum, optioncovpath, wrong_covpath, compilationOptionsWrong, option)
            judge_buggymethods_in_diffmethods(wrong_cov_analysis, revNum, curpath, option)


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
        elif tmpres == wrongres:
            wrongoptionlist.append(opt)
            if opt == compilationOptionsWrong: # 如果该编译选项与orifail编译选项相同，则跳转到下一个
                continue
    return rightoptionlist, wrongoptionlist
def collect_right_optimi(rightoptLevelist, wrongoptLevelist):
    rightDictFile = open(optioncovpath + '/right_exact_dict.txt', 'w')
    wrongDictFile = open(optioncovpath + '/wrong_exact_dict.txt', 'w')
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
        rightDictFile.write(compilationOption + '$' + ','.join(rightoptExactSet) + '\n')
        rightDictFile.flush()
        # if not rightoptExactSet:# 该optlevel没有对应的right option
        #     continue
        # for i in range(len(rightoptExactSet)): # 收集一个option level下的exact option的组合
        #     if i == 0:
        #         continue
        #     for combin in combinations(rightoptExactSet, i + 1):
        #         smallopt = ''
        #         for opt in combin:
        #             smallopt = smallopt + ' ' + opt
        #         smalloptimOption = compilationOption + ' ' + smallopt
        #         tmpres = get_result(revNum, prefixpath, failfile, smalloptimOption, compilationOptionsWrong)
        #         if tmpres == rightres: # 关闭small option后变成pass
        #             print(smalloptimOption)

        # get wrong optimization options
        if 'Os' in compilationOption:
            exact_set = Os_optimi - O1_optimi
        # elif len(wrongoptLevelist) == 1 or i == 0:
        # if 'O2' in compilationOption and 'Os' in rightoptLevelist[-1]:
        #     exact_set = O2_optimi - O1_optimi
        else:
            optimiOption_cur = re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption)
            
            exact_set = eval(optimiOption_cur + '_optimi') - eval(re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', rightoptLevelist[-1]) + '_optimi')
            if not exact_set:
                optimiOption_abo = 'O' + str(int(re.sub('O', '', optimiOption_cur)) - 1)
                exact_set = eval(optimiOption_cur + '_optimi') - eval(optimiOption_abo + '_optimi')
        # else:
        #     exact_set = eval(re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption)+ '_optimi') - eval(re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', wrongoptLevelist[i - 1]) + '_optimi')
        for smallopt in exact_set - tmpwrongOptSet:
            if smallopt.startswith('-fno'):
                smallopt = smallopt.replace('-fno-', '-f', 1)
            else:
                smallopt = smallopt.replace('-f', '-fno-', 1)
            wrongoptExactSet.add(smallopt)
        wrongoptTmpdict[compilationOption] = wrongoptExactSet
        wrongoptExactdict[compilationOption] = wrongoptExactSet
        wrongDictFile.write(compilationOption + '$' + ','.join(wrongoptExactSet) + '\n')
        wrongDictFile.flush()

    rightDictFile.close()
    wrongDictFile.close()
    return rightoptExactdict, wrongoptExactdict

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
    get_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, compilationOptionsWrong)
    # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, compilationOptionsWrong)

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

def analyze_opt(rightoptLevelist, wrongoptLevelist):
    rightoptLevelist_new = []
    wrongoptLevelist_new = []
    for every in rightoptLevelist:
        rightoptLevelist_new.append(every.replace(' ', '+'))
    for every in wrongoptLevelist:
        wrongoptLevelist_new.append(every.replace(' ', '+'))
        
    # with open(covinfoDir + 'optLevel.txt', 'a+') as optLevelFile:
    #     optLevelFile.write(bugId + ' ' + revNum + ' ' + compilationOptionsRight.replace(' ', '+') + ' ' +  compilationOptionsWrong.replace(' ', '+') + '\n')
    #     optLevelFile.write('rightoptLevelist :' + ','.join(rightoptLevelist_new) + '\n')
    #     optLevelFile.write('wrongoptLevelist :' + ','.join(wrongoptLevelist_new) + '\n')
    #     # optLevelFile.write('rightoptLevelist : ' + str(rightoptLevelist) + '\n')
    #     # optLevelFile.write('wrongoptLevelist : ' + str(wrongoptLevelist) + '\n')
    #     if compilationOptionsWrong == wrongoptLevelist[0]:
    #         optLevelFile.write('Yes\n')
    #     else:
    #         optLevelFile.write('No\n')
    with open(covinfoDir + 'optError.txt', 'a+') as optLevelFile:
        # optLevelFile.write('rightoptLevelist : ' + str(rightoptLevelist) + '\n')
        # optLevelFile.write('wrongoptLevelist : ' + str(wrongoptLevelist) + '\n')
        if compilationOptionsWrong == wrongoptLevelist[0]:
            pass
        else:
            optLevelFile.write(bugId + ' ' + revNum + ' ' + compilationOptionsRight.replace(' ', '+') + ' ' +  compilationOptionsWrong.replace(' ', '+') + '\n')
            optLevelFile.write('rightoptLevelist :' + ','.join(rightoptLevelist_new) + '\n')
            optLevelFile.write('wrongoptLevelist :' + ','.join(wrongoptLevelist_new) + '\n')
            optLevelFile.write('No\n')


if __name__ == '__main__':
    revNum = sys.argv[1]
    compilationOptionsRight = sys.argv[2].replace('+',' ')
    compilationOptionsWrong = sys.argv[3].replace('+',' ')
    checkpass = sys.argv[4]
    configFile = sys.argv[5]
    bugId = sys.argv[6]
    
    cfg = ConfigParser()
    cfg.read(configFile)

    gcovpath = '/root/cfl/gccforme/r229639/r229639-build/bin/gcov'
    # r237156
    
    compilerDir = cfg.get('gcc-workplace', 'compilersdir')
    oracleDir = cfg.get('gcc-workplace', 'oracledir')
    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    mianDir = cfg.get('gcc-workplace', 'maindir')
    exactoptimsDir = cfg.get('gcc-workplace', 'exactoptimdir')

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
    orifailCovPath = optioncovpath + '/orifail/testfileCov'
    rightLevelCovPath = optioncovpath + '/rightOptionBig/testfileCov'
    rightLevelCovAnalysis = optioncovpath + '/covAnalysis/rightOptionBig/testfileCov'
    wrongLevelCovPath = optioncovpath + '/wrongOptionBig/testfileCov'
    wrongLevelCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionBig/testfileCov'
    rightFlagCovPath = optioncovpath + '/rightOptionSmall/multifileCov'
    rightFlagCovAnalysis = optioncovpath + '/covAnalysis/rightOptionSmall/multifileCov'
    wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/multifileCov'
    wrongFlagCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionSmall/multifileCov'
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
    # analyze_opt(rightoptLevelist, wrongoptLevelist)
    # # print('rightoptLevelist : ' + str(rightoptLevelist))
    # # print('wrongoptLevelist : ' + str(wrongoptLevelist))
    # wrongOptimiSet = set()
    # rightoptExactdict, wrongoptExactdict = collect_right_optimi(rightoptLevelist, wrongoptLevelist)
    # for key in rightoptExactdict.keys():
    #     print(str(key) + ': ' + str(rightoptExactdict[key]))

    # get coverage of the program under wrong optimization
    # collect_orifail()

    # collect the covinfo of orifail
    for file in os.listdir(orifailCovPath):
        with open(orifailCovPath + '/' + file, 'r') as f:
            failcovlines = f.readlines()
        failset = set()
        for i in range(len(failcovlines)):
            filename = failcovlines[i].strip().split('$')[0]
            stmtlist = failcovlines[i].strip().split('$')[1].split(',')
            for j in range(len(stmtlist)):
                failset.add(filename + ':' + stmtlist[j])
    existingcovset = dict()
    unionCovwithFail = dict()

    wrongoptExactdict, rightoptExactdict = optionDict()

    # collect_bigoption(rightoptLevelist, wrongoptLevelist)
    # get coverage of small options
    # collect_smallrightoption(rightoptExactdict)
    
    collect_smallwrongoption(wrongoptExactdict)
        
    
    


    