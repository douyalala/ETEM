'''
Author: your name
Date: 2021-10-03 13:45:06
LastEditTime: 2021-10-03 15:13:01
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /cfl/ODFL/gcc/analysis/motivation_data.py
'''
import numpy as np

data = np.loadtxt('/root/cfl/ODFL/gcc/analysis/flag_num.csv', delimiter=',', skiprows=1)
dr_sum = data[:,0]
df_sum = data[:,1]
dr_ = data[:,2]
df_ = data[:,3]
print('dr_sum: ' + str(dr_sum.min()) + ',' + str(dr_sum.max()) + ',' + str(np.median(dr_sum)) + ',' + str(dr_sum.mean()))
print('df_sum: ' + str(df_sum.min()) + ',' + str(df_sum.max()) + ',' + str(np.median(df_sum)) + ',' + str(df_sum.mean()))
print('dr_: ' + str(dr_.min()) + ',' + str(dr_.max()) + ',' + str(np.median(dr_)) + ',' + str(dr_.mean()))
print('df_: ' + str(df_.min()) + ',' + str(df_.max()) + ',' + str(np.median(df_)) + ',' + str(df_.mean()))
print(data[:,0])