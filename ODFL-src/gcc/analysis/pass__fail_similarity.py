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
from collect_optioninfo import *
from configparser import ConfigParser

def file_similarity(revisions, bugIds, configFile):

    cfg = ConfigParser()
    cfg.read(configFile)

    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    bugList = cfg.get('gcc-workplace', 'bugList')
    resultFile = cfg.get('gcc-workplace', 'resultFile')
    mainDir = cfg.get('gcc-workplace', 'maindir')
    buggyfilepath = mainDir + '/gcc/buggyfiles_info.txt'


    for i in range(len(revisions)):
        revision = revisions[i]
        bugId = bugIds[i]
        if bugId != '66375':
            continue
        optioncovpath = covinfoDir + bugId

        # compiler excuted lines that orifalling test program was compiled
        # option = compilationOptionsWrong.replace(' ', '+')
        # # # collect the covinfo of orifail
        failFileDict = dict()
        for file in os.listdir(optioncovpath + '/orifail/fileCov'):
            with open(optioncovpath + '/orifail/fileCov/' + file, 'r') as f:
                failcovlines = f.readlines()
            failset = set()
            for i in range(len(failcovlines)):
                filename = failcovlines[i].strip().split('$')[0]
                stmtlist = failcovlines[i].strip().split('$')[1].split(',')
                failFileDict[filename] = stmtlist
                for j in range(len(stmtlist)):
                    failset.add(filename + ':' + stmtlist[j])
        existingcovset = dict()
        unionCovwithFail = dict()


        # # # small wrong: as failing
        # # failcovpath = optioncovpath + '/wrongOptionSmall/fileCov_exact'
        comFailSimiDict_fail = dict()
        comFailSimiList_fail = []
        # failcovpath = optioncovpath + '/wrongOptionSmall/fileCov'
        # for (dirpath, dirnames, filenames) in os.walk(failcovpath):
        #     for filename in filenames:
        #         with open(dirpath + '/' + filename, 'r') as f:
        #             similarity = diff_pass_existing_cov(failcovpath, '/' + filename, failset, existingcovset, unionCovwithFail, failFileDict)
        #             comFailSimiList_fail.append(similarity)
        #             comFailSimiDict_fail[filename] = similarity

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

        # # big wrong: as failing
        failcovpath = optioncovpath + '/wrongOptionBig/fileCov'
        for (dirpath, dirnames, filenames) in os.walk(failcovpath):
            for filename in filenames:
                similarity = diff_pass_existing_cov(failcovpath, '/' + filename, failset, existingcovset, unionCovwithFail, failFileDict)
                comFailSimiList_fail.append(similarity)
                comFailSimiDict_fail[filename] = similarity


        # configFile = '/root/cfl/RecBi-master/config/config.ini'
        # cfg1 = ConfigParser()
        # cfg1.read(configFile)
        # passdir = cfg1.get('gcc-locations', 'passdir') + '1'
        # for i in os.listdir(passdir + '/' + bugId + '/passcov'):
        #     passfile = open(passdir + '/' + bugId + '/passcov/' + i + '/stmt_info.txt')
        #     passlines = passfile.readlines()
        #     passfile.close()
        comFailSimiDict_pass = dict()
        comFailSimiList_pass = []
        # small right options: as passing
        passcovpath = optioncovpath + '/rightOptionSmall/fileCov_exact'
        # passcovpath = optioncovpath + '/rightOptionSmall/fileCov'
        for (dirpath, dirnames, filenames) in os.walk(passcovpath):
            for filename in filenames:
                # with open(dirpath + '/' + filename, 'r') as f:
                #     passlines = f.readlines()
                similarity = diff_pass_existing_cov(passcovpath, '/' + filename, failset, existingcovset, unionCovwithFail, failFileDict)
                comFailSimiList_pass.append(similarity)
                comFailSimiDict_pass[filename] = similarity
        # # big right options: as passing
        passcovpath = optioncovpath + '/rightOptionBig/fileCov'
        for (dirpath, dirnames, filenames) in os.walk(passcovpath):
            for filename in filenames:
                similarity = diff_pass_existing_cov(passcovpath, '/' + filename, failset, existingcovset, unionCovwithFail, failFileDict)
                comFailSimiList_pass.append(similarity)
                comFailSimiDict_pass[filename] = similarity
        print(comFailSimiList_pass)
        print(comFailSimiList_fail)
        if not os.path.exists(covinfoDir + '/similarity'):
            os.system('mkdir -p ' + covinfoDir + '/similarity')
        with open(covinfoDir + '/similarity/' + bugId + '.csv', 'w') as f:
            f.write('pass\n')
            for every in comFailSimiDict_pass.keys():
                f.write(every + ',' + str(comFailSimiDict_pass[every]) + '\n')
            f.write('fail\n')
            for every in comFailSimiDict_fail.keys():
                f.write(every + ',' + str(comFailSimiDict_fail[every]) + '\n')

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
    
    file_similarity(revisions, bugIds, configFile)




