
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import Logutil
from resources.lib.rcb.datamodel.game import Game

import resultmatcher

from resources.lib.heimdall.src.heimdall.core import Engine, Subject
from resources.lib.heimdall.src.heimdall.predicates import *
from resources.lib.heimdall.src.heimdall.threadpools import MainloopThreadPool

from resources.lib.heimdall.src.games import thegamesdb


import logging
logging.basicConfig()
logging.getLogger("heimdall").setLevel(logging.CRITICAL)


def scrapeGame(gamenameFromFile, romCollection, settings, updateOption, gui, progDialogHeader, fileCount):
            
    #gui.writeMsg(progDialogHeader, util.localize(40023) + ": " + gamenameFromFile, scraper.name + " - " + util.localize(40031), fileCount)
    
    result = scrapeHeimdall(gamenameFromFile)
    #check if scraper found a result or if we get a list of game names
    if(type(result[dc.title]) == str):
        game = fromHeimdallToRcb(result)
        return game
    #check if scraper found a result or if we get a list of game names    
    if(type(result[dc.title]) == list):
        Logutil.log('heimdall returned list of game names: %s. Will check for best result.' %result[dc.title], util.LOG_LEVEL_INFO)
        result = resultmatcher.matchResult(result[dc.title], gamenameFromFile, settings, updateOption)
        
        #try again with new gamename
        if (result):
            result = scrapeHeimdall(result)
            game = fromHeimdallToRcb(result)
            return game
                
    return None
    
    
def scrapeHeimdall(gamenameFromFile):
    print "Running Heimdall upon: ", gamenameFromFile.encode('utf-8')

    pool = MainloopThreadPool()
    engine = Engine(pool)
    #engine.registerModule(item.module)
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


