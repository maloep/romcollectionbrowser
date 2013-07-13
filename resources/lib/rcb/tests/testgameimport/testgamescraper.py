
import unittest

from resources.lib.rcb.utils import util
from resources.lib.rcb.gameimport import gamescraper
from resources.lib.rcb.configuration import config
from resources.lib.rcb.configuration.config import *

from resources.lib.heimdall.src.heimdall.predicates import *


class TestDataBaseObject(unittest.TestCase):

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
        
        game = gamescraper.scrapeGame(gamename, romCollection, util.getSettings(), 0, RCBMock(), 'Header', 1)
        
        print game.yearFromScraper
        print game.genreFromScraper
        print type(game.genreFromScraper)
        
        
class RCBMock:
    
    itemCount = 0
    
    def writeMsg(self, msg1, msg2, msg3, count=0):
        return True
