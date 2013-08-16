
import os, urllib

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import Logutil
from resources.lib.heimdall.src.heimdall.predicates import *

import filewalker
import xbmcvfs, xbmcgui


def getArtworkForRelease(inConfig, release, gamenameFromFile, gui, foldername, isLocalArtwork):
    artWorkFound = False
    artworkfiles = {}
    for path in inConfig.mediaPaths:
                    
        Logutil.log("FileType: " +str(path.type), util.LOG_LEVEL_INFO)
        fileName = path.path
        
        #TODO: replace %ROMCOLLECTION%, %PUBLISHER%, ...
        if(path.parent == 'game'):
            file = resolveArtwork(fileName, gamenameFromFile, path, release, isLocalArtwork, gui)
            artworkfiles[path.type] = file
            
        elif(path.parent == 'platform'):
            file = resolveArtwork(fileName, gamenameFromFile, path, release, isLocalArtwork, gui)
            artworkfiles[path.type] = file
            
        elif(path.parent == 'person'):
            for person in release.persons:
                fileName = fileName.replace("%PERSON%", person.name)
                file = resolveArtwork(fileName, gamenameFromFile, path, release, isLocalArtwork, gui)
                artworkfiles[path.type] = file
                
        elif(path.parent == 'company'):
            fileName = path.path.replace("%COMPANY%", release.platform.name)
            file = resolveArtwork(fileName, gamenameFromFile, path, release, isLocalArtwork, gui)
            artworkfiles[path.type] = file
    
    return artworkfiles



def resolveArtwork(fileName, gamenameFromFile, path, release, isLocalArtwork, gui):
    
    fileName = fileName.replace("%GAME%", gamenameFromFile)
    fileName = fileName.replace("%PLATFORM%", release.platform.name)
    
    rootExtFile = os.path.splitext(fileName)
    gameName = rootExtFile[0] + ".*"
    dirs, files, dirname, filemask = filewalker.getFilesByWildcard(gameName)
    
    #check if file already exists
    if(len(files) > 0):
        Logutil.log("File already exists. Won't download again.", util.LOG_LEVEL_INFO)
        return files[0], True
        
    if(isLocalArtwork):
        Logutil.log("local artwork mode. Won't download files", util.LOG_LEVEL_INFO)
        return None, True
    
    Logutil.log("File does not exist. Starting download.", util.LOG_LEVEL_INFO)
    file, continueUpdate = getThumbFromOnlineSource(release, path.type, fileName, gui)
    if(not continueUpdate):
        return None, False
    return file, True    

            

def getThumbFromOnlineSource(game, fileType, fileName, gui):
    Logutil.log("Get thumb from online source", util.LOG_LEVEL_INFO)
    try:        
        thumbUrl = game.artworkurls[fileType]
            
        if(thumbUrl == '' or thumbUrl == None):
            Logutil.log("No artwork of type %s found." %fileType, util.LOG_LEVEL_INFO)
            return None, True
        
        Logutil.log("Get thumb from url: " + str(thumbUrl), util.LOG_LEVEL_INFO)
        
        rootExtFile = os.path.splitext(fileName)
        rootExtUrl = os.path.splitext(thumbUrl)
        
        if(len(rootExtUrl) == 2 and len(rootExtFile) != 0):
            fileName = rootExtFile[0] + rootExtUrl[1]
        
        #create folder structure
        dirname = os.path.dirname(fileName)
        if(not xbmcvfs.exists(dirname)):
            try:
                Logutil.log("Creating directory: %s"%dirname, util.LOG_LEVEL_INFO)
                xbmcvfs.mkdirs(dirname)
            except Exception, (exc):
                Logutil.log("Could not create directory: '%s'. Error message: '%s'" % (dirname, str(exc)), util.LOG_LEVEL_ERROR)
                xbmcgui.Dialog().ok(util.localize(35010), util.localize(35011))                
                return None, False
                    
        Logutil.log("Download file to: " + str(fileName), util.LOG_LEVEL_INFO)

        # fetch thumbnail and save to filepath
        try:
            #download file to local folder and copy it to smb path with xbmcvfs
            if(fileName.startswith('smb://')):
                localFile = util.joinPath(util.getTempDir(), os.path.basename(fileName))
                urllib.urlretrieve(thumbUrl, localFile)
                xbmcvfs.copy(localFile, fileName)
                xbmcvfs.delete(localFile)
            else:
                urllib.urlretrieve(thumbUrl, str(fileName))
        except Exception, (exc):
            #Don't show message box when file download fails
            Logutil.log("Could not create file: '%s'. Error message: '%s'" % (str(fileName), str(exc)), util.LOG_LEVEL_ERROR)
            return None, False
        
        # cleanup any remaining urllib cache
        urllib.urlcleanup()
        Logutil.log("Download finished.", util.LOG_LEVEL_INFO)
    except Exception, (exc):
        Logutil.log("Error in getThumbFromOnlineSource: " + str(exc), util.LOG_LEVEL_WARNING)                        

    return fileName, True
