import unittest
import os
import sys
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

from gamedatabase import GameDataBase, Genre, Year, Publisher, Developer


class TestDBReferencedTables(unittest.TestCase):
    ''' Test the objects linked to the Game DB row by ID
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

    ''' Genres '''

    def test_RetrieveSingleGenreByGameId(self):
        ''' Validate basic retrieve works '''
        genre = Genre(self.gdb).getGenresForGame(28)

        self.assertTrue(genre == 'Role-Playing', 'Genre for game id 28 expected to be Role-Playing')

    def test_RetrieveMultipleGenresByGameId(self):
        ''' Test that games with multiple genres are comma-separated strings FIXME TODO Order of genres '''
        genres = Genre(self.gdb).getGenresForGame(50)

        self.assertTrue(genres == 'Adventure, Action, Role-Playing', 'Expected multiple genres for game to be comma-separated string, was {0}'.format(genres))

    def test_RetrieveGenreWithSlash(self):
        ''' Validate items with genre e.g. Action/Adventure are handled '''
        genres = Genre(self.gdb).getGenresForGame(179)

        self.assertTrue(genres == 'Racing / Driving, Role-Playing (RPG)', 'Game with slash in genre not handled correctly (was {0})'.format(genres))

    def test_FilterGenres_RomCollection(self):
        rows = Genre(self.gdb).getFilteredGenres(1, 0, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 7)

    def test_FilterGenres_Year(self):
        rows = Genre(self.gdb).getFilteredGenres(0, 2, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 2)

    def test_FilterGenres_Publisher(self):
        rows = Genre(self.gdb).getFilteredGenres(0, 0, 3, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 1)

    def test_FilterGenres_Developer(self):
        rows = Genre(self.gdb).getFilteredGenres(0, 0, 0, 1, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 4)

    def test_FilterGenres_MaxPlayers(self):
        rows = Genre(self.gdb).getFilteredGenres(0, 0, 0, 0, '2', 0, 0, '0 = 0')
        self.assertEquals(len(rows), 7)

    def test_FilterGenres_Rating(self):
        rows = Genre(self.gdb).getFilteredGenres(0, 0, 0, 0, 0, 5, 0, '0 = 0')
        self.assertEquals(len(rows), 5)

    def test_FilterGenres_Region(self):
        rows = Genre(self.gdb).getFilteredGenres(0, 0, 0, 0, 0, 0, 'USA', '0 = 0')
        self.assertEquals(len(rows), 7)

    ''' Developer '''
    def test_RetrieveDeveloperByGameId(self):
        ''' Validate basic retrieve works '''
        dev = Developer(self.gdb).getDeveloperForGame(62)

        self.assertTrue(dev == 'Squaresoft', 'Expected developer for game with id 62 to be Squaresoft, was {0}'.format(dev))

    def test_RetrieveDeveloper(self):
        dev = Developer(self.gdb).getDeveloper(2)
        self.assertTrue(dev == 'Activision')

    def test_FilterDevelopers_RomCollection(self):
        rows = Developer(self.gdb).getFilteredDevelopers(1, 0, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 9)

    def test_FilterDevelopers_Genre(self):
        rows = Developer(self.gdb).getFilteredDevelopers(0, 2, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 14)

    def test_FilterDevelopers_Year(self):
        rows = Developer(self.gdb).getFilteredDevelopers(0, 0, 2, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 1)

    def test_FilterDevelopers_Publisher(self):
        rows = Developer(self.gdb).getFilteredDevelopers(0, 0, 0, 3, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 1)

    def test_FilterDevelopers_MaxPlayers(self):
        rows = Developer(self.gdb).getFilteredDevelopers(0, 0, 0, 0, '2', 0, 0, '0 = 0')
        self.assertEquals(len(rows), 12)

    def test_FilterDevelopers_Rating(self):
        rows = Developer(self.gdb).getFilteredDevelopers(0, 0, 0, 0, 0, 5, 0, '0 = 0')
        self.assertEquals(len(rows), 7)

    def test_FilterDevelopers_Region(self):
        rows = Developer(self.gdb).getFilteredDevelopers(0, 0, 0, 0, 0, 0, 'USA', '0 = 0')
        self.assertEquals(len(rows), 7)

    ''' Publisher '''
    def test_RetrievePublisherByGameId(self):
        ''' Validate basic retrieve works '''
        pub = Publisher(self.gdb).getPublisherForGame(6)

        self.assertTrue(pub == 'Stern', 'Expected publisher for game with id 6 to be Stern, was {0}'.format(pub))

    def test_RetrievePublisher(self):
        pub = Publisher(self.gdb).getPublisher(6)
        self.assertTrue(pub == 'Nintendo')

    def test_FilterPublishers_RomCollection(self):
        rows = Publisher(self.gdb).getFilteredPublishers(1, 0, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 9)

    def test_FilterPublishers_Genre(self):
        rows = Publisher(self.gdb).getFilteredPublishers(0, 2, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 9)

    def test_FilterPublishers_Year(self):
        rows = Publisher(self.gdb).getFilteredPublishers(0, 0, 2, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 1)

    def test_FilterPublishers_Developer(self):
        rows = Publisher(self.gdb).getFilteredPublishers(0, 0, 0, 3, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 1)

    def test_FilterPublishers_MaxPlayers(self):
        rows = Publisher(self.gdb).getFilteredPublishers(0, 0, 0, 0, '2', 0, 0, '0 = 0')
        self.assertEquals(len(rows), 10)

    def test_FilterPublishers_Rating(self):
        rows = Publisher(self.gdb).getFilteredPublishers(0, 0, 0, 0, 0, 5, 0, '0 = 0')
        self.assertEquals(len(rows), 7)

    def test_FilterPublishers_Region(self):
        rows = Publisher(self.gdb).getFilteredPublishers(0, 0, 0, 0, 0, 0, 'USA', '0 = 0')
        self.assertEquals(len(rows), 7)

    ''' Year '''
    def test_FilterYears_RomCollection(self):
        rows = Year(self.gdb).getFilteredYears(1, 0, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 6)

    def test_FilterYears_Genre(self):
        rows = Year(self.gdb).getFilteredYears(0, 2, 0, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 10)

    def test_FilterYears_Publisher(self):
        rows = Year(self.gdb).getFilteredYears(0, 0, 2, 0, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 4)

    def test_FilterYears_Developer(self):
        rows = Year(self.gdb).getFilteredYears(0, 0, 0, 3, 0, 0, 0, '0 = 0')
        self.assertEquals(len(rows), 1)

    def test_FilterYears_MaxPlayers(self):
        rows = Year(self.gdb).getFilteredYears(0, 0, 0, 0, '2', 0, 0, '0 = 0')
        self.assertEquals(len(rows), 13)

    def test_FilterYears_Rating(self):
        rows = Year(self.gdb).getFilteredYears(0, 0, 0, 0, 0, 5, 0, '0 = 0')
        self.assertEquals(len(rows), 6)

    def test_FilterYears_Region(self):
        rows = Year(self.gdb).getFilteredYears(0, 0, 0, 0, 0, 0, 'USA', '0 = 0')
        self.assertEquals(len(rows), 4)

if __name__ == "__main__":
    unittest.main()
