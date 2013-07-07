
from resources.lib.rcb.utils import util, romfileutil
from resources.lib.rcb.utils.util import *


def buildFileDict(gui, progDialogRCHeader, files, romCollection, firstScraper):
    
    fileCount = 1
    lastgamename = ""
    crcOfFirstGame = {}
    
    fileDict = {}
    
    for filename in files:
        try:
            gui.writeMsg(progDialogRCHeader, util.localize(40030), "", fileCount)
            fileCount = fileCount + 1
            
            gamename = romfileutil.getGamenameFromFilename(filename, romCollection)
            #check if we are handling one of the additional disks of a multi rom game
            #XBOX Hack: rom files will always be named default.xbe: always detected as multi rom without this hack
            isMultiRomGame = (gamename == lastgamename and lastgamename.lower() != 'default')
            #lastgamename may be overwritten by parsed gamename
            lastgamename = gamename
            gamename = gamename.strip()
            gamename = gamename.lower()
            
            #Logutil.log('gamename in fileDict: ' +str(gamename), util.LOG_LEVEL_INFO)
                                
            #build dictionaries (key=gamename, filecrc or foldername; value=filenames) for later game search
            if(firstScraper.useFoldernameAsCRC):
                Logutil.log('useFoldernameAsCRC = True', util.LOG_LEVEL_INFO)
                foldername = romfileutil.getFoldernameFromRomFilename(filename)
                foldername = foldername.strip()
                foldername = foldername.lower()
                fileDict = buildFilenameDict(fileDict, isMultiRomGame, filename, foldername)
            elif(firstScraper.useFilenameAsCRC):
                Logutil.log('useFilenameAsCRC = True', util.LOG_LEVEL_INFO)
                fileDict = buildFilenameDict(fileDict, isMultiRomGame, filename, gamename)
            elif(firstScraper.searchGameByCRC):
                Logutil.log('searchGameByCRC = True', util.LOG_LEVEL_INFO)
                filecrc = romfileutil.getFileCRC(filename)
                #use crc of first rom if it is a multirom game
                if(not isMultiRomGame):
                    crcOfFirstGame[gamename] = filecrc
                    Logutil.log('Adding crc to crcOfFirstGame-dict: %s: %s' % (gamename, filecrc), util.LOG_LEVEL_INFO)
                else:
                    filecrc = crcOfFirstGame[gamename]
                    Logutil.log('Read crc from crcOfFirstGame-dict: %s: %s' % (gamename, filecrc), util.LOG_LEVEL_INFO)
                    
                fileDict = buildFilenameDict(fileDict, isMultiRomGame, filename, filecrc)
            else:                        
                fileDict = buildFilenameDict(fileDict, isMultiRomGame, filename, gamename)
        except Exception, (exc):
            Logutil.log("an error occured while building file list", util.LOG_LEVEL_WARNING)
            Logutil.log("Error: " + str(exc), util.LOG_LEVEL_WARNING)
            continue
    
    return fileDict


def buildFilenameDict(result, isMultiRomGame, filename, key):
    
    try:                                            
        if(not isMultiRomGame):
            filenamelist = []
            filenamelist.append(filename)
            result[key] = filenamelist
            Logutil.log('Add filename "%s" with key "%s"' % (filename, key), util.LOG_LEVEL_DEBUG)
        else:
            filenamelist = result[key]
            filenamelist.append(filename)
            result[key] = filenamelist
            Logutil.log('Add filename "%s" to multirom game with key "%s"' % (filename, key), util.LOG_LEVEL_DEBUG)
    except Exception, (exc):
        Logutil.log('Error occured in buildFilenameDict: ' + str(exc), util.LOG_LEVEL_WARNING)
        
    return result


def matchDescriptionWithRomfiles(firstScraper, result, fileDict, gamenameFromDesc):
        
    filenamelist = []
    
    if(firstScraper.searchGameByCRC or firstScraper.useFoldernameAsCRC or firstScraper.useFilenameAsCRC):
        resultcrcs = result['crc']
        for resultcrc in resultcrcs:
            Logutil.log("crc in parsed result: " + resultcrc, util.LOG_LEVEL_DEBUG)
            resultcrc = resultcrc.lower()
            resultcrc = resultcrc.strip()
            filenamelist = findFilesByGameDescription(resultcrc, fileDict)
            if(filenamelist != None):
                break
    else:
        Logutil.log("game name in parsed result: " + gamenameFromDesc, util.LOG_LEVEL_INFO)
        gamenameFromDesc = gamenameFromDesc.lower()
        gamenameFromDesc = gamenameFromDesc.strip()
        filenamelist = findFilesByGameDescription(gamenameFromDesc, fileDict)
        
    return filenamelist


def findFilesByGameDescription(key, fileDict):
    
    Logutil.log("searching for Key: " + str(key), util.LOG_LEVEL_INFO)
        
    try:
        filename = fileDict[key]
    except:
        filename = None
        
    if (filename != None):
        Logutil.log("result found: " + str(filename), util.LOG_LEVEL_INFO)                
    
    return filename
