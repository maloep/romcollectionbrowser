# -*- coding: utf-8 -*-
import sys
import os
import json
import responses

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
from mobygames_scraper import Mobygames_Scraper
from rcbexceptions import ScraperExceededAPIQuoteException


class Test_MobygamesScraperResponses(unittest.TestCase):
    """
    Search and Retrieve tests using responses library (https://github.com/getsentry/responses)
    
    Every call to requests.get() will be handled with responses and allows us to return results as we like 
    """

    @responses.activate
    def test_search_game(self):
        responses.add(responses.GET,
                      'https://api.mobygames.com/v1/games?platform=6&format=brief&api_key=FH9VxTkB6BGAEsF3qlnnxQ%3D%3D&title=WipEout',
                      json=self._loadJsonFromFile('mobygames_getgameslist.json'),
                      status=200)

        scraper = Mobygames_Scraper()
        result = scraper.search('WipEout XL', 'PlayStation')

        self.assertEquals(result[0]['title'], 'WipEout XL')

    @responses.activate
    def test_retrieve_game(self):
        # first call gets general game data
        responses.add(responses.GET,
                      'https://api.mobygames.com/v1/games/33250?api_key=FH9VxTkB6BGAEsF3qlnnxQ%3D%3D',
                      json=self._loadJsonFromFile('mobygames_getgame.json'),
                      status=200)

        # second call gets platform specific release data
        responses.add(responses.GET,
                      'https://api.mobygames.com/v1/games/33250/platforms/6?api_key=FH9VxTkB6BGAEsF3qlnnxQ%3D%3D',
                      json=self._loadJsonFromFile('mobygames_getrelease_missingelements.json'),
                      status=200)

        # third call gets platform specific covers
        responses.add(responses.GET,
                      'https://api.mobygames.com/v1/games/33250/platforms/6/covers?api_key=FH9VxTkB6BGAEsF3qlnnxQ%3D%3D',
                      json=self._loadJsonFromFile('mobygames_getcovers.json'),
                      status=200)

        # fourth call gets platform specific screenshots
        responses.add(responses.GET,
                      'https://api.mobygames.com/v1/games/33250/platforms/6/screenshots?api_key=FH9VxTkB6BGAEsF3qlnnxQ%3D%3D',
                      json=self._loadJsonFromFile('mobygames_getscreenshots.json'),
                      status=200)

        scraper = Mobygames_Scraper()
        result = scraper.retrieve(33250, 'PlayStation')

        self.assertEquals(result['Game'], ['WipEot 3 Special Edition / Destrction Derby 2'])
        self.assertEquals(result['ReleaseYear'], ['2003'])
        self.assertEquals(result['Genre'], ['Compilation'])
        self.assertEquals(result['Publisher'], ['Sony Computer Entertainment Europe Ltd.'])
        self.assertEquals(result['Players'], ['1-2 Players'])
        self.assertEquals(result['Filetypeboxback'],
                          ['http://www.mobygames.com/images/covers/l/175220-wipeout-xl-playstation-back-cover.png'])
        self.assertEquals(result['Filetypescreenshot'], [
            'http://www.mobygames.com/images/shots/l/436082-wipeout-xl-playstation-screenshot-wipeout-xl-title-screen.png'])
        self.assertEquals(result['Filetypeboxfront'],
                          ['http://www.mobygames.com/images/covers/l/175218-wipeout-xl-playstation-front-cover.png'])
        self.assertEquals(result['Filetypecartridge'],
                          ['http://www.mobygames.com/images/covers/l/175219-wipeout-xl-playstation-media.png'])

    @responses.activate
    def test_search_game_api_key_exceeded(self):
        responses.add(responses.GET,
                      'https://api.mobygames.com/v1/games?platform=6&format=brief&api_key=FH9VxTkB6BGAEsF3qlnnxQ%3D%3D&title=WipEout',
                      json=self._loadJsonFromFile('mobygames_error_apikey_exceeded.json'),
                      status=429)

        scraper = Mobygames_Scraper()
        with self.assertRaises(ScraperExceededAPIQuoteException):
            scraper.search('WipEout XL', 'PlayStation')

    def _loadJsonFromFile(self, filename):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'mobygames', filename)

        with open(f) as jsonfile:
            data = jsonfile.read()

        return json.loads(data)
