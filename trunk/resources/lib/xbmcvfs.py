
#Dummy module to satisfy the required import in dbupdate

import os

def listdir(dirname):
    return [], os.listdir(dirname)

def exists(pathName):
    return os.path.exists(pathName) 