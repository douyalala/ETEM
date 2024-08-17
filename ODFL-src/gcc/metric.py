'''
Author: your name
Date: 2021-08-16 08:49:04
LastEditTime: 2021-10-08 13:45:21
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/metric.py
'''
'''
Author: your name
Date: 2021-06-02 14:51:44
LastEditTime: 2021-08-16 08:43:17
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/RecBi-master/RecBi/gcc/analyze.py
'''
import os
# from ..util import thirdpos
from configparser import ConfigParser
from collections import defaultdict

def metrics(resultlist):
    result = dict()
    sumouter=0
    for gcc in resultlist:
        gcc.sort()
        if gcc[0]<=1:
            sumouter+=1
    result['Top-1'] = sumouter

    sumouter=0
    for gcc in resultlist:
        gcc.sort()
        if gcc[0]<=3:
            sumouter+=1
    result['Top-3'] = sumouter

    sumouter=0
    for gcc in resultlist:
        gcc.sort()
        if gcc[0]<=5:
            sumouter+=1
    result['Top-5'] = sumouter

    sumouter=0
    for gcc in resultlist:
        gcc.sort()
        if gcc[0]<=10:
            sumouter+=1
    result['Top-10'] = sumouter

    sumouter=0
    for gcc in resultlist:
        gcc.sort()
        if gcc[0]<=20:
            sumouter+=1
    result['Top-20'] = sumouter

    sumouter=0.0
    for gcc in resultlist:
        gcc.sort()
        sumouter+=gcc[0]
    result['MFR'] = sumouter/len(resultlist)

    sumouter=0.0
    for gcc in resultlist:
        gcc.sort()
        suminner=0.0
        for i in range(len(gcc)):
            suminner+=gcc[i]
        sumouter+=(suminner/len(gcc))
    result['MAR'] = sumouter/len(resultlist)

    return result


def analyze(configFile):

    cfg = ConfigParser()
    cfg.read(configFile)

    # reduced = cfg.get('gcc-rev', 'reduced').split(',')
    resultFile = cfg.get('gcc-workplace', 'resultFile')
    # loops = cfg.getint('params', 'loops')

    revisions = []

    finallist=[]
    group1=[]
    resultdict=dict()

    f = open(resultFile)
    lines=f.readlines()
    f.close()

    resultlist=[]
    resultdict = defaultdict(list)
    for i in range(len(lines)):
        linesplit = lines[i].strip().split(',')
        revNum = linesplit[1]
        buggyFile = linesplit[2]
        minRank = int(linesplit[3])
        maxRank = int(linesplit[4])
        resultdict[revNum].append(maxRank)
    for key in resultdict.keys():
        resultlist.append(resultdict[key])
    
    result = metrics(resultlist)
    print('\033[1;35m result = ', result,'\033[0m')
        
    return resultlist


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
    
    resultlist =  analyze(revisions, bugIds, configFile)
    
