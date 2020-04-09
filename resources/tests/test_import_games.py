# coding=utf-8
from builtins import object
import os
import sys
import shutil
import unittest
import responses


# Required for import chain
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

from config import Config, RomCollection
import util as util
from dbupdate import DBUpdate
from gamedatabase import GameDataBase, GameView, File

import xbmcaddon

class RCBMockGui(object):

    itemCount = 0

    def writeMsg(self, msg1, msg2, count=0):
        return True


class TestImportGames(unittest.TestCase):
    """
    This unittest class is used for testing the complete scrape and import process
    """

    gdb = None

    @classmethod
    def get_testdata_path(cls):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata')

    @classmethod
    def setUpClass(cls):
        # This is required so that readScraper() can parse the XML instruction files
        util.RCBHOME = os.path.join(os.path.dirname(__file__), '..', '..')

        # Open the DB
        db_path = os.path.join(cls.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        shutil.copyfile(os.path.join(db_path, 'MyGames_current_empty.db'), os.path.join(db_path, 'MyGames.db'))

        cls.gdb = GameDataBase(db_path)
        cls.gdb.connect()

    @classmethod
    def tearDownClass(cls):
        # Cleanup
        cls.gdb.close()
        os.remove(os.path.join(os.path.join(cls.get_testdata_path(), 'database'), 'MyGames.db'))

    @responses.activate
    def test_import_initial_accurate_gameswithoutdesc(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[1] = conf.romCollections['1']

        self.register_responses()
        self.register_responses_Amiga()

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = GameView(self.gdb).getFilteredGames(1, 0, 0, 0, 0, 0, 0, 0, 0, likeStmnt, '', 0)

        self.assertEquals(len(games), 4)

        airborneRanger = games[0]
        self.assertEquals(airborneRanger[GameView.COL_NAME], 'Airborne Ranger')
        self.assertEquals(airborneRanger[GameView.COL_year], '1989')
        self.assertTrue(airborneRanger[GameView.COL_description].startswith(
            'In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger.'))
        self.assertEquals(airborneRanger[GameView.COL_genre], 'Action, Adventure')
        self.assertEquals(airborneRanger[GameView.COL_publisher], 'MicroProse Software, Inc.')
        self.assertEquals(airborneRanger[GameView.COL_developer], 'Imagitec Design Inc.')
        self.assertEquals(airborneRanger[GameView.COL_maxPlayers], '1')
        roms = File(self.gdb).getRomsByGameId(airborneRanger[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

        chuckRock = games[1]
        self.assertEquals(chuckRock[GameView.COL_NAME], 'Chuck Rock')
        self.assertEquals(chuckRock[GameView.COL_year], '1991')
        self.assertTrue(chuckRock[GameView.COL_description].startswith(
            "Chuck Rock hasn't been the same since his long-time rival in love, the evil Gary Gritter, kidnapped his wife, the beautiful Ophelia."))
        self.assertEquals(chuckRock[GameView.COL_genre], 'Platform')
        self.assertEquals(chuckRock[GameView.COL_publisher], 'Core Design Ltd.')
        self.assertEquals(chuckRock[GameView.COL_developer], 'Core Design Ltd.')
        self.assertEquals(chuckRock[GameView.COL_maxPlayers], '1')
        self.assertEquals(chuckRock[GameView.COL_rating], '')
        roms = File(self.gdb).getRomsByGameId(chuckRock[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

        eliminator = games[2]
        self.assertEquals(eliminator[GameView.COL_NAME], 'Eliminator')
        self.assertEquals(eliminator[GameView.COL_year], None)
        roms = File(self.gdb).getRomsByGameId(eliminator[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

        formulaOne = games[3]
        self.assertEquals(formulaOne[GameView.COL_NAME], 'MicroProse Formula One Grand Prix')
        self.assertEquals(formulaOne[GameView.COL_year], '1991')
        self.assertTrue(formulaOne[GameView.COL_description].startswith(
            "MicroProse Formula One Grand Prix is a racing simulator released in 1991 by MicroProse and created by game designer Geoff Crammond."))
        # HACK: Order of genres depends on id in database. If we run the full set of tests Genre Sports might already be
        # in database and has a lower id than Racing
        self.assertTrue(
            formulaOne[GameView.COL_genre] == 'Racing, Sports' or formulaOne[GameView.COL_genre] == 'Sports, Racing')
        self.assertEquals(formulaOne[GameView.COL_publisher], 'MicroProse Software, Inc.')
        self.assertEquals(formulaOne[GameView.COL_developer], None)
        self.assertEquals(formulaOne[GameView.COL_maxPlayers], '1')
        roms = File(self.gdb).getRomsByGameId(formulaOne[GameView.COL_ID])
        self.assertEquals(len(roms), 4)

    @responses.activate
    def test_import_initial_special_characters(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[3] = conf.romCollections['3']

        self.register_responses()
        self.register_responses_N64()

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'true'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = GameView(self.gdb).getFilteredGames(3, 0, 0, 0, 0, 0, 0, 0, 0, likeStmnt, '', 0)

        self.assertEquals(len(games), 1)
        snowboarding = games[0]
        self.assertEquals(snowboarding[GameView.COL_NAME], u'1080\xb0 Snowboarding')
        # TODO check for description with special characters
        # self.assertTrue(snowboarding[GameView.COL_description].startswith(u"You’re taking a Tahoe 155 snowboard down a steep, bumpy incline at night and you’re about to top off an Indy Nosebone with a 360° Air"))
        self.assertEquals(snowboarding[GameView.COL_year], '1998')
        self.assertEquals(snowboarding[GameView.COL_genre], 'Sports')
        self.assertEquals(snowboarding[GameView.COL_publisher], 'Nintendo')
        self.assertEquals(snowboarding[GameView.COL_developer], 'Nintendo EAD')
        roms = File(self.gdb).getRomsByGameId(snowboarding[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

    @responses.activate
    def test_import_multirompath_multidisc(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[4] = conf.romCollections['4']

        self.register_responses()
        self.register_responses_PSX()

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'true'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = GameView(self.gdb).getFilteredGames(4, 0, 0, 0, 0, 0, 0, 0, 0, likeStmnt, '', 0)

        self.assertEquals(len(games), 2)

        bushido = games[0]
        self.assertEquals(bushido[GameView.COL_NAME], 'Bushido Blade')
        self.assertEquals(bushido[GameView.COL_year], '1997')
        self.assertTrue(bushido[GameView.COL_description].startswith(
            '"Bushido" is the soul of Japan - an ancient honor code deeply followed by samurai warriors for centuries'))
        self.assertEquals(bushido[GameView.COL_genre], 'Fighting')
        self.assertEquals(bushido[GameView.COL_maxPlayers], '2')
        self.assertEquals(bushido[GameView.COL_publisher], 'Squaresoft')
        self.assertEquals(bushido[GameView.COL_developer], 'LightWeight')
        roms = File(self.gdb).getRomsByGameId(bushido[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

        silenthill = games[1]
        self.assertEquals(silenthill[GameView.COL_NAME], 'Silent Hill')
        self.assertEquals(silenthill[GameView.COL_year], '1999')
        self.assertTrue(silenthill[GameView.COL_description].startswith(
            'Silent Hill is a 1999 survival horror video game for the PlayStation.'))
        self.assertEquals(silenthill[GameView.COL_genre], 'Action, Horror')
        self.assertEquals(silenthill[GameView.COL_maxPlayers], '1')
        self.assertEquals(silenthill[GameView.COL_publisher], 'Konami Digital Entertainment, Inc.')
        self.assertEquals(silenthill[GameView.COL_developer], 'Konami')
        roms = File(self.gdb).getRomsByGameId(silenthill[GameView.COL_ID])
        self.assertEquals(len(roms), 2)

    @responses.activate
    def test_import_gameasfolder(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[5] = conf.romCollections['5']

        self.register_responses()
        self.register_responses_SNES()

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'true'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = GameView(self.gdb).getFilteredGames(5, 0, 0, 0, 0, 0, 0, 0, 0, likeStmnt, '', 0)

        self.assertEquals(len(games), 2)

        chronoTrigger = games[0]
        self.assertEquals(chronoTrigger[GameView.COL_NAME], 'Chrono Trigger')
        self.assertEquals(chronoTrigger[GameView.COL_year], '1995')
        self.assertTrue(chronoTrigger[GameView.COL_description].startswith('The 32-Meg quest begins.'))
        self.assertEquals(chronoTrigger[GameView.COL_genre], 'Role-Playing')
        self.assertEquals(chronoTrigger[GameView.COL_maxPlayers], '1')
        self.assertEquals(chronoTrigger[GameView.COL_publisher], 'Squaresoft')
        self.assertEquals(chronoTrigger[GameView.COL_developer], 'Squaresoft')
        roms = File(self.gdb).getRomsByGameId(chronoTrigger[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

        maddennfl = games[1]
        self.assertEquals(maddennfl[GameView.COL_NAME], 'Madden NFL 97')
        self.assertEquals(maddennfl[GameView.COL_year], '1996')
        self.assertTrue(
            maddennfl[GameView.COL_description].startswith(
                'Welcome to Madden NFL 97, the game that captures the excitement of a 30 yard touchdown pass'))
        self.assertEquals(maddennfl[GameView.COL_genre], 'Sports')
        self.assertEquals(maddennfl[GameView.COL_maxPlayers], '2')
        self.assertEquals(maddennfl[GameView.COL_publisher], 'Electronic Arts')
        self.assertEquals(maddennfl[GameView.COL_developer], 'Electronic Arts')
        roms = File(self.gdb).getRomsByGameId(maddennfl[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

    def test_import_initial_prefer_nfo(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')

        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'testdata', 'nfo', 'Amiga', 'Airborne Ranger_orig.nfo'),
                        os.path.join(os.path.dirname(__file__), 'testdata', 'roms', 'Amiga', 'Airborne Ranger.nfo'))
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'testdata', 'nfo', 'Amiga', 'Chuck Rock_orig.nfo'),
                        os.path.join(os.path.dirname(__file__), 'testdata', 'roms', 'Amiga', 'Chuck Rock.nfo'))
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'testdata', 'nfo', 'Amiga', 'Eliminator_orig.nfo'),
                        os.path.join(os.path.dirname(__file__), 'testdata', 'roms', 'Amiga', 'Eliminator.nfo'))
        shutil.copyfile(os.path.join(os.path.dirname(__file__), 'testdata', 'nfo', 'Amiga',
                                     'MicroProse Formula One Grand Prix_orig.nfo'),
                        os.path.join(os.path.dirname(__file__), 'testdata', 'roms', 'Amiga',
                                     'MicroProse Formula One Grand Prix.nfo'))

        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[1] = conf.romCollections['1']

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = ''
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'true'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = GameView(self.gdb).getFilteredGames(1, 0, 0, 0, 0, 0, 0, 0, 0, likeStmnt, '', 0)

        self.assertEquals(len(games), 4)

        airborneRanger = games[0]
        self.assertEquals(airborneRanger[GameView.COL_NAME], 'Airborne Ranger nfo')
        self.assertEquals(airborneRanger[GameView.COL_year], '1989')
        self.assertTrue(airborneRanger[GameView.COL_description].startswith(
            'Description with some special characters:'))
        self.assertEquals(airborneRanger[GameView.COL_genre], 'Action, Adventure')
        self.assertEquals(airborneRanger[GameView.COL_publisher], 'MicroProse')
        self.assertEquals(airborneRanger[GameView.COL_developer], 'Imagitec')
        roms = File(self.gdb).getRomsByGameId(airborneRanger[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

        chuckRock = games[1]
        self.assertEquals(chuckRock[GameView.COL_NAME], 'Chuck Rock nfo')
        self.assertEquals(chuckRock[GameView.COL_year], '1991')
        self.assertTrue(chuckRock[GameView.COL_description].startswith(
            "nfo: Chuck Rock hasn't been the same since his long-time rival in love, the evil Gary Gritter, kidnapped his wife, the beautiful Ophelia."))
        self.assertEquals(chuckRock[GameView.COL_genre], 'Platform')
        self.assertEquals(chuckRock[GameView.COL_publisher], 'Core Design nfo')
        self.assertEquals(chuckRock[GameView.COL_developer], 'Core Design nfo')
        self.assertEquals(chuckRock[GameView.COL_maxPlayers], '1')
        self.assertEquals(chuckRock[GameView.COL_rating], '8')
        roms = File(self.gdb).getRomsByGameId(chuckRock[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

        eliminator = games[2]
        self.assertEquals(eliminator[GameView.COL_NAME], 'Eliminator nfo')
        self.assertEquals(eliminator[GameView.COL_year], None)
        roms = File(self.gdb).getRomsByGameId(eliminator[GameView.COL_ID])
        self.assertEquals(len(roms), 1)

        formulaOne = games[3]
        self.assertEquals(formulaOne[GameView.COL_NAME], 'MicroProse Formula One Grand Prix nfo')
        self.assertEquals(formulaOne[GameView.COL_year], '1991')
        self.assertTrue(formulaOne[GameView.COL_description].startswith(
            "MicroProse Formula One Grand Prix is a racing simulator released in 1991 by MicroProse and created by game designer Geoff Crammond."))
        # HACK: Order of genres depends on id in database. If we run the full set of tests Genre Sports might already be
        # in database and has a lower id than Racing
        self.assertTrue(
            formulaOne[GameView.COL_genre] == 'Racing, Sports' or formulaOne[GameView.COL_genre] == 'Sports, Racing')
        self.assertEquals(formulaOne[GameView.COL_publisher], 'MicroProse')
        self.assertEquals(formulaOne[GameView.COL_developer], None)
        self.assertEquals(formulaOne[GameView.COL_maxPlayers], '1')
        roms = File(self.gdb).getRomsByGameId(formulaOne[GameView.COL_ID])
        self.assertEquals(len(roms), 4)

    def test_import_initial_offline_gdbi(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[2] = conf.romCollections['2']

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = ''
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = GameView(self.gdb).getFilteredGames(2, 0, 0, 0, 0, 0, 0, 0, 0, likeStmnt, '', 0)

        self.assertEquals(len(games), 4)

        adventure = games[0]
        self.assertEquals(adventure[GameView.COL_NAME], 'Adventure')
        self.assertEquals(adventure[GameView.COL_year], '1980')
        self.assertEquals(adventure[GameView.COL_publisher], 'Atari, Inc.')
        self.assertEquals(adventure[GameView.COL_developer], 'Atari, Inc.')
        self.assertEquals(adventure[GameView.COL_genre], 'Adventure')
        self.assertEquals(adventure[GameView.COL_rating], '3.8')
        self.assertEquals(adventure[GameView.COL_maxPlayers], '1 Player')
        self.assertTrue(adventure[GameView.COL_description].startswith(
            'A graphic dungeon quest inspired by the old mainframe game of the same name'))

        airSeaBattle = games[1]
        self.assertEquals(airSeaBattle[GameView.COL_NAME], 'Air-Sea Battle')
        self.assertEquals(airSeaBattle[GameView.COL_year], '1977')
        self.assertEquals(airSeaBattle[GameView.COL_publisher], 'Sears, Roebuck and Co.')
        self.assertEquals(airSeaBattle[GameView.COL_developer], 'Atari, Inc.')
        self.assertEquals(airSeaBattle[GameView.COL_genre], 'Shooter')
        self.assertEquals(airSeaBattle[GameView.COL_rating], '2.4')
        self.assertEquals(airSeaBattle[GameView.COL_maxPlayers], '1-2 Players')
        self.assertTrue(
            airSeaBattle[GameView.COL_description].startswith('Air-Sea Battle is basically a target shooting game.'))

        asteroids = games[2]
        self.assertEquals(asteroids[GameView.COL_NAME], 'Asteroids')
        self.assertEquals(asteroids[GameView.COL_year], '1981')
        self.assertEquals(asteroids[GameView.COL_publisher], 'Atari, Inc.')
        self.assertEquals(asteroids[GameView.COL_developer], 'Atari, Inc.')
        self.assertEquals(asteroids[GameView.COL_genre], 'Shooter')
        self.assertEquals(asteroids[GameView.COL_rating], '3.5')
        self.assertEquals(asteroids[GameView.COL_maxPlayers], '1-2 Players')
        self.assertTrue(
            asteroids[GameView.COL_description].startswith(
                'Asteroids is a conversion of the arcade game of the same name.'))

    def register_responses(self):
        """
        Note: As responses does not check for url params the order of the responses.add-statements is important.
        """
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Developers?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73',
                      body=self.loadXmlFromFile('thegamesdb_Developers.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Publishers?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73',
                      body=self.loadXmlFromFile('thegamesdb_Publishers.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Genres?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73',
                      body=self.loadXmlFromFile('thegamesdb_Genres.json'),
                      status=200)

    def register_responses_Amiga(self):
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=4911&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Airborne+Ranger&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Airborne Ranger_search.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/Images?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&games_id=24471',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Airborne Ranger_images.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=4911&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Chuck+Rock&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Chuck Rock_search.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/Images?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&games_id=35508',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Chuck Rock_images.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=4911&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Eliminator&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Eliminator_search.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/Images?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&games_id=35508',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Eliminator_images.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=4911&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=MicroProse+Formula+One+Grand+Prix&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Formula One Grand Prix_search.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/Images?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&games_id=43812',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Formula One Grand Prix_images.json'),
                      status=200)

    """
    def register_responses_Atari(self):

        responses.add(responses.GET, 
                'http://legacy.thegamesdb.net/api/GetGamesList.php?platform=Atari+2600&name=Adventure+%281980%29+%28Atari%29',
                body=self.loadXmlFromFile('thegamesdb_Atari_Adventure_search.xml'), 
                status=200)

        responses.add(responses.GET, 
                'http://legacy.thegamesdb.net/api/GetGame.php?id=2570',
                body=self.loadXmlFromFile('thegamesdb_Atari_Adventure_result.xml'), 
                status=200)

        responses.add(responses.GET, 
                'http://legacy.thegamesdb.net/api/GetGamesList.php?platform=Atari+2600&name=Air-Sea+Battle+%2832+in+1%29+%281988%29+%28Atari%29+%28PAL%29',
                body=self.loadXmlFromFile('thegamesdb_Atari_Air-Sea Battle_search.xml'), 
                status=200)

        responses.add(responses.GET, 
                'http://legacy.thegamesdb.net/api/GetGame.php?id=5296',
                body=self.loadXmlFromFile('thegamesdb_Atari_Air-Sea Battle_result.xml'), 
                status=200)

        responses.add(responses.GET, 
                'http://legacy.thegamesdb.net/api/GetGamesList.php?platform=Atari+2600&name=Air-Sea+Battle+%2832+in+1%29+%281988%29+%28Atari%29+%28PAL%29',
                body=self.loadXmlFromFile('thegamesdb_Atari_Asteroids_search.xml'), 
                status=200)

        responses.add(responses.GET, 
                'http://legacy.thegamesdb.net/api/GetGame.php?id=1342',
                body=self.loadXmlFromFile('thegamesdb_Atari_Asteroids_result.xml'), 
                status=200)

        responses.add(responses.GET, 
                'http://legacy.thegamesdb.net/api/GetGamesList.php?platform=Atari+2600&name=Unknown',
                body=self.loadXmlFromFile('thegamesdb_Atari_Unknown_search.xml'), 
                status=200)
    """
    def register_responses_N64(self):
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=3&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=1080%C2%B0+Snowboarding&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      body=self.loadXmlFromFile('thegamesdb_N64_1080 Snowboarding_search.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/Images?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&games_id=237',
                      body=self.loadXmlFromFile('thegamesdb_N64_1080 Snowboarding_images.json'),
                      status=200)

    def register_responses_PSX(self):
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Bushido+Blade&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      body=self.loadXmlFromFile('thegamesdb_PSX_Bushido Blade_search.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/Images?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&games_id=8375',
                      body=self.loadXmlFromFile('thegamesdb_PSX_Bushido Blade_images.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=10&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Silent+Hill&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      body=self.loadXmlFromFile('thegamesdb_PSX_Silent Hill_search.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/Images?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&games_id=1014',
                      body=self.loadXmlFromFile('thegamesdb_PSX_Silent Hill_images.json'),
                      status=200)

    def register_responses_SNES(self):
        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=6&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Chrono+Trigger&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      body=self.loadXmlFromFile('thegamesdb_SNES_Chrono Trigger_search.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/Images?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&games_id=1255',
                      body=self.loadXmlFromFile('thegamesdb_SNES_Chrono Trigger_images.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/ByGameName?filter%5Bplatform%5D=6&apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&include=boxart&name=Madden+NFL&fields=id%2Cgame_title%2Crelease_date%2Cdevelopers%2Cpublishers%2Cplayers%2Cgenres%2Coverview%2Crating',
                      body=self.loadXmlFromFile('thegamesdb_SNES_Madden NFL 97_search.json'),
                      status=200)

        responses.add(responses.GET,
                      'https://api.thegamesdb.net/v1/Games/Images?apikey=1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73&games_id=291',
                      body=self.loadXmlFromFile('thegamesdb_SNES_Madden NFL 97_images.json'),
                      status=200)

    def loadXmlFromFile(self, filename):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'importtests', filename)

        with open(f) as xmlfile:
            data = xmlfile.read()

        return data


if __name__ == "__main__":
    unittest.main()
