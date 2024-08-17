import os, random, subprocess

def exccmd(cmd):
    p = os.popen(cmd, "r")
    rs = []
    line = ""
    while True:
        line = p.readline()

        if not line:
            break
        # print line
        # rs.append(line.strip())
    p.close()
    return rs

def thirdpos(tmplist):
    tmp=sorted(tmplist)
    for i in range(len(tmplist)):
        if tmplist[i]==tmp[0]:
            return i+1

def diffWithExistingPass(passtestdir, failtestdir):
    
    # os.system(f'clang-format -i mainvar.c')
    if os.path.exists('difffilefail'):
        exccmd('rm difffilefail')
    if os.path.exists(failtestdir + '/fail.c'):
        # os.system(f'clang-format -i {failtestdir}/fail.c')
        exccmd('diff mainvar.c ' + failtestdir + '/fail.c' + ' >difffilefail')
    else:
        # os.system(f'clang-format -i {failtestdir}ori/fail.c')
        exccmd('diff mainvar.c ' + failtestdir + 'ori' + '/fail.c' + ' >difffilefail')
    difffail = open('difffilefail')
    difffaillines = difffail.readlines()
    difffail.close()

    for i in range(len(difffaillines)):
        if 'printf' in difffaillines[i]:
            return 'fake_passing'  # faking passing
        if '__builtin_abort' in difffaillines[i]:
            return 'fake_passing'  # faking passing

    for f in os.listdir(passtestdir):
        if os.path.exists('difffile'):
            exccmd('rm difffile')
        exccmd('diff mainvar.c ' + passtestdir + '/' + f + ' >difffile')
        difff = open('difffile')
        diffflines = difff.readlines()
        difff.close()
        if len(diffflines) == 0:
            return 'pass_exist'

    return 'diff'

def calSimilarityandDiversity(testname, passingcnt, existingcovset,
                              unionCovwithFail, averageSimilarity, passCov, averageDiversity):
    if passingcnt == 0:
        return 0, 0
    
    # sim
    sim_list = []
    for key in existingcovset.keys():
        if not testname in key:
            continue
        sim_list.append( float(len(existingcovset[key]) / len(unionCovwithFail[key])) )
    similarity = float(sum(sim_list))/len(sim_list)
    averageSimilarity_ = (similarity + averageSimilarity * (passingcnt - 1)) / passingcnt
    
    # div
    averageDiversity_ = 0
    if passingcnt == 1:
        averageDiversity_ = 0
    else:
        div_list = []
        for one_test in passCov.keys():
            if not testname in one_test:
                continue
            for key in passCov.keys():
                if testname in key:
                    continue
                div_list.append(len(passCov[one_test] & passCov[key]) / len(passCov[one_test] | passCov[key]))
        diversity = float(sum(div_list))/len(div_list)
        averageDiversity_ = (diversity + averageDiversity * (passingcnt - 1)) / passingcnt

    return averageSimilarity_, averageDiversity_

def calActionNo(classNo):
    if classNo == 0: return random.randint(0, 2) # addQualifier
    elif classNo == 1: return random.randint(3, 6) # addRepModifier
    elif classNo == 2: return random.randint(7, 13) # remModifierQualifier
    elif classNo == 3: return random.randint(14, 101) # repBinaryOp
    elif classNo == 4: return random.randint(102, 105) # repIntConstant
    elif classNo == 5: return random.randint(106, 130) # repRemUnaryOp
    elif classNo == 6: return 131 # repVarSameScope
    elif classNo == 7: return 132 # addIf
    elif classNo == 8: return 133 # addWhile
    elif classNo == 9: return 134 # addGoto
    elif classNo == 10: return 135 # addFunction
    elif classNo == 11: return 136 # add2Loop
    elif classNo == 12: return 137 # addLoopIf
    elif classNo == 13: return 138 # delLoop
    elif classNo == 14: return random.randint(139, 141)  # repLoopCond
    elif classNo == 15: return random.randint(132, 144) # repLoopVar
    elif classNo == 16: return 145 # add2If
    elif classNo == 17: return 146 # delIf
    elif classNo == 18: return random.randint(147, 149) # repIfCond
    elif classNo == 19: return 150 # addVarDecl
    elif classNo == 20: return 151 # dupStmt
    elif classNo == 21: return 152 # delStmt
    elif classNo == 22: return 153 # moveStmt
    elif classNo == 23: return 154 # repStmtFunction
    elif classNo == 24: return 155 # addFuncArg
    elif classNo == 25: return 156 # addInline
    elif classNo == 26: return 157 # TurnConstantVar
    elif classNo == 27: return 158 # repBinaryExpr
    elif classNo == 28: return 159 # optOff
    elif classNo == 29: return 160 # disableLoopUnroll
    elif classNo == 30: return 161 # disableLoopVect
    else: return -1

def findClassNo(action_no):
    if action_no<=2: return 0
    elif action_no<=6: return 1
    elif action_no<=13: return 2
    elif action_no<=101: return 3
    elif action_no<=105: return 4
    elif action_no<=130: return 5
    elif action_no==131: return 6
    elif action_no==132: return 7
    elif action_no==133: return 8
    elif action_no==134: return 9
    elif action_no==135: return 10
    elif action_no==136: return 11
    elif action_no==137: return 12
    elif action_no==138: return 13
    elif action_no<=141: return 14
    elif action_no<=144: return 15
    elif action_no==145: return 16
    elif action_no==146: return 17
    elif action_no<=149: return 18
    elif action_no==150: return 19
    elif action_no==151: return 20
    elif action_no==152: return 21
    elif action_no==153: return 22
    elif action_no==154: return 23
    elif action_no==155: return 24
    elif action_no==156: return 25
    elif action_no==157: return 26
    elif action_no==158: return 27
    elif action_no==159: return 28
    elif action_no==160: return 29
    elif action_no==161: return 30
    else: return -1
    
def metrics(resultlist):
    result = dict()
    sumouter=0
    for gcc in resultlist:
        gcc.sort()
        if gcc[0]<=1:
            sumouter+=1
    result['Top-1'] = sumouter

    sumouter=0
    for gcc in resultlist:
        gcc.sort()
        if gcc[0]<=5:
            sumouter+=1
    result['Top-5'] = sumouter

    sumouter=0
    for gcc in resultlist:
        gcc.sort()
        if gcc[0]<=10:
            sumouter+=1
    result['Top-10'] = sumouter

    sumouter=0
    for gcc in resultlist:
        gcc.sort()
        if gcc[0]<=20:
            sumouter+=1
    result['Top-20'] = sumouter

    sumouter=0.0
    for gcc in resultlist:
        gcc.sort()
        sumouter+=gcc[0]
    result['MFR'] = sumouter/len(resultlist)

    sumouter=0.0
    for gcc in resultlist:
        gcc.sort()
        suminner=0.0
        for i in range(len(gcc)):
            suminner+=gcc[i]
        sumouter+=(suminner/len(gcc))
    result['MAR'] = sumouter/len(resultlist)

    return result
