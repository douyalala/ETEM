'''
Author: your name
Date: 2021-09-08 08:17:14
LastEditTime: 2021-09-09 07:52:37
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/analysis/main.py
'''
'''
Author: your name
Date: 2021-07-20 04:05:16
LastEditTime: 2021-09-07 13:40:29
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc_main.py
'''
# from gcc import metric
# from gcc.metric import metrics
# from gcc import rank
import os,sys
from configparser import ConfigParser
from multiprocessing import Pool
# from gcc import *
def run(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile):
    print('Run task %s (%s)...' % (bugId, os.getpid()))
    
    path = sys.path[0] + '/multi-flags.py'
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
    logDir = cfg.get(workplace, 'logdir_multiright')
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
    
    p = Pool(processes = batch_num)
    for i in range(len(sumlines)):
        sumsplit = sumlines[i].strip().split(',')
        bugId = sumsplit[0]
        revNum = sumsplit[1]
        compilationOptionsRight = sumsplit[2]
        compilationOptionsWrong = sumsplit[3]
        checkpass = sumsplit[4]
        # if bugId == '58539' or bugId == '68990' or bugId == '57521' :
        #     p.apply_async(run, args=(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile))
        # else:
        #     continue
        
        p.apply_async(run, args=(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile))
        # p.apply_async(run_fail, args=(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile))
            # run(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile)
        # else:
        #     continue
    p.close()
    p.join()

if __name__ == '__main__':
    # configFile = write_workdir()
    os.chdir(sys.path[0])
    cfg = ConfigParser()
    cfg.read('../../conf/config.ini')
    configFile = cfg.get('gcc-workplace', 'configFile')
    multi_process(configFile, 'gcc-workplace')
    # compilerDir = cfg.get('gcc-workplace', 'configfile')
    # sumFile = cfg.get("gcc-workplace", 'buglist')
    # configFile = cfg.get('gcc-workplace', 'configFile')
    # with open(sumFile, 'r') as f:
    #     sumlines = f.readlines()
    # revisions = []
    # bugIds = []
    # rights = []
    # wrongs = []
    # checkpasses = []
    # for i in range(len(sumlines)):
    #     bugIds.append(sumlines[i].strip().split(',')[0])
    #     revisions.append(sumlines[i].strip().split(',')[1])
    #     rights.append(sumlines[i].strip().split(',')[2])
    #     wrongs.append(sumlines[i].strip().split(',')[3])
    #     checkpasses.append(sumlines[i].strip().split(',')[4])
    # rank_file(revisions, bugIds, configFile)
    # # rank_block_file(revisions, bugIds, configFile)
    # analyze(configFile)
