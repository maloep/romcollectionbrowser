import os
import unittest
import inspect
import time

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

from resources.lib.rcb.datamodel.gamedatabase import GameDataBase
from resources.lib.rcb.datamodel.databaseobject import DataBaseObject
from resources.lib.rcb.datamodel.file import File
from resources.lib.rcb.datamodel.game import Game

class TestDataBaseObject(unittest.TestCase):

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
                    
    
    
    def test_getAll(self):
        self._gdb = GameDataBase(self._databasedir, 'MyGames-TestPerformance.db')
        self._gdb.connect()
        results = DataBaseObject.getAll(self._gdb, 'Game')
        print len(results)
        
    
    def test_getAllOrdered(self):
        self._gdb = GameDataBase(self._databasedir, 'MyGames-TestPerformance.db')
        self._gdb.connect()
        results = DataBaseObject.getAllOrdered(self._gdb, 'Game')
        print len(results)
  
        
    def test_getOneByName(self):
        self._gdb = GameDataBase(self._databasedir, 'MyGames-TestPerformance.db')
        self._gdb.connect()
        gamename = 'Super Mario Kart'
        result = DataBaseObject.getOneByName(self._gdb, 'Game', gamename)
        self.assertEqual(result[1], gamename, 'expected: %s, result: %s' %(gamename, result[1]))


    def test_getObjectById(self):
        self._gdb = GameDataBase(self._databasedir, 'MyGames-TestPerformance.db')
        self._gdb.connect()
        gameid = 5
        result = DataBaseObject.getOneById(self._gdb, 'Game', gameid)
        self.assertEqual(result[0], gameid, 'expected: %s, result: %s' %(result[0], gameid))
    
    
    def test_ObjectsByQuery(self):
        self._gdb = GameDataBase(self._databasedir, 'MyGames-TestPerformance.db')
        self._gdb.connect()
        query = "Select * From Game Where launchCount > 0 Order by launchCount desc Limit 10"
        results = DataBaseObject.getByQuery(self._gdb, query, [])
        print len(results)
        
    
    def test_ObjectsByQueryNoArgs(self):
        self._gdb = GameDataBase(self._databasedir, 'MyGames-TestPerformance.db')
        self._gdb.connect()
        query = "SELECT * FROM File WHERE filetypeid = 0"
        results = DataBaseObject.getByQueryNoArgs(self._gdb, query)
        print len(results)
        
        
    def test_getObjectByQuery(self):
        self._gdb = GameDataBase(self._databasedir, 'MyGames-TestPerformance.db')
        self._gdb.connect()
        query = "SELECT * FROM Game WHERE name = ? and romCollectionId = ?"
        args = ("Super Mario Kart", 5)
        result = DataBaseObject.getOneByQuery(self._gdb, query, args)
        gamename =args[0]
        self.assertEqual(gamename, result[1], 'expected: %s, result: %s' %(gamename, result[1]))
    
    
    def test_insert(self):
        self._gdb = GameDataBase(self._databasedir, 'MyGames.db')
        self._gdb.connect()
        self._gdb.dropTables()        
        self._gdb.createTables()
        
        game = Game(self._gdb)
    
        game.name = 'testgame'
        game.insert(False)
        self._gdb.commit()
            
    
    def test_updateAllColumns(self):
        
        self._gdb = GameDataBase(self._databasedir, 'MyGames.db')
        self._gdb.connect()
        self._gdb.dropTables()        
        self._gdb.createTables()
        
        game = Game(self._gdb)
        game.name = 'testgame'
        game.description = 'test description'
        
        game.insert()
        self._gdb.commit()
        
        game.id = self._gdb.cursor.lastrowid
        game.name = 'testgame 2'
        game.updateAllColumns(False)
        self._gdb.commit()
        
        
    def test_updateSingleColumns(self):
        
        self._gdb = GameDataBase(self._databasedir, 'MyGames.db')
        self._gdb.connect()
        self._gdb.dropTables()        
        self._gdb.createTables()
        
        game = Game(self._gdb)
        game.name = 'testgame'
        game.description = 'test description'
        
        game.insert()
        self._gdb.commit()
        
        game.id = self._gdb.cursor.lastrowid
        game.name = 'testgame 3'
        game.updateSingleColumns(('name',), False)
        self._gdb.commit()
    
    
    def test_toDbDict(self):
        
        game = Game(self._gdb)
        
        game.name = 'test game'
        game.description = 'test description'
        
        dict = game.toDbDict()
                        
        expected = ['controllerType', 'rating', 'launchCount', 'developerId', 'alternateGameCmd', 'perspective', 'id', 'numVotes', 'isFavorite', 'gameCmd', 'version', 'reviewerId', 'description', 'translatedBy', 'alternateTitle', 'originalTitle', 'maxPlayers', 'name', 'url', 'region', 'yearId', 'media', 'romCollectionId', 'publisherId']
        self.assertEqual(dict.keys(), expected, 'expected: %s, result: %s' %(expected, dict.keys()))
        expected = ['', '', 0, None, '', '', None, 0, 0, '', '', None, 'test description', '', '', '', 0, 'test game', '', '', None, '', None, None]
        self.assertEqual(dict.values(), expected, 'expected: %s, result: %s' %(expected, dict.values()))
    
    