'''
Author: your name
Date: 2021-07-28 08:15:08
LastEditTime: 2021-08-05 06:55:11
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/check/cov_exist.py
'''


import os,sys
from configparser import ConfigParser


cfg = ConfigParser()
cfg.read('/root/cfl/ODFL/conf/config.ini')
bugList = cfg.get('gcc-workplace', 'buglist')
covInfoDir = cfg.get('gcc-workplace', 'covinfodir')

with open(bugList, 'r') as f:
    buglines = f.readlines()
cnt = 0
for i in range(len(buglines)):
    bugsplit = buglines[i].strip().split(',')
    bugId = bugsplit[0]
    revNum = bugsplit[1]
    compRight = bugsplit[2]
    compWrong = bugsplit[3]
    print(bugId + ' ' + revNum)
    cnt += 1
    print(cnt)
    # if revNum == 'r229937':
    #     print(1)

    # failExactDir = covInfoDir + bugId + '/wrongOptionSmall/fileCov_exact'
    # if not os.path.exists(failExactDir) or not os.listdir(failExactDir):
    #     # print(bugId + ' ' + revNum)
    #     # print(i)
    #     print(buglines[i].strip())
    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    optioncovpath = covinfoDir + bugId
    rightDictFile = optioncovpath + '/right_exact_dict.txt'
    wrongDictFile = optioncovpath + '/wrong_exact_dict.txt'
    if not os.path.exists(rightDictFile) or not os.path.exists(wrongDictFile):
        # print(bugId + ' ' + revNum)
        # print(i)
        print('ERROR: ' + buglines[i].strip() + ' not files')
        continue
    if os.path.exists(rightDictFile):
        with open(rightDictFile, 'r') as f:
            rightlines = f.readlines()
        if len(rightlines) == 0:
            print('ERROR: ' + buglines[i].strip() + ' no right')
        else:
            print('right ' + str(rightlines))
            for line in rightlines:
                splitline = line.strip().split('$')
                if len(splitline) == 1:
                    print('ERROR')
    if os.path.exists(wrongDictFile):
        with open(wrongDictFile) as f:
            wronglines = f.readlines()
        if len(wronglines) == 0:
            print('ERROR: ' + buglines[i].strip() + ' no wrong')
        else:
            print('wrong ' + str(wronglines))
            for line in wronglines:
                splitline = line.strip().split('$')
                if len(splitline) == 1:
                    print('ERROR')