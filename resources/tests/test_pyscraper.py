# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyparsing'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

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

	def test_AddNewElements(self):
		ps = PyScraper()
		existingResults = {"SearchKey": ["Tekken 2"], "Publisher": []}
		newResults = {"SearchKey": ["Tekken 3"], "Description": ["Tekken 2 description &amp; history"], "Publisher": ["Namco"]}
		existingResults = ps.addNewElements(existingResults, newResults)

		self.assertIn("Description", existingResults, "Expected to add Description")
		self.assertEqual(existingResults.get("SearchKey")[0], "Tekken 2",
			"Expected existing field SearchKey to not be overwritten (now {0}".format(existingResults.get("SearchKey")[0]))
		self.assertEqual(existingResults.get("Publisher")[0], "Namco",
			"Expected existing but empty field Publisher to be overwritten")
		self.assertEqual(existingResults.get("Description")[0], "Tekken 2 description & history",
			"Expected HTML special characters to be converted")

	def test_AddNewElementsUnicode(self):
		ps = PyScraper()
		existingResults = {"SearchKey": ["Random Game"]}
		newResults = {"Description": [u"'Super Keirin (スーパー競輪, Super Keirin) is a Japan-exclusive video game"]}
		existingResults = ps.addNewElements(existingResults, newResults)

		self.assertEqual(existingResults.get("Description")[0], u"'Super Keirin (スーパー競輪, Super Keirin) is a Japan-exclusive video game",
			"Expected Unicode string to be handled when adding new search result element")


if __name__ == "__main__":
	unittest.main()
