
import os

import resultmatcher, filewalker, artworkimporter

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import Logutil
from resources.lib.rcb.datamodel.game import Game
from resources.lib.rcb.datamodel.release import Release
from resources.lib.rcb.datamodel.developer import Developer
from resources.lib.rcb.datamodel.publisher import Publisher
from resources.lib.rcb.configuration import config

from resources.lib.heimdall.src.heimdall.core import Engine, Subject
from resources.lib.heimdall.src.heimdall.predicates import *
from resources.lib.heimdall.src.heimdall.threadpools import MainloopThreadPool

from resources.lib.heimdall.src.games import thegamesdb, giantbomb, mobygames


import logging
from resources.lib.rcb.datamodel.platform import Platform
from resources.lib.rcb.datamodel.person import Person
logging.basicConfig()
logging.getLogger("heimdall").setLevel(logging.CRITICAL)


"""
Scrape game with all configured scrapers
Scrape additional items (platform, companies, persons)
Download artwork
"""
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
        artWorkFound, artworkfiles = artworkimporter.getArtworkForRelease(romCollection, game.releases[0], gamenameFromFile, gui, foldername, False)        
        return game, artWorkFound, artworkfiles, game.releases[0].artworkurls
    
                
    return None, False, {}, {}


"""
Scrape additional items (platform, companies, persons, ...)
"""
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
        #nbrBeforeQuit = nbrBeforeQuit + len(gameresult['person'])
        #TODO: limit to 3 persons for test purposes only
        nbrBeforeQuit = nbrBeforeQuit + 3
        
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
    
    
"""
Scrape game with given scraper
"""
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
    
"""
def mergeResults(dicts):
    
    result = {}
    #reverse dicts to have "first come, first go"-logic
    dicts.reverse()
    for dict in dicts:        
        result.update(dict)
    return result
"""


"""
Translate heimdall result to RCB game structure
"""
def fromHeimdallToRcb(results):
    
    game = Game(None)
    release = Release(None)
    
    for scraperresult in results:
        for result in scraperresult:
            
            if(result.Class == 'item.game'):
                gamename = readHeimdallValue(result, dc.title, '')
                #TODO: different names for release and game?
                if(game.name == ''):
                    game.name = gamename
                if(release.name == ''):
                    release.name = gamename
                
                genres = readHeimdallValueList(result, dc.type, 'name')
                for genre in genres:                
                    if(not genre in game.genres):
                        game.genres.append(genre)
                
                if(release.description == ''):
                    release.description = readHeimdallValue(result, dc.description, '')
                
                if(release.year == ''):
                    date = readHeimdallValue(result, dc.date, '')
                    if(len != ''):
                        release.year = date[0:4]
                if(release.ESRBrating == ''):
                    release.ESRBrating = readHeimdallValue(result, media.rating, '')
                if(release.maxPlayers == ''):
                    release.maxPlayers = readHeimdallValue(result, "players", '')
                
                if(release.developer == None):
                    release.developer = Developer(None)
                    release.developer.name = readHeimdallValue(result, swo.SWO_0000396, '')
                if(release.publisher == None):
                    release.publisher = Publisher(None)
                    release.publisher.name = readHeimdallValue(result, swo.SWO_0000397, '')
                
                #TODO: translate heimdall artwork types to RCB artwork type
                #TODO: support more than 1 image per artwork type                
                artworkurl = readHeimdallValue(result, 'fanart', 'fanart')
                if(artworkurl != ''):
                    release.artworkurls['fanart'] = artworkurl
                artworkurl = readHeimdallValue(result, 'boxfront', 'boxfront')
                if(artworkurl != ''):
                    release.artworkurls['boxfront'] = artworkurl
                artworkurl = readHeimdallValue(result, 'boxback', 'boxback')
                if(artworkurl != ''):
                    release.artworkurls['boxback'] = artworkurl
                artworkurl = readHeimdallValue(result, 'cartridge', 'cartridge')
                if(artworkurl != ''):
                    release.artworkurls['cartridge'] = artworkurl
                artworkurls = readHeimdallValue(result, 'screenshot', 'screenshot')
                if(artworkurl != ''):
                    release.artworkurls['screenshot'] = artworkurl
            
            elif(result.Class == 'item.platform'):
                if(release.platform == None):
                    release.platform = Platform(None)
                if(release.platform.name == ''):
                    release.platform.name = readHeimdallValue(result, dc.title, '')
                if(release.platform.description == ''):
                    release.platform.description = readHeimdallValue(result, dc.description, '')
                if(release.platform.releasedate == ''):
                    #TODO: format date
                    release.platform.releasedate = readHeimdallValue(result, dc.date, '')                    
            
            elif(result.Class == 'item.person'):
                person = None
                newPerson = True
                personname = readHeimdallValue(result, dc.title, '')
                if(len(release.persons) == 0):
                    person = Person(None)
                else:
                    #check if we have to update an existing person
                    for p in release.persons:
                        #TODO: name may not be strong enough
                        if(p.name == personname):
                            person = p
                            newPerson = False
                    if(not person):
                        person = Person(None)
                if(person.name == ''):         
                    person.name = personname
                if(person.role == ''):
                    person.role = readHeimdallValue(result, 'role', '')
                if(newPerson):
                    release.persons.append(person)
    
    game.releases.append(release)
    return game


#heimdall results can be string, dict, list or list of dicts
def readHeimdallValueList(indict, key, nestedKey):
    resultlist = []
    result = readFromDict(indict, key)
    if(type(result) == str or type(result) == unicode):
        resultlist.append(result)
    elif(type(result) == list):
        for item in result:
            if(type(item) == str or type(item) == unicode):
                itemString = item
            if(type(item) == dict):
                itemString = readFromDict(item, nestedKey)
            resultlist.append(itemString)
    elif(type(result) == dict):
        item = readFromDict(result, nestedKey)
        resultlist.append(item)
    
    return resultlist


def readHeimdallValue(indict, key, nestedKey):
    resultlist = readHeimdallValueList(indict, key, nestedKey)
    if(len(resultlist) > 0):
        return resultlist[0]
    return ''


def readFromDict(indict, key):
    resultValue = ''
    try:
        resultValue = indict[key]
    except:
        pass
    
    return resultValue
