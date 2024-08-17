import os,random,math
from posix import listdir
from posixpath import dirname
import os.path
import subprocess as subp
import sys
from numpy.core.fromnumeric import partition

from collect_optioninfo import *
from collect_optioninfo import diff_cov_cmporifail
from configparser import ConfigParser
from metric import analyze
from collections import OrderedDict


def optionDict(optioncovpath):
    # print(optioncovpath)
    with open(optioncovpath + '/wrong_exact_dict.txt', 'r') as f:
        wronglines = f.readlines()
    combinNum = OrderedDict()
    wrongoptExactdict = OrderedDict()
    for i in range(len(wronglines)):
        # print(wronglines[i])
        compilationOption = wronglines[i].strip().split('$')[0]
        wrongoptExactList = wronglines[i].strip().split('$')[1].split(',')
        wrongoptExactdict[compilationOption] = wrongoptExactList

    with open(optioncovpath + '/right_exact_dict.txt', 'r') as f:
        rightlines = f.readlines()
    combinNum = OrderedDict()
    rightoptExactdict = OrderedDict()
    for i in range(len(rightlines)):
        # print(rightlines[i])
        compilationOption = rightlines[i].strip().split('$')[0]
        rightoptExactList = rightlines[i].strip().split('$')[1].split(',')
        rightoptExactdict[compilationOption] = rightoptExactList
    return wrongoptExactdict, rightoptExactdict

# 一个不知道为什么写了巨长的根据cov计算SBFL的函数
def rank_file(revisions, bugIds, configFile):

    cfg = ConfigParser()
    cfg.read(configFile)
    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    mainDir = cfg.get('gcc-workplace', 'maindir')
    data = open(covinfoDir + 'FileRank_smalloption_sbfl.csv', 'w')
    buggyfilepath = mainDir + '/gcc/buggyfiles_info.txt'
    sumFile = cfg.get("gcc-workplace", 'buglist')
    with open(sumFile, 'r') as f:
        sumlines = f.readlines()
    for i in range(len(revisions)):
        revision = revisions[i]
        bugId = bugIds[i]      

        optioncovpath = covinfoDir + bugId
        orifailCovPath = optioncovpath + '/orifail/testfileCov'
        rightLevelCovPath = optioncovpath + '/rightOptionBig/testfileCov'
        rightLevelCovAnalysis = optioncovpath + '/covAnalysis/rightOptionBig/testfileCov'
        wrongLevelCovPath = optioncovpath + '/wrongOptionBig/testfileCov'
        wrongLevelCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionBig/testfileCov'
        
        rightFlagCovPath = optioncovpath + '/rightOptionSmall/dismixCov2'
        wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/dismixCov2'


        with open(buggyfilepath, 'r') as f:
            buggyfilelines = f.readlines()
            buggyfiles = []
            jugebuggy = set()
            for buggyfileline in buggyfilelines:
                if buggyfileline.strip().split(' ')[0] == revision:
                    buggyfile = buggyfileline.strip().split(' ')[1].strip().split(',')[0]
                    buggyfiles.append(buggyfile)
                    jugebuggy.add(buggyfile)
        buggyfiles = list(set(buggyfiles))

        failstmt=dict() # the stmt cov information of failing test program
        passstmt=dict()
        failfileset=set() # the set of compiler file that was touched
        passfileset = set()
        failfilemapstmt=dict() # the dict of file and corresponding stmts
        nfstmt = dict() # 记录nfs的覆盖信息
        npstmt = dict()

        failstmtset = set()
        passstmtset = set()

    
        #如果关闭了全部的子优化还是触发了bug，就无法收集到fail覆盖信息
        if not os.path.exists(wrongFlagCovPath) or len(os.listdir(wrongFlagCovPath)) == 0 :
            for orifailcov in os.listdir(orifailCovPath):
                with open(orifailCovPath + '/' + orifailcov, 'r') as f:
                    faillines = f.readlines()
                if faillines == []:
                    print('there is no faillines')
                    continue
            failset = set()
            for i in range(len(faillines)):
                filename = faillines[i].strip().split('$')[0]
                stmtlist = faillines[i].strip().split('$')[1].split(',')
                for j in range(len(stmtlist)):
                    failset.add(filename + ':' + stmtlist[j])
            # excuted lines in every buggy file that falling test program was compiled
            for j in range(len(faillines)):
                faillinesplit = faillines[j].strip().split('$')  
                filename = faillinesplit[0]  # filename
                failfileset.add(filename)
                stmtlist = faillinesplit[1].split(',') # stmts
                if filename not in failfilemapstmt.keys():
                    failfilemapstmt[filename] = set()
                    failfilemapstmt[filename].update(stmtlist)
                else:
                    failfilemapstmt[filename].update(stmtlist)
                for stmt in stmtlist:
                    failstmt[filename+ ','+stmt] = 1  # the statements that the falling test program excuted
                    passstmt[filename+ ','+stmt] = 0  # the statements that the passing test programs excuted
                    nfstmt[filename+ ',' + stmt] = 0
                    failstmtset.add(filename+ ',' +stmt)
                    npstmt[filename+ ',' + stmt] = 0

        wrongoptExactdict, rightoptExactdict = optionDict(optioncovpath)
        if len(list(wrongoptExactdict.keys()))==0:
            lowestOpt = '+'
        else:
            lowestOpt = list(wrongoptExactdict.keys())[0].replace(' ','+')
        
        
        # efs
        for orifailcov in os.listdir(wrongFlagCovPath):
            if not lowestOpt in orifailcov:
                continue
            with open(wrongFlagCovPath + '/' + orifailcov, 'r') as f:
                faillines = f.readlines()
            if faillines == []:
                print('there is no faillines')
                continue
            for j in range(len(faillines)):
                faillinesplit = faillines[j].strip().split('$')  
                filename = faillinesplit[0]  # filename
                failfileset.add(filename)
                stmtlist = faillinesplit[1].split(',') # stmts
                if filename not in failfilemapstmt.keys():
                    failfilemapstmt[filename] = set()
                    failfilemapstmt[filename].update(stmtlist)
                else:
                    failfilemapstmt[filename].update(stmtlist)
                for stmt in stmtlist:
                    if filename+ ','+stmt in failstmt.keys():
                        failstmt[filename+ ','+stmt] += 1  # the statements that the falling test program excuted
                    else:
                        failstmt[filename+ ','+stmt] = 1
                        passstmt[filename+ ','+stmt] = 0  # the statements that the passing test programs excuted
                        nfstmt[filename+ ',' + stmt] = 0
                        failstmtset.add(filename+ ',' +stmt)
                        npstmt[filename+ ',' + stmt] = 0
        # nfs
        for orifailcov in os.listdir(wrongFlagCovPath):
            if not lowestOpt in orifailcov:
                continue
            with open(wrongFlagCovPath + '/' + orifailcov, 'r') as f:
                faillines = f.readlines()
            if faillines == []:
                print('there is no faillines')
                continue
            tmpfailstmtset = set()
            for j in range(len(faillines)):
                faillinesplit = faillines[j].strip().split('$')  
                filename = faillinesplit[0]  # filename
                failfileset.add(filename)
                stmtlist = faillinesplit[1].split(',') # stmts
                for stmt in stmtlist:
                    tmpfailstmtset.add(filename+ ',' +stmt)
            nfset = failstmtset - tmpfailstmtset
            for nf in nfset:
                nfstmt[nf] += 1

       
        # # small right options: as passing
        passcovpath = rightFlagCovPath
        for (dirpath, dirnames, filenames) in os.walk(passcovpath):
            for filename in filenames:
                if not lowestOpt in filename:
                    continue
                with open(dirpath + '/' + filename, 'r') as f:
                    passlines = f.readlines()
                passstmtset = set()
                for j in range(len(passlines)):
                    passlinesplit = passlines[j].strip().split('$')
                    filename = passlinesplit[0]
                    if filename  not in failfileset:
                        continue
                    passfileset.add(filename)
                    stmtlist = passlinesplit[1].split(',')
                    for stmt in set(stmtlist)&failfilemapstmt[filename]:
                        passstmt[filename+ ',' + stmt] += 1   # the bunber of times of statements that the passing test program excuted
                        passstmtset.add(filename+ ',' + stmt)
                npset = failstmtset - passstmtset
                for np in npset:
                    npstmt[np] += 1
        # small right options: as passing
        passcovpath = optioncovpath + '/rightOptionSmall/testfileCov'
        for (dirpath, dirnames, filenames) in os.walk(passcovpath):
            for filename in filenames:
                if not lowestOpt in filename:
                    continue
                with open(dirpath + '/' + filename, 'r') as f:
                    passlines = f.readlines()
                passstmtset = set()
                for j in range(len(passlines)):
                    passlinesplit = passlines[j].strip().split('$')
                    filename = passlinesplit[0]
                    if filename  not in failfileset:
                        continue
                    passfileset.add(filename)
                    stmtlist = passlinesplit[1].split(',')
                    for stmt in set(stmtlist)&failfilemapstmt[filename]:
                        passstmt[filename+ ',' + stmt] += 1   # the bunber of times of statements that the passing test program excuted
                        passstmtset.add(filename+ ',' + stmt)
                npset = failstmtset - passstmtset
                for np in npset:
                    npstmt[np] += 1
        # # big right options: as passing
        passcovpath = rightLevelCovPath
        files = sorted(os.listdir(passcovpath))
        files_ = files
        for filename in files_:
            with open(passcovpath + '/' + filename, 'r') as f:
                passlines = f.readlines()
            passstmtset = set()
            for j in range(len(passlines)):
                passlinesplit = passlines[j].strip().split('$')
                filename = passlinesplit[0]
                if not filename.endswith('.c'): # consider c files
                    continue
                if filename not in failfileset:
                    continue
                stmtlist = passlinesplit[1].split(',')
                for stmt in set(stmtlist)&failfilemapstmt[filename]:
                    passstmt[filename+ ','  + stmt] += 1   # the bunber of times of statements that the passing test program excuted
                npset = failstmtset - passstmtset
                for np in npset:
                    npstmt[np] += 1

        # compute statement score based on SBFL
        score=dict()  # the buggy value of each statement and its line number in each file
        filescore=dict() # the buggy value of each file, and we can get the corresponding statement values
        for key in failstmt.keys():
            # ochia
            score[key]=float(failstmt[key])/math.sqrt(float(failstmt[key] + nfstmt[key])*(failstmt[key]+passstmt[key]))
        
            # Tarantula
            # score[key]=(float(failstmt[key])/(failstmt[key]+nfstmt[key]))/((failstmt[key]/float(failstmt[key] + nfstmt[key]))+(passstmt[key]/(npstmt[key]+passstmt[key])))

            # op2
            # score[key]=failstmt[key] - passstmt[key]/(1+(npstmt[key]+passstmt[key]))

            # dstar
            # if (float(failstmt[key] + nfstmt[key])) + passstmt[key] - failstmt[key] != 0:
            #     # score[key]=(failstmt[key]*failstmt[key])/((float(failstmt[key] + nfstmt[key])) + passstmt[key] - failstmt[key])
            #     score[key]=(failstmt[key]*failstmt[key])/ (nfstmt[key] + passstmt[key])
            # else:
            #     score[key]=0

            # #ochia2
            # score[key]=float(failstmt[key])*npstmt[key]/math.sqrt(float(failstmt[key] +passstmt[key] )*(nfstmt[key]+npstmt[key])*(failstmt[key]+npstmt[key])*(npstmt[key]+passstmt[key]))

            # # Barinel
            # score[key]= 1 - passstmt[key]/(passstmt[key] + failstmt[key])

            keyfile=key.rsplit(',', 1)[0]
            if keyfile not in filescore.keys():
                filescore[keyfile]=[]
                filescore[keyfile].append(score[key])
            else:
                filescore[keyfile].append(score[key])

        # compute the buggy values of each file based on  average aggregation
        if not filescore:
            continue
        fileaggstmtscore=dict()
        for key in filescore.keys():
            # fileaggstmtscore[key]=float(sum(filescore[key]))/len(filescore[key])
            fileaggstmtscore[key] = float(sum(filescore[key][0:int(len(filescore[key])/2)])) / len(filescore[key])
        scorelist=sorted(fileaggstmtscore.items(),key=lambda d:d[1],reverse=True)
        
        # print rank file
        one_rankFile = f'./rankFile-{bugId}'
        f = open(one_rankFile, 'w')
        for score in scorelist:
            file = score[0]
            value = score[1]
            f.write(file + ',' + str(value) + '\n')
        f.close()
          
        for bf in buggyfiles:
            tmp=[]
            error = 0 
            for j in range(len(scorelist)):
                try:
                    if fileaggstmtscore[bf] == scorelist[j][1]:
                        tmp.append(j)
                except:
                    error = 1
                    break
            if not tmp: 
                error = 1
            
            if error == 0:
                print(os.path.split(__file__)[1] +' ' + bugId + ' ' + revision + ' ' + bf +' '+str(min(tmp)+1)+' '+str(max(tmp)+1)+' ' + str(fileaggstmtscore[bf]) )    
                data.write(bugId + ',' + revision + ',' + bf +','+str(min(tmp)+1)+','+str(max(tmp)+1)+',' + str(fileaggstmtscore[bf]) + '\n') 
                data.flush()
            elif error == 1:
                print(os.path.split(__file__)[1] +' '+ bugId + ' ' + revision + ' ' + bf +'   ' + str(fileaggstmtscore[bf]) )    
                data.write(bugId + ',' + revision + ',' + bf +',' + ' ' + ',' + ' ' + ',' + '\n') 
                data.flush()
    data.close()

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
    analyze(configFile)



