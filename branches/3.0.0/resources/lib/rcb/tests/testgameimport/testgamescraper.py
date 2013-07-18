
import unittest

from resources.lib.rcb.utils import util
from resources.lib.rcb.gameimport import gamescraper
from resources.lib.rcb.configuration import config
from resources.lib.rcb.configuration.config import *

from resources.lib.heimdall.src.heimdall.predicates import *


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
        
        gamename = 'Super Mario Kart'
                                
        game, artWorkFound, artworkfiles, artworkurls = gamescraper.scrapeGame(gamename, romCollection, util.getSettings(), '', 0, RCBMock(), 'Header', 1)        
        
        print game.name
        print game.yearFromScraper
        print game.genreFromScraper
        
        
    def test_mergeResults(self):
        
        result1 = {'key 1': 'value 1'}
        result2 = {'key 1': 'value 2',
                   'key 2': 'value 3'}
        result3 = {'key 2': 'value 4',
                   'key 3': 'value 5',
                   'key 4': 'value 6'}
        
        results = []
        results.append(result1)
        results.append(result2)
        results.append(result3)
        
        result = gamescraper.mergeResults(results)
        
        self.assertEqual(4, len(result.keys()), 'Error len')
        self.assertEqual('value 1', result['key 1'], 'Error key 1')
        self.assertEqual('value 3', result['key 2'], 'Error key 2')
        self.assertEqual('value 5', result['key 3'], 'Error key 3')
        self.assertEqual('value 6', result['key 4'], 'Error key 4')
         
        
        
        
class RCBMock:
    
    itemCount = 0
    
    def writeMsg(self, msg1, msg2, msg3, count=0):
        return True
