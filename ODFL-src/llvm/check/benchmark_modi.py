'''
Author: your name
Date: 2021-08-26 09:49:29
LastEditTime: 2021-08-27 00:56:12
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/check/benchmark_modi.py
'''
import sys,os
from configparser import ConfigParser



cfg = ConfigParser()
cfg.read('/root/cfl/ODFL/conf/config.ini')

gcovpath = '/root/cfl/gccforme/r229639/r229639-build/bin/gcov'
# r237156

compilerDir = cfg.get('gcc-workplace', 'compilersdir')
oracleDir = cfg.get('gcc-workplace', 'oracledir')
covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
mianDir = cfg.get('gcc-workplace', 'maindir')
exactoptimsDir = cfg.get('gcc-workplace', 'exactoptimdir')

with open(covinfoDir + 'optLevel.txt', 'r') as f:
    optLevelLine = f.readlines()

compOptWrongList = []
for i in range(len(optLevelLine)):
    


print(revNum + ' ' + bugId)

prefixpath = compilerDir + revNum + '/' + revNum
clangpath = prefixpath + '-build/bin/clang'
# clangbuildpath = prefixpath + '-build/clang'
covdir = prefixpath + '-build'
oraclepath = oracleDir + bugId
curpath = mianDir + '/gcc'
failfile = oraclepath + '/fail.c'
gccpath = prefixpath + '-build/bin/gcc'
gccbuildpath = prefixpath+'-build/gcc'
covdir = prefixpath+'-build'