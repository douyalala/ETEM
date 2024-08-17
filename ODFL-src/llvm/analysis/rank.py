# 先用samemethods_call进行排除（不考虑在samemethods_call中的methods），用小优化选项禁用后编译器编译程序正确的覆盖信息当作passing，使用SBFL以及最大值聚合算法，得到buggy文件的定位
# from llvmforme.r340155.r340155.lldb.test.testcases.python_api.lldbutil.frame.TestFrameUtils import FrameUtilsTestCase

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
sys.path.append('/root/cfl/ODFL/gcc')
from metric import analyze
from collect_optioninfo import *
# from collect_optioninfo import diff_cov_cmporifail
from configparser import ConfigParser

def rank_block_file(revisions, bugIds, configFile):

    cfg = ConfigParser()
    cfg.read(configFile)

    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    bugList = cfg.get('gcc-workplace', 'bugList')
    resultFile = cfg.get('gcc-workplace', 'resultFile')
    mainDir = cfg.get('gcc-workplace', 'maindir')
    data = open(covinfoDir + 'FileRank_block_sbfl.csv', 'w')
    buggyfilepath = mainDir + '/gcc/buggyfiles_info.txt'


    for i in range(len(revisions)):
        revision = revisions[i]
        bugId = bugIds[i]

        optioncovpath = covinfoDir + bugId

        # 覆盖信息文件路径
        orifailCovPath = optioncovpath + '/orifail/fileBlockCov'
        rightLevelCovPath = optioncovpath + '/rightOptionBig/fileBlockCov'
        rightLevelCovAnalysis = optioncovpath + '/covAnalysis/rightOptionBig/fileBlockCov'
        wrongLevelCovPath = optioncovpath + '/wrongOptionBig/fileBlockCov'
        wrongLevelCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionBig/fileBlockCov'
        rightFlagCovPath = optioncovpath + '/rightOptionSmall/fileBlockCov'
        rightFlagCovAnalysis = optioncovpath + '/covAnalysis/rightOptionSmall/fileBlockCov'
        wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/fileBlockCov'
        wrongFlagCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionSmall/fileBlockCov'

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
        # print(buggyfiles)

        failstmt=dict() # the stmt cov information of failing test program
        passstmt=dict()
        failfileset=set() # the set of compiler file that was touched
        passfileset = set()
        failfilemapstmt=dict() # the dict of file and corresponding stmts
        nfstmt = dict() # 记录nfs的覆盖信息

        failstmtset = set()

        # compiler excuted lines that orifalling test program was compiled
        # option = compilationOptionsWrong.replace(' ', '+')
        for orifailcov in os.listdir(orifailCovPath):
            
            with open(orifailCovPath + '/' + orifailcov, 'r') as f:
                faillines = f.readlines()
            if faillines == []:
                print('there is no faillines')
                # errorfile.write(revision + ' ' + 'ERROR: no coverage information\n')
                continue

        # excuted lines in every buggy file that falling test program was compiled
        for j in range(len(faillines)):
            faillinesplit = faillines[j].strip().split('$')  
            # filename=faillinesplit[0].strip().split('.gcda')[0].strip()
            filename = faillinesplit[0]  # filename
            # if filename + ',' + methodname in samemethodset:   # 将覆盖信息完全一致的函数排除掉
            #     continue
            # if not filename in difffiles:
            #     continue
            
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


        # # small wrong: as failing
        # failcovpath = optioncovpath + '/wrongOptionSmall/fileCov_exact'
        failcovpath = wrongFlagCovPath
        for (dirpath, dirnames, filenames) in os.walk(failcovpath):
            for filename in filenames:
                with open(dirpath + '/' + filename, 'r') as f:
                    firstfaillines = f.readlines()
                failingstmtset = set()
                for j in range(len(firstfaillines)):
                    faillinesplit = firstfaillines[j].strip().split('$')
                    filename=faillinesplit[0]  # filename
                    if not filename.endswith('.c'): # consider c and h files
                        continue
                    if filename not in failfileset:
                        continue
                    stmtlist=faillinesplit[1].split(',') # stmts
                    for stmt in set(stmtlist)&failfilemapstmt[filename]:
                        failstmt[filename+',' +stmt] += 1
                        failingstmtset.add(filename+',' +stmt)

                nfset = failstmtset - failingstmtset
                for nf in nfset:
                    nfstmt[nf] += 1


        # big wrong: as failing
        failcovpath = wrongLevelCovPath
        for (dirpath, dirnames, filenames) in os.walk(failcovpath):
            for filename in filenames:
                if 'call' in filename:
                    continue
                else:
                    with open(dirpath + '/' + filename, 'r') as f:
                        firstfaillines = f.readlines()
                    failingstmtset = set()
                    for j in range(len(firstfaillines)):
                        faillinesplit = firstfaillines[j].strip().split('$')
                        filename=faillinesplit[0]  # filename
                        if not filename.endswith('.c'): # consider c and h files
                            continue
                        if filename not in failfileset:
                            continue
                        stmtlist=faillinesplit[1].split(',') # stmts
                        for stmt in set(stmtlist)&failfilemapstmt[filename]:
                            failstmt[filename+',' +stmt] += 1
                            failingstmtset.add(filename+',' +stmt)

                    nfset = failstmtset - failingstmtset
                    for nf in nfset:
                        nfstmt[nf] += 1
        
        # # small right options: as passing
        passcovpath = rightFlagCovPath
        # passcovpath = optioncovpath + '/rightOptionSmall/fileCov'
        for (dirpath, dirnames, filenames) in os.walk(passcovpath):
            for filename in filenames:
                with open(dirpath + '/' + filename, 'r') as f:
                    passlines = f.readlines()
                for j in range(len(passlines)):
                    passlinesplit = passlines[j].strip().split('$')
                    # filename=passlinesplit[0].strip().split('.gcda')[0].strip()
                    filename = passlinesplit[0]
                    # if not filename.endswith('.cpp'): # consider c and h files
                    #     continue
                    if not filename.endswith('.c'): # consider c and h files
                        continue
                    if filename  not in failfileset:
                        continue
                    passfileset.add(filename)
                    stmtlist = passlinesplit[1].split(',')
                    for stmt in set(stmtlist)&failfilemapstmt[filename]:
                        # if filename+','+stmt in failstmt.keys():
                        passstmt[filename+ ',' + stmt] += 1   # the bunber of times of statements that the passing test program excuted
        # big right options: as passing
        passcovpath = rightLevelCovPath
        for (dirpath, dirnames, filenames) in os.walk(passcovpath):
            for filename in filenames:
                if 'call' in filename:
                    continue
                else:
                    with open(dirpath + '/' + filename, 'r') as f:
                        passlines = f.readlines()
                    for j in range(len(passlines)):
                        passlinesplit = passlines[j].strip().split('$')
                        # filename=passlinesplit[0].strip().split('.gcda')[0].strip()
                        filename = passlinesplit[0]
                        # if not filename.endswith('.cpp'): # consider c and h files
                        #     continue
                        if not filename.endswith('.c'): # consider c and h files
                            continue
                        if filename not in failfileset:
                            continue
                        stmtlist = passlinesplit[1].split(',')
                        for stmt in set(stmtlist)&failfilemapstmt[filename]:
                            # if filename+','+stmt in failstmt.keys():
                            passstmt[filename+ ','  + stmt] += 1   # the bunber of times of statements that the passing test program excuted

        # compute statement score based on SBFL
        score=dict()  # the buggy value of each statement and its line number in each file
        methodscore=dict() # the buggy value of each file, and we can get the corresponding statement values
        for key in failstmt.keys():
            score[key]=float(failstmt[key])/math.sqrt(float(failstmt[key] + nfstmt[key])*(failstmt[key]+passstmt[key]))
            # score[key] = (failstmt[key]/float(failstmt[key] + nfstmt[key]))/(failstmt[key]/float(failstmt[key]+nfstmt[key])+passstmt[key]/float(failstmt[key]+nfstmt[key]))
            # if passstmt[key]==0:
            # 	score[key]=1.0
            # else:
            # 	score[key]=float(failstmt[key])/passstmt[key]
            keymethod=key.rsplit(',', 1)[0]
            if keymethod not in methodscore.keys():
                methodscore[keymethod]=[]
                methodscore[keymethod].append(score[key])
            else:
                methodscore[keymethod].append(score[key])

        # compute the buggy values of each file based on  average aggregation
        if not methodscore:
            continue
        fileaggstmtscore=dict()
        for key in methodscore.keys():
            fileaggstmtscore[key]=float(sum(methodscore[key]))/len(methodscore[key])  # 平均聚合
            # fileaggstmtscore[key] = float(max(methodscore[key]))                 # 最大值聚合 
        scorelist=sorted(fileaggstmtscore.items(),key=lambda d:d[1],reverse=True)
        for bf in buggyfiles:
            # for bf in buggyfiles:
            tmp=[]
            error = 0 # 没有识别出对应的函数
            for j in range(len(scorelist)):
                try:
                    if fileaggstmtscore[bf] == scorelist[j][1]:
                        tmp.append(j)
                    # if bf == scorelist[j][0]:
                    #     tmp.append(j)
                        # break
                except:
                    error = 1
                    break
            if not tmp: # 列表为空
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

def rank_file(revisions, bugIds, configFile):

    cfg = ConfigParser()
    cfg.read(configFile)

    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    bugList = cfg.get('gcc-workplace', 'bugList')
    resultFile = cfg.get('gcc-workplace', 'resultFile')
    mainDir = cfg.get('gcc-workplace', 'maindir')
    data = open(covinfoDir + 'multi_onlysmallpass.csv', 'w')
    buggyfilepath = mainDir + '/gcc/buggyfiles_info.txt'


    for i in range(len(revisions)):
        revision = revisions[i]
        bugId = bugIds[i]
        # if bugId != '64853':
        #     continue
        # if bugId == '60452' or bugId == '65318' or bugId == '57341':
        #     continue
        # if bugId != '57303':
        #     continue

        optioncovpath = covinfoDir + bugId
        # 覆盖信息文件路径
        orifailCovPath = optioncovpath + '/orifail/testfileCov'
        rightLevelCovPath = optioncovpath + '/rightOptionBig/testfileCov'
        rightLevelCovAnalysis = optioncovpath + '/covAnalysis/rightOptionBig/testfileCov'
        wrongLevelCovPath = optioncovpath + '/wrongOptionBig/testfileCov'
        wrongLevelCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionBig/testfileCov'
        rightFlagCovPath = optioncovpath + '/rightOptionSmall/multifileCov'
        # rightFlagCovPath = optioncovpath + '/rightOptionSmall/testfileCov'
        rightFlagCovAnalysis = optioncovpath + '/covAnalysis/rightOptionSmall/multifileCov'
        wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/testfileCov'
        # wrongFlagCovPath = optioncovpath + '/wrongOptionSmall/multifileCov'
        wrongFlagCovAnalysis = optioncovpath + '/covAnalysis/wrongOptionSmall/testfileCov'

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
        # print(buggyfiles)

        failstmt=dict() # the stmt cov information of failing test program
        passstmt=dict()
        failfileset=set() # the set of compiler file that was touched
        passfileset = set()
        failfilemapstmt=dict() # the dict of file and corresponding stmts
        nfstmt = dict() # 记录nfs的覆盖信息

        failstmtset = set()

        # 用diff file来缩小buggy file的范围
        difffiles = set()
        # diffinfopath = optioncovpath + '/covAnalysis/rightOptionBig/fileCov'
        diffinfopath = rightLevelCovAnalysis
        if not os.path.exists(diffinfopath):
            print(revision + ' ' + bugId)
            continue
        for filename in os.listdir(diffinfopath):
            if filename.startswith('passnotexe') or filename.startswith('difffiles_call'):
                with open(diffinfopath + '/' + filename) as f:
                    diffinfos = f.readlines()
                for diffinfo in diffinfos:
                    difffiles.add(diffinfo.strip().split(' ')[1].split(',')[0])

        # compiler excuted lines that orifalling test program was compiled
        # option = compilationOptionsWrong.replace(' ', '+')
        for orifailcov in os.listdir(orifailCovPath):
            with open(orifailCovPath + '/' + orifailcov, 'r') as f:
                faillines = f.readlines()
            if faillines == []:
                print('there is no faillines')
                # errorfile.write(revision + ' ' + 'ERROR: no coverage information\n')
                continue
        # orifail 的行覆盖信息集合，用于计算相似度
        failset = set()
        for i in range(len(faillines)):
            filename = faillines[i].strip().split('$')[0]
            stmtlist = faillines[i].strip().split('$')[1].split(',')
            for j in range(len(stmtlist)):
                failset.add(filename + ':' + stmtlist[j])

        # excuted lines in every buggy file that falling test program was compiled
        for j in range(len(faillines)):
            faillinesplit = faillines[j].strip().split('$')  
            # filename=faillinesplit[0].strip().split('.gcda')[0].strip()
            filename = faillinesplit[0]  # filename
            # if filename + ',' + methodname in samemethodset:   # 将覆盖信息完全一致的函数排除掉
            #     continue
            if not filename in difffiles:
                continue
            
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

        # # small wrong: as failing
        # # failcovpath = optioncovpath + '/wrongOptionSmall/fileCov_exact'
        # failcovpath = wrongFlagCovPath
        # for (dirpath, dirnames, filenames) in os.walk(failcovpath):
        #     for filename in filenames:
        #         # if '-O3' in filename:
        #         #     continue
        #         # similarity = diff_cov_cmporifail(failcovpath, '/' + filename, failset)
        #         # if similarity > 0.99:
        #         #     continue
        #         with open(dirpath + '/' + filename, 'r') as f:
        #             firstfaillines = f.readlines()
        #         failingstmtset = set()
        #         for j in range(len(firstfaillines)):
        #             faillinesplit = firstfaillines[j].strip().split('$')
        #             filename=faillinesplit[0]  # filename
        #             if not filename.endswith('.c'): # consider c and h files
        #                 continue
        #             if filename not in failfileset:
        #                 continue
        #             stmtlist=faillinesplit[1].split(',') # stmts
        #             for stmt in set(stmtlist)&failfilemapstmt[filename]:
        #                 failstmt[filename+',' +stmt] += 1
        #                 failingstmtset.add(filename+',' +stmt)

        #         nfset = failstmtset - failingstmtset
        #         for nf in nfset:
        #             nfstmt[nf] += 1

        # # small wrong: as failing--genetic algorithm
        # failcovpath = optioncovpath + '/wrongOptionSmall/fileCov_exact'
        # failcovpath = optioncovpath + '/wrongOptionSmall/fileGene'
        # for (dirpath, dirnames, filenames) in os.walk(failcovpath):
        #     for subdir in dirnames:
        #         abspath = os.path.join(dirpath, subdir)
        #         dir_list = os.listdir(abspath)
        #         dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(abspath, x)), reverse=True)
        #         # for file in os.listdir(abspath):
        #         for i in range(len(dir_list)):
        #             if i > 1:
        #                 break
        #             file = dir_list[i]
        #             with open(abspath + '/' + file, 'r') as f:
        #                 firstfaillines = f.readlines()
        #             failingstmtset = set()
        #             for j in range(len(firstfaillines)):
        #                 faillinesplit = firstfaillines[j].strip().split('$')
        #                 filename=faillinesplit[0]  # filename
        #                 if not filename.endswith('.c'): # consider c and h files
        #                     continue
        #                 if filename not in failfileset:
        #                     continue
        #                 stmtlist=faillinesplit[1].split(',') # stmts
        #                 for stmt in set(stmtlist)&failfilemapstmt[filename]:
        #                     failstmt[filename+',' +stmt] += 1
        #                     failingstmtset.add(filename+',' +stmt)

        #             nfset = failstmtset - failingstmtset
        #             for nf in nfset:
        #                 nfstmt[nf] += 1

        # # big wrong: as failing
        # failcovpath = wrongLevelCovPath
        # for (dirpath, dirnames, filenames) in os.walk(failcovpath):
        #     for filename in filenames:
        #         # similarity = diff_cov_cmporifail(failcovpath, '/' + filename, failset)
        #         # if similarity > 0.99:
        #         #     continue
        #         with open(dirpath + '/' + filename, 'r') as f:
        #             firstfaillines = f.readlines()
        #         failingstmtset = set()
        #         for j in range(len(firstfaillines)):
        #             faillinesplit = firstfaillines[j].strip().split('$')
        #             filename=faillinesplit[0]  # filename
        #             if not filename.endswith('.c'): # consider c and h files
        #                 continue
        #             if filename not in failfileset:
        #                 continue
        #             stmtlist=faillinesplit[1].split(',') # stmts
        #             for stmt in set(stmtlist)&failfilemapstmt[filename]:
        #                 failstmt[filename+',' +stmt] += 1
        #                 failingstmtset.add(filename+',' +stmt)
        #         # print(failstmt['gcc/tree-sra.c,2119'])
        #         # print(failstmt['gcc/tree-sra.c,2120'])
        #         # print(failstmt['gcc/tree-sra.c,2121'])
        #         # # print(failstmt['gcc/tree-sra.c,2122'])
        #         # print(failstmt['gcc/tree-sra.c,2123'])

        #         nfset = failstmtset - failingstmtset
        #         for nf in nfset:
        #             nfstmt[nf] += 1
        # configFile = '/root/cfl/RecBi-master/config/config.ini'
        # cfg1 = ConfigParser()
        # cfg1.read(configFile)
        # passdir = cfg1.get('gcc-locations', 'passdir') + '1'
        # for i in os.listdir(passdir + '/' + bugId + '/passcov'):
        #     passfile = open(passdir + '/' + bugId + '/passcov/' + i + '/stmt_info.txt')
        #     passlines = passfile.readlines()
        #     passfile.close()
        #     for j in range(len(passlines)):
        #         filename = passlines[j].strip().split(':')[0].split('gcda')[0] + 'c'
        #         if not filename.endswith('.c'):  # consider c and h files
        #             continue
        #         if filename not in failfileset:
        #             continue
        #         stmtlist = passlines[j].strip().split(':')[1].split(',')
        #         for stmt in set(stmtlist) & failfilemapstmt[filename]:
        #             # if filename+','+stmt in failstmt.keys():
        #             passstmt[filename + ',' + stmt] += 1
            
        # # small right options: as passing
        passcovpath = rightFlagCovPath
        
        # passcovpath = optioncovpath + '/rightOptionSmall/fileCov'
        for (dirpath, dirnames, filenames) in os.walk(passcovpath):
            passFlagNum = len(filenames)
            for filename in filenames:
                with open(dirpath + '/' + filename, 'r') as f:
                    passlines = f.readlines()
                for j in range(len(passlines)):
                    passlinesplit = passlines[j].strip().split('$')
                    # filename=passlinesplit[0].strip().split('.gcda')[0].strip()
                    filename = passlinesplit[0]
                    # if not filename.endswith('.cpp'): # consider c and h files
                    #     continue
                    # if not filename.endswith('.c'): # consider c and h files
                    #     continue
                    if filename  not in failfileset:
                        continue
                    passfileset.add(filename)
                    stmtlist = passlinesplit[1].split(',')
                    for stmt in set(stmtlist)&failfilemapstmt[filename]:
                        # if filename+','+stmt in failstmt.keys():
                        passstmt[filename+ ',' + stmt] += 1   # the bunber of times of statements that the passing test program excuted

        # print(failstmt['gcc/tree-ssa-sink.c,341'])
        # # big right options: as passing
        # if passFlagNum < 10:
        # passcovpath = rightLevelCovPath
        # for (dirpath, dirnames, filenames) in os.walk(passcovpath):
        #     for filename in filenames:
        #         with open(dirpath + '/' + filename, 'r') as f:
        #             passlines = f.readlines()
        #         for j in range(len(passlines)):
        #             passlinesplit = passlines[j].strip().split('$')
        #             # filename=passlinesplit[0].strip().split('.gcda')[0].strip()
        #             filename = passlinesplit[0]
        #             # if not filename.endswith('.cpp'): # consider c and h files
        #             #     continue
        #             if not filename.endswith('.c'): # consider c and h files
        #                 continue
        #             if filename not in failfileset:
        #                 continue
        #             stmtlist = passlinesplit[1].split(',')
        #             for stmt in set(stmtlist)&failfilemapstmt[filename]:
        #                 # if filename+','+stmt in failstmt.keys():
        #                 passstmt[filename+ ','  + stmt] += 1   # the bunber of times of statements that the passing test program excuted


        # compute statement score based on SBFL
        score=dict()  # the buggy value of each statement and its line number in each file
        methodscore=dict() # the buggy value of each file, and we can get the corresponding statement values
        for key in failstmt.keys():
            # if key == 'gcc/tree-ssa-sink.c,331' or key == 'gcc/tree-ssa-sink.c,334' or key == 'gcc/tree-ssa-sink.c,335' or key == 'gcc/tree-ssa-sink.c,336' or key == 'gcc/tree-ssa-sink.c,337' or key == 'gcc/tree-ssa-sink.c,338' or key == 'gcc/tree-ssa-sink.c,340':
            #     print(key + ' ' + str(failstmt[key]))
            #     print(key + ' ' + str(nfstmt[key]))
            #     print(key + ' ' + str(passstmt[key]))
            score[key]=float(failstmt[key])/math.sqrt(float(failstmt[key] + nfstmt[key])*(failstmt[key]+passstmt[key]))
            # score[key] = (failstmt[key]/float(failstmt[key] + nfstmt[key]))/(failstmt[key]/float(failstmt[key]+nfstmt[key])+passstmt[key]/float(failstmt[key]+nfstmt[key]))
            # if passstmt[key]==0:
            # 	score[key]=1.0
            # else:
            # 	score[key]=float(failstmt[key])/passstmt[key]
            keymethod=key.rsplit(',', 1)[0]
            if keymethod not in methodscore.keys():
                methodscore[keymethod]=[]
                methodscore[keymethod].append(score[key])
            else:
                methodscore[keymethod].append(score[key])

        # compute the buggy values of each file based on  average aggregation
        if not methodscore:
            continue
        fileaggstmtscore=dict()
        for key in methodscore.keys():
            fileaggstmtscore[key]=float(sum(methodscore[key]))/len(methodscore[key])  # 平均聚合
            # fileaggstmtscore[key] = float(max(methodscore[key]))                 # 最大值聚合 
        scorelist=sorted(fileaggstmtscore.items(),key=lambda d:d[1],reverse=True)
        for bf in buggyfiles:
            # for bf in buggyfiles:
            tmp=[]
            error = 0 # 没有识别出对应的函数
            for j in range(len(scorelist)):
                try:
                    if fileaggstmtscore[bf] == scorelist[j][1]:
                        tmp.append(j)
                    # if bf == scorelist[j][0]:
                    #     tmp.append(j)
                        # break
                except:
                    error = 1
                    break
            if not tmp: # 列表为空
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
    # rank_block_file(revisions, bugIds, configFile)
    analyze(configFile)



