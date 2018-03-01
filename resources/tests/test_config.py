import os
import sys
import unittest
from pprint import pprint

# Required for import chain
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

from config import Config, RomCollection
import util as util


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
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_two_valid.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        self.assertIsInstance(conf.romCollections, dict,
                              u'Expected dict object, was {0}'.format(type(conf.romCollections)))

    def test_ParseValidConfigFileWithAllElements(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_two_valid.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        self.assertIsInstance(conf.romCollections, dict,
                              u'Expected dict object, was {0}'.format(type(conf.romCollections)))

    def test_GetRomCollectionNames(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_two_valid.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        list = conf.getRomCollectionNames()
        self.assertEqual(list, ['Atari 2600', 'NES'])

    def test_GetRomCollectionById(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_two_valid.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rc = conf.getRomCollectionById("7")
        self.assertIsInstance(rc, RomCollection, "Expected Rom Collection object to be returned by ID")
        self.assertTrue(rc.name == 'Atari 2600', "Rom Collection name should be returned by ID")

        rc = conf.getRomCollectionById("-1")
        self.assertTrue(rc is None, "Expected searching for invalid rom collection ID to return None")

    def test_GetRomCollectionByName(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_two_valid.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rc = conf.getRomCollectionByName("Atari 2600")
        self.assertIsInstance(rc, RomCollection, "Expected Rom Collection object to be returned by ID")
        self.assertTrue(rc.id == '7', "Rom Collection ID should be returned by name")


if __name__ == "__main__":
    unittest.main()
