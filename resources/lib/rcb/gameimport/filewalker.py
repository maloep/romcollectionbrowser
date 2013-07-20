import xbmcvfs
import fnmatch, glob

from resources.lib.rcb.utils import util
from resources.lib.rcb.datamodel.file import File
from resources.lib.rcb.utils.util import *
from resources.lib.rcb.datamodel.gamedatabase import *


def getRomFilesByRomCollection(gdb, romCollection, enableFullReimport):
                
    Logutil.log("Rom path: " +str(romCollection.romPaths), util.LOG_LEVEL_INFO)
            
    Logutil.log("Reading rom files", util.LOG_LEVEL_INFO)
    files = []
    for romPath in romCollection.romPaths:
        files = walkDownRoot(files, romPath, romCollection.maxFolderDepth)
    
    #only use files that are not already present in database
    if enableFullReimport == False:
        inDBFiles = File(gdb).getFileAllFilesByRCId(romCollection.id)
        files = [f.decode('utf-8') for f in files if not f.decode('utf-8') in inDBFiles]            
    
    files.sort()
    Logutil.log("Files read: " +str(files), util.LOG_LEVEL_INFO)
    
    return files
        
        
def walkDownRoot(files, romPath, maxFolderDepth):
    
    Logutil.log("walkDownPath romPath: " +romPath, util.LOG_LEVEL_INFO)
    
    files = walkDown(files, romPath, maxFolderDepth)
    Logutil.log("files after walkDown = %s" %files, util.LOG_LEVEL_INFO)
    
    return files


def walkDown(files, romPath, maxFolderDepth):
    Logutil.log("Running walkdown on: %s" %romPath, util.LOG_LEVEL_INFO)
            
    dirs, newFiles, dirname, filemask = getFilesByWildcard(romPath)
    files.extend(newFiles)
    
    for dir in dirs:
        newRomPath = util.joinPath(dirname, dir, filemask)
        maxFolderDepth = maxFolderDepth -1
        if(maxFolderDepth > 0):
            walkDown(files, newRomPath, maxFolderDepth)
                
    return files


def getFilesByWildcard(pathName):
    
    Logutil.log('Begin getFilesByWildcard. pathName = %s' %pathName, util.LOG_LEVEL_INFO)
    files = []
    
    dirname = os.path.dirname(pathName)
    Logutil.log("dirname: " +dirname, util.LOG_LEVEL_INFO)
    filemask = os.path.basename(pathName)
    #HACK: escape [] for use with fnmatch
    filemask = filemask.replace('[', '[[]')
    filemask = filemask.replace(']', '[]]')
    #This might be stupid but it was late...
    filemask = filemask.replace('[[[]]', '[[]')
    Logutil.log("filemask: " +filemask, util.LOG_LEVEL_INFO)
    
    dirs, filesLocal = xbmcvfs.listdir(dirname)
    Logutil.log("xbmcvfs dirs: %s" %dirs, util.LOG_LEVEL_INFO)                        
    Logutil.log("xbmcvfs files: %s" %filesLocal, util.LOG_LEVEL_INFO)
    
    for file in filesLocal:
        if(fnmatch.fnmatch(file, filemask)):
        #allFiles = [f.decode(sys.getfilesystemencoding()).encode('utf-8') for f in glob.glob(newRomPath)]
            file = util.joinPath(dirname, file)
            files.append(file)
            
    return dirs, files, dirname, filemask
