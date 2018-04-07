import os, sys
import shutil
import unittest

from xml.etree.ElementTree import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

from config import Config, RomCollection
from configxmlupdater import ConfigxmlUpdater
import util as util

class TestConfigUpdater(unittest.TestCase):

    def test_update_214_220(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'config')

        self.assertTrue(os.path.isfile(os.path.join(config_path, 'config_2.1.4.xml')), "Expected to find config_2.1.4.xml")
        self.assertFalse(os.path.isfile(os.path.join(config_path, 'config.xml')), "config.xml should not exist yet")
        self.assertFalse(os.path.isfile(os.path.join(config_path, 'config.xml.backup 2.1.4')), "config.xml.backup 2.1.4 should not exist yet")

        configFile = os.path.join(config_path, 'config.xml')
        shutil.copyfile(os.path.join(config_path, 'config_2.1.4.xml'), configFile)

        returnCode, message = ConfigxmlUpdater().updateConfig(configFile)
        self.assertTrue(returnCode, "ConfigxmlUpdater returned an error: %s" %message)

        tree = ElementTree().parse(configFile)
        self.assertIsNone(tree.find('Scrapers'), "Scrapers expected to be None")

        fileTypeXml = tree.find('FileTypes/FileType[@name="clearlogo"]')
        self.assertIsNotNone(fileTypeXml)

        scrapers = tree.findall('RomCollections/RomCollection/scraper[@name="thegamesdb.net"]')
        self.assertEquals(2, len(scrapers))

        fileTypeFor = tree.find('ImagePlacing/fileTypeFor[@name="gameinfomamemarquee"]')
        fileTypeForMainViewBackground = fileTypeFor.findall('fileTypeForMainViewBackground')[0]
        self.assertEquals('fanart', fileTypeForMainViewBackground.text)

        fileTypeFor = tree.find('ImagePlacing/fileTypeFor[@name="gameinfomamecabinet"]')
        fileTypeForMainViewBackground = fileTypeFor.findall('fileTypeForMainViewBackground')[0]
        self.assertEquals('fanart', fileTypeForMainViewBackground.text)

        os.remove(os.path.join(config_path, 'config.xml'))
        os.remove(os.path.join(config_path, 'config.xml.backup 2.1.4'))