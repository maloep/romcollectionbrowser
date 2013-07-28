
import unittest

from resources.lib.rcb.utils import util
from resources.lib.rcb.gameimport import dbupdater
from resources.lib.rcb.datamodel.gamedatabase import GameDataBase
from resources.lib.rcb.datamodel.game import Game
from resources.lib.rcb.configuration import config
from resources.lib.rcb.configuration.config import *


class TestDbUpdater(unittest.TestCase):

    def setUp(self):
        util.RCBHOME = os.path.join(os.getcwd(), '..', '..', '..', '..', '..')
        util.ISTESTRUN = True
        
        Logutil.currentLogLevel = util.LOG_LEVEL_INFO
        self._databasedir = os.path.join( os.getcwd(), 'TestDataBase')
        self._gdb = None
    
    def tearDown(self):
        pass
    
    
    def test_updateDb(self):
        
        self._gdb = GameDataBase(self._databasedir, 'MyGames-3.0.db')
        self._gdb.connect()
        self._gdb.dropTables()        
        self._gdb.createTables()
        
        myConfig = Config('config.xml')
        statusOk, errorMsg = myConfig.readXml()

        romCollection = myConfig.romCollections['1']
        
        gamenameFromFile = 'Super Mario Kart'
        gameId = None
        romFiles = []
        foldername = ''
        isUpdate = False
        gui = None
        isLocalArtwork = False
        settings = None
        artworkfiles = []
        artworkurls = {}
        
        game = Game(self._gdb)
        game.name = 'Super Mario Kart'
        
        
        #dbupdater.insertGameFromDesc(self._gdb, game, gamenameFromFile, gameId, romCollection, romFiles, foldername, isUpdate, gui, isLocalArtwork, settings, artworkfiles, artworkurls)
