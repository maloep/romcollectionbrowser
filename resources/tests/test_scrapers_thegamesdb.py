import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyparsing'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
from resources.lib.pyscraper.thegamesdb_scraper import TheGamesDB_Scraper


class Test_GamesDBScraper(unittest.TestCase):

    """
    Test parsing the output of queries to thegamesdb.
    """
    # Parse game search query
    def test_GamesListResults(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'thegamesdb_getgameslist.xml')
        scraper = TheGamesDB_Scraper()

        with open(f) as xmlfile:
            data = xmlfile.read()
        results = scraper._parseSearchResults(data)

        # Expect 3 results
        self.assertEqual(len(results), 3, "Number of search results for multiple search match did not match expected number")

    def test_GamesListResultsNonAscii(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb_getgameslist_nonascii.xml')
        scraper = TheGamesDB_Scraper()

        with open(f) as xmlfile:
            data = xmlfile.read()
        results = scraper._parseSearchResults(data)

        # Expect 289 valid results out of 303 entries
        self.assertEqual(len(results), 289, "Number of search results for multiple search match did not match expected number")

    # Parse game search query using BeautifulSoup parser
    @unittest.skip("BeautifulSoup parser not supported in Kodi")
    def test_GamesListResultsBS(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'thegamesdb_getgameslist.xml')
        scraper = TheGamesDB_Scraper()

        with open(f) as xmlfile:
            data = xmlfile.read()
        results = scraper._parseSearchResultsBS(data)

        # Expect 3 results
        self.assertEqual(len(results), 3, "Number of search results for BeautifulSoup parser multiple search match did not match expected number")

    # Parse game retrieve
    def test_Retrieve(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'thegamesdb_getgame.xml')
        scraper = TheGamesDB_Scraper()
        with open(f) as xmlfile:
            data = xmlfile.read()
        result = scraper._parseGameResult(data)
        self.assertIsInstance(result, dict, "Return value of parseGameResult should be a dict")
        self.assertEqual(result['Game'], ["Tekken 2"], "Expected game name value to be set")
        self.assertEqual(result['Publisher'], ["Namco"], "Expected publisher value to be set")
        self.assertTrue(result['Description'][0].startswith("MORE THAN A SEQUEL. THE UNDISPUT"), "Expected description value to be set")

        self.assertEqual(result['ReleaseYear'], ["1996"], "Expected year = 1996 from test XML")
        self.assertEqual(result['Players'], ["2"], "Expected 2 players in test XML")
        self.assertEqual(len(result['Genre']), 1, "Expected 1 genre from test XML")
        self.assertEqual(result['Genre'], ["Fighting"], "Expected Fighting genre in test XML")

        # FIXME TODO Games with multiple Genres

    # Parse image capture in the retrieve result
    def test_RetrieveImages(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb_getgame.xml')
        scraper = TheGamesDB_Scraper()
        with open(f) as xmlfile:
            data = xmlfile.read()
        result = scraper._parseGameResult(data)

        self.assertEqual(result['Filetypefanart'], ['http://thegamesdb.net/banners/fanart/original/2613-1.jpg'])
        self.assertEqual(result['Filetypeboxfront'], ['http://thegamesdb.net/banners/boxart/original/front/2613-1.png'])
        self.assertEqual(result['Filetypeboxback'], ['http://thegamesdb.net/banners/boxart/original/back/2613-1.jpg'])
        self.assertEqual(result['Filetypescreenshot'], ['http://thegamesdb.net/banners/screenshots/2613-1.jpg'])

    def test_RetrieveImagesWhenNotPresent(self):
        """Make sure that when image types are not present (fanart in this example) that we don't have issues"""
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb_getgame_missingartwork.xml')
        scraper = TheGamesDB_Scraper()
        with open(f) as xmlfile:
            data = xmlfile.read()
        result = scraper._parseGameResult(data)

        self.assertEqual(result['Filetypeboxfront'], ['http://thegamesdb.net/banners/boxart/original/front/291-1.jpg'])
        self.assertEqual(result['Filetypeboxback'], ['http://thegamesdb.net/banners/boxart/original/back/291-1.jpg'])
        self.assertEqual(result['Filetypescreenshot'], ['http://thegamesdb.net/banners/screenshots/291-1.jpg'])

    @unittest.skip("FIXME TODO Not yet implemented")
    def test_InvalidResponse(self):
        # FIXME TODO Implement error handling response xml might be:
        # <Error>The specified platform was not valid.</Error>
        pass

    @unittest.skip("FIXME TODO Not yet implemented")
    def test_ErrorResponse(self):
        # FIXME TODO Implement error handling response xml might be:
        # file:scraper_web_response/thegamesdb_error.xml
        pass

    # Parse game retrieve using BeautifulSoup parser
    @unittest.skip("BeautifulSoup parser not supported in Kodi")
    def test_RetrieveBS(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'thegamesdb_getgame.xml')
        scraper = TheGamesDB_Scraper()
        with open(f) as xmlfile:
            data = xmlfile.read()
        result = scraper._parseGameResultBS(data)
        self.assertIsInstance(result, dict, "Return value of parseGameResult should be a dict")
        self.assertEqual(result['publisher'], "Namco", "Expected publisher value to be set")
        self.assertTrue(result['description'].startswith("MORE THAN A SEQUEL. THE UNDISPUT"), "Expected description value to be set")
        self.assertEqual(len(result['genres']), 1, "Expected 1 genre from test XML")
        self.assertEqual(result['year'], '1996', "Expected year = 1996 from test XML")

    # Parse if no entries found for game search
    def test_GamesListNoResults(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'thegamesdb_getgameslist_noresults.xml')
        scraper = TheGamesDB_Scraper()
        with open(f) as xmlfile:
            data = xmlfile.read()
        results = scraper._parseSearchResults(data)
        self.assertIsInstance(results, list, "Expected search results to return list even if no results found")
        self.assertEqual(len(results), 0, "Empty search results should return empty list")

    @unittest.skip("Skip downloading from site")
    def test_GamesResultWithUnicode(self):
        scraper = TheGamesDB_Scraper()
        gamedata = scraper.retrieve('137')

        self.assertTrue(u"Mushroom Kingdom while avoiding all of Kamek\u2019s clever traps" in gamedata['Description'][0],
                        "Expected non-ASCII strings to be converted to Unicode")

    @unittest.skip("Skip downloading from site")
    def test_CreateScraperFromName(self):
        sname = 'TheGamesDB_Scraper'

        mod = __import__('thegamesdb_scraper')
        class_ = getattr(mod, sname)
        instance = class_()
        print(type(instance))
        print instance.search('Wipeout')    # FIXME TODO Wip3out doesn't work


if __name__ == "__main__":
    unittest.main()
