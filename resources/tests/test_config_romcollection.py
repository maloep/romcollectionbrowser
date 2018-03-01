import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

from config import Config, RomCollection
import util as util


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
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_two_valid.xml')
        self.read_config_file(config_xml_file)

        self.assertIsInstance(self.rom_collections, dict,
                              u'Expected dict object, was {0}'.format(type(self.rom_collections)))

        self.assertTrue(len(self.rom_collections) == 2,
                        u'Expected 2 RomCollections, found {0} items'.format(self.rom_collections))

        self.assertTrue('6' in self.rom_collections)

        # Get the NES rom collection
        rc = self.rom_collections['6']

        # Validate lists for multiple elements
        self.assertTrue(len(rc.mediaPaths) == 5,
                        u'Expected 5 media paths for NES RomCollection, found {0}'.format(len(rc.mediaPaths)))
        self.assertTrue(len(rc.romPaths) == 2,
                        u'Expected 2 ROM paths for NES RomCollection, found {0}'.format(len(rc.romPaths)))
        self.assertTrue(rc.name == 'NES', u'Expected collection name to be NES, was {0}'.format(rc.name))

        # Validate boolean values
        self.assertTrue(rc.useEmuSolo is False,
                        u'Expected boolean value for boolean attribute, was {0}'.format(rc.useEmuSolo))
        self.assertIsInstance(rc.useEmuSolo, bool,
                              u'Expected boolean type for boolean attribute, was {0}'.format(type(rc.useEmuSolo)))
        self.assertTrue(rc.allowUpdate is True,
                        u'Expected boolean value for boolean attribute, was {0}'.format(rc.allowUpdate))

        # Validate empty elements are empty strings
        self.assertTrue(rc.gameclient == '', u'Expected collection gameclient to be \'\', was {0}'.format(rc.gameclient))

        # Validate non-empty elements are as expected
        self.assertTrue(rc.emulatorCmd == '/Path/To/NES/Emulator',
                        u'Incorrect expected value for collection emulatorCmd ({0})'.format(rc.emulatorCmd))

        # Get the Atari2600 rom collection
        rc = self.rom_collections['7']
        self.assertTrue(len(rc.romPaths) == 1,
                        u'Expected 1 ROM paths for Atari2600 RomCollection, found {0}'.format(len(rc.romPaths)))

    @unittest.skip('Skipping until parsing config.xml file returns only the valid collections instead of None')
    def test_ParseCollectionWithMissingAttribsFails(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_invalid_missingattribs.xml')
        self.read_config_file(config_xml_file)

        self.assertTrue(len(self.rom_collections) == 1,
                        u'Expected 1 valid rom collection, found {0}'.format(len(self.rom_collections)))

        # Get the valid SNES rom collection
        rc = self.rom_collections['7']
        self.assertIsInstance(rc, RomCollection, u'Expected RomCollection object, was {0}'.format(type(rc)))
        self.assertTrue(rc.name == 'SNES', u'Expected RomCollection name to be SNES, was {0}'.format(rc.name))

    def test_GetFilenameFromGamename(self):
        rc = RomCollection()
        gamename = rc.getGamenameFromFilename('/path/to/Game.iso')
        self.assertTrue(gamename == "Game", u'Expected gamename to be Game, was {0}'.format(gamename))

        rc.useFoldernameAsGamename = True
        gamename = rc.getGamenameFromFilename('/path/to/Game.iso')
        self.assertTrue(gamename == "to", u'Expected gamename from foldername to be "to", was {0}'.format(gamename))

        rc.useFoldernameAsGamename = False
        rc.diskPrefix = '_Disk.*'
        gamename = rc.getGamenameFromFilename('/path/to/Game_Disk1.iso')
        self.assertTrue(gamename == "Game", u'Expected gamename with disk pattern to be Game, was {0}'.format(gamename))

        # FIXME TODO This fails with an exception - need to fix code
        # rc.diskPrefix = ' (Disk .*'
        # gamename = rc.getGamenameFromFilename('/path/to/Game (Disk 1).iso')
        # self.assertTrue(gamename == "Game", u'Expected gamename with disk pattern to be Game, was {0}'.format(gamename))


if __name__ == "__main__":
    unittest.main()
