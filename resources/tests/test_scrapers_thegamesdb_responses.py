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
    def test_search(self):
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Tekken&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      json=self._loadJsonFromFile('thegamesdb_search_tekken_playstation.json'),
                      status=200)

        scraper = TheGamesDB_Scraper()

        results = scraper.search('Tekken', 'PlayStation')

        # Expect 5 results
        self.assertEqual(len(results), 5, "Number of search results for multiple search match did not match expected number")
        self.assertEqual(len(scraper.resultdata), 5, "Number of search results for multiple search match did not match expected number")

        # Parse game search query

    @responses.activate
    def test_search_gamename_with_info_tags(self):
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Tekken&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      json=self._loadJsonFromFile('thegamesdb_search_tekken_playstation.json'),
                      status=200)

        scraper = TheGamesDB_Scraper()

        results = scraper.search('Tekken (Europa)(En,Fr,De)', 'PlayStation')

        # Expect 5 results
        self.assertEqual(len(results), 5,
                         "Number of search results for multiple search match did not match expected number")
        self.assertEqual(len(scraper.resultdata), 5,
                         "Number of search results for multiple search match did not match expected number")

    @responses.activate
    def test_retrieve(self):
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Tekken&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      json=self._loadJsonFromFile('thegamesdb_search_tekken_playstation.json'),
                      status=200)

        responses.add(responses.GET,'https://api.thegamesdb.net/v1/Genres',
                      json=self._loadJsonFromFile('genres.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Developers',
                      json=self._loadJsonFromFile('developers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Publishers',
                      json=self._loadJsonFromFile('publishers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Games/Images',
                      json=self._loadJsonFromFile('images_tekken.json'), status=200)

        scraper = TheGamesDB_Scraper()

        #do a search to store the found results
        scraper.search('Tekken', 'PlayStation')

        result = scraper.retrieve('2613', 'PlayStation')

        self.assertEquals(result['Game'], [u'Tekken 2'])
        self.assertTrue(result['Description'][0].startswith('MORE THAN A SEQUEL. THE UNDISPUTED #1 FIGHTING GAME ON THE PLANET.'))
        self.assertEquals(result['Developer'], [u'Namco'])
        self.assertEquals(result['Publisher'], [u'Namco'])
        self.assertEquals(result['ReleaseYear'], [u'1996'])
        self.assertEquals(result['Genre'], [u'Fighting'])
        self.assertEquals(result['Players'], [2])

        self.assertEquals(result['Filetypeclearlogo'], [u'https://cdn.thegamesdb.net/images/large/clearlogo/2613.png'])
        self.assertEquals(result['Filetypefanart'],  [u'https://cdn.thegamesdb.net/images/large/fanart/2613-1.jpg'])
        self.assertEquals(result['Filetypescreenshot'], [u'https://cdn.thegamesdb.net/images/large/screenshots/2613-1.jpg'])
        self.assertEquals(result['Filetypeboxfront'], [u'https://cdn.thegamesdb.net/images/large/boxart/front/2613-1.png'])
        self.assertEquals(result['Filetypeboxback'], [u'https://cdn.thegamesdb.net/images/large/boxart/back/2613-1.jpg'])

    def test_get_images(self):

        images = self._loadJsonFromFile('images_tekken.json')
        scraper = TheGamesDB_Scraper()
        result = scraper._parse_image_result(images, '2613')

        self.assertEquals(result['Filetypeclearlogo'], [u'https://cdn.thegamesdb.net/images/large/clearlogo/2613.png'])
        self.assertEquals(result['Filetypefanart'], [u'https://cdn.thegamesdb.net/images/large/fanart/2613-1.jpg'])
        self.assertEquals(result['Filetypescreenshot'], [u'https://cdn.thegamesdb.net/images/large/screenshots/2613-1.jpg'])
        self.assertEquals(result['Filetypeboxfront'], [u'https://cdn.thegamesdb.net/images/large/boxart/front/2613-1.png'])
        self.assertEquals(result['Filetypeboxback'], [u'https://cdn.thegamesdb.net/images/large/boxart/back/2613-1.jpg'])

    @responses.activate
    def test_retrieve_missing_properties(self):

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=4911&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Arkanoid&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      json=self._loadJsonFromFile('thegamesdb_search_arkanoid_amiga.json'),
                      status=200)

        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Genres',
                      json=self._loadJsonFromFile('genres.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Developers',
                      json=self._loadJsonFromFile('developers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Publishers',
                      json=self._loadJsonFromFile('publishers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Games/Images',
                      json=self._loadJsonFromFile('images_arkanoid_amiga.json'), status=200)

        scraper = TheGamesDB_Scraper()

        #do a search to store the found results
        scraper.search('Arkanoid', 'Amiga')

        result = scraper.retrieve('9580', 'Amiga')

        self.assertIsInstance(result, dict, "Return value of parseGameResult should be a dict")
        self.assertEquals(result['Game'], ["Arkanoid"])
        self.assertEquals(result['Developer'], ["Taito Corporation"])
        self.assertEquals(result['Publisher'], ["Discovery"])
        self.assertEquals(result['Players'], [None])
        self.assertTrue(result['Description'][0].startswith(
            "The original Breakout concept involves controlling a bat at the bottom of the screen"))

    @responses.activate
    def test_retrieve_missing_images(self):
        """Make sure that when image types are not present that we don't have issues"""
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=4911&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Arkanoid&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      json=self._loadJsonFromFile('thegamesdb_search_arkanoid_amiga.json'),
                      status=200)

        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Genres',
                      json=self._loadJsonFromFile('genres.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Developers',
                      json=self._loadJsonFromFile('developers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Publishers',
                      json=self._loadJsonFromFile('publishers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Games/Images',
                      json=self._loadJsonFromFile('images_arkanoid_amiga.json'), status=200)

        scraper = TheGamesDB_Scraper()

        #do a search to store the found results
        scraper.search('Arkanoid', 'Amiga')

        result = scraper.retrieve('9580', 'Amiga')

        self.assertEqual(result['Filetypeboxfront'], ['https://cdn.thegamesdb.net/images/large/boxart/front/9580-1.jpg'])
        self.assertEqual(result['Filetypeclearlogo'], ['https://cdn.thegamesdb.net/images/large/clearlogo/9580.png'])

    @responses.activate
    def test_retrieve_multiple_genres(self):
        """Make sure that games with multiple genres are handled correctly"""
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Syphon+Filter&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      json=self._loadJsonFromFile('thegamesdb_search_syphon_playstation.json'),
                      status=200)

        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Genres',
                      json=self._loadJsonFromFile('genres.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Developers',
                      json=self._loadJsonFromFile('developers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Publishers',
                      json=self._loadJsonFromFile('publishers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Games/Images',
                      json=self._loadJsonFromFile('images_syphon_playstation.json'), status=200)

        scraper = TheGamesDB_Scraper()

        #do a search to store the found results
        scraper.search('Syphon Filter', 'PlayStation')

        result = scraper.retrieve('7808', 'PlayStation')

        self.assertEqual(len(result['Genre']), 2)
        self.assertIn("Action", result['Genre'], "Expected genre Action to be retrieved")
        self.assertIn("Stealth", result['Genre'], "Expected genre Stealth to be retrieved")

    @responses.activate
    def test_Retrieve_numeric_publisher(self):
        """Make sure that games with numeric fields that are expected to be strings (e.g. Publisher) are
        handled correctly"""
        """Make sure that games with multiple genres are handled correctly"""
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Syphon+Filter&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      json=self._loadJsonFromFile('thegamesdb_search_syphon_playstation.json'),
                      status=200)

        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Genres',
                      json=self._loadJsonFromFile('genres.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Developers',
                      json=self._loadJsonFromFile('developers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Publishers',
                      json=self._loadJsonFromFile('publishers.json'), status=200)
        responses.add(responses.GET, 'https://api.thegamesdb.net/v1/Games/Images',
                      json=self._loadJsonFromFile('images_syphon_playstation.json'), status=200)

        scraper = TheGamesDB_Scraper()

        #do a search to store the found results
        scraper.search('Syphon Filter', 'PlayStation')

        result = scraper.retrieve('7808', 'PlayStation')

        self.assertEqual(u"989", result['Publisher'][0], "Expected publisher with numeric name to be a string")

    # Parse if no entries found for game search
    @responses.activate
    def test_search_no_results(self):
        """Make sure that games with multiple genres are handled correctly"""
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=No+Game+Found&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      json=self._loadJsonFromFile('thegamesdb_search_no_result.json'),
                      status=200)

        scraper = TheGamesDB_Scraper()

        #do a search to store the found results
        results = scraper.search('No Game Found', 'PlayStation')

        self.assertIsInstance(results, list, "Expected search results to return list even if no results found")
        self.assertEqual(len(results), 0, "Empty search results should return empty list")

    @unittest.skip("FIXME TODO Not yet implemented")
    def test_SearchForGameWithApostropheAndPlatform(self):
        url = "http://thegamesdb.net/api/GetGame.php?name=NBA%20Live%20%2798&platform=Super%20Nintendo%20%28SNES%29"

        #self.assertEqual(results[0].get('Game')[0], "NBA Live 98")
        #self.assertEqual(results[0].get('Platform')[0], "Super Nintendo (SNES)")
        #self.assertEqual(results[0].get('Publisher')[0], "THQ")
        #self.assertEqual(results[0].get('Developer')[0], "EA Sports")

    def _loadJsonFromFile(self, filename):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb', filename)

        with open(f) as jsonfile:
            data = jsonfile.read()

        return json.loads(data)


    @unittest.skip("only for manual testing")
    def test_search_online(self):
        scraper = TheGamesDB_Scraper()
        result = scraper.search('No Game Found', 'PlayStation')

        #game = scraper.retrieve('7808', 'PlayStation')

        """
        import os, json
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'testdata',
                         'scraper_web_responses', 'thegamesdb', 'publishers.json')
        with open(f, 'w') as outfile:
            json.dump(response, outfile)
        """


if __name__ == "__main__":
    unittest.main()
