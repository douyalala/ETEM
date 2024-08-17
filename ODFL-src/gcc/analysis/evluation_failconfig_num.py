'''
Author: your name
Date: 2021-10-09 09:01:59
LastEditTime: 2021-10-09 09:15:32
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/analysis/evluation_failconfig_num.py
'''
import os,sys
from configparser import ConfigParser

if __name__ == '__main__':
    # os.chdir(sys.path[0])
    cfg = ConfigParser()
    cfg.read('/root/cfl/ODFL/conf/config.ini')
    compilerDir = cfg.get('gcc-workplace', 'compilersdir')
    sumFile = cfg.get("gcc-workplace", 'buglist')
    configFile = cfg.get('gcc-workplace', 'configFile')
    oracleDir = cfg.get('gcc-workplace', 'oracledir')
    mianDir = cfg.get('gcc-workplace', 'maindir')
    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    exactoptimsDir = cfg.get('gcc-workplace', 'exactoptimdir')
    # gcovpath = '/root/cfl/gccforme/r229639/r229639-build/bin/gcov'

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
    for i in range(len(sumlines)):
        bugId = sumlines[i].strip().split(',')[0]
        revNum = sumlines[i].strip().split(',')[1]
        compilationOptionsRight = sumlines[i].strip().split(',')[2]
        compilationOptionsWrong = sumlines[i].strip().split(',')[3]

        # print(revNum + ' ' + bugId)
        optioncovpath = covinfoDir + bugId
        rightFlagCovPath = optioncovpath + '/rightOptionSmall/distoenfileCov'
        wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/distoenfileCov'

        passconNum = len(os.listdir(rightFlagCovPath))
        failconNum = len(os.listdir(wrongFlagCovPath))
        singleNum = os.listdir(optioncovpath + '/rightOptionSmall/testfileCov')
        if failconNum == 0:
            print(bugId)