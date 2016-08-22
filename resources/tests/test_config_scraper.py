import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append (os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyparsing'))
sys.path.append (os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest

from config import Config, Scraper
import util

class TestScraper(unittest.TestCase):
    """
    This unittest class is used for testing the parsing of the Scraper and Site objects from the config_template.xml
    file. Tests for the parsing process itself is in test_scrapers.py and test_scrapers_artwork.py
    """

    @classmethod
    def setUpClass(cls):
        # This is required so that readScraper() can parse the XML instruction files
        util.RCBHOME = os.path.join(os.path.dirname(__file__), '..', '..')

    def test_ParseValidFileIsSuccessful(self):
        # Load the default config_template.xml distributed with RCB
        config_xml_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'config_template.xml')
        conf = Config(config_xml_file)
        conf.initXml()
        #self.assertTrue(conf is None, u'Expected conf to be none')

        sites, msg = conf.readScrapers(conf.tree)
        self.assertIsInstance(sites, dict, u'Expected list object, was {0}'.format(type(sites)))

        l = len(sites)
        self.assertTrue(l == 6, u'Expected multiple scraper sites, found {0}'.format(l))

        #self.assertTrue(scrapers['local nfo'].descFilePerGame == 'video')
        #self.assertTrue(ft.parent == 'game')
        #self.assertTrue(ft.id == '12')

if __name__ == "__main__":
    unittest.main()