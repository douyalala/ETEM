'''
Author: your name
Date: 2021-09-10 03:07:53
LastEditTime: 2021-09-13 01:01:33
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/analysis/test.py
'''
from scipy.stats import wilcoxon
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('/root/cfl/ODFL/conf/config.ini')

covinfoDir = cfg.get('gcc-workplace', 'covinfodir')
data1 = []
# with open(covinfoDir + 'FileRank_block_sbfl.csv', 'r') as f:
#     lines = f.readlines()
# for i in range(len(lines)):
#     value = int(lines[i].strip().split(',')[3])
#     data1.append(value)
with open('/root/cfl/RecBi-workplace/gccbugs/resultFile.csv', 'r') as f:
    lines = f.readlines()
for i in range(len(lines)):
    value = int(lines[i].strip().split(',')[0])
    data1.append(value)

data2 = []
with open(covinfoDir + 'file_result.csv', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i in range(len(lines)):
    value = int(lines[i].strip().split(',')[0])
    data2.append(value)


# data1 = [0.873, 2.817, 0.121, -0.945, -0.055, -1.436, 0.360, -1.478, -1.637, -1.869]
# data2 = [1.142, -0.432, -0.938, -0.729, -0.846, -0.157, 0.500, 1.183, -1.075, -0.169,]
stat, p = wilcoxon(data1, data2, )
print('stat=%.3f, p=%.3f' % (stat, p))
if p > 0.05:
    print('不能拒绝原假设，两样本集分布相同')
else:
    print('拒绝原假设，样本集分布可能不同')