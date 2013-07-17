
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
        
        gamename = 'Prince of Persia I'
        
        import json
        jsonResult = json.loads('{"error":"OK","limit":100,"offset":0,"number_of_page_results":2,"number_of_total_results":2,"status_code":1,"results":[{"api_detail_url":"http:\/\/www.giantbomb.com\/api\/game\/3030-19071\/","name":"Super Mario Kart","resource_type":"game"},{"api_detail_url":"http:\/\/www.giantbomb.com\/api\/game\/3030-16769\/","name":"Mario Kart: Super Circuit","resource_type":"game"}],"version":"1.0"}')
                
        print jsonResult['error']
        print jsonResult['status_code']
        print jsonResult['results']
        
                
        """        
        game, artWorkFound, artworkfiles, artworkurls = gamescraper.scrapeGame(gamename, romCollection, util.getSettings(), '', 0, RCBMock(), 'Header', 1)        
        print game.name
        print game.yearFromScraper
        print game.genreFromScraper
        """
        
        
class RCBMock:
    
    itemCount = 0
    
    def writeMsg(self, msg1, msg2, msg3, count=0):
        return True
