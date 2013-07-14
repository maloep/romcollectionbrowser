
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import Logutil
from resources.lib.rcb.datamodel.game import Game

import resultmatcher

from resources.lib.heimdall.src.heimdall.core import Engine, Subject
from resources.lib.heimdall.src.heimdall.predicates import *
from resources.lib.heimdall.src.heimdall.threadpools import MainloopThreadPool,\
    OptimisticThreadPool

from resources.lib.heimdall.src.games import thegamesdb
from resources.lib.heimdall.src import artwork


import logging
logging.basicConfig()
logging.getLogger("heimdall").setLevel(logging.CRITICAL)


def scrapeGame(gamenameFromFile, romCollection, settings, updateOption, gui, progDialogHeader, fileCount):
            
    gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, util.localize(40031), fileCount)
    result = scrapeHeimdall(gamenameFromFile)
        
    #check if scraper found a result or if we get a list of game names    
    if(result != None and type(result[dc.title]) == list):
        Logutil.log('heimdall returned list of game names: %s. Will check for best result.' %result[dc.title], util.LOG_LEVEL_INFO)
        result = resultmatcher.matchResult(result[dc.title], gamenameFromFile, settings, updateOption)
        
        #try again with new gamename
        if (result):
            result = scrapeHeimdall(result)
    
    if(result):
        gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, util.localize(40098), fileCount)
        downloadArtwork(result, romCollection)
        game = fromHeimdallToRcb(result)
        return game
                
    return None
    
    
def scrapeHeimdall(gamenameFromFile):
    print "Running Heimdall upon: ", gamenameFromFile.encode('utf-8')

    pool = MainloopThreadPool()
    engine = Engine(pool)
    engine.registerModule(thegamesdb.module)

    def c(error, subject):
        if error:
            pass
            #raise error
        print subject
        pool.quit()

    metadata = dict()
    metadata[dc.title] = gamenameFromFile
    metadata[edamontology.data_3106] = 'Super Nintendo (SNES)'
    subject = Subject("", metadata)
    subject.extendClass("item.game")

    engine.get(subject, c)

    try:
        pool.join()
    except KeyboardInterrupt:
        pool.quit()

    #if there is not title there won't be anything else
    if(subject[dc.title] == None):
        subject = None
        
    return subject
    
    
def downloadArtwork(result, romCollection):
    
    pool = MainloopThreadPool()
    engine = Engine(pool)
    engine.registerModule(artwork.module)

    artworklist = ["boxfront", "fanart"]
    nbrBeforeQuit = 0
    for key in result.metadata.keys():
        if(key in artworklist):
            nbrBeforeQuit = nbrBeforeQuit +1
     
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
    
    for mediaPath in romCollection.mediaPaths:
        #TDOD: get correct downloadPath
        downloadpath = mediaPath.path.replace("%GAME%.*", "")
        if(mediaPath.fileType.name == "boxfront"):
            if(result["boxfront"]):
                subject = createSubject(result[dc.title], result["boxfront"], downloadpath)
                engine.get(subject, c)
        elif(mediaPath.fileType.name == "fanart"):
            if(result['fanart']):
                #fanart can be string, dict or list of dicts
                fanart = result['fanart']
                if(type(fanart) == list):
                    fanart = fanart[0]['fanart']
                elif(type(fanart) == dict):
                    fanart = fanart['fanart']
                subject = createSubject(result[dc.title], fanart, downloadpath)
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
    game.developerFromScraper = result[swo.SWO_0000396]
    game.publisherFromScraper = result[swo.SWO_0000397]
    game.maxPlayers = result["players"]
    
    return game


