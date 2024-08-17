import math,heapq,os,sys
from src.llvm import *
from src.util import *
from configparser import ConfigParser
from collections import defaultdict
from multiprocessing import Pool
              
def getstmtlines(stmtfile):
    f = open(stmtfile)
    lines = f.readlines()
    f.close()
    return lines

def get_sbfl_score(infodir, passdir, bugId):
    failstmt = dict()
    passstmt = dict()

    # fail
    failcnt = 0
    fail_set = []

    # ori fail
    for testanme in os.listdir(infodir + '/' + bugId + '/fail'):
        if 'small_fail_opt' in testanme:
            cov = getstmtlines(infodir + '/' + bugId + '/fail/'+ testanme)
            failcnt += 1
            this_set = set()
            for line in cov:
                this_set.add(line.strip())
        
            if len(fail_set)==0:
                fail_set.append(this_set)
            else:
                fail_set[0]=(fail_set[0])&this_set

    # other fail
    if os.path.exists(passdir + '/' + bugId + '/stillfailcov'):
        for testanme in os.listdir(passdir + '/' + bugId + '/stillfailcov'):
            for stmt_name in os.listdir(passdir + '/' + bugId + '/stillfailcov/'+testanme):
                if not '_stmt_info.txt' in stmt_name:
                    continue
                stmtfilename = passdir + '/' + bugId + '/stillfailcov/' + testanme + '/' + stmt_name
                failcov = getstmtlines(stmtfilename)
                failcnt += 1
                this_set = set()
                for line in failcov:
                    this_set.add(line.strip())
                if len(fail_set)==0:
                    fail_set.append(this_set)
                else:
                    fail_set[0]=(fail_set[0])&this_set
                
    for line in fail_set[0]:
        if not line in failstmt.keys():
            failstmt[line]=0
            passstmt[line]=0
        failstmt[line]+=failcnt
    
    # pass
    passcnt = 0
    passcovs = []
    
    # pass opt for ori fail
    for testanme in os.listdir(infodir + '/' + bugId + '/fail'):
        if 'small_pass_opt' in testanme:
            # print(infodir + '/' + bugId + '/fail/'+ testanme)
            cov = getstmtlines(infodir + '/' + bugId + '/fail/'+ testanme)
            passcnt += 1
            passcovs.append(cov)

    # witness
    if os.path.exists(passdir + '/' + bugId + '/passcov'):
        for testanme in os.listdir(passdir + '/' + bugId + '/passcov'):
            for stmt_name in os.listdir(passdir + '/' + bugId + '/passcov/'+testanme):
                if not '_stmt_info.txt' in stmt_name:
                    continue
                stmtfilename = passdir + '/' + bugId + '/passcov/' + testanme + '/' + stmt_name
                cov = getstmtlines(stmtfilename)
                passcnt += 1
                passcovs.append(cov)

    # pass cov
    for passlines in passcovs:
        for line in passlines:
            cov_line = line.strip()
            if cov_line in failstmt.keys():
                passstmt[cov_line] += 1
                
    # sbfl
    score = dict()
    filescore = dict()
    for key in failstmt.keys():
        
        # ochiai
        score[key] = float(failstmt[key]) / math.sqrt( float(failcnt)*(failstmt[key]+passstmt[key]) )
        
        keyfile = key.split(':')[0]
        if keyfile not in filescore.keys():
            filescore[keyfile] = []
        filescore[keyfile].append(score[key])
    
    # file aggregation
    fileaggstmtscore = dict()
    for key in filescore.keys():
        # # avg
        # fileaggstmtscore[key] = float(sum(filescore[key])) / len(filescore[key])
        
        # # max
        # fileaggstmtscore[key] = max(filescore[key])
        
        # RS
        filescore[key].sort()
        filescore[key].reverse()
        key_len = len(filescore[key])
        res = 0
        for i in range(1, key_len+1):
            w = float(2*(key_len+1-i))/float(key_len*(key_len+1))
            res+=w*filescore[key][i-1]
        fileaggstmtscore[key] = res
        
    return score, fileaggstmtscore, bugId, passcnt, failcnt

def one_rank(loops, infodir, bugId, one_rankFile):
    
    debug_print = []
    res_print = f'\033[1;35m Ranking list has been recorded in {one_rankFile} \033[0m'
    
    finalrank = {}
    
    for loop in range(1, loops + 1):
        passdir = cfg.get('llvm-locations', 'passdir')
        passdir += str(loop)
        score, fileaggstmtscore, bugId, passcnt, failcnt = get_sbfl_score(infodir, passdir, bugId)
        debug_print.append(f'{loop} {bugId} {passcnt} {failcnt}')
        
        if finalrank == {}:
            finalrank = fileaggstmtscore
        else:
            for key in fileaggstmtscore.keys():
                if key in finalrank.keys():
                    finalrank[key] += fileaggstmtscore[key]
        
    scorelist = sorted(finalrank.items(), key=lambda d: d[1], reverse=True)
    f = open(one_rankFile, 'w')
    for score in scorelist:
        file = score[0]
        value = score[1]
        f.write(file + ',' + str(value) + '\n')
    f.close()
    
    return res_print, debug_print

def batchrank(bugIds, revisions, wrongs, configFile):

    cfg = ConfigParser()
    cfg.read(configFile)
    loops = cfg.getint('params', 'loops')
    infodir = cfg.get('llvm-locations', 'infodir')
    
    rankFile = cfg.get('llvm-locations', 'rankFile')
    
    bug_p = Pool(processes = 60)
    bug_res = []
    
    for idx in range(len(bugIds)):
        bugId = bugIds[idx]
        one_rankFile = rankFile + '-' + bugId
        bug_res.append(bug_p.apply_async(one_rank, args=(loops, infodir, bugId, one_rankFile,)))
    bug_p.close()
    for bug in bug_res:
        bug.wait()
        res_print, debug_print = bug.get()
        # debug
        for line in debug_print:
            print(line)
        print(res_print)
    bug_p.join()

cfg = ConfigParser()
cfg.read('config/config.ini')
configFile = cfg.get('llvm-locations', 'configFile')
bugList = cfg.get('llvm-locations', 'bugList')
compilersdir = cfg.get('llvm-locations', 'compilersdir')

revisions = []
bugIds = []
rights = []
wrongs = []
checkpasses = []

revfile = open(bugList)
revlines = revfile.readlines()
revfile.close()

for i in range(len(revlines)):
    bugIds.append(revlines[i].strip().split(',')[0])
    revisions.append(revlines[i].strip().split(',')[1])
    rights.append(revlines[i].strip().split(',')[2])
    wrongs.append(revlines[i].strip().split(',')[3])
    checkpasses.append(revlines[i].strip().split(',')[4])

print('\033[1;35m Begin batchrank\033[0m')
batchrank(bugIds, revisions, wrongs, configFile)
print('\033[1;35m End batchrank\033[0m')