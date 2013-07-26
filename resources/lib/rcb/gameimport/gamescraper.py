
import os

import resultmatcher, filewalker, artworkimporter

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import Logutil
from resources.lib.rcb.datamodel.game import Game
from resources.lib.rcb.configuration import config

from resources.lib.heimdall.src.heimdall.core import Engine, Subject
from resources.lib.heimdall.src.heimdall.predicates import *
from resources.lib.heimdall.src.heimdall.threadpools import MainloopThreadPool

from resources.lib.heimdall.src.games import thegamesdb, giantbomb, mobygames


import logging
logging.basicConfig()
logging.getLogger("heimdall").setLevel(logging.CRITICAL)


def scrapeGame(gamenameFromFile, romCollection, settings, foldername, updateOption, gui, progDialogHeader, fileCount):
            
    gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, util.localize(40031), fileCount)
    
    results = []
    
    #scrape game
    for scraper in romCollection.scraperSites:
        scraperresults = []
        gameresult = heimdallScrapeGame(gamenameFromFile, romCollection, scraper.name)
            
        #check if scraper found a result or if we get a list of game names    
        if(gameresult != None and type(gameresult[dc.title]) == list):
            Logutil.log('heimdall returned list of game names: %s. Will check for best result.' %gameresult[dc.title], util.LOG_LEVEL_INFO)
            gameresult = resultmatcher.matchResult(gameresult[dc.title], gamenameFromFile, settings, updateOption)
            
            #try again with new gamename
            if (gameresult):
                gameresult = heimdallScrapeGame(gameresult, romCollection, scraper.name)
        
        if(gameresult):
            scraperresults.append(gameresult)
            #scrape additional items (platform, persons, companies, ...)
            scraperresults.extend(heimdallScrapeItems(gameresult, romCollection, scraper.name))
     
        results.append(scraperresults)
    
        
    
    if(len(results) > 0):
        game = fromHeimdallToRcb(results)
        gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, util.localize(40098), fileCount)
        artWorkFound, artworkfiles = artworkimporter.getArtworkForGame(romCollection, game, gamenameFromFile, gui, foldername, False)        
        return game, artWorkFound, artworkfiles, game.artworkurls_dbignore
    
                
    return None, False, {}, {}



def heimdallScrapeItems(gameresult, romCollection, scraper):
    #print "Running Heimdall upon: ", gamenameFromFile.encode('utf-8')
    
    pool = MainloopThreadPool()
    engine = Engine(pool)
    subjects = list()
        
    if(scraper == "thegamesdb.net"):
        #1 for platform scraping
        nbrBeforeQuit = 1
        
        def c(error, subject):
            if error:
                raise error
    
            print subject
            subjects.append(subject)
    
            if len(subjects) >= nbrBeforeQuit:
                pool.quit()
            
        metadata = dict()
        metadata[edamontology.data_3106] = config.consoleDict[romCollection.name][config.INDEX_THEGAMESDB_ID]
        engine.registerModule(thegamesdb.module)
        subject = Subject("", metadata)
        subject.extendClass("item.platform")
        engine.get(subject, c)
    
    elif(scraper == "giantbomb.com"):
        
        #TODO: check if items are already stored in database
        #1 for platform scraping
        nbrBeforeQuit = 1
        nbrBeforeQuit = nbrBeforeQuit + len(gameresult['person'])
        
        def c(error, subject):
            if error:
                raise error
    
            print subject
            subjects.append(subject)
    
            if len(subjects) >= nbrBeforeQuit:
                pool.quit()
                
        metadata = dict()
        metadata['platform_detail_url'] = gameresult['platform_detail_url']
        metadata['apikey'] = util.API_KEYS['%GIANTBOMBAPIKey%']
        engine.registerModule(giantbomb.module)
        subject = Subject("", metadata)
        subject.extendClass("item.platform")
        engine.get(subject, c)
                
        for person in gameresult['person']:
            metadata = dict()
            metadata['person_detail_url'] = person['detail_url']
            metadata['apikey'] = util.API_KEYS['%GIANTBOMBAPIKey%']
            engine.registerModule(giantbomb.module)
            subject = Subject("", metadata)
            subject.extendClass("item.person")
            engine.get(subject, c)
            
        
    """
    elif(scraper == "mobygames.com"):
        metadata[edamontology.data_3106] = config.consoleDict[romCollection.name][config.INDEX_MOBYGAMES]
        #TODO: region mapping
        metadata['preferredregion'] = 'United States'
        engine.registerModule(mobygames.module)
    """

    try:
        pool.join()
    except KeyboardInterrupt:
        pool.quit()
        
    return subjects
    
    
def heimdallScrapeGame(gamenameFromFile, romCollection, scraper):
    print "Running Heimdall upon: ", gamenameFromFile.encode('utf-8')

    pool = MainloopThreadPool()
    engine = Engine(pool)
    
    def c(error, subject):
        if error:
            raise error
        print subject
        pool.quit()
                
    metadata = dict()
    metadata[dc.title] = gamenameFromFile
        
    if(scraper == "thegamesdb.net"):
        metadata[edamontology.data_3106] = config.consoleDict[romCollection.name][config.INDEX_THEGAMESDB]
        engine.registerModule(thegamesdb.module)
    
    elif(scraper == "giantbomb.com"):
        metadata[edamontology.data_3106] = config.consoleDict[romCollection.name][config.INDEX_GIANTBOMB]
        metadata['apikey'] = util.API_KEYS['%GIANTBOMBAPIKey%']
        #TODO: region mapping
        metadata['preferredregion'] = 'United States'
        engine.registerModule(giantbomb.module)
    elif(scraper == "mobygames.com"):
        metadata[edamontology.data_3106] = config.consoleDict[romCollection.name][config.INDEX_MOBYGAMES]
        #TODO: region mapping
        metadata['preferredregion'] = 'United States'
        engine.registerModule(mobygames.module)
    
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


def fromHeimdallToRcb(results):
    
    game = Game(None)
    
    for scraperresult in results:
        for result in scraperresult:
            
            if(result.Class == 'item.game'):
                if(game.name == ''):
                    game.name = readHeimdallValue(result, dc.title)
                
                genres = readHeimdallValue(result, dc.type)
                if(type(genres) == str or type(genres) == unicode):
                    if(not genres in game.genre_dbignore):
                        game.genre_dbignore = [genres,]
                elif(type(genres) == list):
                    for genre in genres:
                        if(not genre in game.genre_dbignore):
                            game.genre_dbignore.append(genre)
                
                if(game.description == ''):
                    game.description = readHeimdallValue(result, dc.description)
                try:
                    date = readHeimdallValue(result, dc.date)
                    if(game.year_dbignore == ''):
                        game.year_dbignore = date[0:4]
                except:
                    # can't be parsed by strptime()
                    pass
                if(game.rating == ''):
                    game.rating = readHeimdallValue(result, media.rating)
                    
                #TODO: add more than 1 developer
                if(game.developer_dbignore == ''):
                    developers = readHeimdallValue(result, swo.SWO_0000396)                
                    if(type(developers) == str or type(developers) == unicode):
                        game.developer_dbignore = developers
                    elif(type(developers) == list):
                        game.developer_dbignore = developers[0]
                    else:
                        print "Developer type %s is not supported" %type(developers)
                            
                #TODO: add more than 1 publisher
                if(game.publisher_dbignore == ''):
                    publishers = readHeimdallValue(result, swo.SWO_0000397)
                    if(type(publishers) == str or type(publishers) == unicode):
                        game.publisher_dbignore = publishers
                    elif(type(publishers) == list):
                        game.publisher_dbignore = publishers[0]
                    else:
                        print "Publisher type %s is not supported" %type(publishers)
                
                if(game.maxPlayers == ''):
                    game.maxPlayers = readHeimdallValue(result, "players")
                
                
                game.artworkurls_dbignore = {}
                #TODO: translate heimdall artwork types to RCB artwork types
                artworkurl = readartworkurl(result, 'fanart')
                if(artworkurl):
                    game.artworkurls_dbignore['fanart'] = artworkurl 
                artworkurl = readartworkurl(result, 'boxfront')
                if(artworkurl):
                    game.artworkurls_dbignore['boxfront'] = artworkurl
                artworkurl = readartworkurl(result, 'boxback')
                if(artworkurl):
                    game.artworkurls_dbignore['boxback'] = artworkurl
                artworkurl = readartworkurl(result, 'cartridge')
                if(artworkurl):
                    game.artworkurls_dbignore['cartridge'] = artworkurl
                artworkurl = readartworkurl(result, 'screenshot')
                if(artworkurl):
                    game.artworkurls_dbignore['screenshot'] = artworkurl
    
    return game


def readHeimdallValue(metadata, key):
    resultValue = ''
    try:
        #heimdalls metadata is storing everything in lists. Just return the first item
        resultValue = metadata[key][0]
    except:
        pass
    
    return resultValue


def readartworkurl(result, artworkType):
    #artwork can be string, dict, list or list of dicts
    artworkurl = None
    if(readHeimdallValue(result, artworkType)):
        artworkurl = readHeimdallValue(result, artworkType)
        #TODO: use more than one images per type
        if(type(artworkurl) == list):
            if(type(artworkurl[0]) == dict):
                artworkurl = artworkurl[0][artworkType]
            else:
                artworkurl = artworkurl[0]
        elif(type(artworkurl) == dict):
            artworkurl = artworkurl[artworkType]
        
    return artworkurl
    
    