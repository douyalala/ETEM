import math,heapq
from src.llvm import *
from src.util import metrics
from configparser import ConfigParser
from collections import defaultdict

cfg = ConfigParser()
cfg.read('config/config.ini')
configFile = cfg.get('llvm-locations', 'configFile')
bugList = cfg.get('llvm-locations', 'bugList')

revisions = []
bugIds = []
rights = []
wrongs = []
checkpasses = []

revfile = open(bugList)
revlines = revfile.readlines()
revfile.close()

for i in range(len(revlines)):
    if revlines[i].strip().split(',')[5] == 'install_no':
        continue
    bugIds.append(revlines[i].strip().split(',')[0])
    revisions.append(revlines[i].strip().split(',')[1])
    rights.append(revlines[i].strip().split(',')[2])
    wrongs.append(revlines[i].strip().split(',')[3])
    checkpasses.append(revlines[i].strip().split(',')[4])

print('\033[1;35m Begin batchrun\033[0m')
batchrun(bugIds, revisions, rights, wrongs, checkpasses, configFile)
print('\033[1;35m End batchrun\033[0m')