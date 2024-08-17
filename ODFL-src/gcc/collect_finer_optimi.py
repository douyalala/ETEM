'''
Author: your name
Date: 2021-07-22 14:25:10
LastEditTime: 2021-10-24 11:35:49
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/collect_exact_optimization.py
'''
'''
Author: your name
Date: 2021-07-22 14:25:10
LastEditTime: 2021-07-23 01:14:44
LastEditors: Please set LastEditors
Description: 收集每个optimization level对应的确切的optimization set
FilePath: /cfl/ODFL/gcc/gccOptInfo/collect_exact_optimization.py
'''
import os,sys
from configparser import ConfigParser
import subprocess

# 收集每个optimization level对应的确切的optimization set
def collect(configFile):    
    cfg = ConfigParser()
    cfg.read(configFile)
    bugList = cfg.get('gcc-workplace', 'buglist')
    compilersDir = cfg.get('gcc-workplace', 'compilersdir')
    exactoptimsDir = cfg.get('gcc-workplace', 'exactoptimdir')

    if not os.path.exists(exactoptimsDir):
        os.system('mkdir ' + exactoptimsDir)

    with open(bugList, 'r') as f:
        sumlines = f.readlines()

    for i in range(len(sumlines)):
        linesplit = sumlines[i].split(',')
        bugId = linesplit[0]
        revNum = linesplit[1]
        
        optimsDir = exactoptimsDir + bugId
        if os.path.exists(optimsDir):
            os.system('rm -r ' + optimsDir)
        os.system('mkdir  ' + optimsDir)
        gccPath = compilersDir + '/' + revNum + '-build/bin/gcc'
        optLevels = ['-O0','-O1', '-O2', '-O3', '-Os']
        for optLevel in optLevels:
            res_bytes = subprocess.Popen(gccPath + ' -Q --help=optimizers ' + optLevel, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            res_list = res_bytes.stdout.read().decode('utf-8').split('\n')
            optimiFile = open(optimsDir + '/' + optLevel + '.txt', 'w')
            for res in res_list:
                # print(res)
                if not '-f' in res or '[disabled]' in res:
                    continue
                else:
                    optimiFile.write(res + '\n')
 
        