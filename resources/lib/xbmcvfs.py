
#Dummy module to satisfy the required import in dbupdate

import os
import shutil

def listdir(dirname):
    return [], os.listdir(dirname)

def exists(pathName):
    return os.path.exists(pathName)

def copy(src, dst):
    print "Copying from {0} to {1}".format (src, dst)
    try:
        shutil.copy(src, dst)
    except:
        pass

def delete(src):
    print "Deleting {0}".format (src)
    try:
        os.remove(src)
    except:
        pass

def mkdirs(path):
    try:
        os.makedirs(path)
    except Exception as err:
        print "Unable to makedirs {0}: {1}".format(path, str(err.message))
        #raise