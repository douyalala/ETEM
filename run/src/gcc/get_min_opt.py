import sys, os, subprocess, re, time
from multiprocessing import Pool
from configparser import ConfigParser
from itertools import combinations, combinations_with_replacement

def collect_small_ori_fail_cov(bugId, rev, checkpass, ori_fail_res, ori_pass_res, small_pass_opts, small_wrong_opts, cfg, tmp_log):
    compilersdir = cfg.get('gcc-locations', 'compilersdir')
    loops = cfg.getint('params', 'loops')
    
    covdir = compilersdir + rev + '-build/gcc'
    bindir = compilersdir + rev + '-build/bin/'
    gcc_path = compilersdir + rev + '-build/bin/gcc'
    
    infodir = cfg.get('gcc-locations', 'infodir')
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
        collect_one_cov_dir(stmtfiledir, stmtfilename, covdir, bindir, small_wrong_opt, ori_fail_test)
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
        collect_one_cov_dir(stmtfiledir, stmtfilename, covdir, bindir, small_pass_opt, ori_fail_test, fail_files)

def recollect_bug_ori_fail_pass_cov(bugId, rev, checkpass, ori_fail_res, ori_pass_res, small_pass_opts, small_wrong_opts, cfg, tmp_log):
    compilersdir = cfg.get('gcc-locations', 'compilersdir')
    loops = cfg.getint('params', 'loops')
    
    covdir = compilersdir + rev + '-build/gcc'
    bindir = compilersdir + rev + '-build/bin/'
    gcc_path = compilersdir + rev + '-build/bin/gcc'
    
    infodir = cfg.get('gcc-locations', 'infodir')
    ori_fail_test = f'{infodir}/{bugId}/fail'
    
    idx = 0
    stmtfiledir = f'{infodir}/{bugId}/fail/'
    os.system(f'rm {stmtfiledir}/*_small_pass_opt_stmt_info.txt')
    for small_pass_opt in small_pass_opts:
        idx+=1
        tmp_log.record_line(f'----- {idx} = {small_pass_opt}')
        stmtfilename = f'{stmtfiledir}/{idx}_small_pass_opt_stmt_info.txt'
        if os.path.exists(stmtfilename):
            continue
        os.system('mkdir -p ' + stmtfiledir)
        tmp_log.record_line(f'collecting...{stmtfilename}')
        collect_one_cov_dir(stmtfiledir, stmtfilename, covdir, bindir, small_pass_opt, ori_fail_test)
        
    idx = 0
    for small_wrong_opt in small_wrong_opts:
        idx+=1
        tmp_log.record_line(f'----- {idx} = {small_wrong_opt}')
        
        # ori fail
        stmtfiledir = f'{infodir}/{bugId}/fail/'
        # os.system(f'rm {stmtfiledir}/{idx}_small_fail_opt_stmt_info.txt')
        stmtfilename = f'{stmtfiledir}/{idx}_small_fail_opt_stmt_info.txt'
        os.system('mkdir -p ' + stmtfiledir)
        tmp_log.record_line(f'collecting...{stmtfilename}')
        collect_one_cov_dir(stmtfiledir, stmtfilename, covdir, bindir, small_wrong_opt, ori_fail_test)
        
    # pass
    for loop in range(1, loops + 1):
        passdir = cfg.get('gcc-locations', 'passdir')
        passdir += str(loop) 
        os.system('rm -rf ' + passdir + '/' + bugId + '/small_opt_passcov')
        os.system('mkdir -p ' + passdir + '/' + bugId + '/small_opt_passcov')
        
        for i in os.listdir(passdir + '/' + bugId + '/passtest'):
            if not i.endswith('.c'):
                continue
            testname = i.split('.c')[0]
            test_path = passdir + '/' + bugId + '/passtest/' + testname
            
            true_pass = True
            for small_wrong_opt in small_wrong_opts:
                if checkpass == 'checkIsPass_zeroandcrush':
                    this_res = get_res_crash(gcc_path, small_wrong_opt, f'{test_path}.c')
                else:
                    this_res = get_res(gcc_path, small_wrong_opt, f'{test_path}.c')
                check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
                if not check=='pass': 
                    true_pass=False
                    break
            
            if not true_pass:
                continue
                
            # real pass
            stmtfiledir = f'{passdir}/{bugId}/small_opt_passcov/{testname}/'
            tmp_log.record_line(f'---real pass: {stmtfiledir}')
            
            idx = 0
            for small_wrong_opt in small_wrong_opts:
                idx+=1
                stmtfilename = f'{stmtfiledir}/{idx}_stmt_info.txt'
                os.system('mkdir -p ' + stmtfiledir)
                if os.path.exists(stmtfilename):
                    continue
                tmp_log.record_line(f'collecting...{stmtfilename}')
                collect_one_cov_dir(stmtfiledir, stmtfilename, covdir, bindir, small_wrong_opt, test_path)
            
        for i in os.listdir(passdir + '/' + bugId + '/weakpasstest'):
            if not i.endswith('.c'):
                continue
            testname = i.split('.c')[0]
            test_path = passdir + '/' + bugId + '/weakpasstest/' + testname
            
            true_pass = True
            for small_wrong_opt in small_wrong_opts:
                if checkpass == 'checkIsPass_zeroandcrush':
                    this_res = get_res_crash(gcc_path, small_wrong_opt, f'{test_path}.c')
                else:
                    this_res = get_res(gcc_path, small_wrong_opt, f'{test_path}.c')
                check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
                if not check=='pass': 
                    true_pass=False
                    break
            
            if not true_pass:
                continue
            
            # real pass
            stmtfiledir = f'{passdir}/{bugId}/small_opt_passcov/weak{testname}/'
            tmp_log.record_line(f'---real pass: {stmtfiledir}')
                
            idx = 0
            for small_wrong_opt in small_wrong_opts:
                idx+=1
                stmtfilename = f'{stmtfiledir}/{idx}_stmt_info.txt'
                os.system('mkdir -p ' + stmtfiledir)
                if os.path.exists(stmtfilename):
                    continue
                tmp_log.record_line(f'collecting...{stmtfilename}')
                collect_one_cov_dir(stmtfiledir, stmtfilename, covdir, bindir, small_wrong_opt, test_path)
        # # fail
        # for loop in range(1, loops + 1):
        #     passdir = cfg.get('gcc-locations', 'passdir')
        #     passdir += str(loop) 
        #     # os.system('rm -rf ' + passdir + '/' + bugId + '/small_opt_failcov')
        #     os.system('mkdir -p ' + passdir + '/' + bugId + '/small_opt_failcov')
                
        #     all_fail_test = dict()
        #     for i in os.listdir(passdir + '/' + bugId + '/firstfailtest'):
        #         if not i.endswith('.c'):
        #             continue
        #         testname = i.split('.c')[0]
        #         test_cnt = testname.split('_')[2]
        #         all_fail_test[testname]=int(test_cnt)
        #     sort_fail_test = sorted(all_fail_test.items(), key=lambda d: d[1])
        #     tmp_cnt=0
        #     for pair in sort_fail_test:
        #         if tmp_cnt>=50:
        #             break
        #         testname=pair[0]
        #         test_path = passdir + '/' + bugId + '/firstfailtest/' + testname
        #         if checkpass == 'checkIsPass_zeroandcrush':
        #             this_res = get_res_crash(gcc_path, small_wrong_opt, f'{test_path}.c')
        #         else:
        #             this_res = get_res(gcc_path, small_wrong_opt, f'{test_path}.c')
        #         check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
        #         if check!='pass': # real fail
        #             tmp_cnt+=1
        #             stmtfiledir = f'{passdir}/{bugId}/small_opt_failcov/{testname}'
        #             stmtfilename = f'{stmtfiledir}/{idx}_stmt_info.txt'
        #             os.system('mkdir -p ' + stmtfiledir)
        #             if os.path.exists(stmtfilename):
        #                 continue
        #             tmp_log.record_line(f'collecting...{stmtfilename}')
        #             collect_one_cov_dir(stmtfiledir, stmtfilename, covdir, bindir, small_wrong_opt, test_path)

def reverse_one_opt(opt):
    if opt.startswith('-fno'):
        reverse_opt = opt.replace('-fno-', '-f', 1)
    else:
        reverse_opt = opt.replace('-f', '-fno-', 1)
    reverse_opt = reverse_opt.split('=')[0].strip()
    return reverse_opt

def get_fine_opt(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, cfg, tmp_log):
    compilersdir = cfg.get('gcc-locations', 'compilersdir')
    gcc_path = f'{compilersdir}/{rev}-build/bin/gcc'

    infodir = cfg.get('gcc-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    opt_levels = ['-O0','-O1', '-O2', '-Os', '-O3', ]
    
    fine_opts = []
    first_fail_O = ''
    for opt_level in opt_levels:
        opt = re.sub('-O([0-3]|s)', opt_level, fail_opt)
        if checkpass == 'checkIsPass_zeroandcrush':
            this_res = get_res_crash(gcc_path, opt, ori_fail_test)
        else:
            this_res = get_res(gcc_path, opt, ori_fail_test)
        check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
        if not check == 'pass': # the smallest big Ox that fail
            first_fail_O = opt_level
            opts = subprocess.Popen(f'{gcc_path} -Q --help=optimizers {opt_level}', shell=True,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            res_list = opts.stdout.read().decode('utf-8').split('\n')
            for res in res_list:
                if not '-f' in res:
                    continue
                if '[disabled]' in res:
                    continue
                if not '[enabled]' in res:
                    continue
                if '-fno-' in res:
                    continue
                if '-frtti' in res:
                    continue
                fine_opts.append(res.strip().split(' ')[0].strip())
            break
    return first_fail_O, fine_opts

def get_ori_fail_pass_res(bugId, rev, pass_opt, fail_opt, checkpass, cfg, tmp_log):
    compilersdir = cfg.get('gcc-locations', 'compilersdir')
    gcc_path = f'{compilersdir}/{rev}-build/bin/gcc'

    infodir = cfg.get('gcc-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    if checkpass == 'checkIsPass_zeroandcrush':
        ori_fail_res = get_res_crash(gcc_path, fail_opt, ori_fail_test)
        ori_pass_res = get_res_crash(gcc_path, pass_opt, ori_fail_test)
    else:
        ori_fail_res = get_res(gcc_path, fail_opt, ori_fail_test)
        ori_pass_res = get_res(gcc_path, pass_opt, ori_fail_test)
    
    return ori_fail_res, ori_pass_res

def find_bug_related_opts(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, fine_opts, cfg, tmp_log):
    compilersdir = cfg.get('gcc-locations', 'compilersdir')
    gcc_path = f'{compilersdir}/{rev}-build/bin/gcc'
    
    infodir = cfg.get('gcc-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    bug_related_opts = []
    for opt in fine_opts:
        reverse_opt = reverse_one_opt(opt)
        if checkpass == 'checkIsPass_zeroandcrush':
            this_res = get_res_crash(gcc_path, f'{fail_opt} {reverse_opt}', ori_fail_test)
        else:
            this_res = get_res(gcc_path, f'{fail_opt} {reverse_opt}', ori_fail_test)
        check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
        if check == 'pass':
            bug_related_opts.append(opt)
    return bug_related_opts

def search_small_opt_set_fail(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, bug_free_opts, n, cfg, tmp_log):
    if n > 2:
        return [set(bug_free_opts)], [fail_opt]
    # return [set(bug_free_opts)], [fail_opt]
    
    compilersdir = cfg.get('gcc-locations', 'compilersdir')
    gcc_path = f'{compilersdir}/{rev}-build/bin/gcc'
    
    infodir = cfg.get('gcc-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    # 搜索的是要开开的bug free， n从1到len
    res_options = []
    res_open_bfs = []
    able_bug_free_sets = combinations(bug_free_opts, n)
    for able_bug_free_set in able_bug_free_sets:
        disable_bug_free_opts = list(set(bug_free_opts)-set(able_bug_free_set))
        options = fail_opt
        for bf in disable_bug_free_opts:
            options += f' {reverse_one_opt(bf)}'

        if checkpass == 'checkIsPass_zeroandcrush':
            this_res = get_res_crash(gcc_path, options, ori_fail_test)
        else:
            this_res = get_res(gcc_path, options, ori_fail_test)
        check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
        tmp_log.record_line(f'- able_bug_free_set: {set(able_bug_free_set)}: {check}')
        if check != 'pass':
            res_options.append(options)
            res_open_bfs.append(set(able_bug_free_set))
            if len(res_options)>=10:
                break
    if len(res_options)!=0:
        return res_open_bfs, res_options
    return search_small_opt_set_fail(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, bug_free_opts, n+1, cfg, tmp_log)

def search_small_opt_set_pass(smalll_pass_opts, small_fail_opts ,bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, bug_related_opts, bug_free_opts, n, cfg, tmp_log, stop=True):
    if n > len(bug_related_opts): # no small pass opt set
        return smalll_pass_opts, small_fail_opts
    
    if len(smalll_pass_opts)>=50:
        return smalll_pass_opts, small_fail_opts
    
    compilersdir = cfg.get('gcc-locations', 'compilersdir')
    gcc_path = f'{compilersdir}/{rev}-build/bin/gcc'
    
    infodir = cfg.get('gcc-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    # 搜索的是要关闭的bug related, n从1到len(bug_related_opts)
    res_options = []
    res_small_fail = []
    disable_bug_related_sets = combinations(bug_related_opts, n)
    for disable_bug_related_set in disable_bug_related_sets:
        options = fail_opt
        disable_opts = list(set(bug_free_opts)|set(disable_bug_related_set))
        for opt in disable_opts:
            options += f' {reverse_one_opt(opt)}'

        if checkpass == 'checkIsPass_zeroandcrush':
            this_res = get_res_crash(gcc_path, options, ori_fail_test)
        else:
            this_res = get_res(gcc_path, options, ori_fail_test)
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
    return search_small_opt_set_pass(smalll_pass_opts+res_options, small_fail_opts+res_small_fail, bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, bug_related_opts, bug_free_opts, n+1, cfg, tmp_log)
        
def search_small_pass_fail_opts(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, fine_opts, bug_related_opts, cfg, tmp_log):
    compilersdir = cfg.get('gcc-locations', 'compilersdir')
    gcc_path = f'{compilersdir}/{rev}-build/bin/gcc'

    infodir = cfg.get('gcc-locations', 'infodir')
    ori_fail_test = infodir + '/' + bugId + '/fail.c'
    
    small_pass_opts = []
    small_fail_opts = []
    
    # bug_free_opts = list(set(fine_opts)-set(bug_related_opts)-{'-frtti'})
    bug_free_opts = list(set(fine_opts)-set(bug_related_opts))
 
    # able bug-related, disable bug-free, fail?
    tmp_log.record_line('---able bug-related, disable bug-free')
    options = fail_opt
    for bf in bug_free_opts:
        options += f' {reverse_one_opt(bf)}'
    
    tmp_log.record_line(f'opts: {options}')
    if checkpass == 'checkIsPass_zeroandcrush':
        this_res = get_res_crash(gcc_path, options, ori_fail_test)
    else:
        this_res = get_res(gcc_path, options, ori_fail_test)
    check = checkIsPass(ori_fail_res, ori_pass_res, this_res, ori_pass_res)
    tmp_log.record_line(f'this_res: {this_res}')
    tmp_log.record_line(f'check: {check}')
    if check != 'pass':
        tmp_log.record_line('able bug-related, disable bug-free, fail')
        tmp_log.record_line('now disable bug-related, looking for near pass opt')
        small_fail_opts.append(options)
        small_pass_opts, small_fail_opts = search_small_opt_set_pass([], small_fail_opts ,bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, bug_related_opts, bug_free_opts, 1, cfg, tmp_log, False)
        return small_pass_opts, small_fail_opts
    
    tmp_log.record_line('able bug-related, disable bug-free, but pass')
    tmp_log.record_line('now able bug-free, looking for near fail opt')
    open_bfs, small_fail_opts = search_small_opt_set_fail(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, bug_free_opts, 1, cfg, tmp_log)
    
    # for i in range(1, len(set(open_bfs[0]))+len(bug_related_opts)+1 ):
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

def get_history_data(logfile):
    f=open(logfile)
    lines = f.readlines()
    f.close()
    
    flag_small_pass_opts = 0
    small_pass_opts = []
    flag_small_fail_opts = 0
    small_fail_opts = []
    for line in lines:
        if line.startswith('-----small_pass_opts'):
            flag_small_pass_opts=1
            continue
        elif line.startswith('-----small_fail_opts'):
            flag_small_pass_opts=0
            flag_small_fail_opts=1
            continue
        elif line.startswith('----- '):
            break
        if flag_small_pass_opts:
            small_pass_opts.append(line.strip())
        elif flag_small_fail_opts:
            small_fail_opts.append(line.strip())
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

    # first_fail_O, fine_opts = get_fine_opt(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, cfg, tmp_log)
    # fail_opt = re.sub('-O([0-3]|s)', first_fail_O, fail_opt)
    # tmp_log.record_line('-----fine_opts:')
    # tmp_log.record_line(first_fail_O + ': ' +' '.join(fine_opts))

    # bug_related_opts = find_bug_related_opts(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, fine_opts, cfg, tmp_log)
    # tmp_log.record_line('-----bug_related_opts:')
    # tmp_log.record_line(','.join(bug_related_opts))

    # small_pass_opts, small_fail_opts = search_small_pass_fail_opts(bugId, rev, fail_opt, checkpass, ori_fail_res, ori_pass_res, fine_opts, bug_related_opts, cfg, tmp_log)
    small_pass_opts = [pass_opt]
    small_fail_opts = [fail_opt]
    
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
main_path = cfg.get('gcc-locations', 'maindir')
sys.path.append(main_path)
from get_res_cov import checkIsPass, get_res, get_res_crash, collect_one_cov, collect_one_cov_dir
from src.util import *

# bugList = '/home/lyj/compFL/run/gccbugs_backup.txt'
bugList = cfg.get('gcc-locations', 'bugList')
infodir = cfg.get('gcc-locations', 'infodir')
revfile = open(bugList)
revlines = revfile.readlines()
revfile.close()

p = Pool(processes = 5)
for revline in revlines:
    if revline.strip().split(',')[5] == 'install_no':
        continue
    bugId = revline.split(',')[0]
    work_dir = f'{infodir}/{bugId}/'
    # get_small_opt(revline, work_dir)
    # break
    p.apply_async(get_small_opt, args=(revline, work_dir,))
p.close()
p.join()
