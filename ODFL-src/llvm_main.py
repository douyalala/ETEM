from llvm import metric
from llvm.metric import metrics
from llvm import rank
import os,sys
from configparser import ConfigParser
from multiprocessing import Pool
from llvm import *
import subprocess

# 单个运行
def run(bugId, revNum, compilationOptionsRight, compilationOptionsWrong, checkpass, logDir, configFile, i):
    print('Run task %s (%s)...' % (bugId, os.getpid())) # 报告bugid，线程号
    os.system("taskset -p -c " + str(i+1) + " " + str(os.getpid()))

    path = sys.path[0] + '/llvm/optconfig.py' #最后的方法
    os.system(f'python3 -u {path} {revNum} {compilationOptionsRight} {compilationOptionsWrong} {checkpass} {configFile} {bugId} > {logDir}{bugId}.log')

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
        if bugId in ['44705']:
            continue
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
    configFile = cfg.get('llvm-workplace', 'configFile')
    
    # run ODFL using ./llvm/optconfig.py
    multi_process(configFile, 'llvm-workplace')
    
    sumFile = cfg.get("llvm-workplace", 'buglist')
    with open(sumFile, 'r') as f:
        sumlines = f.readlines()
    revisions = []
    bugIds = []
    rights = []
    wrongs = []
    checkpasses = []
    for i in range(len(sumlines)):
        if sumlines[i].strip().split(',')[0] in ['44705']:
            continue
        bugIds.append(sumlines[i].strip().split(',')[0])
        revisions.append(sumlines[i].strip().split(',')[1])
        rights.append(sumlines[i].strip().split(',')[2])
        wrongs.append(sumlines[i].strip().split(',')[3])
        checkpasses.append(sumlines[i].strip().split(',')[4])
        
    # SBFL
    rank_file(revisions, bugIds, configFile) # rank.py
    
    # get top-n info
    analyze(configFile) # metric.py
