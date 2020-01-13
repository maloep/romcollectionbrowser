# -*- coding: utf-8 -*-
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
from giantbomb_scraper import GiantBomb_Scraper
from rcbexceptions import ScraperExceededAPIQuoteException


class Test_GiantBombScraper(unittest.TestCase):

    """
    Test parsing the output of queries to giantbomb.com.
    """
    # Parse game search query
    @unittest.skip("Search has been changed")
    def test_GamesListResults(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'giantbomb', 'giantbomb_getgameslist.json')
        scraper = GiantBomb_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()
        results = scraper._parse_search_results(json.loads(data))

        # Expect 10 results per page (regardless of total)
        self.assertEqual(len(results), 10, "Number of search results for multiple search match did not match expected number")
        self.assertEqual(results[0]['title'], "Super Mario World 2: Yoshi's Island", "Incorrect description for first result")
        self.assertEqual(results[0]['id'], 2866, "Incorrect game ID for first result")
        self.assertEqual(results[0]['releaseDate'], "1995", "Incorrect releaseDate for first result")

    # Parse if no results found for the query
    def test_GamesListNoResults(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'giantbomb', 'giantbomb_getgameslist_noresults.json')
        scraper = GiantBomb_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()
        results = scraper._parse_search_results(json.loads(data))

        # Expect 0 results and an empty list
        self.assertIsInstance(results, list, "Expected search results to return list even if no results found")
        self.assertEqual(len(results), 0, "Empty search results should return empty list")

    @unittest.skip("Not yet implemented")
    def test_GamesListInvalidResponse(self):
        # FIXME TODO
        pass

    def test_GameResult(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'giantbomb', 'giantbomb_getgame.json')
        scraper = GiantBomb_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()
        results = scraper._parse_game_result(json.loads(data)['results'])
        print ("Game result is {0}".format(results))

        # FIXME TODO Do we have a double-list, or just a single one?
        self.assertEquals(results['Developer'], ['Psygnosis Limited', 'The Designers Republic'])
        self.assertEquals(results['Publisher'], ['Sony Interactive Entertainment Europe'])
        self.assertEquals(results['ReleaseYear'], ['1999'])

        # Genres
        self.assertEquals(results['Genre'], ['Driving/Racing'])

    def test_RetrieveGameWithMultipleGenres(self):
        """Make sure that games with multiple genres are handled correctly"""
        # Ref https://www.giantbomb.com/api/game/3030-17123/?api_key=API_KEY&format=json&resources=game
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'giantbomb', 'giantbomb_getgame_2genres.json')
        scraper = GiantBomb_Scraper()
        with open(f) as jsonfile:
            data = jsonfile.read()
        result = scraper._parse_game_result(json.loads(data)['results'])
        self.assertEqual(len(result['Genre']), 2)
        self.assertIn("Action", result['Genre'], "Expected genre Action to be retrieved")
        self.assertIn("Platformer", result['Genre'], "Expected genre Platformer to be retrieved")

        self.assertEqual(len(result['Publisher']), 2)
        self.assertIn("Ubisoft S.A.", result['Publisher'], "Expected publisher Ubisoft S.A. to be retrieved")
        self.assertIn("Enix Corporation", result['Publisher'], "Expected publisher Enix Corporation to be retrieved")
        
        
    def test_parse_search_results(self):
        
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'giantbomb', 'giantbomb_getreleaselist.json')
        scraper = GiantBomb_Scraper()
        with open(f) as jsonfile:
            data = jsonfile.read()
        results = scraper._parse_search_results(json.loads(data))
        
        # Expect 10 results per page (regardless of total)
        self.assertEqual(len(results), 2, "Number of search results for multiple search match did not match expected number")
        self.assertEqual(results[0]['title'], "Wip3out", "Incorrect description for first result")
        self.assertEqual(results[0]['id'], '3050-80827', "Incorrect game ID for first result")
        self.assertEqual(results[0]['releaseDate'], "1999", "Incorrect releaseDate for first result")
        self.assertEqual(results[0]['SearchKey'][0], "Wip3out", "Incorrect SearchKey for first result")
        
        
    def test_parse_release_result(self):
        
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'giantbomb', 'giantbomb_getrelease.json')
        scraper = GiantBomb_Scraper()
        with open(f) as jsonfile:
            data = jsonfile.read()
        result = scraper._parse_release_result(json.loads(data)['results'])

        self.assertEqual(result['id'], 12298, "Incorrect game ID")
        self.assertEqual(result['Filetypeboxfront'][0], "https://www.giantbomb.com/api/image/scale_large/691211-wipeout3.png", "Incorrect image")
        

    @unittest.skip("Not yet working")
    def test_ErrorResponseInvalidApiKey(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'giantbomb', 'giantbomb_error_invalidapikey.json')
        scraper = GiantBomb_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()

        with self.assertRaises(ScraperExceededAPIQuoteException):
            scraper._check_status_code(json.loads(data)['status_code'])

    @unittest.skip("Skip downloading from site")
    def test_DownloadGameWithSpecialCharactersReturnsResults(self):
        """GiantBomb doesn't handle searching games with special characters well, so we need to strip any suffix
        metadata from the gamename before we search"""
        scraper = GiantBomb_Scraper()
        results = scraper.search("Super Mario World (USA)", "SNES")
        print ("{0}".format(results))
        self.assertTrue(len(results) > 0, "Expected more than 1 result for Super Mario World")

    @unittest.skip("Skip downloading from site")
    def test_CreateScraperFromName(self):
        sname = 'GiantBomb_Scraper'

        mod = __import__('giantbomb_scraper')
        class_ = getattr(mod, sname)
        instance = class_()
        print(type(instance))
        #print instance.search('Wip3out')
        #print instance.retrieve('12298')


if __name__ == "__main__":
    unittest.main()