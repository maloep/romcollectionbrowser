import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append (os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyparsing'))
sys.path.append (os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest

from config import Config, RomCollection
import util

class TestRomCollection(unittest.TestCase):
    """
    This unittest class is used for testing the parsing of the RomCollection
    """

    @classmethod
    def setUpClass(cls):
        # This is required so that readScraper() can parse the XML instruction files
        util.RCBHOME = os.path.join(os.path.dirname(__file__), '..', '..')

    @classmethod
    def read_config_file(cls, config_xml_file):
        """ This class function parses a specified XML. It is used by all the test cases as a setup.
        """
        conf = Config(config_xml_file)
        conf.initXml()

        # The config_template.xml file has no defined collections, so we expect an empty list
        cls.rom_collections, cls.msg = conf.readRomCollections(conf.tree)

    def test_ParseFileWithNoRomCollectionsReturnsNone(self):
        # Load the default config_template.xml distributed with RCB
        config_xml_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'config_template.xml')
        self.read_config_file(config_xml_file)

        self.assertIsNone(self.rom_collections,
                          u'Expected readRomCollections to return None, was {0}'.format(type(self.rom_collections)))

    def test_ParseFileWithValidCollections(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'romcollections_two_valid.xml')
        self.read_config_file(config_xml_file)

        self.assertIsInstance(self.rom_collections, dict,
                              u'Expected dict object, was {0}'.format(type(self.rom_collections)))

        self.assertTrue(len(self.rom_collections) == 2,
                        u'Expected 2 RomCollections, found {0} items'.format(self.rom_collections))

        self.assertTrue('6' in self.rom_collections)

        # Get the NES rom collection
        rc = self.rom_collections['6']
        self.assertTrue(len(rc.mediaPaths) == 5,
                        u'Expected 5 media paths for NES RomCollection, found {0}'.format(len(rc.mediaPaths)))
        self.assertTrue(len(rc.romPaths) == 2,
                        u'Expected 2 ROM paths for NES RomCollection, found {0}'.format(len(rc.romPaths)))

        # Get the Atari2600 rom collection
        rc = self.rom_collections['7']
        self.assertTrue(len(rc.romPaths) == 1,
                        u'Expected 1 ROM paths for Atari2600 RomCollection, found {0}'.format(len(rc.romPaths)))



if __name__ == "__main__":
    unittest.main()
