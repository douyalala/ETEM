'''
Author: your name
Date: 2021-07-22 09:17:40
LastEditTime: 2021-07-22 09:46:03
LastEditors: Please set LastEditors
Description: 查看gcc版本
FilePath: /cfl/ODFL/gcc/check/version.py
'''
import os
import subprocess

if __name__ == '__main__':
    gcc_version = open('/root/cfl/ODFL/gcc/check/gcc_version.txt', 'w')
    with open('/root/cfl/ODFL/benchmark/gccbugs_summary.txt', 'r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        linesplit = lines[i].split(',')
        revision = linesplit[1]
        res = os.system('/root/cfl/gccforme/' + revision + '/' + revision + '-build/bin/gcc --version > /root/cfl/ODFL/gcc/check/version.txt')
        with open('/root/cfl/ODFL/gcc/check/version.txt', 'r') as f:
            if res:
                print(revision)
                gcc_version.write(revision + '\n')
                gcc_version.flush()
                continue
            versionlines = f.readlines()
            print(revision + ' ' + versionlines[0])
            gcc_version.write(revision + ' ' + versionlines[0].strip().split(') ')[1].split(' ')[0] + '\n')
            gcc_version.flush()
