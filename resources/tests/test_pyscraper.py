
import sys
import os

#sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
#sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyparsing'))
#sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

from resources.lib.pyscraper.pyscraper import PyScraper
from resources.lib.config import Config, Scraper
import resources.lib.util as util

import unittest


class TestPyScraper(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		# This is required so that readScraper() can parse the XML instruction files
		util.RCBHOME = os.path.join(os.path.dirname(__file__), '..', '..')

	def test_PrepareScraperSource(self):
		# Setup the scraper by loading the default config_template.xml distributed with RCB (see test_config_scraper.py)
		config_xml_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'config_template.xml')
		conf = Config(config_xml_file)
		conf.initXml()

		sites, msg = conf.readScrapers(conf.tree)
		scrapers = sites['giantbomb.com'].scrapers

		# Proceed with the test
		ps = PyScraper()
		# FIXME log not set to debug level - needs to be
		url = ps.prepareScraperSource(scrapers[0], scrapers[0].source, "Final Fantasy (USA)")
		self.assertEqual(url, "http://api.giantbomb.com/search/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&query=Final%20Fantasy%20%28USA%29&resources=game&field_list=api_detail_url,name&format=xml", "Expected URL to be parsed correctly")

	@unittest.skip("Not yet implemented")
	def test_checkSequelNoIsEqual(self):
		ps = PyScraper()
		print ps.checkSequelNoIsEqual("Legend of Zelda, The - A Link to the Past (USA)", "5")

	@unittest.skip("Not yet implemented")
	def test_getSequelNoIndex(self):
		ps = PyScraper()
		print ps.getSequelNoIndex("Legend of Zelda, The - A Link to the Past (USA)")
		print ps.getSequelNoIndex("Super Mario World 2 - Yoshi's Island (USA)")

if __name__ == "__main__":
	unittest.main()
