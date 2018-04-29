# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

from matcher import Matcher
import util as util

import unittest


class TestMatcher(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This is required so that readScraper() can parse the XML instruction files
        util.RCBHOME = os.path.join(os.path.dirname(__file__), '..', '..')

    # Test matching against a result set
    def test_getBestResultsWithRomanNumerals(self):
        results = [{'SearchKey': ['Tekken 2']}, {'SearchKey': ['Tekken 3']}, {'SearchKey': ['Tekken IV']}]
        gamename = 'Tekken II'

        m = Matcher()
        x = m.getBestResults(results, gamename)
        self.assertEquals(x.get('SearchKey')[0], 'Tekken 2')

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

    def test_getBestResultsWithBrackets(self):
        results = [{'SearchKey': ['FIFA 98']}, {'SearchKey': ['FIFA 97']}, {'SearchKey': ['FIFA 2001']}]
        gamename = 'FIFA \'98 (1998) [Electronic Arts]'

        m = Matcher()
        x = m.getBestResults(results, gamename)
        self.assertEquals(x.get('SearchKey')[0], 'FIFA 98')


if __name__ == "__main__":
    unittest.main()
