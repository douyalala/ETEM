# 关闭On优化选项对应的小的优化选项，若关闭小的优化选项后程序从fail变成pass，比较关闭优化选项后的函数覆盖信息和之前的覆盖信息，保存具有相同覆盖信息的函数，可以用于排除。

# from Option.smalloptimoption.collect_optioninfo import *
import os
import time
import subprocess
import sys
import collections
import re
# sys.path.append('/root/cfl/innovation/Option/smalloptimoption/file_isolation')
from collect_optioninfo import *
from configparser import ConfigParser
from itertools import combinations, combinations_with_replacement
from collections import OrderedDict

rightcnt_single = 0
rightcnt_all = 0
wrongcnt = 0

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


def collect_smallwrongoption(wrongoptExactdict):
    print('########collect small wrong option')
    covpath = wrongFlagCovPath
    if os.path.exists(covpath):
        os.system('rm -R ' + covpath)
        os.system('mkdir ' + covpath)
    else:
        os.system('mkdir ' + covpath)

    for optlevel in wrongoptExactdict.keys():
        # compilationOption = optlevel[0]
        compilationOption = optlevel
        wrongoptExactSet = wrongoptExactdict[optlevel]
        if len(wrongoptExactSet) == 0:
            continue
        for wrongopt in wrongoptExactSet:
            smalloptimOption = compilationOption + ' ' + wrongopt
            option = smalloptimOption.replace(' ', '+')
            print(smalloptimOption)
            # if len(option) > 150:
            #     optiontmp = option[0:3] + ''.join(random.sample(option, 20))
            # else:
            optiontmp = option
            # get_block_cov(revNum, prefixpath, gcovpath, covpath, failfile, optiontmp, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
            get_cov(revNum, prefixpath, gcovpath, covpath, failfile, optiontmp, smalloptimOption)  # 得到小优化选项对应的method覆盖信息：method某行对应执行多少次
        
        
def collect_smallrightoption(rightoptExactdict):
    print("########collect small right option")
    covpath = rightFlagCovPath
    if os.path.exists(covpath):
        os.system('rm -R ' + covpath)
        os.system('mkdir ' + covpath)
    else:
        os.system('mkdir ' + covpath)

    # optlevel是大-Ox选项
    for optlevel in rightoptExactdict.keys():
        compilationOption = optlevel
        
        # 这里是取了这个大O选项的bug-related选项
        rightoptExactSet = rightoptExactdict[optlevel]
        
        # 一个一个加到大O选项上
        for smallopt in rightoptExactSet:
            smalloptimOption = compilationOption + ' ' + smallopt

            option = smalloptimOption.replace(' ', '+')
            print(smalloptimOption)
            get_cov(revNum, prefixpath, gcovpath, covpath, failfile, option, smalloptimOption)       
        if not rightoptExactSet:# 该optlevel没有对应的right option
            continue
              
            
def collect_bigoption(rightoptLevelist, wrongoptLevelist):
    # right option
    right_covpath = rightLevelCovPath
    if os.path.exists(right_covpath):
        os.system('rm -R ' + right_covpath)
        os.system('mkdir  ' + right_covpath)
    else:
        os.system('mkdir  ' + right_covpath)

    # wrong option
    wrong_covpath = wrongLevelCovPath
    if os.path.exists(wrong_covpath):
        os.system('rm -R ' + wrong_covpath)
        os.system('mkdir  ' + wrong_covpath)
    else:
        os.system('mkdir  ' + wrong_covpath)

    for opt in rightoptLevelist:
        print("########collect big right option")
        print(opt)
        option = opt.replace(' ', '+')
        get_cov(revNum, prefixpath, gcovpath, right_covpath, failfile, option, opt)
        # flagCovIsRepetitive = diff_pass_existing_cov(right_covpath, '/stmt_info_' + option +'.txt', failset, existingcovset, unionCovwithFail)
        flagCovIsRepetitive = 0
        if flagCovIsRepetitive == 1:
            os.system('rm -rf ' + right_covpath + '/stmt_info_' + option +'.txt')
            print('flagCovIsRepetitive ##right cov ' + right_covpath + '/stmt_info_' + option +'.txt')
            continue
        else:
            print('right small cov collect')
    for opt in wrongoptLevelist:
        print("########collect big wrong option")
        print(opt)
        if opt == compilationOptionsWrong: 
            continue
        option = opt.replace(' ', '+')
        get_cov(revNum, prefixpath, gcovpath, wrong_covpath, failfile, option, opt)
        # flagCovIsRepetitive = diff_pass_existing_cov(wrong_covpath, '/stmt_info_' + option +'.txt', failset, existingcovset, unionCovwithFail)
        flagCovIsRepetitive = 0
        if flagCovIsRepetitive == 1:
            print('flagCovIsRepetitive ##wrong cov ' + wrong_covpath + '/stmt_info_' + option +'.txt')
            os.system('rm -rf ' + wrong_covpath + '/stmt_info_' + option +'.txt')
            continue
        else:
            print('wrong big cov collect')

# 查看所有大的选项-Ox，哪些会导致错误，哪些会正确
def classify_optlevel():
    optionlist = ['-O0', '-O1', '-O2', '-Os', '-O3']
    optionlist_ = []
    rightoptionlist = []  # 为保证optimization level的顺序，使用list数据结构
    wrongoptionlist = []
    
    # 构建optionlist_: 将optionlist里面-O2 -w -m32这样的多个编译选项，把其中-O的优化选项替换掉，例如替换成：-O0 -w -m32
    for opt in optionlist:
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

    # 查看所有这样大的选项-Ox哪些会导致错误，哪些会正确
    for opt in optionlist_:
        tmpres = get_result(revNum, prefixpath, failfile, opt, compilationOptionsWrong)
        if tmpres == rightres:
            rightoptionlist.append(opt)
        elif tmpres == wrongres:
            wrongoptionlist.append(opt)
            if opt == compilationOptionsWrong: # 如果该编译选项与orifail编译选项相同，则跳转到下一个
                continue
    return rightoptionlist, wrongoptionlist

# 找反转的bug-related(rightopt...)
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
        # eval(re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption) + '_optimi') 其实就是对应的 O1_optimi, O2_optimi, O3_optimi, Os_optimi, O0_optimi
        for smallopt in eval(re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption) + '_optimi'):
            # 分别反转每个选项，查看结果是否发生变化
            if smallopt.startswith('-fno'):
                smallopt = smallopt.replace('-fno-', '-f', 1)
            else:
                smallopt = smallopt.replace('-f', '-fno-', 1)
            smalloptimOption = compilationOption + ' ' + smallopt
            tmpres = get_result(revNum, prefixpath, failfile, smalloptimOption, compilationOptionsWrong)
            
            # 关闭small option后变成pass：bug-related
            if tmpres == rightres: 
                rightoptExactSet.add(smallopt)
                if smallopt.startswith('-fno'):
                    smallopt = smallopt.replace('-fno-', '-f', 1)
                else:
                    smallopt = smallopt.replace('-f', '-fno-', 1)
                tmpwrongOptSet.add(smallopt)
        
        rightoptExactdict[compilationOption] = rightoptExactSet # 每个大选项对应的bug-related
        rightDictFile.write(compilationOption + '$' + ','.join(rightoptExactSet) + '\n')
        rightDictFile.flush()
    
        # get wrong optimization options
        # 中间的细粒度选项 = 这个触发bug选项-最大不触发bug选项
        if 'Os' in compilationOption:
            exact_set = Os_optimi - O1_optimi
        else:
            optimiOption_cur = re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', compilationOption)
            
            exact_set = eval(optimiOption_cur + '_optimi') - eval(re.sub('-g|-c|-m[0-9]+|-w|\s|-', '', rightoptLevelist[-1]) + '_optimi')
            if not exact_set:
                optimiOption_abo = 'O' + str(int(re.sub('O', '', optimiOption_cur)) - 1)
                exact_set = eval(optimiOption_cur + '_optimi') - eval(optimiOption_abo + '_optimi')
                
        # bug_free = 中间的选项-bug_related 
        # 关闭所有bug_free选项：更可能触发bug
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

def optionDict():
    print(optioncovpath)
    
    # 关掉的 bug-free
    with open(optioncovpath + '/wrong_exact_dict.txt', 'r') as f:
        wronglines = f.readlines()
    combinNum = OrderedDict()
    wrongoptExactdict = OrderedDict()
    for i in range(len(wronglines)):
        print(wronglines[i])
        compilationOption = wronglines[i].strip().split('$')[0]
        wrongoptExactList = wronglines[i].strip().split('$')[1].split(',')
        wrongoptExactdict[compilationOption] = wrongoptExactList

    # 开开的 bug-related
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

# from passing find failing
def recursion(compilationOption, flagOption, num, startTime):
    global rightcnt_single
    global rightcnt_all
    global wrongcnt
    if num == 0:
        return

    # 找bug-free的集合，一个一个集合的开开这些选项
    # 这里搜的是仍然关闭的bf选项，所以是从大往小搜
    flagCombins = combinations(flagOption, num)
    flag = 0
    # 遍历上述组合
    for flagCombin in flagCombins:
        endTime = time.time()
        useTime = endTime - startTime
        if useTime > 3600 and wrongcnt == 0:
            return
        if useTime > 3600*1.5 and wrongcnt >= 2:
            return
        flagOption_ = list(flagCombin)
        optimOption = compilationOption + ' ' + ' '.join(flagOption_)
        res = get_result(revNum, prefixpath, failfile, optimOption, compilationOptionsWrong)
        if res != rightres: # fail：我们希望的，现在开始往下搜pass
            rightcnt_single = 0
            wrongcnt += 1
            flag = 1
            
            bugTriggerSet = set(flagOption) - set(flagOption_)
            # 在{num}个bf选项关闭的时候搜到了wrong，这些bf选项是{flagOption_}
            print('wrong-' + str(num))
            print(f'bugTriggerSet: {bugTriggerSet}')
            
            # 现在真正的开了的选项是：bugTriggerSet + br选项，收集这个fail的cov
            bugTriggerSet = set(flagOption) - set(flagOption_)
            bugTriggerIndex = [1] * len(flagOptionall)
            for flag in flagOption_:
                bugTriggerIndex[flagOptionall.index(flag)] = 0
            covfilename = 'fail' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugTriggerIndex)
            get_cov(revNum, prefixpath, gcovpath, wrongcovpath, failfile, covfilename, optimOption)
            
            if rightcnt_all > 50:
                continue
            
            # 从n个bugTriggerSet元素中筛选n-1个
            # enabledSet：现在真正的开了的选项是：bugTriggerSet + br选项，从这里往下搜
            enabledSet = bugTriggerSet | set(rightoptExactdict[compilationOption])
            for combin_num in range(1, len(enabledSet) +1):
                subbugTriggerSets = combinations(enabledSet, combin_num)
                if rightcnt_single > 30:
                    break
                for subbugTriggerSet in subbugTriggerSets:
                    # 在wrong集合optimOption的基础上加subbugTriggerSet
                    if rightcnt_single > 30:
                        break
                    rightoptimOption = optimOption + ' ' + ' '.join(subbugTriggerSet)
                    res = get_result(revNum, prefixpath, failfile, rightoptimOption, compilationOptionsWrong)
                    if res == rightres: # pass，收集cov
                        rightcnt_single += 1
                        print('use the subset: ' + str(subbugTriggerSet) + ' from fail to pass')
                        subbugTriggerIndex = bugTriggerIndex
                        for flag in subbugTriggerSet:
                            subbugTriggerIndex[flagOptionall.index(flag)] = 0
                        covfilename = 'pass' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in subbugTriggerIndex)
                        print(f'opt:{rightoptimOption}')
                        print(f'covfilename:{covfilename}')
                        get_cov(revNum, prefixpath, gcovpath, rightcovpath, failfile, covfilename, rightoptimOption)
                    else: # fail，这种不要
                        print('##use the subset: ' + str(subbugTriggerSet) + ' not from fail to pass')

            rightcnt_all += rightcnt_single

        elif res == rightres: # pass：继续向上搜fail
            pass

    else:
        if flag != 0:
            return
        else:
            recursion(compilationOption, flagOption, num - 1, startTime)


if __name__ == '__main__':
    revNum = sys.argv[1]
    compilationOptionsRight = sys.argv[2].replace('+',' ')
    compilationOptionsWrong = sys.argv[3].replace('+',' ')
    checkpass = sys.argv[4]
    configFile = sys.argv[5]
    bugId = sys.argv[6]
    
    cfg = ConfigParser()
    cfg.read(configFile)

    gcovpath = 'gcov'
    
    compilerDir = cfg.get('gcc-workplace', 'compilersdir')
    oracleDir = cfg.get('gcc-workplace', 'oracledir')
    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    mianDir = cfg.get('gcc-workplace', 'maindir')
    exactoptimsDir = cfg.get('gcc-workplace', 'exactoptimdir')

    print(revNum + ' ' + bugId)

    prefixpath = compilerDir + '/' + revNum
    covdir = prefixpath + '-build'
    oraclepath = oracleDir + bugId
    curpath = mianDir + '/gcc'
    failfile = oraclepath + '/fail.c'
    gccpath = prefixpath + '-build/bin/gcc'
    gccbuildpath = prefixpath+'-build/gcc'
    covdir = prefixpath+'-build'

    optioncovpath = covinfoDir + bugId
    if not os.path.exists(optioncovpath):
        os.system('mkdir ' + optioncovpath)

    os.chdir(optioncovpath)

    # 覆盖信息文件路径
    orifailCovPath = optioncovpath + '/orifail/testfileCov'
    rightLevelCovPath = optioncovpath + '/rightOptionBig/testfileCov'
    wrongLevelCovPath = optioncovpath + '/wrongOptionBig/testfileCov'
    rightFlagCovPath = optioncovpath + '/rightOptionSmall/dismixCov2'
    wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/dismixCov2'
    # 生成需要的文件夹路径
    judge_dir()

    # 获取每个optimization level对应的exact optimization option
    O1_optimi, O2_optimi, O3_optimi, Os_optimi, O0_optimi = collect_optimi_flags()

    # collect_optioninfo.py
    # 获取初始fail pass的运行结果
    rightres = get_result(revNum, prefixpath, failfile, compilationOptionsRight, compilationOptionsWrong)
    wrongres = get_result(revNum, prefixpath, failfile, compilationOptionsWrong, compilationOptionsWrong)
    if rightres == wrongres:
        print('ERROR: the wrong option and right option has the same result')
        sys.exit(1)

    # 查看所有大的选项-Ox，哪些会导致错误，哪些会正确
    rightoptLevelist, wrongoptLevelist = classify_optlevel()
    print('rightoptLevelist : ' + str(rightoptLevelist))
    print('wrongoptLevelist : ' + str(wrongoptLevelist))
    wrongOptimiSet = set() # 没用过？
    
    # 反转的bug-related(rightoptExactdict)
    rightoptExactdict, wrongoptExactdict = collect_right_optimi(rightoptLevelist, wrongoptLevelist)
    for key in rightoptExactdict.keys():
        print(str(key) + ': ' + str(rightoptExactdict[key])) # bug-related

    # get coverage of the program under wrong optimization
    # 收集初始错误选项的cov
    collect_orifail()

    # 收集大-Ox选项cov，分为right和wrong
    collect_bigoption(rightoptLevelist, wrongoptLevelist)
    
    # # 没用，后面直接删了
    # # get coverage of small options
    # # 大O选项，一个一个分别 + bug-related选项
    # collect_smallrightoption(rightoptExactdict)

    # 读取了：rightoptExactdict, wrongoptExactdict = collect_right_optimi(rightoptLevelist, wrongoptLevelist)，干的事情
    wrongcovpath = wrongFlagCovPath
    if os.path.exists(wrongcovpath):
        os.system('rm -R ' + wrongcovpath)
        os.system('mkdir  ' + wrongcovpath)
    else:
        os.system('mkdir  ' + wrongcovpath)
    
    rightcovpath = rightFlagCovPath
    if os.path.exists(rightcovpath):
        os.system('rm -R ' + rightcovpath)
        os.system('mkdir  ' + rightcovpath)
    else:
        os.system('mkdir  ' + rightcovpath)
    wrongoptExactdict, rightoptExactdict = optionDict()

    # 重新算了wrongoptExactdict：这次bug-free=大选项对应的小选项反转 - bug-related 
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
        # 反转的bug-free（wrongoptExactdict）
        wrongoptExactdict[compilationOption] = list(alloptset - set(rightoptExactdict[compilationOption]))

    # disabe to enable
    # disable all bug-free and bug-related flags
    debugtimeFile = open(covinfoDir + '/searchtime_cpu.csv', 'a')
    lowestOptList = []
    lowestOptList.append(list(wrongoptExactdict.keys())[0])
    # lowestOptList: 导致错误的大O选项里最小的那个
    print(f'lowestOptList: {lowestOptList}')
    
    startTime = time.time()
    for compilationOption in lowestOptList:
        # flagOptionall：所有反转的选项
        flagOptionall = list(alloptset)
        
        # 关掉所有选项，算出结果
        optimOption = compilationOption + ' ' + ' '.join(flagOptionall)
        print(f'optimOption: {optimOption}')
        res = get_result(revNum, prefixpath, failfile, optimOption, compilationOptionsWrong)
        if res != rightres:
            print('disable all also tiggers the bug')
            pass

        # 关掉所有选项是right：很正常的情况，所以继续
        elif res == rightres:
            # disable bug-free and enable bug-related flags
            # 在大O基础上关掉所有bug-free选项（也就是打开所有bug-related选项）：期待出错
            wrongflagOption = wrongoptExactdict[compilationOption] # 所有的bugtrigger flags（关掉的bug-free）
            wrongoptimOption = compilationOption + ' ' + ' '.join(wrongflagOption)
            res = get_result(revNum, prefixpath, failfile, wrongoptimOption, compilationOptionsWrong)
            
            print(f'disable bf: {wrongoptimOption}')
            
            # 关bug-free，开bug-related：出错了
            if res != rightres:
                wrongcnt += 1 # 找到错误+1
                print(revNum + ' ' + bugId + ' disable all bug-free trigger and enable bug-related flags tigger the bug')
                
                # 建立了一个都是1的，长度为所有细分选项的数组：这个数组1代表选项开开，0代表关上，作为以后每个选项配置的id
                bugTriggerIndex = [1] * len(flagOptionall)
                for flag in set(wrongflagOption):
                    bugTriggerIndex[flagOptionall.index(flag)] = 0 # 关掉的bug-free选项在数组里面标记为0
                print('wrong: ' + str(bugTriggerIndex))
                # 收集这个fail的cov
                covfilename = 'fail' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugTriggerIndex)
                get_cov(revNum, prefixpath, gcovpath, wrongcovpath, failfile, covfilename, wrongoptimOption)
                
            # 关bug-free，开bug-related：没出错
            elif res == rightres:
                print('right***ERROR')
                print(revNum + ' ' + bugId + ' disable all bug-free trigger and enable bug-related flags do not trigger the bug')
                flagOption = wrongoptExactdict[compilationOption]
                print('length of the flagOption is: ' + str(len(flagOption)))
                # 开始向上找fail
                recursion(compilationOption, flagOption, len(flagOption)-1, startTime)
                continue

            # 找到的pass>50个就停止，防止太多的pass影响
            if rightcnt_all > 50:
                continue
            
            # 仅当：关bug-free，开bug-related：出错，才可执行到这里
            # 搜索i个元素组成的bug-related集合，看看 pass 还是 fail
            # disable bug-free and enable bug-related flags can trigger the bug, 
            rightcnt_single = 0
            rightflagOption = rightoptExactdict[compilationOption] # 关掉的bug-related
            for i in range(len(rightflagOption)):
                flagCombins = combinations(rightflagOption, i + 1) # 从rightflagOption里面找大小为i+1的所有集合
                if rightcnt_single > 50:  # 找到的pass>50个就停止，防止太多的pass影响
                    break
                for flagCombin in flagCombins: # 对于每个集合，关掉里面的bug-related选项，试图找pass
                    flagOption_ = list(flagCombin)
                    optimOption = wrongoptimOption + ' ' + ' '.join(flagOption_)
                    res = get_result(revNum, prefixpath, failfile, optimOption, compilationOptionsWrong)
                    if res != rightres: # fail
                        wrongcnt += 1
                        print("wrong " + str(len(flagOption_)) + ' in ' + str(len(rightflagOption)) + ':' +f'{flagOption_}')
                        bugTriggerIndex = [1] * len(flagOptionall)
                        for flag in set(wrongflagOption)|set(flagOption_):
                            bugTriggerIndex[flagOptionall.index(flag)] = 0
                        print(str(bugTriggerIndex))
                        covfilename = 'fail' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugTriggerIndex)
                        get_cov(revNum, prefixpath, gcovpath, wrongcovpath, failfile, covfilename, optimOption)
                    elif res == rightres: # pass
                        print('right ' + str(len(flagOption_)) + ' in ' + str(len(rightflagOption)) + ':'+ f'{flagOption_}')
                        bugFreeIndex = [1] * len(flagOptionall)
                        for flag in set(wrongflagOption)|set(flagOption_):
                            bugFreeIndex[flagOptionall.index(flag)] = 0
                        print(str(bugFreeIndex))
                        covfilename = 'pass' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugFreeIndex)
                        get_cov(revNum, prefixpath, gcovpath, rightcovpath, failfile, covfilename, optimOption)
                        rightcnt_single += 1
            rightcnt_all += rightcnt_single
    
    noallFreeflag = 0
    # 如果一个fail都没找到，上面的再来一次，但是这次包含的只有中间的细分选项
    if wrongcnt == 0:
        noallFreeflag = 1
        startTime = time.time()
        wrongoptExactdict, rightoptExactdict = optionDict()

        for compilationOption in lowestOptList:
            flagOptionall = wrongoptExactdict[compilationOption] + rightoptExactdict[compilationOption]
            optimOption = compilationOption + ' ' + ' '.join(flagOptionall)
            res = get_result(revNum, prefixpath, failfile, optimOption, compilationOptionsWrong)
            if res != rightres:
                pass
            elif res == rightres: # 关掉所有选项，pass
                # disable bug-free and enable bug-related flags
                wrongflagOption = wrongoptExactdict[compilationOption] # 所有的bugtrigger flags
                wrongoptimOption = compilationOption + ' ' + ' '.join(wrongflagOption)
                res = get_result(revNum, prefixpath, failfile, wrongoptimOption, compilationOptionsWrong)
                if res != rightres: # fail
                    wrongcnt += 1
                    print(revNum + ' ' + bugId + ' disable all bug-free trigger and enable bug-related flags tigger the bug')
                    bugTriggerIndex = [1] * len(flagOptionall)
                    for flag in set(wrongflagOption):
                        bugTriggerIndex[flagOptionall.index(flag)] = 0
                    print('wrong: ' + str(bugTriggerIndex))
                    covfilename = 'fail' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugTriggerIndex)
                    get_cov(revNum, prefixpath, gcovpath, wrongcovpath, failfile, covfilename, wrongoptimOption)
                elif res == rightres: # pass
                    print('right***ERROR')
                    print(revNum + ' ' + bugId + ' disable all bug-free trigger and enable bug-related flags do not trigger the bug')
                    # 从多到少开始排列bugtrigger flags，知道能触发相同的bug
                    flagOption = wrongoptExactdict[compilationOption]
                    print('length of the flagOption is: ' + str(len(flagOption)))
                    recursion(compilationOption, flagOption, len(flagOption)-1, startTime)
                    continue
                if rightcnt_all > 50:
                    continue
                rightcnt_single = 0
                
                # disable bug-free and enable bug-related flags can trigger the bug, 
                rightflagOption = rightoptExactdict[compilationOption]
                
                for i in range(len(rightflagOption)):
                    flagCombins = combinations(rightflagOption, i + 1)
                    if rightcnt_single > 50:
                        break
                    for flagCombin in flagCombins:
                        flagOption_ = list(flagCombin)
                        optimOption = wrongoptimOption + ' ' + ' '.join(flagOption_)
                        res = get_result(revNum, prefixpath, failfile, optimOption, compilationOptionsWrong)
                        if res != rightres:
                            wrongcnt += 1
                            print("wrong " + str(len(flagOption_)) + ' in ' + str(len(rightflagOption)) + ':')
                            bugTriggerIndex = [1] * len(flagOptionall)
                            for flag in set(wrongflagOption)|set(flagOption_):
                                bugTriggerIndex[flagOptionall.index(flag)] = 0
                            print(str(bugTriggerIndex))
                            covfilename = 'fail' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugTriggerIndex)
                            get_cov(revNum, prefixpath, gcovpath, wrongcovpath, failfile, covfilename, optimOption)
                        elif res == rightres:
                            print('right ' + str(len(flagOption_)) + ' in ' + str(len(rightflagOption)) + ':')
                            bugFreeIndex = [1] * len(flagOptionall)
                            for flag in set(wrongflagOption)|set(flagOption_):
                                bugFreeIndex[flagOptionall.index(flag)] = 0
                            print(str(bugFreeIndex))
                            covfilename = 'pass' + compilationOption.replace(' ', '+') + '_' + ''.join(str(index) for index in bugFreeIndex)
                            get_cov(revNum, prefixpath, gcovpath, rightcovpath, failfile, covfilename, optimOption)
                            rightcnt_single += 1
                rightcnt_all += rightcnt_single
    
    # 计算时间
    if noallFreeflag == 1:
        endTime = time.time() + 3600
    else:
        endTime = time.time()
    spendTime = endTime - startTime
    print('search time: ' + str(spendTime))
    debugtimeFile.write(bugId + ',' + revNum + ',' + str(spendTime) + '\n')
    debugtimeFile.flush()    