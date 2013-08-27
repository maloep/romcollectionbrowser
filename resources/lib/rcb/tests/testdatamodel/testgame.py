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
from resources.lib.rcb.datamodel.release import Release
from resources.lib.rcb.datamodel.platform import Platform
from resources.lib.rcb.datamodel.company import Company
from resources.lib.rcb.datamodel.person import Person
from resources.lib.rcb.datamodel.genre import Genre

class TestGame(unittest.TestCase):

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
            
            
    def test_insert(self):
        self.gdb = GameDataBase(self._databasedir, 'MyGames.db')
        self.gdb.connect()
        self.gdb.dropTables()        
        self.gdb.createTables()
        
        game = Game()        
        game.name = 'testgame'
        
        release = Release()
        release.name = 'testgame release'
        release.description = 'test description'
        release.year = '1992'
        
        platform = Platform()
        platform.name = 'SNES'
        release.platform = platform
        
        publisher = Company()
        publisher.name = 'test publisher'
        release.publisher = publisher
        
        developer = Company()
        developer.name = 'test developer'
        release.developer = developer
        
        person = Person()
        person.name = 'test person 1'
        person.role = 'role 1'
        release.persons.append(person)
        
        person = Person()
        person.name = 'test person 2'
        person.role = 'role 2'
        release.persons.append(person)
        
        game.releases.append(release)
        
        genre = Genre()
        genre.name = 'test genre 1'
        game.genres.append(genre)
        
        genre = Genre()
        genre.name = 'test genre 2'
        game.genres.append(genre)
        
        game.insert(self.gdb, False)
        self.gdb.commit()
        
        
        