import os, time, sys, math, statistics
from random import choice
from configparser import ConfigParser
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

def score_DM(thisset):
    global pass_count
    
    sim_sets = dict()
    for line in pass_count.keys():
        this_count = pass_count[line]
        if not this_count in sim_sets.keys():
            sim_sets[this_count] = set()
        sim_sets[this_count].add(line)
    
    sim_sets_new = dict()
    for line in pass_count.keys():
        this_count = pass_count[line]
        if line in thisset:
            this_count+=1
        if not this_count in sim_sets_new.keys():
            sim_sets_new[this_count] = set()
        sim_sets_new[this_count].add(line)
    
    return float(len(sim_sets_new.values()) - len(sim_sets.values()))/float(len(pass_count.keys()))

def score_DM_fail(thisset):
    global failingcnt, failset, pass_count
    
    sim_sets = dict()
    for line in pass_count.keys():
        this_count = pass_count[line]
        if not this_count in sim_sets.keys():
            sim_sets[this_count] = set()
        sim_sets[this_count].add(line)
    ori_DM = len(sim_sets.values())/float(len(pass_count.keys()))
    
    new_linelen = 0
    sim_sets_new = dict()
    for line in pass_count.keys():
        if line not in thisset:
            continue
        new_linelen+=1
        this_count = pass_count[line]
        if not this_count in sim_sets_new.keys():
            sim_sets_new[this_count] = set()
        sim_sets_new[this_count].add(line)
    new_DM = len(sim_sets_new.values())/float(new_linelen)
    
    return new_DM-ori_DM
    
def get_file_lines(file_name):
    if not os.path.exists(file_name):
        sys.stderr.write(f'ERR: Cannot find file {file_name} !')
        exit(1)
    f=open(file_name)
    lines = f.readlines()
    f.close()
    return lines

def update_pass_cov(testname):
    global passingcnt
    
    all_dM_score = 0
    if testname=='': # add ori test pass stmt
        ori_cov_dir = f'{infodir}/fail/'
        for stmt_name in os.listdir(ori_cov_dir):
            if 'small_pass_opt' in stmt_name:
                passingcnt+=1
                
                cov = get_file_lines(ori_cov_dir+stmt_name)

                thisset = set()
                for line in cov:
                    str_line = line.strip()
                    thisset.add(str_line)
                all_dM_score+=score_DM(thisset) 
                
                for str_line in thisset:
                    if str_line in failset:
                        pass_count[str_line]+=1
    else:
        test_cov_dir = f'{passdir}/passcov/{testname}/'
        for stmt_name in os.listdir(test_cov_dir):
            if not '_stmt_info.txt' in stmt_name:
                continue
            passingcnt+=1
            
            cov = get_file_lines(test_cov_dir+stmt_name)
            
            thisset = set()
            for line in cov:
                str_line = line.strip()
                thisset.add(str_line)
            all_dM_score+=score_DM(thisset)
                
            for str_line in thisset:
                if str_line in failset:
                    pass_count[str_line]+=1
    
    return all_dM_score

def update_fail_cov(testname):
    global failingcnt, failset
    
    cov_dir = f'{passdir}/stillfailcov/{testname}/'
    all_dM_score = 0
    for stmtfile in os.listdir(cov_dir):
        if '_stmt_info' in stmtfile:
            failingcnt+=1
            cov=get_file_lines(cov_dir+stmtfile)
            
            thisset = set()
            for line in cov:
                str_line = line.strip()
                thisset.add(str_line)
            all_dM_score+=score_DM_fail(thisset) 

            for line in failset-thisset:
                del pass_count[line]
            failset=failset&thisset
    return all_dM_score

def delete_pass_cov(testname):
    test_cov_dir = f'{passdir}/passcov/{testname}/'
    for stmt_name in os.listdir(test_cov_dir):
        if not '_stmt_info.txt' in stmt_name:
            continue
        stmtfilename = test_cov_dir+stmt_name
        cov = get_file_lines(stmtfilename)
        for line in cov:
            str_line = line.strip()
            if str_line in failset:
                pass_count[str_line]-=1

def init_env():
    # copy mutator exefile
    mutatordir = cfg.get('llvm-locations', 'mutatedir')
    os.system('cp -r ' + mutatordir + 'exefile .')
    os.system('cp -r ' + mutatordir + 'testFile .')
    # copy ori fail.c
    if os.path.exists(passdir + '/failtest'):
        os.system('rm -rf ' + passdir + '/failtest')
    os.system('mkdir -p ' + passdir + '/failtest')
    os.system('cp ' + infodir + '/fail.c ' + passdir + '/failtest')
    os.system('rm *.c')
    os.system('cp ' + infodir + '/fail.c ' + ' ./main.c')
    # init dir
    os.system('mkdir -p ' + failtestdir + 'ori')
    os.system('mkdir -p ' + passdir + '/passcov')
    os.system('mkdir -p ' + stillfailtestdir)
    os.system('mkdir -p ' + passtestdir)

def get_orifail_cov():
    global failingcnt, pass_count
    fail_cov_set = []
    fail_cov_file_set = []
    
    ori_cov_dir = f'{infodir}/fail/'
    
    for testanme in os.listdir(ori_cov_dir):
        if 'small_fail_opt' in testanme:
            failingcnt+=1
            
            this_set = set()
            this_file_set = set()
            cov = get_file_lines(ori_cov_dir+testanme)
            for line in cov:
                str_line = line.strip()
                file_name = line.strip().split(':')[0]
                this_set.add(str_line)
                this_file_set.add(file_name)
                
            if len(fail_cov_set)==0:
                fail_cov_set.append(this_set)
                fail_cov_file_set.append(this_file_set)
            else:
                fail_cov_set[0]=(fail_cov_set[0])&this_set
                fail_cov_file_set[0]=(fail_cov_file_set[0])&this_file_set
    
    for cov in fail_cov_set[0]:
        pass_count[cov] = 0
                
    return fail_cov_set[0], fail_cov_file_set[0]

def init_position_A2C():
    # return pos_list, pos_rank_list, pos_dict
    os.system('./exefile/mutator-pos ./main.c -- ./exefile/pos_rank.txt init')
    tmp_pos_list=[] # all avaliable positions
    tmp_pos_rank_list=[] # positions' score, also the state of position A2C
    tmp_pos_dict=dict() # <pos, index in rank list array>, just for the convenience of finding the index
    tmp_cnt=0
    rank_file=open('./exefile/pos_rank.txt','r')
    rank_lines = rank_file.readlines()
    for line in rank_lines:
        pos=line.split(':')[0].strip()
        score=0
        tmp_pos_dict[pos]=tmp_cnt
        tmp_pos_list.append(pos)
        tmp_pos_rank_list.append(float(score))
        tmp_cnt+=1
    rank_file.close()
    return tmp_pos_list, tmp_pos_rank_list, tmp_pos_dict

def init_avaliable_actions():
    tmp_actions=[]
    tmp_pos_ind_available=[]
    tmp_mutator_available_in_class=[]
    for i in range(M_NET_DIM):
        tmp_mutator_available_in_class.append(set())
    action_file_path = cfg.get('llvm-locations', 'actionFile')
    action_file = open(action_file_path)
    lines = action_file.readlines()
    for i in range(len(lines)):
        line = lines[i].strip()
        tmp_actions.append(line)
        # collect pos can mutate
        classfile = line.split(';')[0]
        inputslist = line.split(';')[1].split(',')
        for j in range(len(inputslist)):
            inputslist[j] = '\"' + inputslist[j] + '\"'
        inputsstr = ' '.join(inputslist)
        if inputsstr=='""':
            inputsstr=' '
        if i<134:
            os.system('./exefile/' + classfile+'-sel' + ' ./main.c -- ' + inputsstr +' ./exefile/pos_sel.txt')
        else:
            os.system('./exefile/' + classfile+'-sel' + ' ./main.c -- ./exefile/pos_sel.txt')
        
        positions = set()
        pos_file=open('./exefile/pos_sel.txt','r')
        pos_lines = pos_file.readlines()
        for line in pos_lines:
            pos=line.strip()
            positions.add(pos_dict[pos])
        pos_file.close()
        
        tmp_pos_ind_available.append(positions)
        
        # collect mutator can mutate
        if len(positions)!=0:
            tmp_mutator_available_in_class[findClassNo(i)].add(i)
    return tmp_actions, tmp_mutator_available_in_class, tmp_pos_ind_available

def read_small_opts(small_pass_opt_record_path, small_fail_opt_record_path):
    f_pass=open(small_pass_opt_record_path)
    small_pass_opts=f_pass.readlines()
    f_pass.close()
    
    for i in range(0,len(small_pass_opts)):
        small_pass_opts[i]=small_pass_opts[i].strip()
    
    f_fail=open(small_fail_opt_record_path)
    small_fail_opts=f_fail.readlines()
    f_fail.close()
    
    for i in range(0,len(small_fail_opts)):
        small_fail_opts[i]=small_fail_opts[i].strip()
    
    return small_pass_opts, small_fail_opts

def res_consist(res_1, res_2):
    if res_1==res_2:
        return True
    if ('Please submit a full bug report' in res_1) and ('Please submit a full bug report' in res_2):
        return True
    return False

def check_before_collect_cov(actionNo):
    ### test if mutate file is same with ori file
    if os.path.exists('difftmp'):
        os.system('rm difftmp')
    os.system('diff main.c mainvar.c > difftmp')
    f = open('difftmp')
    difflines = f.readlines()
    f.close()
    if len(difflines) == 0:
        return False, 'Mutate Diff=0'

    ### test if this prog exist or is a fake passing
    flagIsDiff = diffWithExistingPass(passtestdir, failtestdir) # in toolkit.py
    if flagIsDiff != 'diff' and actionNo < 159: # #pragma never cause fake pass
        return False, flagIsDiff
    flagIsDiff = diffWithExistingPass(stillfailtestdir, failtestdir) # in toolkit.py
    if flagIsDiff != 'diff' and actionNo < 159: # #pragma never cause fake pass
        return False, flagIsDiff

    ### test if mutate file pass
    this_pass_res = []
    for small_pass_opt in small_pass_opts:
        tmp_pass_res = get_big_res(llvmpath, small_pass_opt, 'mainvar.c')
        if tmp_pass_res=='FL_checkpass_err' or tmp_pass_res=='FL_time_out':
            return False, 'pass_opt checkpass_fail'
        if len(this_pass_res)==0:
            this_pass_res.append(tmp_pass_res)
        else:
            if not res_consist(this_pass_res[0], tmp_pass_res):
                return False, 'pass_res_inconsist'
    
    this_fail_res = []
    for small_fail_opt in small_fail_opts:
        tmp_fail_res = get_big_res(llvmpath, small_fail_opt, 'mainvar.c')
        if len(this_fail_res)==0:
            this_fail_res.append(tmp_fail_res)
        else:
            if not res_consist(this_fail_res[0], tmp_fail_res):
                return False, 'fail_res_inconsist'

    if res_consist(this_pass_res[0], this_fail_res[0]):
        return True, 'pass'
    else:
        return True, 'fail'

###################################################### main process

### args
revisionnumber = sys.argv[1]
compilationOptionsRight = sys.argv[2].replace('+', ' ')
compilationOptionsWrong = sys.argv[3].replace('+', ' ')
checkpass = sys.argv[4]
roundcount = sys.argv[5]
configFile = sys.argv[6]
bugId = sys.argv[7]

### basic config
cfg = ConfigParser()
cfg.read(configFile)
main_path = cfg.get('llvm-locations', 'maindir')
sys.path.append(main_path)
from get_res_cov import checkIsPass, get_big_res, get_small_res, collect_one_cov_dir_big, collect_one_cov_dir_small
from delete import delete
from src.util import *
GAMMA = cfg.getfloat('params', 'gamma')
alpha = cfg.getfloat('params', 'alpha')
compilersdir = cfg.get('llvm-locations', 'compilersdir') + '/' + revisionnumber + '-build/'
passdir = cfg.get('llvm-locations', 'passdir') + roundcount + '/' + bugId
infodir = cfg.get('llvm-locations', 'infodir') + bugId
bindir = compilersdir + 'bin/'
llvmpath = compilersdir + 'bin/clang'
if bugId=='44705':
    gcovpath = '/home/lyj/build-gcc-7.5.0/bin/gcov'
else:
    gcovpath = 'gcov'
covdir = compilersdir

### opts
small_pass_opt_record_path = f'{infodir}/small_pass_opt.txt'
small_fail_opt_record_path = f'{infodir}/small_fail_opt.txt'
small_pass_opts, small_fail_opts = read_small_opts(small_pass_opt_record_path, small_fail_opt_record_path)

failtestdir = './failtest'
stillfailtestdir = './stillfailtest'
passtestdir = './passtest'

### init pass dir (the work dir)
if os.path.exists(passdir):
    os.system('rm -rf ' + passdir)
os.system('mkdir -p ' + passdir)
os.chdir(passdir)

### init env
init_env()

### init cov
## init cnt
all_test_cnt = 0
passingcnt = 0
failingcnt = 0 
pass_count = dict()
## get ori fail/pass cov
failset, fail_f_set = get_orifail_cov()

print(f'fail_f_set:{fail_f_set}')

## add ori test pass cov
init_score = update_pass_cov('')

### init A2C
## basic
stepForward = cfg.getint('params', 'miu') # how many future steps we analyze
cntStepForward = 0 # cntStepForward is the number of step in one batch, used for recording and quiting one batch
## mutator A2C
# buffer_s, buffer_a, buffer_r are used to record the states, actions and rewards during one 'stepForward'
buffer_s = []
buffer_a = []
buffer_r = []
# last_reward_score = 0
# input/output dim
M_NET_DIM = 31
# init state
ini_stat = np.zeros(M_NET_DIM)
# the net
net = Net(M_NET_DIM, M_NET_DIM)
optim = torch.optim.Adam(net.parameters(), lr = cfg.getfloat('params', 'beta'))

## position A2C 
pos_buffer_s = []
pos_buffer_a = []
# input/output dim: changed every fail program: so need to compute
pos_list=[] # all avaliable positions
pos_rank_list=[] # positions' score, also the state of position A2C
pos_dict=dict() # <pos, index in rank list array>, just for the convenience of finding the index
pos_list, pos_rank_list, pos_dict = init_position_A2C()
N_NET_DIM=len(pos_list) # number of avaliable positions, input/output dim of A2C
# init state
pos_rank_list=np.array(pos_rank_list)
# the net
pos_net = Net(N_NET_DIM, N_NET_DIM)
pos_optim = torch.optim.Adam(pos_net.parameters(), lr = cfg.getfloat('params', 'beta'))

### init avaliable actions (and their positions)
actions = []
mutator_available_in_class = [] # mutate class - set of avaliable actions(action == a mutator)
pos_ind_available = [] # action - set of avaliable positions (index in pos_list)
actions, mutator_available_in_class, pos_ind_available = init_avaliable_actions()

### begin main search process
log_writer = Log('recordfile.txt', pos_list, actions)
starttime = time.time()

while True:
    ### record time
    endtime = time.time()
    gaptime = endtime - starttime
    if gaptime > 3600: # set the time limit to one hour
        break
    
    ################### get mutate test
    
    ####### get actionNo, mutate_pos
    ### classNo
    mutate_class_available = [i for i, s in enumerate(mutator_available_in_class) if len(s) > 0]
    classNo = random.choice(list(mutate_class_available))
    
    ### actionNo
    avaliable_action = [act for act in mutator_available_in_class[classNo]]
    actionNo = random.choice(avaliable_action)
    
    mutationNo = actionNo + 1
    commandMutate = actions[actionNo]
    classfile = commandMutate.strip().split(';')[0]
    
    inputslist = commandMutate.strip().split(';')[1].split(',')
    for i in range(len(inputslist)):
        inputslist[i] = '\"' + inputslist[i] + '\"'
    inputsstr = ' '.join(inputslist)
    if inputsstr=='""':
        inputsstr=' '
    
    ### mutate_pos
    available_pos = pos_ind_available[actionNo]
    mutate_pos = pos_list[random.choice(list(available_pos))]
    
    ####### do mutate
    testname = f'{classfile}_{actionNo}_{mutate_pos}_{all_test_cnt+1}'
    
    ### mut_cmd_line
    mut_cmd_line = f'./exefile/{classfile}-mul ./main.c -- {inputsstr} {mutate_pos}'
    if actionNo==134: # goto need another pos, random choose one
        mutate_pos_ind_2 = random.choice(list(available_pos))
        mutate_pos_2 = pos_list[mutate_pos_ind_2]
        mut_cmd_line += f' {mutate_pos_2}'
        
    ### record this mutate
    log_writer.record_new_mut(commandMutate)
    log_writer.record_mut_pos(mutate_pos, mut_cmd_line)
    log_writer.record_stat_before_mut(pos_ind_available, actionNo, mutator_available_in_class)
    
    ### mutate
    if os.path.exists('mainvar.c'):
        os.system('rm mainvar.c')
    os.system(f'timeout 10 {mut_cmd_line}')

        
    
    ####### do some check
    check_res, check_type = check_before_collect_cov(actionNo)
    if not check_res:
        log_writer.record_false(check_type, time.time()-starttime)
        continue
    log_writer.record_line(f'Get: {check_type}')
    
    ####### get a true fail test
    if check_type=='fail':
        ### collect fail cov
        all_test_cnt += 1
        begin_cov_time = time.time()
        
        stmtdir = f'{passdir}/stillfailcov/{testname}'
        exccmd(f'mkdir -p {stmtdir}')
        
        idx=0
        for small_fail_opt in small_fail_opts:
            idx+=1
            stmtfilename = f'{stmtdir}/{idx}_stmt_info.txt'
            collect_one_cov_dir_big('.', stmtfilename, covdir, gcovpath, llvmpath, small_fail_opt, 'mainvar', fail_f_set)
        log_writer.record_time('Collect cov Gap', time.time()-begin_cov_time)
        
        ### add to fail_cont
        reward_score = update_fail_cov(testname)
        os.system(f'mv mainvar.c {stillfailtestdir}/{testname}.c')
        
        log_writer.record_true(reward_score, time.time()-starttime)
    else: # pass
        ### collect pass cov
        all_test_cnt += 1
        begin_cov_time = time.time()
        
        stmtdir = f'{passdir}/passcov/{testname}'
        exccmd(f'mkdir -p {stmtdir}')
    
        idx=0
        for small_fail_opt in small_fail_opts:
            idx+=1
            stmtfilename = f'{stmtdir}/{idx}_stmt_info.txt'
            collect_one_cov_dir_big('.', stmtfilename, covdir, gcovpath, llvmpath, small_fail_opt, 'mainvar', fail_f_set)
        log_writer.record_time('Collect cov Gap', time.time()-begin_cov_time)
    
        ### add to pass_cont
        reward_score = update_pass_cov(testname)
        os.system(f'mv mainvar.c {passtestdir}/{testname}.c')
        
        log_writer.record_true(reward_score, time.time()-starttime)

delete(bugId, roundcount, configFile)

