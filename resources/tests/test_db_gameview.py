import unittest
import os, sys, shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

from gamedatabase import GameDataBase, GameView



class TestDbGameView(unittest.TestCase):
    
    gdb = None

    @classmethod
    def get_testdata_path(cls):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata')

    @classmethod
    def setUpClass(cls):
        # Open the DB
        db_path = os.path.join(cls.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        shutil.copyfile(os.path.join(db_path, 'MyGames_current_117_games.db'), os.path.join(db_path, 'MyGames.db'))

        cls.gdb = GameDataBase(db_path)
        cls.gdb.connect()

    @classmethod
    def tearDownClass(cls):
        # Cleanup
        cls.gdb.close()
        os.remove(os.path.join(os.path.join(cls.get_testdata_path(), 'database'), 'MyGames.db'))
        
    
    def test_RetrieveGameById(self):
        ''' Validate basic retrieve works '''
        game = GameView(self.gdb).getGameById(1)

        self.assertTrue(game[GameView.COL_NAME] == 'Adventure', 'Game with ID 1 expected to be Adventure but was %s' %game[GameView.COL_NAME])
        self.assertTrue(game[GameView.COL_publisher] == 'Atari', 'Publisher of game with ID 1 expected to be Atari but was %s' %game[GameView.COL_publisher])
        self.assertTrue(game[GameView.COL_developer] == 'Atari', 'Developer of game with ID 1 expected to be Atari but was %s' %game[GameView.COL_developer])
        self.assertTrue(game[GameView.COL_year] == '1978', 'Year of game with ID 1 expected to be 1978 but was %s' %game[GameView.COL_year])
        self.assertTrue(game[GameView.COL_genre] == 'Adventure', 'Genre of game with ID 1 expected to be Adventure but was %s' %game[GameView.COL_genre])
        
    def test_RetrieveGameByIdMultipleGenres(self):
        
        game = GameView(self.gdb).getGameById(50)
        
        self.assertTrue(game[GameView.COL_NAME] == 'Legend of Zelda, The - A Link to the Past (USA)', 'Game with ID 50 expected to be Legend of Zelda, The - A Link to the Past (USA) but was %s' %game[GameView.COL_NAME])
        self.assertTrue(game[GameView.COL_publisher] == 'Nintendo', 'Publisher of game with ID 50 expected to be Nintendo EAD but was %s' %game[GameView.COL_publisher])
        self.assertTrue(game[GameView.COL_developer] == 'Nintendo EAD', 'Developer of game with ID 50 expected to be Nintendo but was %s' %game[GameView.COL_developer])
        self.assertTrue(game[GameView.COL_year] == '1992', 'Year of game with ID 50 expected to be 1992 but was %s' %game[GameView.COL_year])
        self.assertTrue(game[GameView.COL_genre] == 'Adventure, Action, Role-Playing', 'Genre of game with ID 50 expected to be Adventure, Action, Role-Playing but was %s' %game[GameView.COL_genre])

    def test_GetGamesByFilter(self):
        db_path = 'C:\\Users\\lom\\AppData\\Roaming\\Kodi\\userdata\\addon_data\\script.games.rom.collection.browser\\'
        gdb = GameDataBase(db_path)
        gdb.connect()
        gdb.checkDBStructure()

        #gdb.cursor.execute("VACUUM")
        #gdb.cursor.execute("PRAGMA optimize")
        gdb.cursor.execute("PRAGMA cache_size = 20000")

        import time
        timestamp1 = time.clock()
        #games = Game(gdb).getGamesByFilter(0, 0, 0, 0, 0, '0 = 0', 0)
        games = GameView(gdb).getFilteredGames(0, 0, 0, 0, 0, '0 = 0', 0)
        #games = Game(gdb).getAll()
        timestamp2 = time.clock()
        diff = (timestamp2 - timestamp1) * 1000
        print "load %d games from db in %d ms" % (len(games), diff)

        timestamp1 = time.clock()
        #Game(gdb).getGameById(5000)
        row = GameView(gdb).getGameById(5000)
        timestamp2 = time.clock()
        diff = (timestamp2 - timestamp1) * 1000
        print "load 1 game from db in %d ms" % diff

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()