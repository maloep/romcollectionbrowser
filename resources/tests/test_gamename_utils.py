# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

from pyscraper.gamename_utils import SequelNumberHandler, GameNameUtil
import util as util

import unittest


class TestGamenameUtils(unittest.TestCase):

    def test_normalizeName(self):
        gnu = GameNameUtil()

        x = gnu.normalize_name("Madden NFL '97")
        self.assertEqual('MADDENNFL97', x)
        x = gnu.normalize_name("Lemmings 2: The Tribes")
        self.assertEqual('LEMMINGS2TRIBES', x)
        x = gnu.normalize_name("Lemmings 2 - The Tribes")
        self.assertEqual('LEMMINGS2TRIBES', x)
        x = gnu.normalize_name("Lemmings 2_The Tribes")
        self.assertEqual('LEMMINGS2TRIBES', x)
        x = gnu.normalize_name("Lemmings__2__The__Tribes")
        self.assertEqual('LEMMINGS2TRIBES', x)
        x = gnu.normalize_name("Alien vs. Predator")
        self.assertEqual('ALIENVSPREDATOR', x)
        x = gnu.normalize_name("1080° Snowboarding")
        self.assertEqual('1080SNOWBOARDING', x)
        #TODO: X-Men is converted to 10MEN
        x = gnu.normalize_name("Spider-Man & the X-Men in Arcade's Rev")
        self.assertEqual('SPIDERMAN10MENINARCADESREV', x)
        x = gnu.normalize_name("Spider-Man and the X-Men in Arcade's Rev")
        self.assertEqual('SPIDERMAN10MENINARCADESREV', x)
        x = gnu.normalize_name("Prince of Persia I")
        self.assertEqual('PRINCEOFPERSIA', x)
        x = gnu.normalize_name("Prince of Persia 1")
        self.assertEqual('PRINCEOFPERSIA', x)


    def test_prepare_gamename_for_webrequest(self):
        gnu = GameNameUtil()

        result = gnu.prepare_gamename_for_searchrequest("Chrono Trigger (USA)")
        self.assertEqual(result, "Chrono Trigger")
        result = gnu.prepare_gamename_for_searchrequest("Chrono Trigger [cr TCS] (USA)")
        self.assertEqual(result, "Chrono Trigger")
        result = gnu.prepare_gamename_for_searchrequest("Crash Bandicoot 2: Cortex Strikes Back")
        self.assertEqual(result, "Crash Bandicoot")
        result = gnu.prepare_gamename_for_searchrequest("Crash Bandicoot 2")
        self.assertEqual(result, "Crash Bandicoot")
        result = gnu.prepare_gamename_for_searchrequest("Crash Bandicoot II: Cortex Strikes Back")
        self.assertEqual(result, "Crash Bandicoot")
        result = gnu.prepare_gamename_for_searchrequest("Crash Bandicoot II")
        self.assertEqual(result, "Crash Bandicoot")
        result = gnu.prepare_gamename_for_searchrequest("Super Mario World 2 - Yoshi's Island (USA)")
        self.assertEqual(result, "Super Mario World")
        result = gnu.prepare_gamename_for_searchrequest("Madden NFL '97 (USA)")
        self.assertEqual(result, "Madden NFL")
        result = gnu.prepare_gamename_for_searchrequest("Legend of Zelda, The - A Link to the Past (USA)")
        self.assertEqual(result, "Legend of Zelda")
        result = gnu.prepare_gamename_for_searchrequest("FIFA '98: Road to Worldcup (1998) [Electronic Arts]")
        self.assertEqual("FIFA", result)
        result = gnu.prepare_gamename_for_searchrequest("FIFA '98 (1998) [Electronic Arts]")
        self.assertEqual("FIFA", result)
        result = gnu.prepare_gamename_for_searchrequest("FIFA '98: Road to Worldcup")
        self.assertEqual("FIFA", result)
        result = gnu.prepare_gamename_for_searchrequest("3 Ninjas kick back")
        self.assertEqual("3 Ninjas kick back", result)


    def test_strip_addinfo_from_name(self):
        gnu = GameNameUtil()
        result = gnu.strip_addinfo_from_name("FIFA '98 (1998) [Electronic Arts]")
        self.assertEqual("FIFA 98", result)
        #subtitles should be kept intact
        result = gnu.strip_addinfo_from_name("Chuck Rock 2: Son of Chuck")
        self.assertEqual("Chuck Rock 2: Son of Chuck", result)
        result = gnu.strip_addinfo_from_name("Chuck Rock 2-Son of Chuck")
        self.assertEqual("Chuck Rock 2-Son of Chuck", result)
        result = gnu.strip_addinfo_from_name("Chuck Rock 2 - Son of Chuck")
        self.assertEqual("Chuck Rock 2 - Son of Chuck", result)


    def test_strip_subtitle_from_name(self):
        gnu = GameNameUtil()
        result = gnu.strip_subtitle_from_name("Chuck Rock 2: Son of Chuck")
        self.assertEqual("Chuck Rock 2", result)
        result = gnu.strip_subtitle_from_name("Chuck Rock 2-Son of Chuck")
        self.assertEqual("Chuck Rock 2", result)
        result = gnu.strip_subtitle_from_name("Chuck Rock 2 - Son of Chuck")
        self.assertEqual("Chuck Rock 2", result)
        result = gnu.strip_subtitle_from_name("Chuck Rock 2, Son of Chuck")
        self.assertEqual("Chuck Rock 2", result)
        # additional info should be kept intact
        result = gnu.strip_subtitle_from_name("FIFA '98 (1998) [Electronic Arts]")
        self.assertEqual("FIFA 98 (1998) [Electronic Arts]", result)


    def test_remove_sequel_no_one(self):
        s = SequelNumberHandler()
        result = s.remove_sequel_no_one("Arkanoid 1")
        self.assertEqual("Arkanoid", result)
        result = s.remove_sequel_no_one("Arkanoid I")
        self.assertEqual("Arkanoid", result)
        result = s.remove_sequel_no_one("Fifa 1998")
        self.assertEqual("Fifa 1998", result)
        result = s.remove_sequel_no_one("HANOI")
        self.assertEqual("HANOI", result)


    def test_replace_roman_to_int(self):
        s = SequelNumberHandler()
        replaced = s.replace_roman_to_int("Final Fantasy IX")
        self.assertEqual("Final Fantasy 9", replaced)
        replaced = s.replace_roman_to_int("Final Fantasy X")
        self.assertEqual("Final Fantasy 10", replaced)
        replaced = s.replace_roman_to_int("Final Fantasy XI")
        self.assertEqual("Final Fantasy 11", replaced)
        replaced = s.replace_roman_to_int("Final Fantasy XII")
        self.assertEqual("Final Fantasy 12", replaced)
        replaced = s.replace_roman_to_int("Final Fantasy XIII")
        self.assertEqual("Final Fantasy 13", replaced)
        replaced = s.replace_roman_to_int("Final Fantasy XIV")
        self.assertEqual("Final Fantasy 14", replaced)
        replaced = s.replace_roman_to_int("Final Fantasy XV")
        self.assertEqual("Final Fantasy 15", replaced)
        replaced = s.replace_roman_to_int("Chuck Rock II: Son of Chuck")
        self.assertEqual("Chuck Rock 2: Son of Chuck", replaced)

        #Test names that contain roman numerals that should not be replaced
        replaced = s.replace_roman_to_int("Space Invaders")
        self.assertEqual("Space Invaders", replaced)
        replaced = s.replace_roman_to_int("Maniac Mansion")
        self.assertEqual("Maniac Mansion", replaced)

        #TODO: this is still converted to 10-Men
        #replaced = s.replace_roman_to_int("X-Men")
        #self.assertEqual("X-Men", replaced)

    def test_replace_int_to_roman(self):
        s = SequelNumberHandler()
        replaced = s.replace_int_to_roman("Final Fantasy 9")
        self.assertEqual("Final Fantasy IX", replaced)
        replaced = s.replace_int_to_roman("Final Fantasy 10")
        self.assertEqual("Final Fantasy X", replaced)
        replaced = s.replace_int_to_roman("Final Fantasy 11")
        self.assertEqual("Final Fantasy XI", replaced)
        replaced = s.replace_int_to_roman("Final Fantasy 12")
        self.assertEqual("Final Fantasy XII", replaced)
        replaced = s.replace_int_to_roman("Final Fantasy 13")
        self.assertEqual("Final Fantasy XIII", replaced)
        replaced = s.replace_int_to_roman("Final Fantasy 14")
        self.assertEqual("Final Fantasy XIV", replaced)
        replaced = s.replace_int_to_roman("Final Fantasy 15")
        self.assertEqual("Final Fantasy XV", replaced)
        replaced = s.replace_int_to_roman("Chuck Rock 2: Son of Chuck")
        self.assertEqual("Chuck Rock II: Son of Chuck", replaced)

    def test_get_sequel_no_index(self):
        s = SequelNumberHandler()
        index = s.get_sequel_no_index("Final Fantasy IX")
        self.assertEqual(14, index)
        index = s.get_sequel_no_index("Final Fantasy 9")
        self.assertEqual(14, index)
        index = s.get_sequel_no_index("Final Fantasy")
        self.assertEqual(-1, index)


if __name__ == "__main__":
    unittest.main()
