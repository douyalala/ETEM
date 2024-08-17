import sys, os, subprocess, re, time
from multiprocessing import Pool
from configparser import ConfigParser
from itertools import combinations, combinations_with_replacement

def collect_small_ori_fail_cov(bugId, rev, checkpass, ori_fail_res, ori_pass_res, small_pass_opts, small_wrong_opts, cfg, tmp_log):
    compilersdir = cfg.get('llvm-locations', 'compilersdir')
    loops = cfg.getint('params', 'loops')
    
    covdir = f'{compilersdir}/{rev}-build/'
    llvm_path = f'{compilersdir}/{rev}-build/bin/clang'
    gcov_path = 'gcov'
    
    infodir = cfg.get('llvm-locations', 'infodir')
    ori_fail_test = f'{infodir}/{bugId}/fail'
    
    stmtfiledir = f'{infodir}/{bugId}/fail/'
    os.system('rm -rf ' + stmtfiledir)
    os.system('mkdir -p ' + stmtfiledir)
    
    fail_files = set()
    
    idx = 0
    for small_wrong_opt in small_wrong_opts:
        idx+=1
        tmp_log.record_line(f'----- {idx} = {small_wrong_opt}')
        stmtfilename = f'{stmtfiledir}/{idx}_small_fail_opt_stmt_info.txt'
        
        tmp_log.record_line(f'collecting...{stmtfilename}')
        collect_one_cov_dir_big(stmtfiledir, stmtfilename, covdir, gcov_path, llvm_path, small_wrong_opt, ori_fail_test)
        f=open(stmtfilename)
        lines=f.readlines()
        f.close()
        # collect-utils.c:172
        for line in lines:
            file_name = line.split(':')[0]
            fail_files.add(file_name)
    
    idx = 0
    for small_pass_opt in small_pass_opts:
        idx+=1
        tmp_log.record_line(f'----- {idx} = {small_pass_opt}')
        stmtfilename = f'{stmtfiledir}/{idx}_small_pass_opt_stmt_info.txt'
        
        tmp_log.record_line(f'collecting...{stmtfilename}')
        collect_one_cov_dir_big(stmtfiledir, stmtfilename, covdir, gcov_path, llvm_path, small_pass_opt, ori_fail_test, fail_files)

def reverse_one_opt(opt):
    if '=' in opt_line:
        opt_line = opt.split('=')[0].strip()
        now_value = opt.split('=')[1].strip()
        
        if now_value=='0':
            return opt_line+'=1'
        else:
            return opt_line+'=0'
    else:
        os.system(f'echo {opt_line} err! > /data1/lyj/err.log')

def get_fine_opt(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, cfg, tmp_log):
    compilersdir = cfg.get('llvm-locations', 'compilersdir')
    llvm_path = f'{compilersdir}/{rev}-build/bin/clang'
    llvm_bin_path = f'{compilersdir}/{rev}-build/bin'

    infodir = cfg.get('llvm-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    opt_levels = ['-O0','-O1', '-O2', '-Os', '-O3']
    
    fine_opts = []
    last_pass_O = '-1'
    first_fail_O = ''
    for opt_level in opt_levels:
        opt = re.sub('-O([0-3]|s)', opt_level, fail_opt)
        this_res = get_big_res(llvm_path, opt, ori_fail_test)
        check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
        if not check == 'pass': # the smallest big Ox that fail
            first_fail_O = opt_level

            help_bytes = subprocess.Popen(f'{llvm_bin_path}/clang {opt} -mllvm --help-hidden {ori_fail_test}', shell=True,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            help_list = help_bytes.stdout.read().decode('utf-8').split('\n')
            
            res_bytes = subprocess.Popen(f'{llvm_bin_path}/clang {opt} -mllvm --print-all-options {ori_fail_test}', shell=True,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            res_list = res_bytes.stdout.read().decode('utf-8').split('\n')
            
            for line in res_list:
                # --inline-call-penalty = 25 (default: 25)
                if '(' not in line or '--' not in line:
                    continue
                opt_line = line.split('=')[0].strip()
                now_val = line.split('=')[1].strip().split('(')[0].strip()
                
                if '--print-all-options' in opt_line or '--stats' in opt_line:
                    continue
                if not (now_val=='0' or now_val=='1'):
                    continue
                
                skip = True
                for help_line in help_list:
                    if (opt_line+' ' in help_line) and (opt_line+'=' not in help_line):
                        if (('Enable' in help_line) or ('enable' in help_line)) and now_val=='1':
                            skip = False
                        elif (('Disable' in help_line) or ('disable' in help_line)) and now_val=='0':
                            skip = False
                    if not skip:
                        break
                if not skip:
                    fine_opts.append(f'{opt_line}={now_val}')
            break
        else:
            last_pass_O = opt_level
    return last_pass_O, first_fail_O, fine_opts

def get_ori_fail_pass_res(bugId, rev, pass_opt, fail_opt, checkpass, cfg, tmp_log):
    compilersdir = cfg.get('llvm-locations', 'compilersdir')
    llvm_path = f'{compilersdir}/{rev}-build/bin/clang'

    infodir = cfg.get('llvm-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    ori_fail_res = get_big_res(llvm_path, fail_opt, ori_fail_test)
    ori_pass_res = get_big_res(llvm_path, pass_opt, ori_fail_test)
    
    return ori_fail_res, ori_pass_res

def check_spilt_opt_can_fail(bugId, rev, first_fail_O, checkpass, ori_fail_res, ori_pass_res, fine_opts, cfg, tmp_log):
    compilersdir = cfg.get('llvm-locations', 'compilersdir')
    llvm_path = f'{compilersdir}/{rev}-build/bin/clang'
    
    infodir = cfg.get('llvm-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    opt_lines = f'{first_fail_O} -mllvm ' + ' -mllvm '.join(fine_opts)
    this_res = get_big_res(llvm_path, opt_lines, ori_fail_test)
    
    tmp_log.record_line(f'---opts:all')
    tmp_log.record_line(this_res)
    
    check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
    if not check == 'still_fail':
        return False
    return True

def find_bug_related_opts(bugId, rev, first_fail_O, checkpass, ori_fail_res, ori_pass_res, fine_opts, cfg, tmp_log):
    compilersdir = cfg.get('llvm-locations', 'compilersdir')
    llvm_path = f'{compilersdir}/{rev}-build/bin/clang'
    
    infodir = cfg.get('llvm-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    bug_related_opts = []
    
    for i in range(0, len(fine_opts)):
        opt = fine_opts[i]
        tmp_opts = fine_opts.copy()
        tmp_opts[i] = reverse_one_opt(opt)
        opt_lines = f'{first_fail_O} -mllvm '+' -mllvm '.join(tmp_opts)

        this_res = get_big_res(llvm_path, opt_lines, ori_fail_test)
        
        # tmp_log.record_line(f'--ori-opt:{opt}')
        # tmp_log.record_line(this_res)
        
        check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
        if check == 'pass':
            bug_related_opts.append(opt)
    return bug_related_opts

def search_small_opt_set_fail(bugId, rev, fail_opt, first_fail_O, checkpass, ori_fail_res, ori_pass_res, bug_free_opts, bug_related_opts, n, cfg, tmp_log):
    if n > 2:
        return [set(bug_free_opts)], [fail_opt]
    # return [set(bug_free_opts)], [fail_opt]
    
    compilersdir = cfg.get('llvm-locations', 'compilersdir')
    llvm_path = f'{compilersdir}/{rev}-build/bin/clang'
    
    infodir = cfg.get('llvm-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    # 搜索的是要开开的bug free， n从1到len
    res_options = []
    res_open_bfs = []
    able_bug_free_sets = combinations(bug_free_opts, n)
    for able_bug_free_set in able_bug_free_sets:
        disable_bug_free_opts = list(set(bug_free_opts)-set(able_bug_free_set))
        enable_options = list(set(bug_related_opts)|set(able_bug_free_set))
        options = first_fail_O
        for bf in disable_bug_free_opts:
            options += f' -mllvm {reverse_one_opt(bf)}'
        for br in enable_options:
            options += f' -mllvm {br}'
        this_res = get_big_res(llvm_path, options, ori_fail_test)
        check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
        tmp_log.record_line(f'- able_bug_free_set: {set(able_bug_free_set)}: {check}')
        if check != 'pass':
            res_options.append(options)
            res_open_bfs.append(set(able_bug_free_set))
            if len(res_options)>=10:
                break
    if len(res_options)!=0:
        return res_open_bfs, res_options
    return search_small_opt_set_fail(bugId, rev, fail_opt, first_fail_O, checkpass, ori_fail_res, ori_pass_res, bug_free_opts, bug_related_opts, n+1, cfg, tmp_log)

def search_small_opt_set_pass(smalll_pass_opts, small_fail_opts ,bugId, rev, first_fail_O, checkpass, ori_fail_res, ori_pass_res, bug_related_opts, bug_free_opts, n, cfg, tmp_log, stop=True):
    if n > len(bug_related_opts): # no small pass opt set
        return smalll_pass_opts, small_fail_opts
    
    if len(smalll_pass_opts)>=50:
        return smalll_pass_opts, small_fail_opts
    
    compilersdir = cfg.get('llvm-locations', 'compilersdir')
    llvm_path = f'{compilersdir}/{rev}-build/bin/clang'
    
    infodir = cfg.get('llvm-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    # 搜索的是要关闭的bug related, n从1到len(bug_related_opts)
    res_options = []
    res_small_fail = []
    disable_bug_related_sets = combinations(bug_related_opts, n)
    for disable_bug_related_set in disable_bug_related_sets:
        options = first_fail_O
        disable_opts = list(set(bug_free_opts)|set(disable_bug_related_set))
        enable_opts = list(set(bug_related_opts)-set(disable_bug_related_set))
        for opt in disable_opts:
            options += f' -mllvm {reverse_one_opt(opt)}'
        for opt in enable_opts:
            options += f' -mllvm {opt}'
        this_res = get_big_res(llvm_path, options, ori_fail_test)
        check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
        tmp_log.record_line(f'- disable_bug_related_set: {set(disable_bug_related_set)}: {check}')
        if check == 'pass':
            res_options.append(options)
            if len(smalll_pass_opts+res_options)>=50:
                break
        elif check != 'pass':
            res_small_fail.append(options)
    if (stop==False) and (len(res_options)!=0):
        return res_options, small_fail_opts+res_small_fail

    if len(smalll_pass_opts+res_options)>=50:
        return smalll_pass_opts+res_options, small_fail_opts+res_small_fail
    return search_small_opt_set_pass(smalll_pass_opts+res_options, small_fail_opts+res_small_fail, bugId, rev, first_fail_O, checkpass, ori_fail_res, ori_pass_res, bug_related_opts, bug_free_opts, n+1, cfg, tmp_log)
        
def search_small_pass_fail_opts(bugId, rev, first_fail_O, checkpass, ori_fail_res, ori_pass_res, fine_opts, bug_related_opts, cfg, tmp_log):
    compilersdir = cfg.get('llvm-locations', 'compilersdir')
    llvm_path = f'{compilersdir}/{rev}-build/bin/clang'

    infodir = cfg.get('llvm-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    small_pass_opts = []
    small_fail_opts = []
    
    # bug_free_opts = list(set(fine_opts)-set(bug_related_opts)-{'-frtti'})
    bug_free_opts = list(set(fine_opts)-set(bug_related_opts))
 
    # able bug-related, disable bug-free, fail?
    tmp_log.record_line('---able bug-related, disable bug-free')
    options = first_fail_O
    for bf in bug_free_opts:
        options += f' -mllvm {reverse_one_opt(bf)}'
    for br in bug_related_opts:
        options += f' -mllvm {br}'
    
    tmp_log.record_line(f'opts: {options}')
    this_res = get_big_res(llvm_path, options, ori_fail_test)
    check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
    tmp_log.record_line(f'this_res: {this_res}')
    tmp_log.record_line(f'check: {check}')
    if check != 'pass':
        tmp_log.record_line('able bug-related, disable bug-free, fail')
        tmp_log.record_line('now disable bug-related, looking for near pass opt')
        small_fail_opts.append(options)
        small_pass_opts, small_fail_opts = search_small_opt_set_pass([], small_fail_opts ,bugId, rev, first_fail_O, checkpass, ori_fail_res, ori_pass_res, bug_related_opts, bug_free_opts, 1, cfg, tmp_log, False)
        return small_pass_opts, small_fail_opts
    
    tmp_log.record_line('able bug-related, disable bug-free, but pass')
    tmp_log.record_line('now able bug-free, looking for near fail opt')
    open_bfs, small_fail_opts = search_small_opt_set_fail(bugId, rev, fail_opt, first_fail_O, checkpass, ori_fail_res, ori_pass_res, bug_free_opts, bug_related_opts, 1, cfg, tmp_log)
    
    for i in range(1, 2):
        for open_bf in open_bfs:
            tmp_log.record_line(f'---open bf: {open_bf}, search num:{i}')
            open_bf_list = list(open_bf)
            new_bf_list = list(set(bug_free_opts)-open_bf)
            near_pass_opt, small_fail_opts = search_small_opt_set_pass([], small_fail_opts ,bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, bug_related_opts+open_bf_list, new_bf_list, i, cfg, tmp_log, False)
            small_pass_opts = small_pass_opts+near_pass_opt
            small_pass_opts = list(dict.fromkeys(small_pass_opts)) # 保留顺序，去重
            if len(small_pass_opts)>=50:
                break
        if len(small_pass_opts)>=50:
            break
    return small_pass_opts, small_fail_opts

def get_small_opt(revline, work_dir):
    os.chdir(work_dir)
    
    bugId = revline.split(',')[0]
    rev = revline.split(',')[1]
    pass_opt = revline.split(',')[2].replace('+', ' ')
    fail_opt = revline.split(',')[3].replace('+', ' ')
    checkpass = revline.split(',')[4]
    
    start_time = time.time()
    
    log_path = f'{work_dir}/get_small_opt.log'
    if os.path.exists(log_path):
        os.system(f'rm -rf {log_path}')
    
    print(f'log in {log_path}')
    tmp_log = Log(log_path)
    tmp_log.record_line(revline)

    ori_fail_res, ori_pass_res = get_ori_fail_pass_res(bugId, rev, pass_opt, fail_opt, checkpass, cfg, tmp_log)
    tmp_log.record_line('-----ori_fail_res:')
    tmp_log.record_line(ori_fail_res)
    tmp_log.record_line('-----ori_pass_res:')
    tmp_log.record_line(ori_pass_res)

    last_pass_O, first_fail_O, fine_opts = get_fine_opt(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, cfg, tmp_log)
    fail_opt = re.sub('-O([0-3]|s)', first_fail_O, fail_opt)
    small_opt_num = len(fine_opts)
    tmp_log.record_line(f'-----fine_opts:{small_opt_num}')
    tmp_log.record_line(first_fail_O + ': ' +' '.join(fine_opts))
    
    check_can_fail = check_spilt_opt_can_fail(bugId, rev, first_fail_O, checkpass, ori_fail_res, ori_pass_res, fine_opts, cfg, tmp_log)
    if not check_can_fail:
        small_pass_opts = [re.sub('-O([0-3]|s)', last_pass_O, fail_opt)]
        small_fail_opts = [fail_opt]
    else:
        bug_related_opts = find_bug_related_opts(bugId, rev, first_fail_O, checkpass, ori_fail_res, ori_pass_res, fine_opts, cfg, tmp_log)
        tmp_log.record_line('-----bug_related_opts:')
        tmp_log.record_line(','.join(bug_related_opts))
        small_pass_opts, small_fail_opts = search_small_pass_fail_opts(bugId, rev, first_fail_O, checkpass, ori_fail_res, ori_pass_res, fine_opts, bug_related_opts, cfg, tmp_log)
        if len(small_pass_opts)==0:
            small_pass_opts = [re.sub('-O([0-3]|s)', last_pass_O, fail_opt)]
    
    tmp_log.record_line('-----small_pass_opts:')
    tmp_log.record_line('\n'.join(small_pass_opts[0:50]))
    tmp_log.record_line('-----small_fail_opts:')
    tmp_log.record_line('\n'.join(small_fail_opts[0:10]))
    
    small_pass_opt_record_path = f'{work_dir}/small_pass_opt.txt'
    small_fail_opt_record_path = f'{work_dir}/small_fail_opt.txt'
    if os.path.exists(small_pass_opt_record_path):
        os.system(f'rm -rf {small_pass_opt_record_path}')
        os.system(f'rm -rf {small_fail_opt_record_path}')
    small_pass_opt_record = Log(small_pass_opt_record_path)
    small_fail_opt_record = Log(small_fail_opt_record_path)
    small_pass_opt_record.record_line( '\n'.join(small_pass_opts[0:50]) )
    small_fail_opt_record.record_line( '\n'.join(small_fail_opts[0:10]) )
    
    end_time = time.time()
    tmp_log.record_line(f'-----search time: {end_time - start_time}')

    collect_small_ori_fail_cov(bugId, rev, checkpass, ori_fail_res, ori_pass_res, small_pass_opts[0:50], small_fail_opts[0:10], cfg, tmp_log)
    
    tmp_log.record_line('finish')
    print(f'{bugId} finish')
    
    end_time = time.time()
    tmp_log.record_line(f'time: {end_time - start_time}')

configFile = sys.argv[1]
cfg = ConfigParser()
cfg.read(configFile)
main_path = cfg.get('llvm-locations', 'maindir')
sys.path.append(main_path)
from get_res_cov import checkIsPass, get_big_res, collect_one_cov_dir_big
from src.util import *

bugList = cfg.get('llvm-locations', 'bugList')
infodir = cfg.get('llvm-locations', 'infodir')
revfile = open(bugList)
revlines = revfile.readlines()
revfile.close()

p = Pool(processes = 5)
skip = True
for revline in revlines:
    if revline.strip().split(',')[5] == 'install_no':
        continue
    bugId = revline.split(',')[0]
    if bugId in ['44705']:
        continue
    work_dir = f'{infodir}/{bugId}/'
    p.apply_async(get_small_opt, args=(revline, work_dir,))
p.close()
p.join()
