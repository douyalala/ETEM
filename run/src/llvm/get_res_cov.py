import os, time
from configparser import ConfigParser
import subprocess

from src.util import exccmd

def get_big_res(llvmPath, options, fileName):
    if os.path.exists('a.out'):
        os.system('rm ./a.out')
    os.system(f'timeout 60 {llvmPath} {options} {fileName} -o a.out > ori_wrong_file 2>&1')
    if not os.path.exists('a.out'):
        return 'FL_checkpass_err'

    start = time.time()
    output = subprocess.Popen('timeout 10 ./a.out', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = output.stdout.read().strip().decode('utf-8')
    end=time.time()
    
    if (end-start)>=10:
        return 'FL_time_out'
    
    return res

def get_small_res(llvmPath, optPath, options, fileName, use_new_pm):
    if os.path.exists('a.bc'):
        os.system('rm ./a.bc')
    if os.path.exists('a-opt.bc'):
        os.system('rm ./a-opt.bc')
    if os.path.exists('a.out'):
        os.system('rm ./a.out')
    
    os.system(f'{llvmPath} -c -emit-llvm {fileName} -o a.bc > ori_wrong_file 2>&1')
    if not os.path.exists('a.bc'):
        return 'FL_checkpass_err'
    if use_new_pm:
        os.system(f'{optPath} -passes=\'{options}\' a.bc -o a-opt.bc > ori_wrong_file 2>&1')
    else:
        os.system(f'{optPath} {options} a.bc -o a-opt.bc > ori_wrong_file 2>&1')
    if not os.path.exists('a-opt.bc'):
        return 'FL_checkpass_err'
    os.system(f'{llvmPath} a-opt.bc -o a.out  > ori_wrong_file 2>&1')
    if not os.path.exists('a.out'):
        return 'FL_checkpass_err'

    start = time.time()
    output = subprocess.Popen('timeout 10 ./a.out', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = output.stdout.read().strip().decode('utf-8')
    end=time.time()
    
    if (end-start)>=10:
        return 'FL_time_out'
    
    return res
  
def checkIsPass(ori_fail_res, ori_pass_res, this_fail_res, this_pass_res):
    if ori_pass_res==this_pass_res:
        if ori_pass_res==this_fail_res:
            return 'pass'
        elif ori_fail_res==this_fail_res:
            return 'still_fail'
        elif ('Please submit a full bug report' in ori_fail_res) and ('Please submit a full bug report' in this_fail_res):
            return 'still_fail' # for crash
    return 'other_fail'
    
# run and collect one file's cov
def collect_one_cov(stmtfilename, covdir, bindir, options, testname, collectfiles = {}):
    
    stmtfile = open(stmtfilename, 'w')
    
    # delete all .gcda files
    os.system(f'find {covdir} -name \"*.gcda\" | xargs rm -f')
    # compile test program
    name_opt = options.replace(' ', '+')
    os.system(f'{bindir}/gcc {options} {testname}.c -o a.out > {testname}_{name_opt}.log 2>&1')
    
    if os.path.exists('gcdalist'):
        exccmd('rm gcdalist')
    os.system(f'find {covdir} -name \"*.gcda\" > gcdalist')
    
    f = open('gcdalist')
    lines = f.readlines()
    f.close()
    
    for i in range(len(lines)):
        gcdafile=lines[i].strip()
        cov_file_name = gcdafile.split('.gcda')[0].split('-build/gcc/')[1]+'.c'
        
        if '/gcc/testsuite/' in gcdafile:
            continue
        if collectfiles!={}:
            if cov_file_name not in collectfiles:
                continue
        
        exccmd('rm *.gcov')
        exccmd(f'{bindir}/gcov {gcdafile} > gcovfile 2>&1')
        
        gcovfile_name = gcdafile.strip().split('/')[-1].split('.gcda')[0] + '.c.gcov'
        if not os.path.exists(gcovfile_name):
            continue
        
        f = open(gcovfile_name)
        stmtlines = f.readlines()
        f.close()

        tmp = []
        for j in range(len(stmtlines)):
            if stmtlines[j] == '------------------\n':
                continue
            covcnt = stmtlines[j].strip().split(':')[0].strip()
            linenum = stmtlines[j].strip().split(':')[1].strip()
            if covcnt != '-' and covcnt != '#####':
                tmp.append(linenum)
        for lineno in tmp:
            stmtfile.write(cov_file_name+':'+lineno+'\n')
    stmtfile.close()
    
def collect_one_cov_dir_big(workdir, stmtfilename, covdir, gcov_path, llvm_path, options, testname, collectfiles = {}):
    
    oridir = os.getcwd()
    os.chdir(workdir)
    
    stmtfile = open(stmtfilename, 'w')
    
    # delete all .gcda files
    
    covdir = covdir.strip()
    
    os.system(f'find {covdir} -name \"*.gcda\" | xargs rm -f')
    
    # compile test program
    os.system(f'{llvm_path} {options} {testname}.c > {testname}.log 2>&1')

    if os.path.exists('gcdalist'):
        exccmd('rm gcdalist')
    os.system(f'find {covdir} -name \"*.gcda\" > gcdalist')
    
    f = open('gcdalist')
    lines = f.readlines()
    f.close()
    
    for i in range(len(lines)):
        gcdafile = lines[i].strip()
        
        gcdafile_name = gcdafile.split('.gcda')[0]
        cov_file_name_ori = gcdafile_name.split(covdir)[-1]
        
        dir_names = cov_file_name_ori.split('/')
        cov_file_name = ''
        for i in range(0, len(dir_names)):
            if dir_names[i] != 'CMakeFiles' and not '.dir' in dir_names[i] and dir_names[i] != '':
                cov_file_name += dir_names[i]
                cov_file_name += '/'
        cov_file_name = cov_file_name[:-1]
        
        if '/clang/test/' in gcdafile:
            continue
        if collectfiles!={}:
            if cov_file_name not in collectfiles:
                continue
        
        exccmd('rm *.gcov')
        exccmd(f'{gcov_path} {gcdafile} > gcovfile 2>&1')
        
        gcovfile_name = gcdafile.strip().split('/')[-1].split('.gcda')[0] + '.gcov'
        if not os.path.exists(gcovfile_name):
            continue
        
        f = open(gcovfile_name)
        stmtlines = f.readlines()
        f.close()

        tmp = []
        for j in range(len(stmtlines)):
            if stmtlines[j] == '------------------\n':
                continue
            covcnt = stmtlines[j].strip().split(':')[0].strip()
            linenum = stmtlines[j].strip().split(':')[1].strip()
            if covcnt != '-' and covcnt != '#####' and linenum!='':
                tmp.append(linenum)
        for lineno in tmp:
            stmtfile.write(cov_file_name+':'+lineno+'\n')
    stmtfile.close()
    
    os.chdir(oridir)
    
def collect_one_cov_dir_small(workdir, stmtfilename, covdir, gcov_path, llvm_path, options, testname, use_new_pm, collectfiles = {}):
    print(f'stmt in: {stmtfilename}')
    
    oridir = os.getcwd()
    os.chdir(workdir)
    
    stmtfile = open(stmtfilename, 'w')
    
    # delete all .gcda files
    os.system(f'find {covdir} -name \"*.gcda\" | xargs rm -f')
    # compile test program
    os.system(f'{llvmPath} -c -emit-llvm {fileName} -o a.bc > ori_wrong_file 2>&1')
    if use_new_pm:
        os.system(f'{optPath} -passes=\'{options}\' a.bc -o a-opt.bc > ori_wrong_file 2>&1')
    else:
        os.system(f'{optPath} {options} a.bc -o a-opt.bc > ori_wrong_file 2>&1')
    os.system(f'{llvmPath} a-opt.bc -o a.out  > ori_wrong_file 2>&1')
    
    if os.path.exists('gcdalist'):
        exccmd('rm gcdalist')
    os.system(f'find {covdir} -name \"*.gcda\" > gcdalist')
    
    f = open('gcdalist')
    lines = f.readlines()
    f.close()
    
    for i in range(len(lines)):
        gcdafile = lines[i].strip()
        cov_file_name_ori = gcdafile.split('.gcda')[0].split(f'{covdir}')[-1]
        
        dir_names = cov_file_name_ori.split('/')
        cov_file_name = ''
        for i in range(0, len(dir_names)):
            if dir_names[i] != 'CMakeFiles' and not '.dir' in dir_names[i] and dir_names[i] != '':
                cov_file_name += dir_names[i]
                cov_file_name += '/'
        cov_file_name = cov_file_name[:-1]
        
        if '/clang/test/' in gcdafile:
            continue
        
        if collectfiles!={}:
            if cov_file_name not in collectfiles:
                continue
        
        exccmd('rm *.gcov')
        exccmd(f'{gcov_path} {gcdafile} > gcovfile 2>&1')
        
        gcovfile_name = gcdafile.strip().split('/')[-1].split('.gcda')[0] + '.gcov'
        if not os.path.exists(gcovfile_name):
            continue
        
        f = open(gcovfile_name)
        stmtlines = f.readlines()
        f.close()

        tmp = []
        for j in range(len(stmtlines)):
            if stmtlines[j] == '------------------\n':
                continue
            covcnt = stmtlines[j].strip().split(':')[0].strip()
            linenum = stmtlines[j].strip().split(':')[1].strip()
            if covcnt != '-' and covcnt != '#####' and linenum!='':
                tmp.append(linenum)
        for lineno in tmp:
            stmtfile.write(cov_file_name+':'+lineno+'\n')
    stmtfile.close()
    
    os.chdir(oridir)

# run and collect one file's cov
def collect_one_cov_dir(workdir, stmtfilename, covdir, bindir, options, testname, collectfiles = {}):
    
    print(f'stmt in: {stmtfilename}')
    
    oridir = os.getcwd()
    os.chdir(workdir)
    
    stmtfile = open(stmtfilename, 'w')
    
    # delete all .gcda files
    os.system(f'find {covdir} -name \"*.gcda\" | xargs rm -f')
    # compile test program
    os.system(f'{bindir}/gcc {options} {testname}.c > {testname}.log 2>&1')
    
    if os.path.exists('gcdalist'):
        exccmd('rm gcdalist')
    os.system(f'find {covdir} -name \"*.gcda\" > gcdalist')
    
    f = open('gcdalist')
    lines = f.readlines()
    f.close()
    
    for i in range(len(lines)):
        gcdafile=lines[i].strip()
        cov_file_name = gcdafile.split('.gcda')[0].split('-build/gcc/')[1]+'.c'
        
        if '/gcc/testsuite/' in gcdafile:
            continue
        if collectfiles!={}:
            if cov_file_name not in collectfiles:
                continue

        exccmd('rm *.gcov')
        exccmd(f'{bindir}/gcov {gcdafile} > gcovfile 2>&1')
        
        gcovfile_name = gcdafile.strip().split('/')[-1].split('.gcda')[0] + '.c.gcov'
        if not os.path.exists(gcovfile_name):
            continue
        
        f = open(gcovfile_name)
        stmtlines = f.readlines()
        f.close()

        tmp = []
        for j in range(len(stmtlines)):
            if stmtlines[j] == '------------------\n':
                continue
            covcnt = stmtlines[j].strip().split(':')[0].strip()
            linenum = stmtlines[j].strip().split(':')[1].strip()
            if covcnt != '-' and covcnt != '#####':
                tmp.append(linenum)
        for lineno in tmp:
            stmtfile.write(cov_file_name+':'+lineno+'\n')
    stmtfile.close()

    os.chdir(oridir)

# collect a list of bug's ori fail&pass cov
def collect(compilersdir, infodir, bugIds, revisions, rightoptions, wrongoptions):

    for i in range(len(bugIds)):

        rightoption = rightoptions[i].replace('+', ' ')
        wrongoption = wrongoptions[i].replace('+', ' ')
        bugId = bugIds[i]
        revision = revisions[i]

        testname = 'fail'

        covdir = compilersdir + revision + '-build/gcc'
        bindir = compilersdir + revision + '-build/bin'
        resdir = infodir + bugId

        os.chdir(resdir)
        exccmd('mkdir ' + resdir + '/' + testname)
        
        collect_one_cov(f'{resdir}/{testname}/stmt_info.txt', covdir, bindir, wrongoption, testname)
        collect_one_cov(f'{resdir}/{testname}/oriright_stmt_info.txt', covdir, bindir, rightoption, testname)
