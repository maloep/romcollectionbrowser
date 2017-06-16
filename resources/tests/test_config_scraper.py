import os

from resources.lib.config import Config, Scraper
import resources.lib.util as util
import unittest


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

        sites, msg = conf.readScrapers(conf.tree)

        self.assertIsInstance(sites, dict, u'Expected dict object, was {0}'.format(type(sites)))

        l = len(sites)
        self.assertTrue(l == 6, u'Expected multiple scraper sites, found {0}'.format(l))

        scrapers = sites['giantbomb.com'].scrapers
        self.assertTrue(len(scrapers) == 2, u'Expected 2 scrapers for giantbomb.com, found {0}'.format(len(scrapers)))
        self.assertIsInstance(scrapers[0], Scraper, u'Expected Scraper object, was {0}'.format(type(scrapers[0])))

if __name__ == "__main__":
    unittest.main()