import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
from nfo_scraper import NFO_Scraper


class Test_NFOScraper(unittest.TestCase):

    def test_search(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'nfo', 'Amiga', 'Arkanoid I.nfo')

        scraper = NFO_Scraper()
        scraper.nfo_file = f

        results = scraper.search("Arkanoid")

        self.assertEqual(1, len(results))
        self.assertEqual("Arkanoid", results[0]['id'])
        self.assertEqual("Arkanoid", results[0]['title'])
        with self.assertRaises(KeyError):
            results[0]['SearchKey']



    def test_retrieve(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'nfo', 'Amiga', 'Arkanoid I.nfo')

        scraper = NFO_Scraper()
        scraper.nfo_file = f

        result = scraper.retrieve(1, 'Amiga')

        self.assertEqual(["Arkanoid"], result['Game'])
        self.assertEqual(["1987"], result['ReleaseYear'])
        self.assertEqual(["Discovery"], result['Publisher'])
        self.assertEqual(["Taito"], result['Developer'])
        self.assertEqual(["Top-Down"], result['Perspective'])
        self.assertEqual(["Joystick"], result['Controller'])
        self.assertEqual(["Floppy"], result['Media'])
        self.assertEqual(["USA"], result['Region'])
        self.assertEqual(["v1.00"], result['Version'])
        self.assertEqual(["1"], result['Players'])
        self.assertEqual(["0"], result['LaunchCount'])
        self.assertEqual(["0"], result['IsFavorite'])
        self.assertEqual(["3.8"], result['Rating'])
        self.assertEqual(["128"], result['Votes'])
        self.assertTrue(result['Description'][0].startswith("The original Breakout concept involves controlling a bat at the bottom of the screen"))
        self.assertEqual(len(result['Genre']), 2)
        self.assertIn("Action", result['Genre'])
        self.assertIn("Platform", result['Genre'])
