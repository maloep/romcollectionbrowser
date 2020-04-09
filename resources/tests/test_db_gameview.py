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
        self.assertTrue(game[GameView.COL_genre] == 'Action, Adventure, Role-Playing', 'Genre of game with ID 50 expected to be Action, Adventure, Role-Playing but was %s' %game[GameView.COL_genre])

    def test_RetrieveNonExistantGameById(self):
        ''' Validate retrieve of unavailable ID returns an empty gameobj '''
        game = GameView(self.gdb).getGameById(9999999)
        #self.assertIsInstance(game, gameobj, u'Expected type of return object to be {0}, was {1}'.format(gameobj, type(game)))

        self.assertIsNone(game)

    def test_RetrieveGameWithUnicode(self):
        ''' Validate items with unicode descriptions are stored/retrieved correctly '''
        game = GameView(self.gdb).getGameById(66)

        self.assertTrue(game[GameView.COL_description].startswith(u'Mario\u2019s off'), 'Game with unicode plot not handled correctly')

    def test_RetrieveMultipleGamesByYear(self):
        ''' Validate retrieve by year works '''
        newgames = GameView(self.gdb).getFilteredGames(0, 0, 9, 0, 0, 0, 0, 0, 0, '0 = 0', '', 0)

        #self.assertIsInstance(newgames[0], gameobj, u'Expected type of return objects to be {0}, was {1}'.format(gameobj, type(newgames[0])))
        self.assertTrue(len(newgames) == 5, u'Expected 5 games found for year = 9 (1992), found {0}'.format(len(newgames)))

    def test_FilterGames_RomCollection(self):
        genres = GameView(self.gdb).getFilteredGames(1, 0, 0, 0, 0, 0, 0, 0, 0, '0 = 0', '')
        self.assertEquals(len(genres), 51)

    def test_FilterGames_Genre(self):
        genres = GameView(self.gdb).getFilteredGames(0, 2, 0, 0, 0, 0, 0, 0, 0, '0 = 0', '')
        self.assertEquals(len(genres), 21)

    def test_FilterGames_Year(self):
        genres = GameView(self.gdb).getFilteredGames(0, 0, 2, 0, 0, 0, 0, 0, 0, '0 = 0', '')
        self.assertEquals(len(genres), 2)

    def test_FilterGames_Publisher(self):
        genres = GameView(self.gdb).getFilteredGames(0, 0, 0, 3, 0, 0, 0, 0, 0, '0 = 0', '')
        self.assertEquals(len(genres), 1)

    def test_FilterGames_Developer(self):
        genres = GameView(self.gdb).getFilteredGames(0, 0, 0, 0, 1, 0, 0, 0, 0, '0 = 0', '')
        self.assertEquals(len(genres), 9)

    def test_FilterGames_MaxPlayers(self):
        genres = GameView(self.gdb).getFilteredGames(0, 0, 0, 0, 0, '2', 0, 0, 0, '0 = 0', '')
        self.assertEquals(len(genres), 24)

    def test_FilterGames_Rating(self):
        genres = GameView(self.gdb).getFilteredGames(0, 0, 0, 0, 0, 0, 5, 0, 0, '0 = 0', '')
        self.assertEquals(len(genres), 12)

    def test_FilterGames_Region(self):
        genres = GameView(self.gdb).getFilteredGames(0, 0, 0, 0, 0, 0, 0, 'USA', 0, '0 = 0', '')
        self.assertEquals(len(genres), 11)

    def test_FilterGames_IsFavorite(self):
        genres = GameView(self.gdb).getFilteredGames(0, 0, 0, 0, 0, 0, 0, 0, 1, '0 = 0', '')
        self.assertEquals(len(genres), 7)

    def test_FilterGames_Character(self):
        genres = GameView(self.gdb).getFilteredGames(0, 0, 0, 0, 0, 0, 0, 0, 0, "name LIKE 'A%'", '')
        self.assertEquals(len(genres), 7)

    def test_GetMaxPlayers_NoFilter(self):
        maxplayers = GameView(self.gdb).getFilteredMaxPlayers(0, 0, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(maxplayers), 4)

    def test_GetMaxPlayers_RomCollection(self):
        maxplayers = GameView(self.gdb).getFilteredMaxPlayers(1, 0, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(maxplayers), 3)

    def test_GetMaxPlayers_Genre(self):
        maxplayers = GameView(self.gdb).getFilteredMaxPlayers(0, 1, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(maxplayers), 2)

    def test_GetRegions_NoFilter(self):
        regions = GameView(self.gdb).getFilteredRegions(0, 0, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(regions), 3)

    def test_GetRegions_RomCollection(self):
        regions = GameView(self.gdb).getFilteredRegions(1, 0, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(regions), 3)

    def test_GetRegions_Genre(self):
        regions = GameView(self.gdb).getFilteredRegions(0, 3, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(regions), 1)

    @unittest.skip('only used for performance tests')
    def test_GetGamesByFilter(self):
        db_path = 'C:\\Users\\lom\\AppData\\Roaming\\Kodi\\userdata\\addon_data\\script.games.rom.collection.browser\\'
        gdb = GameDataBase(db_path)
        gdb.connect()
        gdb.checkDBStructure()
        gdb.cursor.execute("PRAGMA cache_size = 20000")

        import time
        timestamp1 = time.clock()
        games = GameView(gdb).getFilteredGames(0, 0, 0, 0, 0, 0, 0, 0, 0, '0 = 0', '', 0)
        #games = Game(gdb).getAll()
        timestamp2 = time.clock()
        diff = (timestamp2 - timestamp1) * 1000
        print ("load %d games from db in %d ms" % (len(games), diff))

        timestamp1 = time.clock()
        #Game(gdb).getGameById(5000)
        row = GameView(gdb).getGameById(5000)
        timestamp2 = time.clock()
        diff = (timestamp2 - timestamp1) * 1000
        print ("load 1 game from db in %d ms" % diff)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()