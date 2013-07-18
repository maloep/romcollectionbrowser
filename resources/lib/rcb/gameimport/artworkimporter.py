
import os, urllib

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import Logutil
from resources.lib.heimdall.src.heimdall.predicates import *

import filewalker, dbupdater
import xbmcvfs, xbmcgui


#TODO use game instead of result
def getArtworkForGame(romCollection, result, gamenameFromFile, gui, foldername, isLocalArtwork):
    artWorkFound = False
    artworkfiles = {}
    artworkurls = {}
    for path in romCollection.mediaPaths:
                    
        Logutil.log("FileType: " +str(path.fileType.name), util.LOG_LEVEL_INFO)            
        
        #TODO replace %ROMCOLLECTION%, %PUBLISHER%, ... 
        fileName = path.path.replace("%GAME%", gamenameFromFile)
                                
        
        if(not isLocalArtwork):
            continueUpdate, artworkurls = getThumbFromOnlineSource(result, path.fileType.name, fileName, gui, artworkurls)
            if(not continueUpdate):
                return False, None, None
        
        
        gamename = ''
        publisher = ''
        developer = ''
        if(result):
            gamename = result[dc.title][0]
            publisher = result[swo.SWO_0000397][0]
            developer = result[swo.SWO_0000396][0]
        
        Logutil.log("Additional data path: " +str(path.path), util.LOG_LEVEL_DEBUG)
        files = resolvePath((path.path,), gamename, gamenameFromFile, foldername, romCollection.name, publisher, developer)
        if(len(files) > 0):
            artWorkFound = True
            
            #HACK: disable static image check as a preparation for new default image handling (this code has problems with [] in rom names)                
            """
            imagePath = str(self.resolvePath((path.path,), gamename, gamenameFromFile, foldername, romCollection.name, publisher, developer))
            staticImageCheck = imagePath.upper().find(gamenameFromFile.upper())
            
            #make sure that it was no default image that was found here
            if(staticImageCheck != -1):
                artWorkFound = True
            """                            
        
        artworkfiles[path.fileType] = files
    
    return artWorkFound, artworkfiles, artworkurls
    
    
def resolvePath(paths, gamename, gamenameFromFile, foldername, romCollectionName, publisher, developer):        
    resolvedFiles = []                
            
    for path in paths:
        files = []
        Logutil.log("resolve path: " + path, util.LOG_LEVEL_INFO)
        
        if(path.find("%GAME%") > -1):
            
            pathnameFromFile = path.replace("%GAME%", gamenameFromFile)                                    
            Logutil.log("resolved path from rom file name: " + pathnameFromFile, util.LOG_LEVEL_INFO)                    
            files = filewalker.getFilesByWildcard(pathnameFromFile)
            if(len(files) == 0):
                files = filewalker.getFilesByGameNameIgnoreCase(pathnameFromFile)
            
            if(gamename != gamenameFromFile and len(files) == 0):
                pathnameFromGameName = path.replace("%GAME%", gamename)
                Logutil.log("resolved path from game name: " + pathnameFromGameName, util.LOG_LEVEL_INFO)                
                files = filewalker.getFilesByWildcard(pathnameFromGameName)
                if(len(files) == 0):
                    files = filewalker.getFilesByGameNameIgnoreCase(pathnameFromGameName)                                
                                
            if(gamename != foldername and len(files) == 0):
                pathnameFromFolder = path.replace("%GAME%", foldername)                    
                Logutil.log("resolved path from rom folder name: " + pathnameFromFolder, util.LOG_LEVEL_INFO)                    
                files = filewalker.getFilesByWildcard(pathnameFromFolder)
                if(len(files) == 0):
                    files = filewalker.getFilesByGameNameIgnoreCase(pathnameFromFolder)
            
            
        #TODO could be done only once per RomCollection
        if(path.find("%ROMCOLLECTION%") > -1 and romCollectionName != None and len(files) == 0):
            pathnameFromRomCollection = path.replace("%ROMCOLLECTION%", romCollectionName)
            Logutil.log("resolved path from rom collection name: " + pathnameFromRomCollection, util.LOG_LEVEL_INFO)
            files = filewalker.getFilesByWildcard(pathnameFromRomCollection)                
            
        if(path.find("%PUBLISHER%") > -1 and publisher != None and len(files) == 0):
            pathnameFromPublisher = path.replace("%PUBLISHER%", publisher)
            Logutil.log("resolved path from publisher name: " + pathnameFromPublisher, util.LOG_LEVEL_INFO)
            files = filewalker.getFilesByWildcard(pathnameFromPublisher)                
            
        if(path.find("%DEVELOPER%") > -1 and developer != None and len(files) == 0):
            pathnameFromDeveloper = path.replace("%DEVELOPER%", developer)
            Logutil.log("resolved path from developer name: " + pathnameFromDeveloper, util.LOG_LEVEL_INFO)
            files = filewalker.getFilesByWildcard(pathnameFromDeveloper)                                                    
        
        if(path.find("%GAME%") == -1 & path.find("%ROMCOLLECTION%") == -1 & path.find("%PUBLISHER%") == -1 & path.find("%DEVELOPER%") == -1):
            pathnameFromStaticFile = path
            Logutil.log("using static defined media file from path: " + pathnameFromStaticFile, util.LOG_LEVEL_INFO)
            files = filewalker.getFilesByWildcard(pathnameFromStaticFile)            
            
        if(len(files) == 0):
            Logutil.log('No files found for game "%s" at path "%s". Make sure that file names are matching.' % (gamename, path), util.LOG_LEVEL_WARNING)
        for file in files:
            if(xbmcvfs.exists(file)):
                resolvedFiles.append(file)
                
    return resolvedFiles
            

def getThumbFromOnlineSource(result, fileType, fileName, gui, artworkurls):
    Logutil.log("Get thumb from online source", util.LOG_LEVEL_INFO)
    try:
        #HACK: translate heimdall artwork types to RCB artwork types
        if(fileType == 'fanart'):
            #fanart can be string, dict or list of dicts
            thumbUrl = result['fanart'][0]
            if(type(thumbUrl) == list):
                thumbUrl = thumbUrl[0]['fanart']
            elif(type(thumbUrl) == dict):
                thumbUrl = thumbUrl['fanart']
        else:
            thumbUrl = result[fileType][0]
            
        if(thumbUrl == '' or thumbUrl == None):
            Logutil.log("No artwork of type %s found." %fileType, util.LOG_LEVEL_INFO)
            return True, artworkurls
        
        artworkurls[fileType] = thumbUrl
        
        Logutil.log("Get thumb from url: " + str(thumbUrl), util.LOG_LEVEL_INFO)
        
        rootExtFile = os.path.splitext(fileName)
        rootExtUrl = os.path.splitext(thumbUrl)
        
        if(len(rootExtUrl) == 2 and len(rootExtFile) != 0):
            fileName = rootExtFile[0] + rootExtUrl[1]
            gameName = rootExtFile[0] + ".*"
            files = filewalker.getFilesByWildcard(gameName)
        
        #check if folder exists
        dirname = os.path.dirname(fileName)
        #check parent folder
        parent = os.path.dirname(dirname)
        if(not xbmcvfs.exists(parent)):
            try:
                xbmcvfs.mkdir(parent)
            except Exception, (exc):
                xbmcgui.Dialog().ok(util.localize(35010), util.localize(35011))
                Logutil.log("Could not create directory: '%s'. Error message: '%s'" % (parent, str(exc)), util.LOG_LEVEL_ERROR)
                return False, artworkurls
            
        #check artwork specific folders
        if(not xbmcvfs.exists(dirname)):
            try:
                xbmcvfs.mkdir(dirname)
            except Exception, (exc):
                xbmcgui.Dialog().ok(util.localize(35010), util.localize(35011))
                Logutil.log("Could not create directory: '%s'. Error message: '%s'" % (dirname, str(exc)), util.LOG_LEVEL_ERROR)
                return False, artworkurls
            
        
        Logutil.log("Download file to: " + str(fileName), util.LOG_LEVEL_INFO)            
        if(len(files) == 0):
            Logutil.log("File does not exist. Starting download.", util.LOG_LEVEL_INFO)
            
            """
            #Dialog Status Art Download
            try:
                if(dialogDict != ''):
                    progDialogHeader = dialogDict["dialogHeaderKey"]
                    gamenameFromFile = dialogDict["gameNameKey"]
                    scraperSiteName = dialogDict["scraperSiteKey"]
                    fileCount = dialogDict["fileCountKey"]
                    gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, str(scraperSiteName[thumbKey]) + " - downloading art", fileCount)
            except:
                pass
            """

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
                #xbmcgui.Dialog().ok(util.localize(35012), util.localize(35011))
                Logutil.log("Could not create file: '%s'. Error message: '%s'" % (str(fileName), str(exc)), util.LOG_LEVEL_ERROR)
                return False, artworkurls
            
            # cleanup any remaining urllib cache
            urllib.urlcleanup()
            Logutil.log("Download finished.", util.LOG_LEVEL_INFO)
        else:
            Logutil.log("File already exists. Won't download again.", util.LOG_LEVEL_INFO)
    except Exception, (exc):
        Logutil.log("Error in getThumbFromOnlineSource: " + str(exc), util.LOG_LEVEL_WARNING)                        

    return True, artworkurls
