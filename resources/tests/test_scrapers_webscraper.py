import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
from thegamesdb_scraper import TheGamesDB_Scraper
from giantbomb_scraper import GiantBomb_Scraper
from mobygames_scraper import Mobygames_Scraper
from web_scraper import WebScraper


class TestWebScraper(unittest.TestCase):
    def test_GetPlatformTheGamesDB(self):
        scraper = TheGamesDB_Scraper()
        platform = scraper.get_platform_for_scraper('PlayStation')
        self.assertEqual(platform, "10",
                         "Did not get expected platform name for {0} scraper".format(scraper.name))

    def test_GetPlatformGiantBomb(self):
        scraper = GiantBomb_Scraper()
        platform = scraper.get_platform_for_scraper('PlayStation')
        self.assertEqual(platform, "22", "Did not get expected platform name for {0} scraper".format(scraper.name))

    def test_GetPlatformMobygames(self):
        scraper = Mobygames_Scraper()
        platform = scraper.get_platform_for_scraper('PlayStation')
        self.assertEqual(platform, "6", "Did not get expected platform name for {0} scraper".format(scraper.name))

    def test_Date(self):
        scraper = WebScraper()
        self.assertEqual(scraper._parse_date("1982"), "1982", "Unexpected date response for valid date format")
        self.assertEqual(scraper._parse_date("1983-08-14"), "1983", "Unexpected date response for valid date format")
        self.assertEqual(scraper._parse_date("1986-08-14 00:00:00"), "1986",
                         "Unexpected date response for valid date format")
        self.assertEqual(scraper._parse_date("19/08/1980"), "1980", "Unexpected date response for valid date format")
        self.assertEqual(scraper._parse_date("1980-08"), "1980", "Unexpected date response for valid date format")
        self.assertEqual(scraper._parse_date(""), "1970", "Unexpected date response for invalid date format")
        self.assertEqual(scraper._parse_date("no date"), "1970", "Unexpected date response for invalid date format")
        self.assertEqual(scraper._parse_date(None), "1970", "Unexpected date response for invalid date format")
        self.assertEqual(scraper._parse_date("test"), "1970", "Unexpected date response for invalid date format")


if __name__ == "__main__":
    unittest.main()
