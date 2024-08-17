# delete all redundant mutation strategy files, such as addIf, addWhile...
import os
from configparser import ConfigParser

MR = ['./exefile/', './testFile/']

def delete(bugId, k, configFile):
    cfg = ConfigParser()
    cfg.read(configFile)

    pass_path = cfg.get('llvm-locations', 'passdir')
    path = f'{pass_path}/{k}/{bugId}'

    os.chdir(path)
    for mr in MR:
        os.system('rm -rf '+ mr)

def delete_all(configFile):
    cfg = ConfigParser()
    cfg.read(configFile)
    
    path = cfg.get('llvm-locations', 'passdir')

    files = os.listdir(path)
    for f in files:
        files2 = os.listdir(path + f)
        for f2 in files2:
            os.chdir(path+f+'/'+f2)
            for mr in MR:
                os.system('rm -rf '+ mr)