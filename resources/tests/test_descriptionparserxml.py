import unittest
import os
import sys
import time
from xml.etree.ElementTree import *
from resources.lib.pyscraper.descriptionparserxml import DescriptionParserXml


# This class tests parsing the description returned from a HTTP request or opening a file
# Note the response data (descFile in most test cases) is in test data, not retrieved from the site
class TestDescriptionParserXML(unittest.TestCase):
	def getGrammarNodeFromFile(self, descParseInstructionFile):
		with open(descParseInstructionFile, 'r') as fp:
			tree = fromstring(fp.read())

		return tree.find('GameGrammar')

	# Validate the GrammarNode parsing works for a game retrieve
	def test_ParseDescriptionFromFile(self):
		descFile = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'thegamesdb_getgame.xml')
		grammarNode = self.getGrammarNodeFromFile(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'scraper', '02 - thegamesdb.xml'))

		parser = DescriptionParserXml(grammarNode)
		result = parser.parseDescription(descFile, "utf-8")
		print result

		self.assertEqual(result[0].get('SearchKey')[0], result[0].get('Game')[0], "Expected SearchKey to be set to Game value")
		self.assertEqual(result[0].get('SearchKey')[0], 'Tekken 2', "Expected title (SearchKey) to be 'Tekken 2'")
		self.assertEqual(result[0].get('Publisher')[0], 'Namco', "Expected publisher to be 'Namco'")
		self.assertTrue(type(result[0].get('ReleaseYear')[0]) is time.struct_time,
						"Expected type of ReleaseYear to be date, is {}".format(type(result[0].get('ReleaseYear')[0])))

		# This returns a generator
		result = parser.scanDescription(descFile, None, "utf-8")
		for r in result:
			print r

	# Validate the GrammarNode parsing works for a game search
	def test_ParseGrammarNodeAppends(self):
		# Search GiantBomb: https://www.giantbomb.com/api/search/?query=tekken&api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&field_list=api_detail_url,name&format=xml&resources=game
		descFile = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata', 'scraper_web_responses', 'giantbomb_getgameslist.xml')
		grammarNode = self.getGrammarNodeFromFile(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'scraper', '03.01 - giantbomb - search.xml'))

		parser = DescriptionParserXml(grammarNode)
		result = parser.parseDescription(descFile, "utf-8")
		print result

		self.assertTrue(len(result) == 10, "Expected 10 results from GiantBomb search query")
		self.assertEqual(result[0].get('url')[0], "https://www.giantbomb.com/api/game/3030-10081/?api_key=%GIANTBOMBAPIKey%&field_list=id,name,image,images,releases,expected_release_year,genres,developers,publishers,description,site_detail_url",
						 "GrammarNode with appendResultWith did not append")
