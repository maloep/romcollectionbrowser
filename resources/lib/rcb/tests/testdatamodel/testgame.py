import os
import unittest
import inspect
import time

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

from resources.lib.rcb.datamodel.gamedatabase import GameDataBase
from resources.lib.rcb.datamodel.databaseobject import DataBaseObject
from resources.lib.rcb.datamodel.game import Game

class TestGame(unittest.TestCase):

    def setUp(self):
        
        util.RCBHOME = os.path.join(os.getcwd(), '..', '..', '..', '..', '..')
        util.ISTESTRUN = True

        Logutil.currentLogLevel = util.LOG_LEVEL_INFO
        self._databasedir = os.path.join( os.getcwd(), 'TestDataBase')
        self._gdb = None
        
    
    def tearDown(self):
        if(self._gdb):
            self._gdb.close()
            time.sleep(0.5)
            
        
    
    def test_getAllPerformance(self):
        
        self._gdb = GameDataBase(self._databasedir, 'MyGames-TestPerformance.db')
        self._gdb.connect()
        
        results = Game(self._gdb).getAllnew()
        
        print len(results)
        print results[12].maxPlayers
        
    
    
    def test_insert(self):
        
        self._gdb = GameDataBase(self._databasedir, 'MyGames.db')
        self._gdb.connect()
        self._gdb.dropTables()        
        self._gdb.createTables()
        
        game = Game(self._gdb)
    
        game.name = 'testgame'
        game.description = 'test description'
        game.insertnew(game)
        self._gdb.commit()
            
    
    def test_updateAllColumns(self):
        
        self._gdb = GameDataBase(self._databasedir, 'MyGames.db')
        self._gdb.connect()
        self._gdb.dropTables()        
        self._gdb.createTables()
        
        game = Game(self._gdb)
        game.name = 'testgame'
        game.description = 'test description'
        
        game.insertnew(game)
        self._gdb.commit()
        
        game.id = self._gdb.cursor.lastrowid
        game.name = 'testgame 2'
        game.updateAllColumns(game, False)
        self._gdb.commit()
        
        
    def test_updateSingleColumns(self):
        
        self._gdb = GameDataBase(self._databasedir, 'MyGames.db')
        self._gdb.connect()
        self._gdb.dropTables()        
        self._gdb.createTables()
        
        game = Game(self._gdb)
        game.name = 'testgame'
        game.description = 'test description'
        
        game.insertnew(game)
        self._gdb.commit()
        
        game.id = self._gdb.cursor.lastrowid
        game.name = 'testgame 3'
        game.updateSingleColumns(('name',), game, False)
        self._gdb.commit()
    
    
    def test_toDict(self):
        
        game = Game(self._gdb)
        
        game.name = 'test game'
        game.description = 'test description'
        
        dict = game.toDict()
                        
        expected = ['controllerType', 'rating', 'launchCount', 'developerId', 'alternateGameCmd', 'perspective', 'id', 'numVotes', 'isFavorite', 'gameCmd', 'version', 'reviewerId', 'description', 'translatedBy', 'alternateTitle', 'originalTitle', 'maxPlayers', 'name', 'url', 'region', 'yearId', 'media', 'romCollectionId', 'publisherId']
        self.assertEqual(dict.keys(), expected, 'expected: %s, result: %s' %(expected, dict.keys()))
        expected = ['', '', 0, None, '', '', None, 0, 0, '', '', None, 'test description', '', '', '', 0, 'test game', '', '', None, '', None, None]
        self.assertEqual(dict.values(), expected, 'expected: %s, result: %s' %(expected, dict.values()))
    
    