import os,sys
from configparser import ConfigParser
import subprocess
import re

# 收集每个optimization level对应的确切的optimization set
def collect(configFile):    
    cfg = ConfigParser()
    cfg.read(configFile)
    bugList = cfg.get('llvm-workplace', 'buglist')
    compilersDir = cfg.get('llvm-workplace', 'compilersdir')
    exactoptimsDir = cfg.get('llvm-workplace', 'exactoptimdir')
    oracledir =  cfg.get('llvm-workplace', 'oracledir')

    if not os.path.exists(exactoptimsDir):
        os.system('mkdir ' + exactoptimsDir)

    with open(bugList, 'r') as f:
        sumlines = f.readlines()

    for i in range(len(sumlines)):
        linesplit = sumlines[i].split(',')
        bugId = linesplit[0]
        revNum = linesplit[1]
        compilationOptionsWrong = linesplit[3].replace('+',' ')
        fail_file = f'{oracledir}/{bugId}/fail.c'
        
        optimsDir = exactoptimsDir + bugId
        if os.path.exists(optimsDir):
            os.system('rm -r ' + optimsDir)
        os.system('mkdir  ' + optimsDir)
        llvm_bin_path = f'{compilersDir}/{revNum}-build/bin'
        llvmPath = f'{llvm_bin_path}/clang'
        
        optLevels = ['O0','O1', 'O2', 'O3', 'Os']
        for optLevel in optLevels:
            big_opt = re.sub('-O([0-3]|s)', '-'+optLevel, compilationOptionsWrong)
            
            help_bytes = subprocess.Popen(f'{llvm_bin_path}/clang {big_opt} -mllvm --help-hidden {fail_file}', shell=True,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            help_list = help_bytes.stdout.read().decode('utf-8').split('\n')
        
            res_bytes = subprocess.Popen(f'{llvm_bin_path}/clang {big_opt} -mllvm --print-all-options {fail_file}', shell=True,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            res_list = res_bytes.stdout.read().decode('utf-8').split('\n')
            
            
            optimiFile = open(optimsDir + '/' + optLevel + '.txt', 'w')
            
            
            for line in res_list:
                # optimiFile.write(f'{line}\n')
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
                    optimiFile.write(f'{opt_line}={now_val}\n')
