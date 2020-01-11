# -*- coding: utf-8 -*-
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
from mobygames_scraper import Mobygames_Scraper
from rcbexceptions import ScraperExceededAPIQuoteException


class Test_MobygamesScraper(unittest.TestCase):
    """
    Note that typos are very common. Response JSON is what it is.
    """

    def test_GamesListResults(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getgameslist.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()
        results = scraper._parse_search_results(json.loads(data))

        # Expect 10 results per page (regardless of total)
        self.assertEqual(len(results), 5,
                         "Number of search results for multiple search match did not match expected number")
        self.assertEqual(results[0]['title'], "WipEout XL",
                         "Incorrect title for first result")
        self.assertEqual(results[0]['id'], 3134, "Incorrect game ID for first result")
        # MobyGames does not return release date in brief results
        self.assertEqual(results[0]['releaseDate'], "", "Incorrect releaseDate for first result")

    def test_parse_game_result(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getgame.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()
        result = scraper._parse_game_result(json.loads(data))
        print ("Game result is {0}".format(result))

        self.assertEquals(result['Game'], ['WipEot 3 Special Edition / Destrction Derby 2'])

        # The release date for PlayStation in this result set is %Y
        #ReleaseYear is moved to parse_release_data
        #self.assertEquals(result['ReleaseYear'], ['2003'])

        # Genres
        self.assertEquals(result['Genre'], ['Compilation'])

    def test_parse_game_result_WithMultipleGenres(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getgame_2genres.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()
        result = scraper._parse_game_result(json.loads(data))
        print ("Game result is {0}".format(result))

        # Genres - multiple genres, but only 2 "Basic Genres"
        self.assertEquals(len(result['Genre']), 2, "Expected 2 genres")
        self.assertIn("Racing / Driving", result['Genre'], "Expected genre Racing / Driving to be retrieved")
        self.assertIn("Action", result['Genre'], "Expected genre Action to be retrieved")

    # FIXME TODO Perspective

    # The release date for PlayStation in this result set is %Y-%m-%d
    #ReleaseYear is moved to parse_release_data
    #self.assertEquals(result['ReleaseYear'], ['1996'])

    def test_parse_release_result(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getrelease.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()
        result = scraper._parse_release_result(json.loads(data))
        print ("Release result is {0}".format(result))

        self.assertEquals(result['ReleaseYear'], ['1994'])
        self.assertEquals(result['Publisher'], ['Interplay Productions, Inc.'])
        self.assertEquals(result['Developer'], ['Infogrames Europe SA'])
        self.assertEquals(result['Players'], ['1 Player'])
        self.assertEquals(result['Controller'], ['Controller Pad'])

    def test_parse_release_result_missingelements(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getrelease_missingelements.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()
        result = scraper._parse_release_result(json.loads(data))
        print ("Release result is {0}".format(result))

    def test_parse_covers_result(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getcovers.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()

        result = scraper._parse_covers_result(json.loads(data))
        print ("Covers result is {0}".format(result))

        self.assertEquals(result['Filetypeboxfront'],
                          ['http://www.mobygames.com/images/covers/l/175218-wipeout-xl-playstation-front-cover.png'])
        self.assertEquals(result['Filetypeboxback'],
                          ['http://www.mobygames.com/images/covers/l/175220-wipeout-xl-playstation-back-cover.png'])
        self.assertEquals(result['Filetypecartridge'],
                          ['http://www.mobygames.com/images/covers/l/175219-wipeout-xl-playstation-media.png'])

    def test_parse_covers_result_empty(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getcovers_empty.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()

        result = scraper._parse_covers_result(json.loads(data))
        print ("Covers result is {0}".format(result))

        self.assertEquals(len(result), 0, 'Result length expected to be 0')

    def test_parse_screenshots_result(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getscreenshots.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()

        result = scraper._parse_screenshots_result(json.loads(data))
        print ("Screenshots result is {0}".format(result))

        self.assertEquals(result['Filetypescreenshot'], [
            'http://www.mobygames.com/images/shots/l/436082-wipeout-xl-playstation-screenshot-wipeout-xl-title-screen.png'])

    def test_parse_screenshots_result_empty(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getscreenshots_empty.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()

        result = scraper._parse_screenshots_result(json.loads(data))
        print ("Screenshots result is {0}".format(result))

        self.assertEquals(len(result), 0, 'Result length expected to be 0')

    def test_GamesListNoResults(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_getgameslist_noresults.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()
        results = scraper._parse_search_results(json.loads(data))

        # Expect 0 results and an empty list
        self.assertIsInstance(results, list, "Expected search results to return list even if no results found")
        self.assertEqual(len(results), 0, "Empty search results should return empty list")

    def test_GamesResultWithHTMLEntities(self):
        # Test that any HTML code, particularly in the description field (e.g. <br>), is ignored
        # FIXME TODO Need BeautifulSoup HTML parsing
        pass

    @unittest.skip("Might be caught by HTTP428 response code")
    def test_ErrorResponseAPIKeyExeeded(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', 'mobygames_error_apikey_exceeded.json')
        scraper = Mobygames_Scraper()

        with open(f) as jsonfile:
            data = jsonfile.read()

        with self.assertRaises(ScraperExceededAPIQuoteException):
            scraper._check_status_code(json.loads(data)['status_code'])

    def test_CreateScraperFromName(self):
        sname = 'Mobygames_Scraper'

        module = __import__('mobygames_scraper')
        class_ = getattr(module, sname)
        instance = class_()
        print(type(instance))

    # FIXME TODO tests for japanese characters? tests for whitespace handling/HTML encodings (e.g. <br> etc)
