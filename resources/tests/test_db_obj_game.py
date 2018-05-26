import unittest
import os
import sys
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

from gamedatabase import GameDataBase, GameView


class TestDBObjGame(unittest.TestCase):
    ''' Test the retrieval of the Game and the mapping to the gameobj
    '''
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

        self.assertTrue(game[GameView.COL_NAME] == 'Adventure', 'Game with ID 1 expected to be Adventure')

    @unittest.skip("getGameById returns None")
    def test_RetrieveNonExistantGameById(self):
        ''' Validate retrieve of unavailable ID returns an empty gameobj '''
        game = GameView(self.gdb).getGameById(9999999)
        #self.assertIsInstance(game, gameobj, u'Expected type of return object to be {0}, was {1}'.format(gameobj, type(game)))

        self.assertTrue(game[GameView.COL_NAME] == '', 'Not found game with ID 9999999 expected to have empty details')

    def test_RetrieveGameWithUnicode(self):
        ''' Validate items with unicode descriptions are stored/retrieved correctly '''
        game = GameView(self.gdb).getGameById(66)

        self.assertTrue(game[GameView.COL_description].startswith(u'Mario\u2019s off'), 'Game with unicode plot not handled correctly')

    def test_RetrieveMultipleGamesByYear(self):
        ''' Validate retrieve by year works '''
        newgames = GameView(self.gdb).getFilteredGames(0, 0, 9, 0, 0, 0, 0, 0, 0, '0 = 0', '', 0)

        #self.assertIsInstance(newgames[0], gameobj, u'Expected type of return objects to be {0}, was {1}'.format(gameobj, type(newgames[0])))
        self.assertTrue(len(newgames) == 5, u'Expected 5 games found for year = 9 (1992), found {0}'.format(len(newgames)))

    def function_to_raise_assertion(self, game):
        print game.propertydoesnotexist

    def test_UnknownPropertyThrowsException(self):
        ''' Validate that trying to reference an unknown runtime property throws an exception '''
        game = GameView(self.gdb).getGameById(1)
        self.assertRaises(AttributeError, self.function_to_raise_assertion, game)

if __name__ == "__main__":
    unittest.main()
