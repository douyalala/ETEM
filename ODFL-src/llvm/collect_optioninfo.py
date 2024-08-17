import os
import time
import subprocess
import sys
import collections
import random

# from numpy.core.fromnumeric import partition

def get_cov_big(revisionnumber, prefixpath, gcovpath, covpath, filepath, filename, compilationOption):
    
    llvmpath = prefixpath+'-build/bin/clang'
    covdir = prefixpath+'-build'
    gcovpath = 'gcov'
    # gcovpath = '/home/lyj/build-gcc-7.5.0/bin/gcov'
    oricwd = os.getcwd()
    
    stmtfile = open(covpath + '/stmt_info_' + filename +'.txt','w')

    if os.path.exists(revisionnumber):
        os.system('rm ' + revisionnumber)
        
    os.system('find '+covdir+' -name \"*.gcda\" | xargs rm -f')
    
    if ' -c ' in compilationOption:
        os.system('timeout 60 '+ llvmpath + ' ' + compilationOption + ' ' + filepath + ' > ' + revisionnumber + ' 2>&1')
    else:
        os.system('timeout 60 '+ llvmpath + ' ' + compilationOption + ' ' + filepath + ' -o ' + revisionnumber + ' > ' + revisionnumber + '.log 2>&1')

    if os.path.exists(revisionnumber + 'gcdalist'): # all files to be collected
        os.system('rm ' + revisionnumber + 'gcdalist')
    os.system('find '+covdir+' -name \"*.gcda\" > '+ revisionnumber + 'gcdalist')

    with open(revisionnumber + 'gcdalist', 'r') as f:
        lines=f.readlines()
    
    for i in range(len(lines)):
        # 对于该test program编译生成的每一个*.gcda文件，循环生成对应的*.gcov文件
        gcdafile=lines[i].strip()
        if '/clang/test/' in gcdafile:
            continue
        
        gcdacwd = oricwd+'/gcdacwd/'
        os.system(f'rm -rf {gcdacwd}')
        os.system(f'mkdir -p {gcdacwd}')
        os.chdir(gcdacwd)
        
        # Output summaries for each function
        os.system('find '+covdir+' -name \"*.gcov\" | xargs rm -f')
        if os.path.exists(revisionnumber + 'gcovfile'):
            os.system('rm ' + revisionnumber + 'gcovfile')
        os.system(gcovpath + ' -f ' + gcdafile + ' > ' + revisionnumber + 'gcovfile 2>&1')

        # get the *.c.gcov corresponding to gcda -- gcov -b对应的信息
        gcovfile = gcdafile.strip().split('/')[-1].split('.gcda')[0]+'.gcov'
        if not os.path.exists(gcovfile):
            continue
        with open(gcovfile, 'r', encoding='utf-8') as f:
            stmtlines = f.readlines()
            
        os.chdir(oricwd)
        
        # stmt_info
        tmp=[]
        for j in range(len(stmtlines)):
            if ':' in stmtlines[j].strip():
                covcnt=stmtlines[j].strip().split(':')[0].strip()
                linenum=stmtlines[j].strip().split(':')[1].strip()
                if covcnt!='-' and covcnt!='#####' and linenum!='' and not linenum in tmp:
                    tmp.append(linenum)
        if len(tmp)==0:
            continue
        
        failcovline = gcdafile.split(covdir+'/')[-1].split('.gcda')[0]+'$'+','.join(tmp)+'\n'
        stmtfile.write(failcovline)
        stmtfile.flush()

    stmtfile.close()

def get_cov_small(revisionnumber, prefixpath, gcovpath, covpath, filepath, filename, compilationOption, is_c, use_new_pm):
    
    llvmpath = prefixpath+'-build/bin/clang'
    covdir = prefixpath+'-build'
    gcovpath = 'gcov'
    # gcovpath = '/home/lyj/build-gcc-7.5.0/bin/gcov'
    optpath = prefixpath+'-build/bin/opt'
    oricwd = os.getcwd()
    
    stmtfile = open(covpath + '/stmt_info_' + filename +'.txt','w')

    testname = filepath.split('/')[-1].split('.')[0]

    if os.path.exists(revisionnumber):
        os.system('rm ' + revisionnumber)
        
    os.system('find '+covdir+' -name \"*.gcda\" | xargs rm -f')
    
    if is_c:
        os.system('timeout 60 '+ llvmpath+' -c -emit-llvm ' + filepath + ' -o a.bc >' + revisionnumber + '.log 2>&1')
        os.system('timeout 60 '+ optpath+' -passes=\''+compilationOption+'\' a.bc -o a-opt.bc >' + revisionnumber + '.log 2>&1')
    else:
        os.system('timeout 60 '+ llvmpath+' -c -emit-llvm ' + filepath + ' -o a.bc >' + revisionnumber + '.log 2>&1')
        if use_new_pm:
            os.system('timeout 60 '+ optpath+' -passes=\''+compilationOption+'\' a.bc -o a-opt.bc >' + revisionnumber + '.log 2>&1')
        else:
            os.system('timeout 60 '+ optpath+' '+option+' a.bc -o a-opt.bc >' + revisionnumber + '.log 2>&1')
        os.system('timeout 60 '+ llvmpath+' a-opt.bc -o ' + revisionnumber + ' >' + revisionnumber + '.log 2>&1')

    if os.path.exists(revisionnumber + 'gcdalist'): # all files to be collected
        os.system('rm ' + revisionnumber + 'gcdalist')
    os.system('find '+covdir+' -name \"*.gcda\" > '+ revisionnumber + 'gcdalist')

    with open(revisionnumber + 'gcdalist', 'r') as f:
        lines=f.readlines()
    
    for i in range(len(lines)):
        # 对于该test program编译生成的每一个*.gcda文件，循环生成对应的*.gcov文件
        gcdafile=lines[i].strip()
        if '/clang/test/' in gcdafile:
            continue
        
        gcdacwd = oricwd+'/gcdacwd/'
        os.system(f'rm -rf {gcdacwd}')
        os.system(f'mkdir -p {gcdacwd}')
        os.chdir(gcdacwd)
        
        # Output summaries for each function
        os.system('find '+covdir+' -name \"*.gcov\" | xargs rm -f')
        if os.path.exists(revisionnumber + 'gcovfile'):
            os.system('rm ' + revisionnumber + 'gcovfile')
        os.system(gcovpath + ' -f ' + gcdafile + ' > ' + revisionnumber + 'gcovfile 2>&1')

        # get the *.c.gcov corresponding to gcda -- gcov -b对应的信息
        gcovfile = gcdafile.strip().split('/')[-1].split('.gcda')[0]+'.gcov'
        if not os.path.exists(gcovfile):
            continue
        with open(gcovfile, 'r', encoding='utf-8') as f:
            stmtlines = f.readlines()

        os.chdir(oricwd)
        
        # stmt_info
        tmp=[]
        for j in range(len(stmtlines)):
            if ':' in stmtlines[j].strip():
                covcnt=stmtlines[j].strip().split(':')[0].strip()
                linenum=stmtlines[j].strip().split(':')[1].strip()
                if covcnt!='-' and covcnt!='#####' and linenum!='' and not linenum in tmp:
                    tmp.append(linenum)
        if len(tmp)==0:
            continue
        
        failcovline = gcdafile.split(covdir+'/')[-1].split('.gcda')[0]+'$'+','.join(tmp)+'\n'
        stmtfile.write(failcovline)
        stmtfile.flush()

    stmtfile.close()

def get_result_big(revisionnumber, prefixpath, failfile, option, compilationOptionsWrong):
    
    llvmpath = prefixpath+'-build/bin/clang'
    covdir = prefixpath+'-build'
    if os.path.exists(revisionnumber):
        os.system('rm ' + revisionnumber)
    
    os.system('find '+covdir+' -name \"*.gcda\" | xargs rm -f')
    
    if ' -c' in option:
        cmd = 'timeout 60 '+ llvmpath+' '+option+' ' + failfile
        output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        res = output.stdout.read().strip().decode('utf-8')
        return res
    
    os.system('timeout 60 '+ llvmpath+' '+option+' ' + failfile + ' -o ' + revisionnumber + ' >' + revisionnumber + '.log 2>&1')
    if not os.path.exists(revisionnumber):
        return 'checkpass_error'

    start=time.time()
    output = subprocess.Popen('timeout 10 ./'+revisionnumber, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = output.stdout.read().strip().decode('utf-8')
    end=time.time()
    
    if (end-start)>=10:
        return False

    return res

def get_result_small(revisionnumber, prefixpath, failfile, option, is_c, use_new_pm):
    
    llvmpath = prefixpath+'-build/bin/clang'
    optpath = prefixpath+'-build/bin/opt'
    covdir = prefixpath+'-build'
    
    if os.path.exists(revisionnumber):
        os.system('rm ' + revisionnumber)
    if os.path.exists('a.bc'):
        os.system('rm a.bc')
    if os.path.exists('a-opt.bc'):
        os.system('rm a-opt.bc')
        
    os.system('find '+covdir+' -name \"*.gcda\" | xargs rm -f')
    
    if is_c:
        os.system('timeout 60 '+ llvmpath+' -c -emit-llvm ' + failfile + ' -o a.bc >' + revisionnumber + '.log 2>&1')
        if not os.path.exists('a.bc'):
            return 'checkpass_error'

        cmd = 'timeout 60 '+ optpath+' -passes=\''+option+'\' a.bc -o a-opt.bc'
        output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        res = output.stdout.read().strip().decode('utf-8')
        return res
    else:
        os.system('timeout 60 '+ llvmpath+' -c -emit-llvm ' + failfile + ' -o a.bc >' + revisionnumber + '.log 2>&1')
        if not os.path.exists('a.bc'):
            return 'checkpass_error'
        
        if use_new_pm:
            os.system('timeout 60 '+ optpath+' -passes=\''+option+'\' a.bc -o a-opt.bc >' + revisionnumber + '.log 2>&1')
        else:
            os.system('timeout 60 '+ optpath+' '+option+' a.bc -o a-opt.bc >' + revisionnumber + '.log 2>&1')
        if not os.path.exists('a-opt.bc'):
            return 'checkpass_error'
        
        os.system('timeout 60 '+ llvmpath+' a-opt.bc -o ' + revisionnumber + ' >' + revisionnumber + '.log 2>&1')
        if not os.path.exists(revisionnumber):
            return 'checkpass_error'

    start=time.time()
    output = subprocess.Popen('timeout 10 ./'+revisionnumber, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = output.stdout.read().strip().decode('utf-8')
    end=time.time()
    
    if (end-start)>=10:
        return False

    return res
