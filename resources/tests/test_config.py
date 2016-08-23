import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append (os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyparsing'))
sys.path.append (os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest

from config import Config
import util
from pprint import pprint

class TestConfig(unittest.TestCase):
    """
    This unittest class is used for testing the parsing of the Config object
    """

    @classmethod
    def setUpClass(cls):
        # This is required so that readScraper() can parse the XML instruction files
        util.RCBHOME = os.path.join(os.path.dirname(__file__), '..', '..')

    def test_ParseValidConfigFile(self):
        # Load a config file with 2 valid RomCollections
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'romcollections_two_valid.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        self.assertIsInstance(conf.romCollections, dict,
                              u'Expected dict object, was {0}'.format(type(conf.romCollections)))

if __name__ == "__main__":
    unittest.main()
