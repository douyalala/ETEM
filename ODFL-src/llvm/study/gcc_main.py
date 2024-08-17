'''
Author: your name
Date: 2021-07-20 04:05:16
LastEditTime: 2021-10-21 07:12:51
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc_main.py
'''

import os,sys
sys.path.append('/root/cfl/ODFL')
from gcc import metric
from gcc.metric import metrics
from gcc import rank
from configparser import ConfigParser
from multiprocessing import Pool
from gcc import *
def run(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile, i):
    print('Run task %s (%s)...' % (bugId, os.getpid()))
    os.system("taskset -p -c " + str(i) + " " + str(os.getpid()))
    # path = sys.path[0] + '/gcc/option_debug_improvewrong_copy.py'
    # path = sys.path[0] + '/gcc/optconfig.py' #最后的方法
    # path = sys.path[0] + '/gcc/option_study.py' # study flag type和数量对编译器覆盖信息的影响
    # path = sys.path[0] + '/gcc/optconfig_copy.py' #最后的方法
    path = sys.path[0] + '/coverage_line.py' #最后的方法 ODFL/gcc/study/coverage_line.py
    print(path)
    os.system('python3.6 -u ' + path + ' ' + revNum + ' ' + compilationOptionsRight + ' ' + compilationOptionsWrong + ' ' + checkpass + ' ' + configFile + ' ' + bugId + ' > ' + logDir + bugId + '.log 2>&1')
    # optiondebug(revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, configFile, bugId)

def run_fail(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile):
    print('Run task %s (%s)...' % (bugId, os.getpid()))
    
    path = sys.path[0] + '/gcc/GeneticAlgorithm.py'
    print(path)
    os.system('python3.6 -u ' + path + ' ' + revNum + ' ' + compilationOptionsRight + ' ' + compilationOptionsWrong + ' ' + checkpass + ' ' + configFile + ' ' + bugId + ' > ' + logDir + bugId + '.log 2>&1')

def multi_process(configFile, workplace):
    cfg = ConfigParser()
    cfg.read(configFile)
    compilerDir = cfg.get(workplace, 'configfile')
    sumFile = cfg.get(workplace, 'buglist')
    logDir = cfg.get(workplace, 'logdir_studyOptNum')
    # logDir = cfg.get(workplace, 'logdir_block')
    batch_num = cfg.getint('params', 'batch_num')

    if os.path.exists(logDir):
        # os.system('rm -r ' + logDir)
        # os.system('mkdir ' + logDir)
        pass
    else:
        os.system('mkdir ' + logDir)

    with open(sumFile, 'r') as f:
        sumlines = f.readlines()
    
    # p = Pool(processes = batch_num)
    p = Pool(processes = 2)
    for i in range(len(sumlines)):
        sumsplit = sumlines[i].strip().split(',')
        # if i != 0:
        #     continue
        bugId = sumsplit[0]
        revNum = sumsplit[1]
        compilationOptionsRight = sumsplit[2]
        compilationOptionsWrong = sumsplit[3]
        checkpass = sumsplit[4]
        if not (bugId == '57719' or bugId == '66894'):
            continue
        
        # if revNum == 'r247550' or revNum == 'r250895' or revNum == 'r251580' :
        #     p.apply_async(run, args=(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile))
        # else:
        #     continue
        # if bugId == '57303' or bugId == '61140' or bugId == '64853' or bugId == '65318' or bugId == '66863' or bugId == '66894' or bugId == '80622' or bugId == '82078' or bugId == '69951':
            # p.apply_async(run, args=(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile))
        p.apply_async(run, args=(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile, i))
        # p.apply_async(run_fail, args=(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile))
        # run(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile, i)
        # else:
        #     continue
    p.close()
    p.join()

if __name__ == '__main__':
    # configFile = write_workdir()
    # os.chdir(sys.path[0])
    cfg = ConfigParser()
    cfg.read('/root/cfl/ODFL/conf/config.ini')
    configFile = cfg.get('gcc-workplace', 'configFile')
    multi_process(configFile, 'gcc-workplace')
    compilerDir = cfg.get('gcc-workplace', 'compilersdir')
    sumFile = cfg.get("gcc-workplace", 'buglist')
    configFile = cfg.get('gcc-workplace', 'configFile')
    with open(sumFile, 'r') as f:
        sumlines = f.readlines()
    revisions = []
    bugIds = []
    rights = []
    wrongs = []
    checkpasses = []
    for i in range(len(sumlines)):
        bugIds.append(sumlines[i].strip().split(',')[0])
        revisions.append(sumlines[i].strip().split(',')[1])
        rights.append(sumlines[i].strip().split(',')[2])
        wrongs.append(sumlines[i].strip().split(',')[3])
        checkpasses.append(sumlines[i].strip().split(',')[4])
    # rank_file(revisions, bugIds, configFile)
    # # rank_block_file(revisions, bugIds, configFile)
    # analyze(configFile)
