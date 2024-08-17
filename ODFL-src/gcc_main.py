'''
Author: your name
Date: 2021-07-20 04:05:16
LastEditTime: 2021-10-24 11:40:55
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc_main.py
'''
from gcc import metric
from gcc.metric import metrics
from gcc import rank
import os,sys
from configparser import ConfigParser
from multiprocessing import Pool
from gcc import *
import subprocess

# 单个运行
def run(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile, i):
    print('Run task %s (%s)...' % (bugId, os.getpid())) # 报告bugid，线程号
    os.system("taskset -p -c " + str(i+1) + " " + str(os.getpid()))

    path = sys.path[0] + '/gcc/optconfig.py' #最后的方法
    os.system(f'python3 -u {path} {revNum} {compilationOptionsRight} {compilationOptionsWrong} {checkpass} {configFile} {bugId} > {logDir}{bugId}.log 2>&1')

# 从buglist读取要运行的bug，多线程运行
def multi_process(configFile, workplace):
    cfg = ConfigParser()
    cfg.read(configFile)
    compilerDir = cfg.get(workplace, 'configfile')
    sumFile = cfg.get(workplace, 'buglist')
    logDir = cfg.get(workplace, 'logdir')
    batch_num = cfg.getint('params', 'batch_num')

    if os.path.exists(logDir):
        os.system('rm -r ' + logDir)
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
        p.apply_async(run, args=(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile,i))
    p.close()
    p.join()

if __name__ == '__main__':
    os.chdir(sys.path[0])
    cfg = ConfigParser()
    cfg.read('conf/config.ini')
    configFile = cfg.get('gcc-workplace', 'configFile')
    
    # run ODFL using ./gcc/optconfig.py
    multi_process(configFile, 'gcc-workplace')
    
    sumFile = cfg.get("gcc-workplace", 'buglist')
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
        
    # SBFL
    rank_file(revisions, bugIds, configFile) # rank.py
    
    # get top-n info
    analyze(configFile) # metric.py
