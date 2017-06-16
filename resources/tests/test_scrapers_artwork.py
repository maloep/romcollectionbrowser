#  -*- coding: utf-8 -*-

import os
import unittest
from pyparsing import *
from resources.lib.pyscraper.descriptionparserfactory import DescriptionParserFactory


@unittest.skip("Can't be bothered waiting for HTTP requests")
class TestScrapersArtwork(unittest.TestCase):
    def get_scraper_xml_path(self, xml_filename):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'scraper', xml_filename)

    @unittest.skip("FIXME TODO")
    def test_ArtworkDetail_CoverBack_MobyGames(self):
        parseInstruction = self.get_scraper_xml_path('04.06 - mobygames - coverdetail back.xml')
        descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art/gameCoverId,170208"
        pass

    @unittest.skip("FIXME TODO")
    def test_ArtworkDetail_Media_MobyGames(self):
        parseInstruction = self.get_scraper_xml_path('04.08 - mobygames - coverdetail media.xml')
        descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art/gameCoverId,17623"
        pass

    @unittest.skip("FIXME TODO")
    def test_ArtworkDetail_Screenshot_MobyGames(self):
        parseInstruction = self.get_scraper_xml_path('04.10 - mobygames - screenshot detail.xml')
        descFile = "http://www.mobygames.com/game/snes/actraiser/screenshots/gameShotId,27458/"
        pass

    def test_ArtworkLink_Screenshot_MobyGames(self):
        from descriptionparserfactory import DescriptionParserFactory

        parseInstruction = self.get_scraper_xml_path('04.09 - mobygames - screenshotlink.xml')
        descFile = "http://www.mobygames.com/game/snes/actraiser/screenshots"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = None
        try:
            results = parser.parseDescription(descFile, 'utf-8')
        except ParseException as e:
            print e
        except NameError as n:
            print n

        self.assertFalse(results is None)
        self.assertTrue(len(results) == 29, "Expected 29 screenshots from Mobygames")

        # Expect 29 shots, all from the SNES

    def test_ArtworkLink_FrontCover_MobyGames(self):
        parseInstruction = self.get_scraper_xml_path('04.03 - mobygames - coverlink front.xml')
        descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art"
        # http://www.mobygames.com/game/actraiser/cover-art  FIXME Add check that this returns more, for other platforms

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = None
        try:
            results = parser.parseDescription(descFile, 'utf-8')
        except ParseException as e:
            print e
        except NameError as n:
            print n

        self.assertFalse(results is None)
        self.assertTrue(len(results) == 13, "Expected 13 front covers from Mobygames")
        self.assertTrue(results[0].get('url')[0].startswith("http://www.mobygames.com"),
                        "Expected mobygames URL prefix to be added due to appendTo clause")

        # FIXME TODO This doesn't include covers from other platforms

    def test_ArtworkLink_BackCover_MobyGames(self):
        parseInstruction = self.get_scraper_xml_path('04.05 - mobygames - coverlink back.xml')
        descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = None
        try:
            results = parser.parseDescription(descFile, 'utf-8')
        except ParseException as e:
            print e
        except NameError as n:
            print n

        self.assertFalse(results is None)
        self.assertTrue(len(results) == 3, "Expected 3 back covers from Mobygames")
        self.assertTrue(results[0].get('url')[0].startswith("http://www.mobygames.com"),
                        "Expected mobygames URL prefix to be added due to appendTo clause")

    def test_ArtworkLink_Media_MobyGames(self):
        parseInstruction = self.get_scraper_xml_path('04.07 - mobygames - coverlink media.xml')
        descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = None
        try:
            results = parser.parseDescription(descFile, 'utf-8')
        except ParseException as e:
            print e
        except NameError as n:
            print n

        self.assertFalse(results is None)
        self.assertTrue(len(results) == 3, "Expected 3 media items from Mobygames")
        self.assertTrue(results[0].get('url')[0].startswith("http://www.mobygames.com"),
                        "Expected mobygames URL prefix to be added due to appendTo clause")

    # FIXME TODO Add entries for all the other scrapers

    def test_ArtworkDetail_CoverFront_MobyGames(self):
        parseInstruction = self.get_scraper_xml_path('04.04 - mobygames - coverdetail front.xml')
        descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art/gameCoverId,170207"

        parser = DescriptionParserFactory().getParser(parseInstruction)
        results = parser.parseDescription(descFile, 'utf-8')

        filetype_boxfront_url = results[0].get('Filetypeboxfront')[0]
        # Mobygames parser extracts filename as /images/covers...; we prefix this with the domain name
        self.assertTrue(filetype_boxfront_url.startswith("http://www.mobygames.com"),
                        "Expected mobygames URL prefix to be added due to appendTo clause")
        self.assertEqual(filetype_boxfront_url, 'http://www.mobygames.com/images/covers/l/170207-actraiser-snes-front-cover.jpg')

if __name__ == "__main__":
    unittest.main()