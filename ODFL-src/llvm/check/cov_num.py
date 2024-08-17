'''
Author: your name
Date: 2021-08-24 03:23:38
LastEditTime: 2021-09-29 02:33:30
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/check/cov_file_num.py
'''
# 先用samemethods_call进行排除（不考虑在samemethods_call中的methods），用小优化选项禁用后编译器编译程序正确的覆盖信息当作passing，使用SBFL以及最大值聚合算法，得到buggy文件的定位
import os,random,math
from posix import listdir
from posixpath import dirname
import datetime
import os.path
import subprocess as subp
import sys
import threading
from numpy.core.fromnumeric import partition
# import pandas as pd
sys.path.append('/root/cfl/innovation/Option/smalloptimoption/file_isolation')
from collect_optioninfo import *
from configparser import ConfigParser

def rank_file(revisions, bugIds, configFile):

    cfg = ConfigParser()
    cfg.read(configFile)

    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    bugList = cfg.get('gcc-workplace', 'bugList')
    resultFile = cfg.get('gcc-workplace', 'resultFile')
    mainDir = cfg.get('gcc-workplace', 'maindir')
    
    curpath = sys.path[0]
    covNumFile = open(curpath + '/cov_num.csv', 'w')
    for i in range(len(revisions)):
        revision = revisions[i]
        bugId = bugIds[i]

        optioncovpath = covinfoDir + bugId
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
        # rightFlagCovPath = optioncovpath + '/rightOptionSmall/testfileCov'
        # rightFlagCovPath = optioncovpath + '/rightOptionSmall/disallfileCov'
        # rightFlagCovAnalysis = optioncovpath + '/covAnalysis/rightOptionSmall/disallfileCov'
        # wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/disallfileCov'
        # wrongFlagCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionSmall/disallfileCov'

        failLevelCnt = 1
        failFlagCnt = 0
        passLevelCnt = 0
        passFlagCnt = 0
        failCovCnt = 0
        passCovCnt = 0
        # # # small wrong: as failing
        for (dirpath, dirnames, filenames) in os.walk(wrongFlagCovPath):
            for filename in filenames:
                failFlagCnt += 1

        # # big wrong: as failing
        for (dirpath, dirnames, filenames) in os.walk(wrongLevelCovPath):
            for filename in filenames:
                failLevelCnt += 1
                
        # # small right options: as passing
        for (dirpath, dirnames, filenames) in os.walk(rightFlagCovPath):
            for filename in filenames:
                passFlagCnt += 1
        # big right options: as passing
        for (dirpath, dirnames, filenames) in os.walk(rightLevelCovPath):
            for filename in filenames:
                passLevelCnt += 1

        covNumFile.write(bugId + ',' + revision + ',' + str(failLevelCnt) + ',' + str(failFlagCnt) + ',' + str(passLevelCnt) + ',' + str(passFlagCnt) + '\n')
        covNumFile.flush()
    covNumFile.close()


if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('/root/cfl/ODFL/conf/config.ini')
    compilerDir = cfg.get('gcc-workplace', 'configfile')
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
    
    rank_file(revisions, bugIds, configFile)




