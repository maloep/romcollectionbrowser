#  -*- coding: utf-8 -*-

import sys
import os
import unittest
import datetime
from pprint import pprint
from urllib2 import HTTPError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append (os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

class TestScrapers(unittest.TestCase):

    def get_scraper_xml_path(self, xml_filename):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'scraper', xml_filename)

    def get_testdata_path(self):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata')

    def test_SearchWithMultipleMatches(self):
        from resources.lib.pyscraper.descriptionparserflatfile import DescriptionParserFlatFile
        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path ('04.01 - mobygames - gamesearch.xml')
        descFile = "http://www.mobygames.com/search/quick?game=Actraiser&p=15"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')

        self.assertTrue(len(results) == 2)

    def test_GameDetails_MobyGames_Sega(self):

        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        #descFile = "http://www.mobygames.com/game/sega-32x/blackthorne"
        #parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\04.02 - mobygames - details.xml"

        parseInstruction = self.get_scraper_xml_path ('04.02 - mobygames - details.xml')
        descFile = "http://www.mobygames.com/game/sega-32x/metal-head"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')

        self.assertEqual(results[0].get('Game')[0], "Metal Head")
        self.assertEqual(results[0].get('Developer')[0], "SEGA&nbsp;Enterprises&nbsp;Ltd.")
        self.assertEqual(results[0].get('Perspective')[0], "1st-person")
        self.assertEqual(results[0].get('ReleaseYear')[0], "1994")
        self.assertEqual(results[0].get('Publisher')[0], "SEGA&nbsp;of&nbsp;America,&nbsp;Inc.")


    def test_GameDetails_MobyGames_Atari5200(self):

        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path ('04.02 - mobygames - details.xml')
        descFile = "http://www.mobygames.com/game/atari-5200/gyruss"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')
        pprint (results)
        # FIXME TODO No Perspective value

    def test_TheGamesDB_SearchByNameWithApostropheAndPlatform(self):
        from resources.lib.pyscraper.descriptionparserflatfile import DescriptionParserFlatFile
        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path ('02 - thegamesdb.xml')
        descFile = "http://thegamesdb.net/api/GetGame.php?name=NBA%20Live%20%2798&platform=Super%20Nintendo%20%28SNES%29"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')
        pprint (results)

        self.assertEqual(results[0].get('Game')[0], "NBA Live 98")
        self.assertEqual(results[0].get('Platform')[0], "Super Nintendo (SNES)")
        self.assertEqual(results[0].get('Publisher')[0], "THQ")
        self.assertEqual(results[0].get('Developer')[0], "EA Sports")

    def test_TheGamesDB_RetrieveByIdWithMultipleGenres(self):
        from resources.lib.pyscraper.descriptionparserflatfile import DescriptionParserFlatFile
        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path ('02 - thegamesdb.xml')
        #descFile = "http://www.thegamesdb.net/game/7808/"   # Syphon Filter, Publisher 989
        descFile = "http://thegamesdb.net/api/GetGame.php?id=7808"  # Syphon Filter, Publisher 989

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')
        pprint (results)

        self.assertEqual(results[0].get('Game')[0], "Syphon Filter")
        self.assertEqual(results[0].get('Genre')[0], "Action")
        self.assertEqual(results[0].get('Genre')[1], "Stealth")
        self.assertTrue(type (results[0].get('ReleaseYear')[0]) is datetime.date,
                        "Expected type of ReleaseYear to be date, is {}".format (type (results[0].get('ReleaseYear')[0])))

    def test_PublisherWithNumericName(self):
        from resources.lib.pyscraper.descriptionparserflatfile import DescriptionParserFlatFile
        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path ('02 - thegamesdb.xml')
        descFile = "http://thegamesdb.net/api/GetGame.php?name=Syphon%20Filter&platform=Sony%20Playstation"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')

        self.assertEqual(results[0].get('Publisher')[0], "989", 'Expected publisher with numeric name to be a string')

    def test_GiantBomb_Search(self):
        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path ('03.01 - giantbomb - search.xml')
        descFile = "http://api.giantbomb.com/search/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&query=Actraiser&resources=game&format=xml"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')
        pprint (results)

        self.assertFalse(results is None)
        self.assertTrue(len(results) == 2, 'Expected 2 results for Giantbomb search criteria')
        self.assertTrue(results[0])
        self.assertEqual(results[0].get('SearchKey')[0], "ActRaiser 2", "Expected ActRaiser 2 to be the first SearchKey in the results")
        self.assertEqual(results[1].get('SearchKey')[0], "ActRaiser", "Expected ActRaiser 2 to be the second SearchKey in the results")

        self.assertTrue('api_key=%GIANTBOMBAPIKey%' in str (results[1].get('url')[0]), "Expected %GIANTBOMBAPIKey% in URL link")

        pprint (results)

    def test_GiantBomb_GameDetails(self):
        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path ('03.02 - giantbomb - detail.xml')
        descFile = "http://www.giantbomb.com/api/game/3030-17123/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&resources=game&format=xml"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')
        pprint (results)

        self.assertFalse(results is None)
        self.assertTrue(len (results) == 1, "Expected 1 result for GiantBomb Game Details")
        self.assertEqual(results[0].get('Publisher')[0], "989")
        self.assertTrue(len(results[0].get('Publisher') == 2), "Expected 2 publishers for GiantBomb Game Details for ActRaiser 2")
        self.assertTrue(len(results[0].get('Genre') == 2), "Expected 2 genres for GiantBomb Game Details for ActRaiser 2")


        pprint (results)


    def test_LocalNFO(self):
        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path ('00 - local nfo.xml')
        descFile = os.path.join(self.get_testdata_path(), 'psx', 'Bushido Blade [SCUS-94180].nfo')

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')
        pprint (results)
        self.assertEqual(results[0].get('Game')[0], "Bushido Blade", "Expected game title to be Bushido Blade from .nfo")



    def test_ContentNotFound404_ArchiveVG(self):
        from resources.lib.pyscraper.descriptionparserflatfile import DescriptionParserFlatFile
        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory


        #descFile = "http://api.archive.vg/1.0/Game.getInfoByCRC/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/b710561b"
        #parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\05.01 - archive - search.xml"

        #descFile = "http://api.archive.vg/1.0/Archive.search/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/Alien+Breed"
        #http://api.archive.vg/1.0/Game.getInfoByID/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/19970

        #http://api.archive.vg/1.0/System.getGames/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/SYSTEM

        parseInstruction = self.get_scraper_xml_path ('05.01 - archive - search.xml')
        descFile = "http://api.archive.vg/1.0/Game.getInfoByCRC/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/b710561b"

        # This will throw a HTTPError which we need to handle (currently the code doesn't handle it)
        parser = DescriptionParserFactory().getParser(parseInstruction)
        self.assertRaises(HTTPError, parser.parseDescription, descFile, 'utf-8',
                          "Expected 404 response from unavailable site archive.vg")


    def test_ContentNotFound404_MAWS(self):
        from resources.lib.pyscraper.descriptionparserflatfile import DescriptionParserFlatFile
        from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path ('06 - maws.xml')
        descFile = "http://maws.mameworld.info/maws/romset/88games"

        # This will throw a HTTPError which we need to handle (currently the code doesn't handle it)
        parser = DescriptionParserFactory().getParser(parseInstruction)
        self.assertRaises(HTTPError, parser.parseDescription, descFile, 'utf-8',
                          "Expected 404 response from unavailable site MAWS")


if __name__ == "__main__":
    unittest.main()