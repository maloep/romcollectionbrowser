
import unittest

from resources.lib.rcb.utils import util
from resources.lib.rcb.gameimport import gamescraper
from resources.lib.rcb.configuration import config
from resources.lib.rcb.configuration.config import *

from resources.lib.heimdall.src.heimdall.predicates import *
from resources.lib.heimdall.src.heimdall.core import Subject


class TestGameScraper(unittest.TestCase):

    def setUp(self):
        util.RCBHOME = os.path.join(os.getcwd(), '..', '..', '..', '..', '..')
        util.ISTESTRUN = True
    
    def tearDown(self):
        pass
    
    
    def test_scrapeGame(self):
        
        myConfig = Config('config.xml')
        statusOk, errorMsg = myConfig.readXml()

        romCollection = myConfig.romCollections['1']
        
        gamename = "NBA Live 98"
                
        game, continueUpdate = gamescraper.scrapeGame(gamename, '', myConfig, romCollection, util.getSettings(), '', 0, RCBMock(), 'Header', 1)
        
        print game.name
        print game.releases[0].year
        print game.genres
        print game.releases[0].artworkurls
        
        
        
    def test_fromHeimdallToRcb(self):
        
        myConfig = Config('config.xml')
        statusOk, errorMsg = myConfig.readXml()

        romCollection = myConfig.romCollections['1']
        
        scraperresults = []
        scraperresult = []
        #thegamesdb results
        metadata = dict()
        metadata[dc.title] = ['Super Mario Kart']
        metadata[edamontology.data_3106] = ['Super Nintendo (SNES)']
        subject = Subject('item.game', metadata)
        scraperresult.append(subject)
        metadata = dict()
        metadata[dc.title] = ['Super Nintendo (SNES)']
        metadata[dc.description] = ['Console from Nintendo']
        metadata['cpu'] = ['16-bit 65c816 Ricoh 5A22 3.58 MHz']
        subject = Subject('item.platform', metadata)
        scraperresult.append(subject)
        scraperresults.append(scraperresult)
        
        #giantbomb
        metadata = dict()
        scraperresult = []
        metadata[dc.title] = ['Super Mario Kart 2']
        metadata[dc.date] = ['1992-09-01 00:00:00']
        subject = Subject('item.game', metadata)
        scraperresult.append(subject)
        metadata = dict()
        metadata[dc.title] = ['Super Nintendo Entertainment System']
        metadata['originalprice'] = ['199.00']
        subject = Subject('item.platform', metadata)
        scraperresult.append(subject)
        metadata = dict()
        metadata[dc.title] = ['Shigeru Miyamoto']
        metadata['birthdate'] = ['1952-11-16']
        subject = Subject('item.person', metadata)
        scraperresult.append(subject)
        metadata = dict()
        metadata[dc.title] = ['Hiroshi Yamauchi']
        metadata['birthdate'] = ['1927-11-07']
        subject = Subject('item.person', metadata)
        scraperresult.append(subject)
        scraperresults.append(scraperresult)
        
        #mobygames
        metadata = dict()
        scraperresult = []
        metadata[dc.title] = ['Super Mario Kart 2']
        metadata[dc.date] = ['1992-09-01 00:00:00']
        subject = Subject('item.game', metadata)
        scraperresult.append(subject)
        metadata = dict()
        metadata[dc.title] = ['SNES']        
        subject = Subject('item.platform', metadata)
        scraperresult.append(subject)
        metadata = dict()
        metadata[dc.title] = ['Shigeru Miyamoto']
        metadata[dc.description] = ['Shigeru Miyamoto Desc']
        metadata['role'] = ['Producer']
        subject = Subject('item.person', metadata)
        scraperresult.append(subject)
        metadata = dict()
        metadata[dc.title] = ['Hiroshi Yamauchi']
        metadata[dc.description] = ['Hiroshi Yamauchi Desc']
        metadata['role'] = ['Developer']
        subject = Subject('item.person', metadata)
        scraperresult.append(subject)
        scraperresults.append(scraperresult)
        
        game = gamescraper.fromHeimdallToRcb(scraperresults, 'Super Mario Kart', '', myConfig, romCollection)
        print game.name
        print game.releases[0].year
        print game.releases[0].platform.name
        print game.releases[0].platform.description
        print game.releases[0].persons[0].name
        print game.releases[0].persons[0].role
        
        
        
class RCBMock:
    
    itemCount = 0
    
    def writeMsg(self, msg1, msg2, msg3, count=0):
        return True
