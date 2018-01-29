import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyparsing'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

import unittest
from resources.lib.pyscraper.thegamesdb_scraper import TheGamesDB_Scraper
from resources.lib.pyscraper.giantbomb_scraper import GiantBomb_Scraper
from resources.lib.pyscraper.web_scraper import WebScraper


class TestWebScraper(unittest.TestCase):
	def test_GetPlatformTheGamesDB(self):
		scraper = TheGamesDB_Scraper()
		platform = scraper.get_platform_for_scraper('PlayStation')
		self.assertEqual(platform, "Sony Playstation", "Did not get expected platform name for {0} scraper".format(scraper.name))

	@unittest.skip("GiantBomb not yet coded for this function")
	def test_GetPlatformGiantBomb(self):
		scraper = GiantBomb_Scraper()
		platform = scraper.get_platform_for_scraper('PlayStation')
		self.assertEqual(platform, "22", "Did not get expected platform name for {0} scraper".format(scraper.name))

	def test_PrepareGameName(self):
		scraper = WebScraper()
		x = scraper.prepare_gamename_for_request("Chrono Trigger (USA)")
		self.assertEqual(x, "Chrono Trigger")

		x = scraper.prepare_gamename_for_request("Chrono Trigger [cr TCS] (USA)")
		self.assertEqual(x, "Chrono Trigger")

		x = scraper.prepare_gamename_for_request("Crash Bandicoot 2: Cortex Strikes Back")
		self.assertEqual(x, "Crash Bandicoot 2")


if __name__ == "__main__":
	unittest.main()
