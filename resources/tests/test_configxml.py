#  -*- coding: utf-8 -*-

"""
Unit tests for config.py, reading/writing XML file

To invoke, from the top-level directory, run:
python -m unittest discover -v resources/tests/ "test_configxml.py"
or as part of a full test suite:
python -m unittest discover -v resources/tests/

"""

import sys
import os
import unittest
from xml.etree.ElementTree import *
from pprint import pprint

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyparsing'))

class TestInvalidConfigXML(unittest.TestCase):
    '''
    This class is used to evaluate negative test cases against the config.xml parsing. We load a valid
    config.xml file into an XML tree and modify the tree directly, before parsing it
    '''
    config = None
    tree = None

    @classmethod
    def setUpClass(cls):
        from resources.lib.config import Config, Scraper, Site

        configfile = os.path.join(os.path.dirname(__file__), 'testdata', 'config.xml')
        cls.config = Config(configFile=configfile)
        cls.tree = ElementTree().parse(configfile)

    def test_InvalidRomCollectionIsSkipped_DuplicateAttribute(self):

        # Now edit the tree
        for coll in self.tree.find('RomCollections').findall('RomCollection'):
            if coll.get('name') == 'Atari 2600':
                coll.set('id', '2')

        # Now read the collections from the tree
        colls, msg = self.config.readRomCollections(self.tree)

        # Instead of 5 valid collections, we should only return 4
        self.assertTrue(len(colls) == 4,
                        "Expected 4 collections (invalid collection skipped), instead got {0}".format (len(colls)))

    def test_InvalidRomCollectionIsSkipped_MissingName(self):
        # Now edit the tree
        for coll in self.tree.find('RomCollections').findall('RomCollection'):
            if coll.get('name') == 'Atari 2600':
                coll.attrib.pop('name')

        # Now read the collections from the tree
        colls, msg = self.config.readRomCollections(self.tree)

        # Instead of 5 valid collections, we should only return 4
        self.assertTrue(len(colls) == 4,
                        "Expected 4 collections (invalid collection skipped), instead got {0}".format (len(colls)))

    def test_InvalidRomCollectionIsSkipped_MissingId(self):
        # Now edit the tree
        for coll in self.tree.find('RomCollections').findall('RomCollection'):
            if coll.get('name') == 'Atari 2600':
                coll.attrib.pop('id')

        # Now read the collections from the tree
        colls, msg = self.config.readRomCollections(self.tree)

        # Instead of 5 valid collections, we should only return 4
        self.assertTrue(len(colls) == 4,
                        "Expected 4 collections (invalid collection skipped), instead got {0}".format (len(colls)))

class TestValidConfigXML(unittest.TestCase):

    config = None

    def get_parseinstruction_filename(self, inst):
        import resources.lib.util as util
        return os.path.join(util.RCBHOME, 'resources', 'scraper', inst)

    @classmethod
    def setUpClass(cls):
        from resources.lib.config import Config, Scraper, Site

        configfile = os.path.join(os.path.dirname(__file__), 'testdata', 'config.xml')
        cls.config = Config(configFile=configfile)

    def test_ReadSites(self):
        resp = self.config.readXml()

        # Asserts - Number of Site in XML file
        self.assertTrue(len(self.config.scraperSites.items()) == 6, "Expected 6 scraper sites in test config XML")
        self.assertTrue('local nfo' in self.config.scraperSites, "Local NFO site not found")

        # Asserts Site details
        for key, value in self.config.scraperSites.iteritems():
            if key == 'local nfo':
                self.assertTrue(value.descFilePerGame, "Local NFO site descFilePerGame should be true")
                self.assertFalse(value.searchGameByCRC, "Local NFO site searchGameByCRC should be false")
                self.assertFalse(value.useFoldernameAsCRC, "Unspecified site attribute should be false")

    def test_ReadSiteScrapers(self):
        resp = self.config.readXml()

        # Asserts - number of Scrapers in each Site
        mbg = self.config.scraperSites.get('mobygames.com')
        #pprint (mbg)
        self.assertTrue(len(mbg.scrapers) == 10, "Expected 10 scrapers for Mobygames")
        gb = self.config.scraperSites.get('giantbomb.com')
        self.assertTrue(len(gb.scrapers) == 2, "Expected 2 scrapers for Giantbomb")
        local = self.config.scraperSites.get('local nfo')
        self.assertTrue(len(local.scrapers) == 1, "Expected 1 scraper for local nfo")

        # Asserts - Scraper details
        #pprint (gb.scrapers[0])
        self.assertTrue(gb.scrapers[0].parseInstruction == self.get_parseinstruction_filename ("03.01 - giantbomb - search.xml"),
                        "Parse instruction 0 incorrect for GB")
        self.assertTrue(gb.scrapers[0].source == "http://api.giantbomb.com/search/?api_key=%GIANTBOMBAPIKey%&query=%GAME%&resources=game&field_list=api_detail_url,name&format=xml",
                        "Parse source 0 not sanitised for GB")
        self.assertTrue(gb.scrapers[1].parseInstruction == self.get_parseinstruction_filename ("03.02 - giantbomb - detail.xml"),
                        "Parse instruction 1 incorrect for GB")
        self.assertTrue(gb.scrapers[1].source == "1")
        self.assertTrue(isinstance (gb.scrapers[0].returnUrl, (bool)),
                        "Expected boolean value is not boolean ({0}, {1})".format (gb.scrapers[0].returnUrl, type(gb.scrapers[0].returnUrl)))
        self.assertTrue(gb.scrapers[0].returnUrl == True, "XML tag not interpreted as boolean")
        self.assertTrue(gb.scrapers[1].returnUrl == False, "Missing XML boolean value should be interpreted as False")

    def test_ReadCollections(self):
        resp = self.config.readXml()

        self.assertTrue(len(self.config.romCollections) == 5,
                        "Expected 5 valid collections, instead got {0}".format (len(self.config.romCollections)))

    def test_ReadFileTypes(self):
        resp = self.config.readXml()

        # Image layout file types

    def test_ImagePlacing(self):
        resp = self.config.readXml()

        placing, msg = self.config.readImagePlacing('gameinfobig', self.config.tree)
        self.assertTrue(placing.name == 'gameinfobig', "Expected name to be gameinfobig")
        self.assertTrue(len (placing.fileTypesForGameList) == 4, "Expected 4 fileTypesForGameList entries")
        self.assertTrue(len (placing.fileTypesForMainViewGameInfoUpperLeft) == 0, "Expected 0 fileTypesForMainViewGameInfoUpperLeft entries")
        self.assertTrue(placing.fileTypesForMainView1[0].name == 'publisher',
                        "Expected name of fileTypeForMainView1 to be Publisher (is {0})".format (placing.fileTypesForMainView1[0].name))

    def test_openXML(self):
        resp = self.config.readXml()

        self.assertTrue(resp)   # Assert that the config loaded




if __name__ == "__main__":
    unittest.main()