import os
# from ..util import thirdpos
from configparser import ConfigParser
from collections import defaultdict

def metrics(resultlist):
    result = dict()
    top_1=0
    top_3=0
    top_5=0
    top_10=0
    top_20=0
    
    for llvm in resultlist:
        llvm.sort()
        if llvm[0]<=1:
            top_1+=1
        if llvm[0]<=3:
            top_3+=1
        if llvm[0]<=5:
            top_5+=1
        if llvm[0]<=10:
            top_10+=1
        if llvm[0]<=20:
            top_20+=1
    result['Top-1'] = top_1
    result['Top-3'] = top_3
    result['Top-5'] = top_5
    result['Top-10'] = top_10
    result['Top-20'] = top_20

    sumouter=0.0
    for llvm in resultlist:
        llvm.sort()
        sumouter+=llvm[0]
    result['MFR'] = sumouter/len(resultlist)

    sumouter=0.0
    for llvm in resultlist:
        llvm.sort()
        suminner=0.0
        for i in range(len(llvm)):
            suminner+=llvm[i]
        sumouter+=(suminner/len(llvm))
    result['MAR'] = sumouter/len(resultlist)

    return result


def analyze(configFile):

    cfg = ConfigParser()
    cfg.read(configFile)

    resultFile = cfg.get('llvm-workplace', 'resultFile')

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

    
