# -*- coding: utf-8 -*-
import sys
import os
import json
import responses

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
from giantbomb_scraper import GiantBomb_Scraper
from rcbexceptions import ScraperExceededAPIQuoteException


class Test_GiantBombScraperResponses(unittest.TestCase):

    """
    Search and Retrieve tests using responses library (https://github.com/getsentry/responses)
    
    Every call to requests.get() will be handled with responses and allows us to return results as we like 
    """
    @responses.activate
    def test_search_release(self):                
        
        responses.add(responses.GET,
                'https://www.giantbomb.com/api/releases?filter=platform%3A22%2Cname%3AWip&api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&field_list=id%2Cguid%2Cname%2Crelease_date&format=json',
                json=self._loadJsonFromFile('giantbomb_getreleaselist.json'), 
                status=200)
        
        scraper = GiantBomb_Scraper()
        result = scraper.search('Wip3out', 'PlayStation')
        
        self.assertEquals(result[0]['title'], 'Wip3out')
        self.assertEquals(result[0]['id'], '3050-80827')
    
    
    @responses.activate
    def test_retrieve_release(self):                
        
        responses.add(responses.GET, 
                'https://www.giantbomb.com/api/release/3050-80827/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&format=json',
                json=self._loadJsonFromFile('giantbomb_getrelease.json'), 
                status=200)
        
        responses.add(responses.GET, 
                'https://www.giantbomb.com/api/game/12298/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&format=json',
                json=self._loadJsonFromFile('giantbomb_getgame.json'), 
                status=200)
        
        scraper = GiantBomb_Scraper()
        result = scraper.retrieve('3050-80827', 'PlayStation')
        
        self.assertEquals(result['Publisher'][0], 'Sony Interactive Entertainment Europe')
        self.assertEquals(result['Filetypeboxfront'][0], 'https://www.giantbomb.com/api/image/scale_large/691211-wipeout3.png')
        self.assertEquals(result['Game'][0], 'WipEout 3')
        self.assertEquals(result['ReleaseYear'][0], '1999')
        self.assertEquals(result['Genre'][0], 'Driving/Racing')
        self.assertEquals(result['Developer'][0], 'Psygnosis Limited')
    
    
    def _loadJsonFromFile(self, filename):
        
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'giantbomb', filename)

        with open(f) as jsonfile:
            data = jsonfile.read()

        return json.loads(data)


if __name__ == "__main__":
    unittest.main()