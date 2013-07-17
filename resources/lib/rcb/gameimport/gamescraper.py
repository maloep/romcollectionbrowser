
import os

import resultmatcher, filewalker, artworkimporter

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import Logutil
from resources.lib.rcb.datamodel.game import Game
from resources.lib.rcb.configuration import config

from resources.lib.heimdall.src.heimdall.core import Engine, Subject
from resources.lib.heimdall.src.heimdall.predicates import *
from resources.lib.heimdall.src.heimdall.threadpools import MainloopThreadPool

from resources.lib.heimdall.src.games import thegamesdb, giantbomb


import logging
logging.basicConfig()
logging.getLogger("heimdall").setLevel(logging.DEBUG)


def scrapeGame(gamenameFromFile, romCollection, settings, foldername, updateOption, gui, progDialogHeader, fileCount):
            
    gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, util.localize(40031), fileCount)
    
    results = []
    for scraper in romCollection.scraperSites:
        result = scrapeHeimdall(gamenameFromFile, scraper.name)
            
        #check if scraper found a result or if we get a list of game names    
        if(result != None and type(result[dc.title]) == list):
            Logutil.log('heimdall returned list of game names: %s. Will check for best result.' %result[dc.title], util.LOG_LEVEL_INFO)
            result = resultmatcher.matchResult(result[dc.title], gamenameFromFile, settings, updateOption)
            
            #try again with new gamename
            if (result):
                result = scrapeHeimdall(result, scraper.name)
        #append results from different scrapers
        if(result):
            results.append(result)
            
    #TODO merge results
    result = results[1]
    
    if(result):
        gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, util.localize(40098), fileCount)
        artWorkFound, artworkfiles, artworkurls = artworkimporter.getArtworkForGame(romCollection, result, gamenameFromFile, gui, foldername, False)
        game = fromHeimdallToRcb(result)
        return game, artWorkFound, artworkfiles, artworkurls
                
    return None, False, {}, {}
    
    
def scrapeHeimdall(gamenameFromFile, scraper):
    print "Running Heimdall upon: ", gamenameFromFile.encode('utf-8')

    pool = MainloopThreadPool()
    engine = Engine(pool)
    
    def c(error, subject):
        if error:
            pass
            #raise error
        print subject
        pool.quit()
                
    metadata = dict()
    metadata[dc.title] = gamenameFromFile
        
    if(scraper == "thegamesdb.net"):
        #TODO platform mapping
        metadata[edamontology.data_3106] = 'Super Nintendo (SNES)'
        engine.registerModule(thegamesdb.module)
    
    elif(scraper == "giantbomb.com"):
        #TODO platform mapping
        metadata[edamontology.data_3106] = '9'
        metadata['apikey'] = util.API_KEYS['%GIANTBOMBAPIKey%']
        #TODO region mapping
        metadata['preferredregion'] = 'United States'
        engine.registerModule(giantbomb.module)
    
    subject = Subject("", metadata)
    subject.extendClass("item.game")
    engine.get(subject, c)

    try:
        pool.join()
    except KeyboardInterrupt:
        pool.quit()

    #if there is no title there won't be anything else
    if(subject[dc.title] == None):
        subject = None
        
    return subject
    
    
"""
def downloadArtwork(result, romCollection):
    
    pool = MainloopThreadPool()
    engine = Engine(pool)
    engine.registerModule(artwork.module)

    #check when we have to quit processing
    artworklist = ["boxfront", "fanart"]
    nbrBeforeQuit = 0
    for key in result.metadata.keys():
        if(key in artworklist):
            nbrBeforeQuit = nbrBeforeQuit +1
     
    #if there is no artwork, return immediately
    if(nbrBeforeQuit == 0):
        return
    
    subjects = []

    def c(error, subject):
        if error:
            raise error

        print subject
        subjects.append(subject)

        if len(subjects) >= nbrBeforeQuit:
            pool.quit()
        
    #check and download every single artwork type
    for mediaPath in romCollection.mediaPaths:
        if(mediaPath.fileType.name == "boxfront"):
            if(result["boxfront"]):
                artworkFilename = getArtworkFilename(mediaPath, result[dc.title], result["boxfront"])
                continueDownload = checkLocalArtworkfolders(mediaPath, result[dc.title], result["boxfront"])
                subject = createSubject(result[dc.title], result["boxfront"], artworkFilename)
                engine.get(subject, c)
        elif(mediaPath.fileType.name == "fanart"):
            if(result['fanart']):
                artworkFilename = getArtworkFilename(mediaPath, result[dc.title], result["fanart"])
                #fanart can be string, dict or list of dicts
                fanart = result['fanart']
                if(type(fanart) == list):
                    fanart = fanart[0]['fanart']
                elif(type(fanart) == dict):
                    fanart = fanart['fanart']
                subject = createSubject(result[dc.title], fanart, artworkFilename)
                engine.get(subject, c)
        
    try:
        pool.join()
    except KeyboardInterrupt:
        pool.quit()
        

def createSubject(title, artworkurl, artworkpath):
    metadata = dict()
    metadata[dc.title] = title
    metadata['artworkurl'] = artworkurl
    metadata['artworkpath'] = artworkpath
    subject = Subject("", metadata)
    subject.extendClass("item.artwork")
    return subject    

def getArtworkFilename(mediaPath, gamename, artworkurl):
    #TODO replace %ROMCOLLECTION%, %PUBLISHER%, ... 
    filename = mediaPath.path.replace("%GAME%", gamename)
    
    rootExtFile = os.path.splitext(filename)
    rootExtUrl = os.path.splitext(artworkurl)
    
    if(len(rootExtUrl) == 2 and len(rootExtFile) != 0):
        filename = rootExtFile[0] + rootExtUrl[1]
    
    return filename


def checkLocalArtworkfolders(mediaPath, gamename, artworkurl):
    #TODO replace %ROMCOLLECTION%, %PUBLISHER%, ... 
    filename = mediaPath.path.replace("%GAME%", gamename)
    
    rootExtFile = os.path.splitext(filename)
    rootExtUrl = os.path.splitext(artworkurl)
    
    files = []
    if(len(rootExtUrl) == 2 and len(rootExtFile) != 0):
        gameName = rootExtFile[0] + ".*"
        files = filewalker.getFilesByWildcard(gameName)
        
    if(len(files > 0)):
        Logutil.log("File '%s' does already exist. Won't download again." %files[0], util.LOG_LEVEL_INFO)
        return False
    
    return True
"""


def fromHeimdallToRcb(result):
    
    game = Game(None)
    
    game.name = result[dc.title]
    
    genres = result[dc.type]
    if(type(genres) == str):
        game.genreFromScraper = [genres,]
    elif(genres):
        game.genreFromScraper = []
        for genre in genres:
            game.genreFromScraper.append(genre)
    
    game.description = result[dc.description]
    try:
        # Deserialize MM/DD/YYYY
        game.yearFromScraper = result[dc.date][0:4]
    except:
        # can't be parsed by strptime()
        pass
    game.rating = result[media.rating]
        
    #TODO add more than 1 developer
    developers = result[swo.SWO_0000396]
    if(type(developers) == str or type(developers) == unicode):
        game.developerFromScraper = developers
    elif(type(developers) == list):
        game.developerFromScraper = developers[0]
    else:
        print "Developer type %s is not supported" %type(developers)
                
    #TODO add more than 1 publisher
    publishers = result[swo.SWO_0000397]
    if(type(publishers) == str or type(publishers) == unicode):
        game.publisherFromScraper = publishers
    elif(type(publishers) == list):
        game.publisherFromScraper = publishers[0]
    else:
        print "Publisher type %s is not supported" %type(publishers)
    
    game.maxPlayers = result["players"]
    
    return game


