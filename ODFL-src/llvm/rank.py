import os,random,math
from posix import listdir
from posixpath import dirname
import os.path
import subprocess as subp
import sys
from numpy.core.fromnumeric import partition
sys.path.append('/data1/lyj/final-FL-eval/ODFL/ODFL/llvm')
from collect_optioninfo import *
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
    covinfoDir = cfg.get('llvm-workplace', 'covinfodir')
    mainDir = cfg.get('llvm-workplace', 'maindir')
    data = open(covinfoDir + 'FileRank_smalloption_sbfl.csv', 'w')
    oracledir = cfg.get('llvm-workplace', 'oracledir')
    sumFile = cfg.get("llvm-workplace", 'buglist')
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

        oracle = set()
        oraclefile = open(oracledir + '/' + bugId + '/locations')
        oraclelines = oraclefile.readlines()
        oraclefile.close()
        for line in oraclelines:
            if line.startswith('file:'):
                file_name = line.strip().split('llvm/')[1].split(';')[0]
                oracle.add('/'+file_name)
        buggyfiles = list(oracle)

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
            
        if (not os.path.exists(wrongFlagCovPath)) or len(os.listdir(wrongFlagCovPath)) == 0 :
            # 收集原始fail的cov
            if os.path.exists(orifailCovPath):
                for orifailcov in os.listdir(orifailCovPath):
                    with open(orifailCovPath + '/' + orifailcov, 'r') as f:
                        faillines = f.readlines()
                    if faillines == []:
                        print('there is no faillines')
                        continue
                
                # 原始fail的各个sbfl数值
                for j in range(len(faillines)):
                    faillinesplit = faillines[j].strip().split('$')  
                    filename = faillinesplit[0]  # filename
                    stmtlist = faillinesplit[1].split(',') # stmts
                    failfileset.add(filename)
                    
                    if filename not in failfilemapstmt.keys():
                        failfilemapstmt[filename] = set()
                    failfilemapstmt[filename].update(stmtlist)
                    
                    for stmt in stmtlist:
                        failstmt[filename+ ','+stmt] = 1  # the statements that the falling test program excuted
                        passstmt[filename+ ','+stmt] = 0  # the statements that the passing test programs excuted
                        nfstmt[filename+ ',' + stmt] = 0
                        failstmtset.add(filename+ ',' +stmt)
                        npstmt[filename+ ',' + stmt] = 0
            else:
                continue

        # 获取了bf和br选项
        wrongoptExactdict, rightoptExactdict = optionDict(optioncovpath)
        if len(list(wrongoptExactdict.keys()))==0:
            lowestOpt = '+'
        else:
            lowestOpt = list(wrongoptExactdict.keys())[0].replace(' ','+')
        
        # efs
        # 找到的fail
        for orifailcov in os.listdir(wrongFlagCovPath):
            with open(wrongFlagCovPath + '/' + orifailcov, 'r') as f:
                faillines = f.readlines()
            if faillines == []:
                print('there is no faillines')
                continue
            
            for j in range(len(faillines)):
                faillinesplit = faillines[j].strip().split('$')  
                filename = faillinesplit[0]  # filename
                stmtlist = faillinesplit[1].split(',') # stmts
                failfileset.add(filename)
                
                if filename not in failfilemapstmt.keys():
                    failfilemapstmt[filename] = set()
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
        # 计算原始fail中，没有被搜到的fail执行到的指令数量（ochiai不需要这个，可能别的公式需要）
        for orifailcov in os.listdir(wrongFlagCovPath):
            with open(wrongFlagCovPath + '/' + orifailcov, 'r') as f:
                faillines = f.readlines()
            if faillines == []:
                print('there is no faillines')
                continue
            tmpfailstmtset = set()
            
            for j in range(len(faillines)):
                faillinesplit = faillines[j].strip().split('$')  
                filename = faillinesplit[0]  # filename
                stmtlist = faillinesplit[1].split(',') # stmts
                failfileset.add(filename)
                for stmt in stmtlist:
                    tmpfailstmtset.add(filename+ ',' +stmt)
                    
            nfset = failstmtset - tmpfailstmtset
            for nf in nfset:
                nfstmt[nf] += 1

        # # small right options: as passing
        # 搜到的pass的cov
        for filename in os.listdir(rightFlagCovPath):
            with open(rightFlagCovPath + '/' + filename, 'r') as f:
                passlines = f.readlines()
            passstmtset = set()
            for j in range(len(passlines)):
                passlinesplit = passlines[j].strip().split('$')
                filename = passlinesplit[0]
                if filename not in failfileset:
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
        # 大的pass的cov
        for filename in os.listdir(rightLevelCovPath):
            with open(rightLevelCovPath + '/' + filename, 'r') as f:
                passlines = f.readlines()
            passstmtset = set()
            for j in range(len(passlines)):
                passlinesplit = passlines[j].strip().split('$')
                filename = passlinesplit[0]
                if filename not in failfileset:
                    continue
                stmtlist = passlinesplit[1].split(',')
                for stmt in set(stmtlist)&failfilemapstmt[filename]:
                    passstmt[filename+ ','  + stmt] += 1   # the bunber of times of statements that the passing test program excuted
                npset = failstmtset - passstmtset
                for np in npset:
                    npstmt[np] += 1

        # compute statement score based on SBFL
        # 最终算SBFL
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

        # compute the buggy values of each file based on  average aggregation
        if not filescore:
            continue
        fileaggstmtscore=dict()
        for key in filescore.keys():
            
            if 'CMakeFiles' in key:
                files = key.split('/')
                files2 = '/'
                for i in range(len(files)):
                    if files[i] != 'CMakeFiles' and not '.dir' in files[i] and files[i] != '':
                        files2 += files[i]
                        files2 += '/'
                new_key = files2[:-1]
            
            fileaggstmtscore[new_key]=float(sum(filescore[key]))/len(filescore[key])
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
                print(os.path.split(__file__)[1] +' '+ bugId + ' ' + revision + ' ' + bf +'   error')    
                data.write(bugId + ',' + revision + ',' + bf +',' + ' ' + ',' + ' ' + ',' + '\n') 
                data.flush()
    data.close()
