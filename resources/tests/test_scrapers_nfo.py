import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
import xml.etree.ElementTree as ET
from nfo_scraper import NFO_Scraper


class Test_NFOScraper(unittest.TestCase):

    def test_retrieve(self):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'nfo', 'Amiga', 'Arkanoid I.nfo')

        tree = ET.ElementTree()
        if sys.version_info >= (2, 7):
            parser = ET.XMLParser(encoding='utf-8')
        else:
            parser = ET.XMLParser()

        tree.parse(f, parser)

        scraper = NFO_Scraper()
        scraper.tree = tree

        result = scraper.retrieve(1, 'Amiga')
        print result

        self.assertEqual(["Arkanoid"], result['Game'])
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
