import os
from re import T
import time
import subprocess
import sys
import collections
import random

from numpy.core.fromnumeric import partition


def diff_pass_existing_cov(passcovPath, testname, failset, existingcovset, unionCovwithFail, failFileDict):
    # if len(os.listdir(passcovPath))==1:
    #     with open(passcovPath + testname) as thisfile:
    #         thislines=thisfile.readlines()
    #     thisset=set()
    #     for i in range(len(thislines)):
    #         filenameitem=thislines[i].strip().split('$')[0]
    #         lineitems=thislines[i].strip().split('$')[1].split(',')
    #         for j in range(len(lineitems)):
    #             thisset.add(filenameitem+':'+lineitems[j])
    #     existingcovset[testname] = thisset & failset
    #     unionCovwithFail[testname] = thisset | failset
    #     return 0 # different

    with open(passcovPath + testname, 'r') as f:
        thislines = f.readlines()
        thisset=set()
    for i in range(len(thislines)):
        filenameitem=thislines[i].strip().split('$')[0]
        lineitems=thislines[i].strip().split('$')[1].split(',')
        for j in range(len(lineitems)):
            thisset.add(filenameitem+':'+lineitems[j])
    similarity = len(thisset&failset)/len(thisset | failset)
    

    thisFileDict = dict()
    for i in range(len(thislines)):
        filename = thislines[i].strip().split('$')[0]
        stmtlist = thislines[i].strip().split('$')[1].split(',')
        thisFileDict[filename] = stmtlist
    similarityDict = dict()
    for compilerFile in failFileDict.keys():
        if compilerFile in thisFileDict.keys():
            simtmp = len(set(thisFileDict[compilerFile]) & set(failFileDict[compilerFile]))/len(set(thisFileDict[compilerFile]) | set(failFileDict[compilerFile]))
            similarityDict[compilerFile] = simtmp
        else:
            simtmp = 0
            similarityDict[compilerFile] = simtmp
    return similarity
    # return similarityDict




    if len(existingcovset) == 0:
        similarity = len(thisset&failset)/len(thisset | failset)
    else:
        for key in existingcovset.keys():
            similarity=float(len(existingcovset[key]&(thisset&failset)))/len(existingcovset[key]|(thisset&failset))
            if similarity==1:
                return 1 # same
    existingcovset[testname]=thisset&failset
    unionCovwithFail[testname] = thisset | failset
    return 0 #different

def diff_fail_existing_cov(passcovPath, testname, failset):
    # if len(os.listdir(passcovPath))==1:
    existingcovset = dict()
    unionCovwithFail = dict()
    with open(passcovPath + testname) as thisfile:
        thislines=thisfile.readlines()
    thisset=set()
    for i in range(len(thislines)):
        filenameitem=thislines[i].strip().split('$')[0]
        lineitems=thislines[i].strip().split('$')[1].split(',')
        for j in range(len(lineitems)):
            thisset.add(filenameitem+':'+lineitems[j])
    existingcovset[testname] = thisset & failset
    unionCovwithFail[testname] = thisset | failset
    # similarity=float(len(existingcovset[testname]&(thisset&failset)))/len(existingcovset[testname]|(thisset&failset))
    similarity = float(len(existingcovset[testname]))/len(unionCovwithFail[testname])
    return similarity # different

    # thisfile=open(passcovPath + testname)
    # thislines=thisfile.readlines()
    # thisfile.close()

    # thisset=set()
    # for i in range(len(thislines)):
    #     filenameitem=thislines[i].strip().split('$')[0]
    #     lineitems=thislines[i].strip().split('$')[1].split(',')
    #     for j in range(len(lineitems)):
    #         thisset.add(filenameitem+':'+lineitems[j])

    # for key in existingcovset.keys():
    #     similarity = float(len(existingcovset[key]&(thisset&failset)))/len(existingcovset[key]|(thisset&failset))
    #     if similarity==1:
    #         return 1 # same
    # existingcovset[testname]=thisset&failset
    # unionCovwithFail[testname] = thisset | failset
    # return similarity #different

def judge_buggymethods_in_diffmethods(cov_analysis, revisionnumber, buggyfilepath, option):
    # option = compilationOption.replace(' ', '+')
    with open(cov_analysis + '/passnotexe_' + option + '.txt', 'r') as f:  # pass 没有执行到，但是orifail执行到；或者fail执行到，但是orifail没有执行到
        difffiles = f.readlines()
    difffileset = set()
    for i in range(len(difffiles)):
        rev = difffiles[i].strip().split(' ')[0]
        file = difffiles[i].strip().split(' ')[1]
        difffileset.add(file)

    with open(cov_analysis + '/difffiles_call' + option + '.txt', 'r') as f: # pass和fail都执行到，但是执行到的行号不相同，即执行轨迹不相同
        difffiles2 = f.readlines()
    difffileset2 = set()
    for i in range(len(difffiles2)):
        rev = difffiles2[i].strip().split(' ')[0]
        file = difffiles2[i].strip().split(' ')[1]
        difffileset2.add(file)

    with open(buggyfilepath + '/buggyfiles_info.txt', 'r') as f:
        buggyfilelines = f.readlines()
        buggyfiles = []
        jugebuggy = set()
        for buggyfileline in buggyfilelines:
            if buggyfileline.strip().split(' ')[0] == revisionnumber:
                buggyfile = buggyfileline.strip().split(' ')[1].strip().split(',')[0]
                buggyfiles.append(buggyfile)
                jugebuggy.add(buggyfile)
    if jugebuggy.issubset(difffileset):
        print('Buggyfiles all in difffiles*********')
    else:
        missfiles = jugebuggy - difffileset
        print('Miss files number is: ' + str(len(missfiles)) + ' in ' + str(len(jugebuggy)))

    if jugebuggy.issubset(difffileset | difffileset2):
        print('Buggyfiles all in difffiles and difflines*********')
    else:
        missfiles = jugebuggy - (difffileset2 | difffileset)
        print('Miss files number is: ' + str(len(missfiles)) + ' in ' + str(len(jugebuggy)))


# def judge_buggymethods_in_diffmethods_wrong(cov_analysis, revisionnumber, aggregationpath, compilationOption):
#     option = compilationOption.replace(' ', '+')
#     with open(cov_analysis + '/passnotexe_' + option + '.txt', 'r') as f:
#         diffmethods = f.readlines()
#     diffmethodset = set()
#     for i in range(len(diffmethods)):
#         rev = diffmethods[i].strip().split(' ')[0]
#         method = diffmethods[i].strip().split(' ')[1]
#         diffmethodset.add(method)
#     with open(aggregationpath + '/method_info.txt', 'r') as f:
#         buggymethodlines = f.readlines()
#         buggymethods = []
#         jugebuggy = set()
#         for buggymethodline in buggymethodlines:
#             if buggymethodline.strip().split(' ')[0] == revisionnumber:
#                 buggymethod = buggymethodline.strip().split(' ')[1].strip()
#                 buggymethods.append(buggymethod)
#                 jugebuggy.add(buggymethod)
#     if jugebuggy.issubset(diffmethodset):
#         print('Buggymethods all in diffmethods*********')
#     else:
#         missmethods = jugebuggy - diffmethodset
#         print('Miss methods number is: ' + str(len(missmethods)) + ' in ' + str(len(jugebuggy)))
    
    

def diff_cov_right(cov_analysis, revisionnumber, optioncovpath, _covpath, compilationOptionsWrong, compilationOption):
    if not os.path.exists(cov_analysis):
        subprocess.run('mkdir -p ' + cov_analysis, shell=True)
    option = compilationOption.replace(' ', '+')
    difffiles = open(cov_analysis + '/difffiles_call' + option + '.txt', 'w')
    samefiles = open(cov_analysis + '/samefiles_call' + option + '.txt', 'w')
    buggyfiles = open(cov_analysis +'/passnotexe_' + option + '.txt', 'w')


    failstmt=dict() # the stmt cov information of failing test program
    passstmt=dict()
    failfileset=set() # the set of compiler file that was touched
    failfilemapstmt=dict() # the dict of file and corresponding stmts
    # nfstmt = dict() # 记录nfs的覆盖信息
    failstmtset = set()

    failfileset = set() # the set of compiler file that was touched
    passfileset = set()
    failfilemapstmt = collections.OrderedDict() # 顺序dict
    passfilemapstmt = collections.OrderedDict()
    
    # compiler excuted lines that falling test program was compiled
    option = compilationOptionsWrong.replace(' ', '+')
    # covpath = locationdir + '/' + revisionnumber[1:] + '/fail/method_line_' + option +'.txt'    
    covpath = optioncovpath + '/orifail/fileCov/stmt_info_' + option +'.txt'    
    with open(covpath, 'r') as f:
        faillines = f.readlines()
    # excuted lines in every buggy file that falling test program was compiled
    for j in range(len(faillines)):
        faillinesplit=faillines[j].strip().split('$')  
        # filename=faillinesplit[0].strip().split('.gcda')[0].strip()
        filename=faillinesplit[0]  # filename
        # if not filename.endswith('.cpp'):
        #     continue
        failfileset.add(filename)

        stmtlist=faillinesplit[1].split(',') # stmts
        if filename not in failfilemapstmt.keys():
            failfilemapstmt[filename] = set()
            failfilemapstmt[filename].update(set(stmtlist))
        else:
            failfilemapstmt[filename].update(set(stmtlist))

    print('Total files number: ' + str(len(failfileset)))

    # right option 对应的函数覆盖信息
    option = compilationOption.replace(' ', '+')
    rightcovpath = _covpath + '/stmt_info_' + option + '.txt'
    with open(rightcovpath, 'r') as f:
        rightcovlines = f.readlines()
    for j in range(len(rightcovlines)):
        rightlinesplit=rightcovlines[j].strip().split('$')
        # filename=passlinesplit[0].strip().split('.gcda')[0].strip()
        filename = rightlinesplit[0]
        passfileset.add(filename)
        stmtlist = rightlinesplit[1].split(',')
        if filename not in passfilemapstmt.keys():
            passfilemapstmt[filename] = set()
            passfilemapstmt[filename].update(set(stmtlist))
        else:
            passfilemapstmt[filename].update(set(stmtlist))

    intersection = failfileset & passfileset # fail和pass都运行到的
    buggyfileset = failfileset - passfileset # 只有fail运行到，但是right option并没有运行到
    print('The failed program is executed but the successful does not - files number: ' + str(len(buggyfileset)))
    for every in iter(buggyfileset):
        buggyfiles.write(revisionnumber + ' ' + every + '\n')
        buggyfiles.flush()
    samecnt = 0
    diffcnt = 0
    for file in iter(intersection):
        if failfilemapstmt[file] == passfilemapstmt[file]:  ############注意，还没有考虑到运行次数
            samecnt += 1
            # print(revisionnumber + ' ' + file + ' ' + ','.join(passfilemapstmt[file]) + '\n')
            samefiles.write(revisionnumber + ' ' + file + ' ' + ','.join(passfilemapstmt[file]) + '\n') #保存运到代码行完全一致的files
            samefiles.flush()
        else:
            diffcnt += 1
            # print(revisionnumber + ' ' + file + ' ' + ','.join(passfilemapstmt[file]) + '\n')
            difffiles.write(revisionnumber + ' ' + file + ' ' + ','.join(passfilemapstmt[file]) + '\n')
            difffiles.flush()
    print('the number of files with the same covinfo are: ' + str(samecnt) + ' ')
    print('the number of files with diffrent covinfo are: ' + str(diffcnt) + ' ')


def diff_cov_wrong(cov_analysis, revisionnumber, optioncovpath, _covpath, compilationOptionsWrong, option):
    if not os.path.exists(cov_analysis):
        subprocess.run('mkdir -p ' + cov_analysis, shell=True)
    # option = compilationOption.replace(' ', '+')
    difffiles = open(cov_analysis + '/difffiles_call' + option + '.txt', 'w')
    samefiles = open(cov_analysis + '/samefiles_call' + option + '.txt', 'w')
    buggyfiles = open(cov_analysis +'/passnotexe_' + option + '.txt', 'w')


    failstmt=dict() # the stmt cov information of failing test program
    passstmt=dict()
    failfileset=set() # the set of compiler file that was touched
    failfilemapstmt=dict() # the dict of file and corresponding stmts
    # nfstmt = dict() # 记录nfs的覆盖信息
    failstmtset = set()

    failfileset = set() # the set of compiler file that was touched
    passfileset = set()
    failfilemapstmt = collections.OrderedDict() # 顺序dict
    passfilemapstmt = collections.OrderedDict()
    
    # compiler excuted lines that falling test program was compiled
    option_ = compilationOptionsWrong.replace(' ', '+')
    # covpath = locationdir + '/' + revisionnumber[1:] + '/fail/file_line_' + option +'.txt'    
    covpath = optioncovpath + '/orifail/fileCov/stmt_info_' + option_ +'.txt'    
    with open(covpath, 'r') as f:
        faillines = f.readlines()
    # excuted lines in every buggy file that falling test program was compiled

    for j in range(len(faillines)):
        faillinesplit=faillines[j].strip().split('$')  
        # filename=faillinesplit[0].strip().split('.gcda')[0].strip()
        filename=faillinesplit[0]  # filename
        # if not filename.endswith('.cpp'):
        #     continue
        failfileset.add(filename)

        stmtlist=faillinesplit[1].split(',') # stmts
        if filename not in failfilemapstmt.keys():
            failfilemapstmt[filename] = set()
            failfilemapstmt[filename].update(set(stmtlist))
        else:
            failfilemapstmt[filename].update(set(stmtlist))

    print('Total files number: ' + str(len(failfileset)))

    # right option 对应的函数覆盖信息
    # option = compilationOption.replace(' ', '+')
    # rightcovpath = locationdir + '/' + revisionnumber[1:] + '/fail/file_line_' + option + '.txt'
    rightcovpath = _covpath + '/stmt_info_' + option + '.txt'
    with open(rightcovpath, 'r') as f:
        rightcovlines = f.readlines()
    for j in range(len(rightcovlines)):
        rightlinesplit=rightcovlines[j].strip().split('$')
        # filename=passlinesplit[0].strip().split('.gcda')[0].strip()
        filename = rightlinesplit[0]
        passfileset.add(filename)
        stmtlist = rightlinesplit[1].split(',')
        if filename not in passfilemapstmt.keys():
            passfilemapstmt[filename] = set()
            passfilemapstmt[filename].update(set(stmtlist))
        else:
            passfilemapstmt[filename].update(set(stmtlist))

    intersection = failfileset & passfileset # fail和pass都运行到的
    buggyfileset = failfileset - passfileset # 只有fail运行到，但是right option并没有运行到
    print('The failed program is executed but the new failed does not - files number: ' + str(len(buggyfileset)))
    for every in iter(buggyfileset):
        buggyfiles.write(revisionnumber + ' ' + every + '\n')
        buggyfiles.flush()
    samecnt = 0
    diffcnt = 0
    for file in iter(intersection):
        if failfilemapstmt[file] == passfilemapstmt[file]:  ############注意，还没有考虑到运行次数
            samecnt += 1
            # print(revisionnumber + ' ' + file + ' ' + ','.join(passfilemapstmt[file]) + '\n')
            samefiles.write(revisionnumber + ' ' + file + ' ' + ','.join(passfilemapstmt[file]) + '\n') #保存运到代码行完全一致的files
            samefiles.flush()
        else:
            diffcnt += 1
            # print(revisionnumber + ' ' + file + ' ' + ','.join(passfilemapstmt[file]) + '\n')
            difffiles.write(revisionnumber + ' ' + file + ' ' + ','.join(passfilemapstmt[file]) + '\n')
            difffiles.flush()
    print('the number of files with the same covinfo are: ' + str(samecnt) + ' ')
    print('the number of files with diffrent covinfo are: ' + str(diffcnt) + ' ')


def get_cov(revisionnumber, prefixpath, gcovpath, covpath, filepath, filename, compilationOption):
    
    gccpath = prefixpath+'-build/bin/gcc'
    gccbuildpath = prefixpath+'-build/gcc'
    covdir = prefixpath+'-build'

    # methodfile = open(covpath +'/method_info_' + filename + '.txt','w')
    
    stmtfile = open(covpath + '/stmt_info_' + filename +'.txt','w')
    # methodlinefile = open(covpath + '/method_line_' + filename + '.txt', 'w') # 每个method执行到的行
    # methodcallfile = open(covpath + '/method_line_call_' + filename + '.txt', 'w') # 每个method执行到的行，已经执行的次数

    testname = filepath.split('/')[-1].split('.')[0]

    if os.path.exists(revisionnumber):
        subprocess.run('rm ' + revisionnumber, shell=True)
    subprocess.run('find '+covdir+' -name \"*.gcda\" | xargs rm -f', shell=True)
    if ' -c' in compilationOption:
        subprocess.run(gccpath + ' ' + compilationOption + ' ' + filepath + ' > ' + revisionnumber + ' 2>&1', shell=True)
    else:
        subprocess.run(gccpath + ' ' + compilationOption + ' ' + filepath + ' -o ' + revisionnumber + ' > ' + revisionnumber + '.log 2>&1', shell=True)
        # if not os.path.exists(revisionnumber):
        #     return 0

    if os.path.exists(revisionnumber + 'gcdalist'): # all files to be collected
        subprocess.run('rm ' + revisionnumber + 'gcdalist', shell=True)
    subprocess.run('find '+covdir+' -name \"*.gcda\" > '+ revisionnumber + 'gcdalist', shell=True)
    # os.system('find '+srcdir+' -name \"*.h\" >> gcdalist')

    with open(revisionnumber + 'gcdalist', 'r') as f:
        lines=f.readlines()
    
    for i in range(len(lines)):
        # 对于该test program编译生成的每一个*.gcda文件，循环生成对应的*.gcov文件
        gcdafile=lines[i].strip()
        if '/clang/test/' in gcdafile:
            continue
        # os.system('cp '+lines[i].strip()+' '+gcdafile)
        # go to gcda file to get gcov, then back to cwd
        oricwd = os.getcwd()
        gcdacwd = gccbuildpath
        os.chdir(gcdacwd)
        
        # Output summaries for each function
        subprocess.run('find '+covdir+' -name \"*.gcov\" | xargs rm -f', shell=True)
        if os.path.exists(revisionnumber + 'gcovfile'):
            subprocess.run('rm ' + revisionnumber + 'gcovfile', shell=True)
        # os.system(gcovpath + ' -b ' + gcdafile + ' > ' + revisionnumber + 'gcovfile 2>&1') # The output information of the gcov command
        # os.system(gcovpath + ' -i ' + gcdafile + ' > ' + revisionnumber + 'gcovfile 2>&1')
        gcovpath = prefixpath +'-build/bin/gcov'
        subprocess.run(gcovpath + ' -f ' + gcdafile + ' > ' + revisionnumber + 'gcovfile 2>&1', shell=True)

        # get the *.c.gcov corresponding to gcda -- gcov -b对应的信息
        gcovfile = gcdafile.strip().split('/')[-1].split('.gcda')[0]+'.c.gcov'
        # if gcovfile == 'gimple-pretty-print.c.gcov':
        #     print(1)
        if not os.path.exists(gcovfile):
            continue
        with open(gcovfile, 'r', encoding='utf-8') as f:
            stmtlines = f.readlines()

        # # get the *.gcda.gcov  -- gcov -i 对应的信息
        # gcovfile = gcdafile.strip().split('/')[-1] + '.gcov'
        # if not os.path.exists('./' + gcovfile):
        #     continue
        # with open(gcovfile, 'r') as f:
        #     methodlines = f.readlines()

        os.chdir(oricwd)

        # # method_line_call
        # for j in range(len(methodlines)):
            
        #     if gcdafile.strip().split('/')[-1].split('.gcda')[0]+'.c' in methodlines[j]:
        #         funclinedict = collections.OrderedDict()
        #         methodlinedict = collections.OrderedDict() 
        #         for k in range(j + 1, len(methodlines)):
        #             if 'function:' in methodlines[k] and 'file:' not in methodlines[k]:
        #                 funcsplit = methodlines[k].strip().split(':')[1].split(',')
        #                 start_line = int(funcsplit[0])
        #                 execution_count = funcsplit[1]
        #                 if execution_count == '0':
        #                     continue
        #                 compiledFuncName = funcsplit[2]
        #                 res = subprocess.check_output('c++filt ' + compiledFuncName, shell=True)
        #                 # funcName = res.decode('utf-8').strip().split('(')[0].strip()
        #                 funcName = res.decode('utf-8').strip()
        #                 try:
        #                     if 'function:' in methodlines[k + 1]:
        #                         funcsplit = methodlines[k + 1].strip().split(':')[1].split(',')
        #                         end_line = int(funcsplit[0])
        #                     else:
        #                         end_line = 99999
        #                 except:
        #                     end_line = 99999

        #                 if not funcName in funclinedict.keys():
        #                     funclinedict[funcName] = []
        #                     funclinedict[funcName].append(start_line)
        #                     funclinedict[funcName].append(end_line)
        #                 else:
        #                     # funclinedict[funcName][1] = int(end_line)
        #                     print(gcdafile.split(covdir+'/')[-1].split('.gcda')[0]+'.c'+':' + key + ':' + 'method line: function error ##### the same function appear')  # 这里存在问题，因为存在重名的函数，这些重名的函数的参数不相同，现在暂时不管


        #             elif 'lcount' in methodlines[k]:
        #                 linesplit = methodlines[k].strip().split(':')[1].split(',')
        #                 linenum = int(linesplit[0])
        #                 linecount = linesplit[1]
        #                 if linecount != '0':
        #                     for key in funclinedict.keys():
        #                         if linenum >= funclinedict[key][0] and linenum < funclinedict[key][1]:
        #                             if key not in methodlinedict.keys():
        #                                 methodlinedict[key] = []
        #                                 methodlinedict[key].append(str(linenum) + ':' + linecount)
        #                             else:
        #                                 methodlinedict[key].append(str(linenum) + ':' + linecount)
        #                         else:
        #                             continue
        #             # else:
        #             #     break
        #             elif 'file' in methodlines[k]:
        #                 break
        #         for key in methodlinedict.keys():
        #             line = gcdafile.split(covdir+'/')[-1].split('.gcda')[0]+'.c'+'$' + key + '$' + ','.join(methodlinedict[key]) + '\n'
        #             methodcallfile.write(line)
        #             methodcallfile.flush()
        #         # print(methodlinedict)
        #     else:
        #         continue

        # # method_line
        # for j in range(len(methodlines)):
            
        #     if gcdafile.strip().split('/')[-1].split('.gcda')[0]+'.c' in methodlines[j]:
        #         funclinedict = collections.OrderedDict()
        #         methodlinedict = collections.OrderedDict() 
        #         for k in range(j + 1, len(methodlines)):
        #             if 'function:' in methodlines[k] and 'file:' not in methodlines[k]:
        #                 funcsplit = methodlines[k].strip().split(':')[1].split(',')
        #                 start_line = int(funcsplit[0])
        #                 execution_count = funcsplit[1]
        #                 if execution_count == '0':
        #                     continue
        #                 compiledFuncName = funcsplit[2]
        #                 res = subprocess.check_output('c++filt ' + compiledFuncName, shell=True)
        #                 # funcName = res.decode('utf-8').strip().split('(')[0].strip()
        #                 funcName = res.decode('utf-8').strip()
        #                 try:
        #                     if 'function:' in methodlines[k + 1]:
        #                         funcsplit = methodlines[k + 1].strip().split(':')[1].split(',')
        #                         end_line = int(funcsplit[0])
        #                     else:
        #                         end_line = 99999
        #                 except:
        #                     end_line = 99999

        #                 if not funcName in funclinedict.keys():
        #                     funclinedict[funcName] = []
        #                     funclinedict[funcName].append(start_line)
        #                     funclinedict[funcName].append(end_line)
        #                 else:
        #                     # funclinedict[funcName][1] = int(end_line)
        #                     print(gcdafile.split(covdir+'/')[-1].split('.gcda')[0]+'.c'+':' + key + ':' + 'method line: function error ##### the same function appear')  # 这里存在问题，因为存在重名的函数，这些重名的函数的参数不相同，现在暂时不管


        #             elif 'lcount' in methodlines[k]:
        #                 linesplit = methodlines[k].strip().split(':')[1].split(',')
        #                 linenum = int(linesplit[0])
        #                 linecount = linesplit[1]
        #                 if linecount != '0':
        #                     for key in funclinedict.keys():
        #                         if linenum >= funclinedict[key][0] and linenum < funclinedict[key][1]:
        #                             if key not in methodlinedict.keys():
        #                                 methodlinedict[key] = []
        #                                 methodlinedict[key].append(str(linenum))
        #                             else:
        #                                 methodlinedict[key].append(str(linenum))
        #                         else:
        #                             continue
        #             # else:
        #             #     break
        #             elif 'file' in methodlines[k]:
        #                 break
        #         for key in methodlinedict.keys():
        #             line = gcdafile.split(covdir+'/')[-1].split('.gcda')[0]+'.c'+'$' + key + '$' + ','.join(methodlinedict[key]) + '\n'
        #             methodlinefile.write(line)
        #             methodlinefile.flush()
        #         # print(methodlinedict)
        #     else:
        #         continue
        
        # stmt_info
        tmp=[]
        for j in range(len(stmtlines)):
            if ':' in stmtlines[j].strip():
                covcnt=stmtlines[j].strip().split(':')[0].strip()
                linenum=stmtlines[j].strip().split(':')[1].strip()
                if covcnt!='-' and covcnt!='#####':
                    tmp.append(linenum)
        if len(tmp)==0:
            continue
        
        failcovline = gcdafile.split(covdir+'/')[-1].split('.gcda')[0]+'.c'+'$'+','.join(tmp)+'\n'
        stmtfile.write(failcovline)
        stmtfile.flush()

        # method_info
        # for j in range(len(stmtlines)):
        #     line = stmtlines[j].strip()
            # if "function" in line and "called" in line and "returned" in line:
            #     if '_Z41__static_initialization' in line.split(' ')[1] or '_GLOBAL__sub_' in line.split(' ')[1]: # or '_Z20' in line.split(' ')[1] or "GLOBAL" in line.split(' ')[1]:
            #         continue
            #     try:
            #         methodname = stmtlines[j + 1].split(':')[2].strip()
            #         if methodname == '':
            #             continue
            #     except IndexError:
            #         # print(gcdafile + ' ' +line + '\n' + stmtlines[j+1] + ': method name: #########IndexError########, and continue')
            #         continue
            #     linesplit = line.split(' ')
            #     calltime = linesplit[3]
            #     returnperc = linesplit[5].strip('%')
            #     execperc = linesplit[8].strip('%')
            #     if calltime == '0':
            #         continue
            #     else:
            #         covinfo = gcdafile.split(covdir+'/')[-1].split('.gcda')[0]+'.c' + '$' + methodname + '$' + calltime + '$' + returnperc + '$' + execperc +'\n'
            #         methodfile.write(covinfo)
            #         methodfile.flush()
                
    # methodfile.close()
    stmtfile.close()
    # methodlinefile.close()
    # methodcallfile.close()



def get_result(revisionnumber, prefixpath, failfile, option, compilationOptionsWrong):
    if not '-O' in option:
        option = ''
        optionsplit = compilationOptionsWrong.split(' ')
        for opt in optionsplit:
            if not '-O' in opt:
                option = option + opt + ' '
        option = option + '-O0'
    gccpath = prefixpath+'-build/bin/gcc'
    covdir = prefixpath+'-build'
    if os.path.exists(revisionnumber):
        subprocess.run('rm ' + revisionnumber, shell=True)
    subprocess.run('find '+covdir+' -name \"*.gcda\" | xargs rm -f', shell=True)
    
    if ' -c' in option:
        cmd = gccpath+' '+option+' ' + failfile
        output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        res = output.stdout.read().strip().decode('utf-8')
        return res

    else:
        subprocess.run(gccpath+' '+option+' ' + failfile + ' -o ' + revisionnumber + ' >' + revisionnumber + '.log 2>&1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        if not os.path.exists(revisionnumber):
        
            cmd = gccpath+' '+option+' ' + failfile
            output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            res = output.stdout.read().strip().decode('utf-8')
            return res
            # return False # compilation error

    start=time.time()
    # os.system('timeout 10 ./a.out 2>&1 | tee rightfile')
    # res = subprocess.check_output('./a.out', shell=True, stderr=subprocess.STDOUT)
    # res = res.decode('utf-8').strip()
    output = subprocess.Popen('timeout 10 ./'+revisionnumber, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = output.stdout.read().strip().decode('utf-8')

    # os.system('{ timeout 10 ./'+ revisionnumber +' ; }')
    end=time.time()
    
    if (end-start)>=10:
        return False


    # with open(resultfile, 'r') as f: 
    #     lines=f.readlines()
    # # if len(lines)!=1:
    # #     return False
    # # else:
    # #     if 'core dumped' in lines[0] or 'dumped core' in lines[0] or 'exception' in lines[0] or 'Abort' in lines[0] or 'Segmentation' in lines[0]:
    # #         return False
    # if len(lines) != 0 and ('core dumped' in lines[0] or 'dumped core' in lines[0] or 'exception' in lines[0] or 'Abort' in lines[0] or 'Segmentation' in lines[0]):
    #     return False

    return res
