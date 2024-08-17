'''
Author: your name
Date: 2021-10-08 01:45:31
LastEditTime: 2021-10-08 01:51:10
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/check/gcc_fie_num.py
'''
import os
import subprocess
from configparser import ConfigParser

if __name__ == '__main__':
    
    cfg = ConfigParser()
    cfg.read('/root/cfl/ODFL/conf/config.ini')
    configFile = cfg.get('gcc-workplace', 'configFile')
    mianDir = cfg.get('gcc-workplace', 'maindir')
    compilerDir = cfg.get('gcc-workplace', 'compilersdir')
    oracleDir = cfg.get('gcc-workplace', 'oracledir')
    sumFile = cfg.get("gcc-workplace", 'buglist')
    configFile = cfg.get('gcc-workplace', 'configFile')
    covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
    with open(sumFile, 'r') as f:
        lines = f.readlines()
    
    
    cnt = 0
    gcc_cnt = 0
    for i in range(len(lines)):
        bugId = lines[i].strip().split(',')[0]
        revNum = lines[i].strip().split(',')[1]

        prefixpath = compilerDir + revNum + '/' + revNum
        gccpath = prefixpath + '/gcc'
        
        os.chdir(gccpath)
        res_bytes = subprocess.Popen('find ./ -name \"*.c\" | wc -l', shell=True,  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        res_text = res_bytes.stdout.read().strip().decode('utf-8')
        print(res_text)
        cnt += int(res_text)
        gcc_cnt += 1

    ave = cnt / gcc_cnt
    print(ave)
    