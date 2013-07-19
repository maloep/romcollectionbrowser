
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
        result = scrapeHeimdall(gamenameFromFile, romCollection, scraper.name)
            
        #check if scraper found a result or if we get a list of game names    
        if(result != None and type(result[dc.title]) == list):
            Logutil.log('heimdall returned list of game names: %s. Will check for best result.' %result[dc.title], util.LOG_LEVEL_INFO)
            result = resultmatcher.matchResult(result[dc.title], gamenameFromFile, settings, updateOption)
            
            #try again with new gamename
            if (result):
                result = scrapeHeimdall(result, romCollection, scraper.name)
        #append results from different scrapers
        if(result):
            results.append(result.metadata)
                
    result = mergeResults(results)
    
    #TODO use game instead of result to grab artwork
    if(result):
        game = fromHeimdallToRcb(result)
        gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, util.localize(40098), fileCount)
        artWorkFound, artworkfiles = artworkimporter.getArtworkForGame(romCollection, game, gamenameFromFile, gui, foldername, False)        
        return game, artWorkFound, artworkfiles, game.artworkurls_dbignore
                
    return None, False, {}, {}
    
    
def scrapeHeimdall(gamenameFromFile, romCollection, scraper):
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
        metadata[edamontology.data_3106] = config.consoleDict[romCollection.name][config.INDEX_THEGAMESDB]
        engine.registerModule(thegamesdb.module)
    
    elif(scraper == "giantbomb.com"):
        #TODO platform mapping
        metadata[edamontology.data_3106] = config.consoleDict[romCollection.name][config.INDEX_GIANTBOMB]
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
    

def mergeResults(dicts):
    
    result = {}
    #reverse dicts to have "first come, first go"-logic
    dicts.reverse()
    for dict in dicts:        
        result.update(dict)
    return result


def fromHeimdallToRcb(result):
    
    game = Game(None)
    
    game.name = readHeimdallValue(result, dc.title)
    
    genres = readHeimdallValue(result, dc.type)
    if(type(genres) == str):
        game.genre_dbignore = [genres,]
    elif(genres):
        game.genre_dbignore = []
        for genre in genres:
            game.genre_dbignore.append(genre)
    
    game.description = readHeimdallValue(result, dc.description)
    try:
        date = readHeimdallValue(result, dc.date)
        game.year_dbignore = date[0:4]
    except:
        # can't be parsed by strptime()
        pass
    game.rating = readHeimdallValue(result, media.rating)
        
    #TODO add more than 1 developer
    developers = readHeimdallValue(result, swo.SWO_0000396)
    if(type(developers) == str or type(developers) == unicode):
        game.developer_dbignore = developers
    elif(type(developers) == list):
        game.developer_dbignore = developers[0]
    else:
        print "Developer type %s is not supported" %type(developers)
                
    #TODO add more than 1 publisher
    publishers = readHeimdallValue(result, swo.SWO_0000397)
    if(type(publishers) == str or type(publishers) == unicode):
        game.publisher_dbignore = publishers
    elif(type(publishers) == list):
        game.publisher_dbignore = publishers[0]
    else:
        print "Publisher type %s is not supported" %type(publishers)
    
    game.maxPlayers = readHeimdallValue(result, "players")
    
    
    game.artworkurls_dbignore = {}    
    #TODO: translate heimdall artwork types to RCB artwork types
    #fanart from thegamesdb can be string, dict or list of dicts
    if(readHeimdallValue(result, 'fanart')):
        artworkurl = readHeimdallValue(result, 'fanart')
        if(type(artworkurl) == list):
            artworkurl = artworkurl[0]['fanart']
        elif(type(artworkurl) == dict):
            artworkurl = artworkurl['fanart']
        game.artworkurls_dbignore['fanart'] = artworkurl
    if(readHeimdallValue(result, 'boxfront')):
        game.artworkurls_dbignore['boxfront'] = readHeimdallValue(result, 'boxfront')
    
    return game


def readHeimdallValue(metadata, key):
    resultValue = ''
    try:
        #heimdalls metadata is storing everything in lists. Just return the first item
        resultValue = metadata[key][0]
    except:
        pass
    
    return resultValue
    
    