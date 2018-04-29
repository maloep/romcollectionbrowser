# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
from rcbexceptions import *
from mame_scraper import MAME_Scraper


class Test_MAMEHistoryScraper(unittest.TestCase):
    #path to history.dat is stored in config.xml. We can hard code it here.
    path = 'testdata/scraper_web_responses/history.dat'

    @classmethod
    def setUpClass(cls):
        pass

    def test_GameSearch(self):
        scraper = MAME_Scraper()
        scraper.path = self.path
        result = scraper.search("88games")
        self.assertEqual(result[0]['Game'], ["'88 Games"], "Expected title to be '88 Games")
        self.assertEqual(result[0]['ReleaseYear'], ["1988"], "Expected year to be 1988")
        self.assertEqual(result[0]['Publisher'], ["Konami"], "Expected manufacturer to be Konami")

    def test_SearchForGameWithClones(self):
        scraper = MAME_Scraper()
        scraper.path = self.path
        result = scraper.search("1942")
        self.assertEqual(result[0]['Game'], ["1942"], "Expected title to be 1942")
        self.assertEqual(result[0]['ReleaseYear'], ["1984"], "Expected year to be 1984")
        self.assertEqual(result[0]['Publisher'], ["Capcom"], "Expected manufacturer to be Capcom")

    def test_SearchForGameWithSimilarPrefix(self):
        # Make sure we aren't confused with aof, aof2 etc
        scraper = MAME_Scraper()
        scraper.path = self.path
        result = scraper.search("aof")
        self.assertEqual(result[0]['Game'], ["Art of Fighting"], "Expected title to be Art of Fighting")
        self.assertEqual(result[0]['ReleaseYear'], ["1992"], "Expected year to be 1992")
        self.assertEqual(result[0]['Publisher'], ["SNK"], "Expected manufacturer to be SNK")

    def test_DescriptionRegexExcludesTechnicalData(self):
        scraper = MAME_Scraper()
        scraper.path = self.path
        result = scraper.search("1943kai")
        self.assertEquals(result[0]['Description'],
                          ["Control a WWII airplane fighting against small airplanes and big airplanes."],
                          "Description regex failed")

    def test_RegexWorksWithNewerHistoryFormat(self):
        # More recent versions have a slightly modified layout
        scraper = MAME_Scraper()
        scraper.path = self.path
        result = scraper.search("10yard")
        self.assertTrue(len(result) == 1, "Expected 1 result when searching newer history.dat format")
        self.assertTrue(result[0]['Description'][0].startswith("Export version. Game developed in Japan by Irem Corp"),
                        "Unexpected description when handling newer history.dat format")
        self.assertEquals(result[0]['ReleaseYear'], ["1983"],
                          "Unexpected release year when handling newer history.dat format")
        self.assertEquals(result[0]['Publisher'], ["Electrocoin Automatics, Limited"],
                          "Unexpected publisher when handling newer history.dat format")

    @unittest.skip("Clone search not working")
    def test_SearchForClone(self):
        scraper = MAME_Scraper()
        scraper.path = self.path
        result = scraper.search("1942a")
        self.assertEqual(result[0]['Game'], ["1942a"], "Expected title to be 1942a")

    @unittest.skip("Not quite working")
    def test_GameSearchNoResultsRaisesException(self):
        # asdasd - not found
        scraper = MAME_Scraper()
        scraper.path = self.path
        self.assertRaises(ScraperNoSearchResultsFoundException, scraper.search, "adsjdhjdsf")

    def test_GameTitleJapaneseCharacters(self):
        # Newer versions use the Japanese title with an English translation underneath
        scraper = MAME_Scraper()
        scraper.path = self.path
        result = scraper.search("aofx")
        self.assertEqual(result[0]['Game'][0], u"龍虎の拳",
                         u"Expected title to be 龍虎の拳, was {0}".format(result[0]['Game'][0]))
        self.assertTrue(result[0]['Description'][0].startswith("An early Neo-Geo martial arts"),
                        "Expected description to skip translation")

    def test_RegexWorkWithAgeDescriptionFormat(self):
        """More recent versions add a description between the bio line and the title line, e.g.
        $info=aof2,
        $bio

        A 24-year-old SNK Neo-Geo MVS Cart.

        龍虎の拳2 (c) 1994 SNK Corp.
        (Ryuuko no Ken 2)
        """
        scraper = MAME_Scraper()
        scraper.path = self.path
        result = scraper.search("aof2age")
        self.assertEqual(result[0]['Game'][0], u"龍虎の拳2",
                         u"Expected title to be 龍虎の拳2, was {0}".format(result[0]['Game'][0]))


if __name__ == "__main__":
    unittest.main()
