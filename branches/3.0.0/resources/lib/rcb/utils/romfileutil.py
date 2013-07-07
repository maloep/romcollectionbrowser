
import zipfile
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

#HACK: zlib isn't shipped with some linux distributions
try:
    import zlib
except:
    Logutil.log("Error while loading zlib library. You won't be able to import games using crc values (only used when importing offline game descriptions).", util.LOG_LEVEL_WARNING)



def getFileCRC(filename):
    
    try:
        #get crc value of the rom file - this can take a long time for large files, so it is configurable
        filecrc = ''        
        if (zipfile.is_zipfile(str(filename))):            
                Logutil.log("handling zip file", util.LOG_LEVEL_INFO)
                zip = zipfile.ZipFile(str(filename), 'r')
                zipInfos = zip.infolist()
                if(len(zipInfos) > 1):
                    Logutil.log("more than one file in zip archive is not supported! Checking CRC of first entry.", util.LOG_LEVEL_WARNING)
                filecrc = "%0.8X" % (zipInfos[0].CRC & 0xFFFFFFFF)
                Logutil.log("crc in zipped file: " + filecrc, util.LOG_LEVEL_INFO)            
        else:                        
            prev = 0
            for eachLine in open(str(filename), "rb"):
                prev = zlib.crc32(eachLine, prev)                    
            filecrc = "%0.8X" % (prev & 0xFFFFFFFF)
            Logutil.log("crc for current file: " + str(filecrc), util.LOG_LEVEL_INFO)
        
        filecrc = filecrc.strip()
        filecrc = filecrc.lower()
    except Exception, (exc):
        Logutil.log("Error while creating crc: " + str(exc), util.LOG_LEVEL_ERROR)
        return "000000"
    
    return filecrc
    
    
def getGamenameFromFilename(filename, romCollection):
                    
    Logutil.log("current rom file: " + filename, util.LOG_LEVEL_INFO)

    #build friendly romname
    if(not romCollection.useFoldernameAsGamename):
        gamename = os.path.basename(filename)
    else:
        gamename = os.path.basename(os.path.dirname(filename))
        
    Logutil.log("gamename (file): " +gamename, util.LOG_LEVEL_INFO)
            
    #use regular expression to find disk prefix like '(Disk 1)' etc.        
    match = False
    if(romCollection.diskPrefix != ''):
        match = re.search(romCollection.diskPrefix.lower(), gamename.lower())
    
    if match:
        gamename = gamename[0:match.start()]
    else:
        gamename = os.path.splitext(gamename)[0]                    
    
    gamename = gamename.strip()
    
    Logutil.log("gamename (friendly): " +gamename, util.LOG_LEVEL_INFO)        
    
    return gamename
    
    
def getFoldernameFromRomFilename(filename):
    Logutil.log("Begin getFoldernameFromRomFilename: %s" + filename, util.LOG_LEVEL_INFO)        
    foldername = ''
    dirname = os.path.dirname(filename)
    Logutil.log("dirname: %s" % dirname, util.LOG_LEVEL_INFO)
    if(dirname != None):
        pathTuple = os.path.split(dirname)
        if(len(pathTuple) == 2):
            foldername = pathTuple[1]                
            
    return foldername