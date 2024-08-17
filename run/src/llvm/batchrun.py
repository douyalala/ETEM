from multiprocessing import Pool
from ..util import *
from configparser import ConfigParser

def run(bugId, revision, right, wrong, checkpass, k, configFile):
    cfg = ConfigParser()
    cfg.read(configFile)
    logdir = cfg.get('llvm-locations', 'logdir')
    logfile = logdir+'/'+bugId+'.log'
    err_logfile = logdir+'/'+bugId+'_err.log'
    print(f'run: loop-{k}, bug-{bugId}')
    
    exccmd(f'python3 src/llvm/search.py {revision} {right} {wrong} {checkpass} {str(k)} {configFile} {bugId} 1>{logfile} 2>{err_logfile}')

def batchrun(bugIds, revisions, rights, wrongs, checkpasses, configFile):

    cfg = ConfigParser()
    cfg.read(configFile)
    batch_num = cfg.getint('params', 'batch_num')
    loops = cfg.getint('params', 'loops')

    p = Pool(processes = batch_num)
    for k in range(1, loops+1):
        for i in range(len(bugIds)):
            bugId = bugIds[i]
            revision = revisions[i]
            right = rights[i]
            wrong = wrongs[i]
            checkpass = checkpasses[i]
            p.apply_async(run, args=(bugId, revision, right, wrong, checkpass, k, configFile))
    p.close()
    p.join()