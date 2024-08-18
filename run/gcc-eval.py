from src.gcc import *
import math
from src.util import metrics
from configparser import ConfigParser

def batcheval(bugIds, configFile):
    
    cfg = ConfigParser()
    cfg.read(configFile)
    infodir = cfg.get('gcc-locations', 'infodir')
    
    rankFile = cfg.get('gcc-locations', 'rankFile')
    
    top_1 = 0
    top_3 = 0
    top_5 = 0
    top_10 = 0
    top_20 = 0
    
    mfr=0.0
    mar=0.0
    
    tmp_len = 0
    for bugId in bugIds:
        one_rankFile_name = rankFile + '-' + bugId
        
        oracle = set()
        oraclefile = open(infodir + '/' + bugId + '/locations')
        oraclelines = oraclefile.readlines()
        oraclefile.close()
        for line in oraclelines:
            if line.startswith('file:'):
                file_name = line.strip().split('gcc/')[1].split(';')[0]
                oracle.add(file_name)
        
        if not os.path.exists(one_rankFile_name):
            continue
        one_rankFile = open(one_rankFile_name)
        ranklines = one_rankFile.readlines()
        one_rankFile.close()
        
        i = 0
        rank_list = []
        for line in ranklines:
            i += 1
            file_name = line.split(',')[0].strip()
            if file_name in oracle:
                rank_list.append(i)
        if len(rank_list)==0:
            continue
            print(f'err:{bugId}')
            exit(0)
        tmp_len+=1
        mfr+=rank_list[0]
        mar+=(float(sum(rank_list))/float(len(rank_list)))
        
        rank_value = rank_list[0]
        print(bugId + ':' + str(rank_value))
        if rank_value <=1:
            top_1 += 1
        if rank_value <=3:
            top_3 += 1
        if rank_value <=5:
            top_5 += 1
        if rank_value <=10:
            top_10 += 1
        if rank_value <=20:
            top_20 += 1
    
    mfr = float(mfr)/float(tmp_len)
    mar = float(mar)/float(tmp_len)
    print(f'top_1:{top_1}, top_3:{top_3}, top_5:{top_5}, top_10:{top_10}, top_20:{top_20}')
    print(f'MFR:{mfr}, MAR:{mar}')

cfg = ConfigParser()
cfg.read('config/config.ini')
path = os.getcwd()
cfg.set('gcc-locations', 'maindir', path)
f = open('config/config.ini', 'w')
cfg.write(f)
f.close()

configFile = cfg.get('gcc-locations', 'configFile')
bugList = cfg.get('gcc-locations', 'bugList') 

revfile = open(bugList)
revlines = revfile.readlines()
revfile.close()

bugIds = []
for i in range(len(revlines)):
    bugIds.append(revlines[i].strip().split(',')[0])

print('\033[1;35m Begin batcheval\033[0m')
batcheval(bugIds, configFile)