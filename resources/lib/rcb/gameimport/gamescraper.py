
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
        gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, util.localize(40098), fileCount)
        artWorkFound, artworkfiles, artworkurls = artworkimporter.getArtworkForGame(romCollection, result, gamenameFromFile, gui, foldername, False)
        game = fromHeimdallToRcb(result)
        return game, artWorkFound, artworkfiles, artworkurls
                
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
    
    game.name = result[dc.title][0]
    
    genres = result[dc.type][0]
    if(type(genres) == str):
        game.genreFromScraper = [genres,]
    elif(genres):
        game.genreFromScraper = []
        for genre in genres:
            game.genreFromScraper.append(genre)
    
    game.description = result[dc.description][0]
    try:
        # Deserialize MM/DD/YYYY
        game.yearFromScraper = result[dc.date][0][0:4]
    except:
        # can't be parsed by strptime()
        pass
    game.rating = result[media.rating][0]
        
    #TODO add more than 1 developer
    developers = result[swo.SWO_0000396][0]
    if(type(developers) == str or type(developers) == unicode):
        game.developerFromScraper = developers
    elif(type(developers) == list):
        game.developerFromScraper = developers[0]
    else:
        print "Developer type %s is not supported" %type(developers)
                
    #TODO add more than 1 publisher
    publishers = result[swo.SWO_0000397][0]
    if(type(publishers) == str or type(publishers) == unicode):
        game.publisherFromScraper = publishers
    elif(type(publishers) == list):
        game.publisherFromScraper = publishers[0]
    else:
        print "Publisher type %s is not supported" %type(publishers)
    
    game.maxPlayers = result["players"][0]
    
    return game


