import os, sys, re, io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
import xml.etree.ElementTree as ET
from offline_gdbi_scraper import Offline_GDBI_Scraper


#used to provide our own test files in _get_xml_path()
class Offline_GDBI_Scraper_Mock(Offline_GDBI_Scraper):
    xmlpath = ''

    def _get_xml_path(self):
        return self.xmlpath


class Test_Offline_GDBI_Scraper(unittest.TestCase):

    def test_search(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_offline', 'gdbi', 'Atari 2600.xml')

        gdbi = Offline_GDBI_Scraper_Mock()
        gdbi.xmlpath = f

        results = gdbi.search("Air Raid")

        self.assertEqual(2, len(results))
        self.assertEqual("Air Raid", results[0]['id'])
        self.assertEqual("Air Raid", results[0]['title'])
        self.assertEqual(["Air Raid"], results[0]['SearchKey'])
        self.assertEqual("Air Raiders", results[1]['id'])
        self.assertEqual("Air Raiders", results[1]['title'])
        self.assertEqual(["Air Raiders"], results[1]['SearchKey'])


    def test_retrieve(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_offline', 'gdbi', 'Atari 2600.xml')

        gdbi = Offline_GDBI_Scraper_Mock()
        gdbi.xmlpath = f

        result = gdbi.retrieve("Air Raid")

        self.assertEqual(["Air Raid"], result['Game'])
        self.assertEqual(["1982"], result['ReleaseYear'])
        self.assertEqual(["Men-A-Vision"], result['Publisher'])
        self.assertEqual(["Men-A-Vision"], result['Developer'])
        self.assertEqual(["1 Player"], result['Players'])
        self.assertEqual(["3.4"], result['Rating'])
        self.assertTrue(result['Description'][0].startswith(
            "The object of this game is to defend the buildings at the bottom of the screen."))
        self.assertEqual(len(result['Genre']), 2)
        self.assertIn("Action", result['Genre'])
        self.assertIn("Shoot-'Em-Up", result['Genre'])
