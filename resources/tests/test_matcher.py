# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyparsing'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

from resources.lib.pyscraper.matcher import Matcher
from resources.lib.config import Config, Scraper
import resources.lib.util as util

import unittest


class TestMatcher(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		# This is required so that readScraper() can parse the XML instruction files
		util.RCBHOME = os.path.join(os.path.dirname(__file__), '..', '..')

	def test_ReplaceSequelNumbers(self):
		# Tests identifying a sequel number and converting to roman numeral equivalent
		m = Matcher()
		x = m.replaceSequelNumbers("Final Fantasy 9")
		self.assertEqual(x, "Final Fantasy IX", "Sequel number at end of game not replaced properly")
	
		x = m.replaceSequelNumbers("Final Fantasy 9: Subtitle")
		self.assertEqual(x, "Final Fantasy IX: Subtitle", "Sequel number at end of game not replaced properly")
	
		x = m.replaceSequelNumbers("Final Fantasy 9 (Subtitle)")
		self.assertEqual(x, "Final Fantasy IX (Subtitle)", "Sequel number at end of game not replaced properly")
	
		x = m.replaceSequelNumbers("Final Fantasy IX")
		self.assertEqual(x, "Final Fantasy IX", "Sequel number in roman numeral form should be retained")
	
	
	# FIXME TODO An example where this doesn't work
	# x = m.replaceSequelNumbers("Final Fantasy 11")
	# self.assertEqual(x, "Final Fantasy XI", "Multiple digits should be interpreted as a group")
	
	# x = m.replaceSequelNumbers("Miner 2049er")
	# self.assertEqual(x, "Miner 2049er", "Non-sequel number should not be replaced")
	
	# Test matching against a result set
	def test_getBestResultsWithRomanNumerals(self):
		results = [{'SearchKey': ['Tekken 2']}, {'SearchKey': ['Tekken 3']}, {'SearchKey': ['Tekken IV']}]
		gamename = 'Tekken II'
	
		m = Matcher()
		x = m.getBestResults(results, gamename)
		self.assertIsInstance(x, dict, "Expected a matching dict to be returned")
		self.assertTrue(x.get('SearchKey')[0] == 'Tekken 2',
						"Expected to match title (was {0})".format(x.get('SearchKey')[0]))
	
	
	def test_getBestResultsWithApostropheAndYear(self):
		results = [{'SearchKey': ['FIFA 98']}, {'SearchKey': ['FIFA 97']}, {'SearchKey': ['FIFA 2001']}]
		gamename = 'FIFA \'98'
	
		m = Matcher()
		x = m.getBestResults(results, gamename)
		self.assertTrue(x.get('SearchKey')[0] == 'FIFA 98',
						"Expected to match title (was {0})".format(x.get('SearchKey')[0]))
	
	
	def test_getBestResultsMatchingWithUnicode(self):
		results = [{'SearchKey': [u'スーパー競輪']}]
		gamename = u'スーパー競輪'
		m = Matcher()
		x = m.getBestResults(results, gamename)
		self.assertTrue(x.get('SearchKey')[0] == u'スーパー競輪', "Expected matching unicode strings to match")
	
	
	def test_getBestResultsNonMatchingWithUnicode(self):
		results = [{'SearchKey': [u'スーパー競輪']}]
		gamename = 'Super Test Game'
		m = Matcher()
		x = m.getBestResults(results, gamename)
		self.assertIsNone(x, "Expected non-matching strings to not match, including unicode")
	
	
	@unittest.skip("This fails and the code needs to be fixed as this is a legitimate filename")
	def test_getBestResultsWithBrackets(self):
		results = [{'SearchKey': ['FIFA 98']}, {'SearchKey': ['FIFA 97']}, {'SearchKey': ['FIFA 2001']}]
		gamename = 'FIFA \'98 (1998) [Electronic Arts]'
	
		m = Matcher()
		x = m.getBestResults(results, gamename)
		self.assertTrue(x.get('SearchKey')[0] == 'FIFA 98',
						"Expected to match title (was {0})".format(x.get('SearchKey')[0]))
	
	
	def test_checkSequelNoIsEqual(self):
		m = Matcher()
		self.assertTrue(m.checkSequelNoIsEqual("Final Fantasy IX", "Final Fantasy 9"), "Expected IX to match with 9")
		self.assertTrue(m.checkSequelNoIsEqual("Final Fantasy X", "Final Fantasy 10"), "Expected X to match with 10")
		self.assertTrue(m.checkSequelNoIsEqual("Final Fantasy II", "Final Fantasy 2"), "Expected II to match with 2")
		self.assertTrue(m.checkSequelNoIsEqual("Fifa 98", "FIFA 98"), "Game ending with a year should be matched")
	
	
	def test_getSequelNoIndex(self):
		m = Matcher()
		y = m.getSequelNoIndex("Legend of Zelda, The - A Link to the Past (USA)")
		self.assertTrue(y == -1, "Game name with no number should return -1")
		y = m.getSequelNoIndex("Super Mario World 2 - Yoshi's Island (USA)")
		self.assertTrue(y == 8, "Did not find sequel index for number (found {0})".format(y))
		y = m.getSequelNoIndex("Final Fantasy XIII")
		self.assertTrue(y != -1, "Did not find sequel index for roman numeral above 10 (found {0})".format(y))
	
if __name__ == "__main__":
	unittest.main()