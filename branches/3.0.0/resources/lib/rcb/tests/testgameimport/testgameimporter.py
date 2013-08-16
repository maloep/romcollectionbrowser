import unittest

from resources.lib.rcb.datamodel.gamedatabase import GameDataBase
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

        Logutil.currentLogLevel = util.LOG_LEVEL_INFO
        self._databasedir = os.path.join( os.getcwd(), 'TestDataBase')
        self.gdb = None
        
    
    def tearDown(self):
        if(self.gdb):
            self.gdb.close()
            time.sleep(1.0)
            
            
    def test_importgame(self):
        
        self.gdb = GameDataBase(self._databasedir, 'MyGames.db')
        self.gdb.connect()
        self.gdb.dropTables()        
        self.gdb.createTables()
        
        myConfig = Config('config.xml')
        statusOk, errorMsg = myConfig.readXml()
        romCollection = myConfig.romCollections['1']
        
        gamename = "Super Mario Kart"
        game, artworkfiles, artworkurls = gamescraper.scrapeGame(gamename, '', myConfig, romCollection, util.getSettings(), '', 0, RCBMock(), 'Header', 1)
        
        game.insert(self.gdb, False)
        self.gdb.commit()


class RCBMock:
    
    itemCount = 0
    
    def writeMsg(self, msg1, msg2, msg3, count=0):
        return True
