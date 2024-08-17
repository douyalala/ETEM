'''
Author: your name
Date: 2021-09-23 02:15:46
LastEditTime: 2021-09-28 08:24:10
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/check/optconfigure.py
'''
import os,sys
from configparser import ConfigParser

if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('/root/cfl/ODFL/conf/config.ini')
    sumFile = cfg.get("gcc-workplace", 'buglist')
    compilerDir = cfg.get('gcc-workplace', 'compilersdir')
    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    with open(sumFile, 'r') as f:
        lines = f.readlines()
    
    cnt = 0

    for i in range(len(lines)):
        bugId = lines[i].strip().split(',')[0]
        revNum = lines[i].strip().split(',')[1]
        compilationOptionsRight = lines[i].strip().split(',')[2]
        compilationOptionsWrong = lines[i].strip().split(',')[3]
        checkpass = lines[i].strip().split(',')[4]

        optioncovpath = covinfoDir + bugId
        # prefixpath = compilerDir + revNum + '/' + revNum
        rightFlagCovPath = optioncovpath + '/rightOptionSmall/disallfileCov'
        rightFlagCovAnalysis = optioncovpath + '/covAnalysis/rightOptionSmall/disallfileCov'
        wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/disallfileCov'
        wrongFlagCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionSmall/disallfileCov'
        # rightFlagCovPath = optioncovpath + '/rightOptionSmall/distoenfileCov'
        # rightFlagCovAnalysis = optioncovpath + '/covAnalysis/rightOptionSmall/distoenfileCov'
        # wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/distoenfileCov'
        # wrongFlagCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionSmall/distoenfileCov'
        
        if not os.listdir(wrongFlagCovPath):
            print('bugID: ' + bugId + '; revNum:' + revNum + ' has no file')
            pass
        else:
            print('bugID: ' + bugId + '; revNum:' + revNum)
            # if bugId == '61140' or bugId == '57303' or bugId == '58418':
            #     print('bugID: ' + bugId + '; revNum:' + revNum)
            #     files = os.listdir(wrongFlagCovPath)
            #     print(str(files))
            cnt += 1
    print(cnt)
        
        # failcovpath = optioncovpath + '/wrongOptionSmall/fileGene'
        # for (dirpath, dirnames, filenames) in os.walk(failcovpath):
        #     for subdir in dirnames:
        #         abspath = os.path.join(dirpath, subdir)
        #         if not os.listdir(abspath):
        #             print(bugId + ' ' + revNum)    