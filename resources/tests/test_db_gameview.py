import unittest
import os, sys, shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

from gamedatabase import GameDataBase, Game, gameobj



class TestDbGameView(unittest.TestCase):
    
    gdb = None

    @classmethod
    def get_testdata_path(cls):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata')

    @classmethod
    def setUpClass(cls):
        # Open the DB
        db_path = os.path.join(cls.get_testdata_path(), 'dbupgrade')

        # Setup data - MyGames.db is the hard-coded expected DB name
        shutil.copyfile(os.path.join(db_path, 'test-2.1.6.db'), os.path.join(db_path, 'MyGames.db'))

        cls.gdb = GameDataBase(db_path)
        cls.gdb.connect()

    @classmethod
    def tearDownClass(cls):
        # Cleanup
        cls.gdb.close()
        os.remove(os.path.join(os.path.join(cls.get_testdata_path(), 'dbupgrade'), 'MyGames.db'))
        
    
    def test_RetrieveGameById(self):
        ''' Validate basic retrieve works '''
        game = Game(self.gdb).getGameById(1)

        self.assertTrue(game.name == 'Adventure', 'Game with ID 1 expected to be Adventure but was %s' %game.name)
        self.assertTrue(game.publisher == 'Atari', 'Publisher of game with ID 1 expected to be Atari but was %s' %game.publisher)
        self.assertTrue(game.developer == 'Atari', 'Developer of game with ID 1 expected to be Atari but was %s' %game.developer)
        self.assertTrue(game.year == '1978', 'Year of game with ID 1 expected to be 1978 but was %s' %game.year)
        self.assertTrue(game.genre == 'Adventure', 'Genre of game with ID 1 expected to be Adventure but was %s' %game.genre)
        self.assertTrue(game.firstRom == '/path/to/roms/Atari2600/Adventure (1980) (Atari).a26', 'First rom of game with ID 1 expected to be /path/to/roms/Atari2600/Adventure (1980) (Atari).a26 but was %s' %game.firstRom)
        
        
    def test_RetrieveGameByIdMultipleGenres(self):
        
        game = Game(self.gdb).getGameById(50)
        
        self.assertTrue(game.name == 'Legend of Zelda, The - A Link to the Past (USA)', 'Game with ID 50 expected to be Legend of Zelda, The - A Link to the Past (USA) but was %s' %game.name)
        self.assertTrue(game.publisher == 'Nintendo', 'Publisher of game with ID 50 expected to be Nintendo EAD but was %s' %game.publisher)
        self.assertTrue(game.developer == 'Nintendo EAD', 'Developer of game with ID 50 expected to be Nintendo but was %s' %game.developer)
        self.assertTrue(game.year == '1992', 'Year of game with ID 50 expected to be 1992 but was %s' %game.year)
        self.assertTrue(game.genre == 'Adventure, Action, Role-Playing', 'Genre of game with ID 50 expected to be Adventure, Action, Role-Playing but was %s' %game.genre)
        self.assertTrue(game.firstRom == '/path/to/roms/SNES/ROMs/Legend of Zelda, The - A Link to the Past (USA).zip', 'First rom of game with ID 50 expected to be /path/to/roms/SNES/ROMs/Legend of Zelda, The - A Link to the Past (USA).zip but was %s' %game.firstRom)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()