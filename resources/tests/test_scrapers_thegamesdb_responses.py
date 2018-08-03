import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
import json
import responses
from thegamesdb_scraper import TheGamesDB_Scraper


class Test_GamesDBScraper(unittest.TestCase):

    """
    Test parsing the output of queries to thegamesdb.
    """
    # Parse game search query
    @responses.activate
    def test_search_ByGameName(self):
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/Games/ByGameName?name=Tekken&filter[platform]=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&fields=overview,players,publishers,genres,rating&include=boxart',
                      json=self._loadJsonFromFile('thegamesdb_search_tekken_playstation.json'),
                      status=200)

        scraper = TheGamesDB_Scraper()

        results = scraper.search('Tekken', 'PlayStation')

        # Expect 5 results
        self.assertEqual(len(results), 5, "Number of search results for multiple search match did not match expected number")
        self.assertEqual(len(scraper.resultdata), 5, "Number of search results for multiple search match did not match expected number")

    @responses.activate
    def test_Retrieve(self):
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/Games/ByGameName?name=Tekken&filter[platform]=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&fields=overview,players,publishers,genres,rating&include=boxart',
                      json=self._loadJsonFromFile('thegamesdb_search_tekken_playstation.json'),
                      status=200)

        responses.add(responses.GET,'https://api.thegamesdb.net/Genres',
                      json=self._loadJsonFromFile('genres.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/Developers',
                      json=self._loadJsonFromFile('developers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/Publishers',
                      json=self._loadJsonFromFile('publishers.json'), status=200)

        scraper = TheGamesDB_Scraper()

        #do a search to store the found results
        scraper.search('Tekken', 'PlayStation')

        result = scraper.retrieve('2613', 'PlayStation')
        print result

    # Parse game retrieve
    def test_Retrieve_Old(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'thegamesdb_legacy', 'thegamesdb_getgame.xml')
        scraper = TheGamesDB_Scraper_Legacy()
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
        
        
    # Parse game retrieve
    def test_RetrieveMissingProperties(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'thegamesdb_legacy', 'thegamesdb_getgame_missingproperties.xml')
        scraper = TheGamesDB_Scraper_Legacy()
        with open(f) as xmlfile:
            data = xmlfile.read()
        result = scraper._parseGameResult(data)
        self.assertIsInstance(result, dict, "Return value of parseGameResult should be a dict")
        self.assertEqual(result['Game'], ["Arkanoid"], "Expected game name value to be set")
        self.assertEqual(result['Developer'], ["Taito"], "Expected developer value to be set")
        self.assertEqual(result['Publisher'], ["Discovery"], "Expected publisher value to be set")
        self.assertTrue(result['Description'][0].startswith("The original Breakout concept involves controlling a bat at the bottom of the screen"), "Expected description value to be set")

    # Parse image capture in the retrieve result
    def test_RetrieveImages(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb_legacy', 'thegamesdb_getgame.xml')
        scraper = TheGamesDB_Scraper_Legacy()
        with open(f) as xmlfile:
            data = xmlfile.read()
        result = scraper._parseGameResult(data)

        self.assertEqual(result['Filetypefanart'], ['http://legacy.thegamesdb.net/banners/fanart/original/2613-1.jpg'])
        self.assertEqual(result['Filetypeboxfront'], ['http://legacy.thegamesdb.net/banners/boxart/original/front/2613-1.png'])
        self.assertEqual(result['Filetypeboxback'], ['http://legacy.thegamesdb.net/banners/boxart/original/back/2613-1.jpg'])
        self.assertEqual(result['Filetypescreenshot'], ['http://legacy.thegamesdb.net/banners/screenshots/2613-1.jpg'])

    def test_RetrieveImagesWhenNotPresent(self):
        """Make sure that when image types are not present (fanart in this example) that we don't have issues"""
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb_legacy', 'thegamesdb_getgame_missingartwork.xml')
        scraper = TheGamesDB_Scraper_Legacy()
        with open(f) as xmlfile:
            data = xmlfile.read()
        result = scraper._parseGameResult(data)

        self.assertEqual(result['Filetypeboxfront'], ['http://legacy.thegamesdb.net/banners/boxart/original/front/291-1.jpg'])
        self.assertEqual(result['Filetypeboxback'], ['http://legacy.thegamesdb.net/banners/boxart/original/back/291-1.jpg'])
        self.assertEqual(result['Filetypescreenshot'], ['http://legacy.thegamesdb.net/banners/screenshots/291-1.jpg'])

    def test_RetrieveGameWithMultipleGenres(self):
        """Make sure that games with multiple genres are handled correctly"""
        # Ref http://thegamesdb.net/api/GetGame.php?id=7808"  # Syphon Filter, Publisher 989
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb_legacy', 'thegamesdb_getgame_2genres.xml')
        scraper = TheGamesDB_Scraper_Legacy()
        with open(f) as xmlfile:
            data = xmlfile.read()
        result = scraper._parseGameResult(data)
        self.assertEqual(len(result['Genre']), 2)
        self.assertIn("Action", result['Genre'], "Expected genre Action to be retrieved")
        self.assertIn("Stealth", result['Genre'], "Expected genre Stealth to be retrieved")

    def test_RetrieveGameWithNumericPublisher(self):
        """Make sure that games with numeric fields that are expected to be strings (e.g. Publisher) are
        handled correctly"""
        # Ref http://thegamesdb.net/api/GetGame.php?id=7808"  # Syphon Filter, Publisher 989
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb_legacy', 'thegamesdb_getgame_2genres.xml')
        scraper = TheGamesDB_Scraper_Legacy()
        with open(f) as xmlfile:
            data = xmlfile.read()
        result = scraper._parseGameResult(data)
        self.assertEqual(u"989", result['Publisher'][0], "Expected publisher with numeric name to be a string")

    @unittest.skip("FIXME TODO Not yet implemented")
    def test_SearchForGameWithApostropheAndPlatform(self):
        url = "http://thegamesdb.net/api/GetGame.php?name=NBA%20Live%20%2798&platform=Super%20Nintendo%20%28SNES%29"

        #self.assertEqual(results[0].get('Game')[0], "NBA Live 98")
        #self.assertEqual(results[0].get('Platform')[0], "Super Nintendo (SNES)")
        #self.assertEqual(results[0].get('Publisher')[0], "THQ")
        #self.assertEqual(results[0].get('Developer')[0], "EA Sports")

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

    # Parse if no entries found for game search
    def test_GamesListNoResults(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'thegamesdb_legacy', 'thegamesdb_getgameslist_noresults.xml')
        scraper = TheGamesDB_Scraper_Legacy()
        with open(f) as xmlfile:
            data = xmlfile.read()
        results = scraper._parseSearchResults(data)
        self.assertIsInstance(results, list, "Expected search results to return list even if no results found")
        self.assertEqual(len(results), 0, "Empty search results should return empty list")

    def test_search_online(self):
        scraper = TheGamesDB_Scraper()
        result = scraper.search('Tekken', 'PlayStation')

        game = scraper.retrieve('2613', 'PlayStation')

        """
        import os, json
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb', 'publishers.json')
        with open(f, 'w') as outfile:
            json.dump(publishers, outfile)
        """




    def _loadJsonFromFile(self, filename):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb', filename)

        with open(f) as jsonfile:
            data = jsonfile.read()

        return json.loads(data)


if __name__ == "__main__":
    unittest.main()
