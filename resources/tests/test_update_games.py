# coding=utf-8
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
from gamedatabase import GameDataBase, Game, gameobj, File

import xbmcaddon

class RCBMockGui:

    itemCount = 0

    def writeMsg(self, msg1, msg2, msg3, count=0):
        return True


class TestUpdateGames(unittest.TestCase):
    """
    This unittest class is used for testing the complete scrape and import process
    """
    
    gdb = None
    
    @classmethod
    def get_testdata_path(cls):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata')

    @classmethod
    def setUp(cls):
        # This is required so that readScraper() can parse the XML instruction files
        util.RCBHOME = os.path.join(os.path.dirname(__file__), '..', '..')
        
        # Open the DB
        db_path = os.path.join(cls.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        shutil.copyfile(os.path.join(db_path, 'MyGames_2.2.0_full.db'), os.path.join(db_path, 'MyGames.db'))

        cls.gdb = GameDataBase(db_path)
        cls.gdb.connect()

    @classmethod
    def tearDown(cls):
        # Cleanup
        cls.gdb.close()
        os.remove(os.path.join(os.path.join(cls.get_testdata_path(), 'database'), 'MyGames.db'))


    @responses.activate
    def test_update_rescrape(self):
        """test if update a rom collection works at all: all properties should have been updated"""
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()
        
        rcs = {}
        rcs[1] = conf.romCollections['1']
        
        self.register_responses_Amiga()
        
        #adjust settings        
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'
        xbmcaddon._settings['rcb_enableFullReimport'] = 'true'
        xbmcaddon._settings['rcb_overwriteWithNullvalues'] = 'false'
        
        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)
        
        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(1, 0, 0, 0, 0, likeStmnt)
        
        self.assertEquals(len(games), 4)
        
        airborneRanger = games[0]
        self.assertEquals(airborneRanger.name, 'Airborne Ranger Update')
        self.assertEquals(airborneRanger.year, '1990')
        self.assertTrue(airborneRanger.plot.startswith('Update: In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger.'))
        self.assertEquals(airborneRanger.genre, 'Action, Adventure, Update')
        self.assertEquals(airborneRanger.publisher, 'MicroProse (Update)')
        self.assertEquals(airborneRanger.developer, 'Imagitec (Update)')
        self.assertEquals(airborneRanger.maxPlayers, '2')
        roms = File(self.gdb).getRomsByGameId(airborneRanger.id)
        self.assertEquals(len(roms), 1)


    @responses.activate
    def test_update_rescrape_nonullvalues(self):
        """test if update works when rcb_overwriteWithNullvalues is set to false"""
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[1] = conf.romCollections['1']

        self.register_responses_Amiga_nullvalues()

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'
        xbmcaddon._settings['rcb_enableFullReimport'] = 'true'
        xbmcaddon._settings['rcb_overwriteWithNullvalues'] = 'false'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(1, 0, 0, 0, 0, likeStmnt)

        self.assertEquals(len(games), 4)

        airborneRanger = games[0]
        self.assertEquals(airborneRanger.name, 'Airborne Ranger Update')
        self.assertEquals(airborneRanger.year, '1989')
        self.assertTrue(airborneRanger.plot.startswith(
            'In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger.'))
        self.assertEquals(airborneRanger.genre, 'Action, Adventure')
        self.assertEquals(airborneRanger.publisher, 'MicroProse')
        self.assertEquals(airborneRanger.developer, 'Imagitec')
        self.assertEquals(airborneRanger.maxPlayers, '1')
        roms = File(self.gdb).getRomsByGameId(airborneRanger.id)
        self.assertEquals(len(roms), 1)

    @responses.activate
    def test_update_rescrape_nullvalues(self):
        """test if update works when rcb_overwriteWithNullvalues is set to true"""
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[1] = conf.romCollections['1']

        self.register_responses_Amiga_nullvalues()

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'
        xbmcaddon._settings['rcb_enableFullReimport'] = 'true'
        xbmcaddon._settings['rcb_overwriteWithNullvalues'] = 'true'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(1, 0, 0, 0, 0, likeStmnt)

        self.assertEquals(len(games), 4)

        airborneRanger = games[0]
        self.assertEquals(airborneRanger.name, 'Airborne Ranger Update')
        self.assertEquals(airborneRanger.year, None)
        self.assertEquals(airborneRanger.plot, '')
        #HACK: genres are stored in genregame link table and are not overwritten with null values
        self.assertEquals(airborneRanger.genre, 'Action, Adventure')
        self.assertEquals(airborneRanger.publisher, None)
        self.assertEquals(airborneRanger.developer, None)
        self.assertEquals(airborneRanger.maxPlayers, '')
        roms = File(self.gdb).getRomsByGameId(airborneRanger.id)
        self.assertEquals(len(roms), 1)


    @responses.activate
    def test_update_norescrape_addonsettings(self):
        """test if update is skipped when rcb_enableFullReimport is set to false"""
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[1] = conf.romCollections['1']

        self.register_responses_Amiga_nullvalues()

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'
        xbmcaddon._settings['rcb_enableFullReimport'] = 'false'
        xbmcaddon._settings['rcb_overwriteWithNullvalues'] = 'true'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(1, 0, 0, 0, 0, likeStmnt)

        self.assertEquals(len(games), 4)
        airborneRanger = games[0]
        self.assertEquals(airborneRanger.name, 'Airborne Ranger')
        self.assertEquals(airborneRanger.year, '1989')
        self.assertTrue(airborneRanger.plot.startswith(
            'In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger.'))
        self.assertEquals(airborneRanger.genre, 'Action, Adventure')
        self.assertEquals(airborneRanger.publisher, 'MicroProse')
        self.assertEquals(airborneRanger.developer, 'Imagitec')
        self.assertEquals(airborneRanger.maxPlayers, '1')
        roms = File(self.gdb).getRomsByGameId(airborneRanger.id)
        self.assertEquals(len(roms), 1)


    @responses.activate
    def test_update_norescrape_config_ignoreonscan(self):
        """test if update is skipped when ignoreonscan is set to true in config.xml"""
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_ignoreonscan.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[1] = conf.romCollections['1']

        self.register_responses_Amiga_nullvalues()

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'
        xbmcaddon._settings['rcb_enableFullReimport'] = 'true'
        xbmcaddon._settings['rcb_overwriteWithNullvalues'] = 'true'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(1, 0, 0, 0, 0, likeStmnt)

        self.assertEquals(len(games), 4)
        airborneRanger = games[0]
        self.assertEquals(airborneRanger.name, 'Airborne Ranger')
        self.assertEquals(airborneRanger.year, '1989')
        self.assertTrue(airborneRanger.plot.startswith(
            'In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger.'))
        self.assertEquals(airborneRanger.genre, 'Action, Adventure')
        self.assertEquals(airborneRanger.publisher, 'MicroProse')
        self.assertEquals(airborneRanger.developer, 'Imagitec')
        self.assertEquals(airborneRanger.maxPlayers, '1')
        roms = File(self.gdb).getRomsByGameId(airborneRanger.id)
        self.assertEquals(len(roms), 1)

    @responses.activate
    def test_update_norescrape_config_allowupdate(self):
        """test if update is skipped when allowupdate is set to false in config.xml"""
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_allowupdate.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[1] = conf.romCollections['1']

        self.register_responses_Amiga_nullvalues()

        # adjust settings
        xbmcaddon._settings['rcb_nfoFolder'] = './script.games.rom.collection.browser/nfo/'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_PreferNfoFileIfAvailable'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'
        xbmcaddon._settings['rcb_enableFullReimport'] = 'true'
        xbmcaddon._settings['rcb_overwriteWithNullvalues'] = 'true'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(1, 0, 0, 0, 0, likeStmnt)

        self.assertEquals(len(games), 4)
        airborneRanger = games[0]
        self.assertEquals(airborneRanger.name, 'Airborne Ranger')
        self.assertEquals(airborneRanger.year, '1989')
        self.assertTrue(airborneRanger.plot.startswith(
            'In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger.'))
        self.assertEquals(airborneRanger.genre, 'Action, Adventure')
        self.assertEquals(airborneRanger.publisher, 'MicroProse')
        self.assertEquals(airborneRanger.developer, 'Imagitec')
        self.assertEquals(airborneRanger.maxPlayers, '1')
        roms = File(self.gdb).getRomsByGameId(airborneRanger.id)
        self.assertEquals(len(roms), 1)


    def register_responses_Amiga(self):
        
        """
        Note: As responses does not check for url params the order of the responses.add-statements is important.
        """
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Amiga&name=Airborne+Ranger',
                body=self.loadXmlFromFile('thegamesdb_Amiga_Airborne Ranger_search.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGame.php?id=24471',
                body=self.loadXmlFromFile('thegamesdb_Amiga_Airborne Ranger_result.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Amiga&name=Chuck+Rock',
                body=self.loadXmlFromFile('thegamesdb_Amiga_Chuck Rock_search.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGame.php?id=35508',
                body=self.loadXmlFromFile('thegamesdb_Amiga_Chuck Rock_result.xml'),
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Amiga&name=Eliminator',
                body=self.loadXmlFromFile('thegamesdb_Amiga_Eliminator_search.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Amiga&name=Formula+One+Grand+Prix',
                body=self.loadXmlFromFile('thegamesdb_Amiga_Formula One Grand Prix_search.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGame.php?id=43812',
                body=self.loadXmlFromFile('thegamesdb_Amiga_Formula One Grand Prix_result.xml'),
                status=200)


    def register_responses_Amiga_nullvalues(self):
        """
        Note: As responses does not check for url params the order of the responses.add-statements is important.
        """

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGamesList.php?platform=Amiga&name=Airborne+Ranger',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Airborne Ranger_search.xml'),
                      status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGame.php?id=24471',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Airborne Ranger_result_nullvalues.xml'),
                      status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGamesList.php?platform=Amiga&name=Chuck+Rock',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Chuck Rock_search.xml'),
                      status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGame.php?id=35508',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Chuck Rock_result.xml'),
                      status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGamesList.php?platform=Amiga&name=Eliminator',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Eliminator_search.xml'),
                      status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGamesList.php?platform=Amiga&name=Formula+One+Grand+Prix',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Formula One Grand Prix_search.xml'),
                      status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGame.php?id=43812',
                      body=self.loadXmlFromFile('thegamesdb_Amiga_Formula One Grand Prix_result.xml'),
                      status=200)


    def loadXmlFromFile(self, filename):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'updatetests', filename)

        with open(f) as xmlfile:
            data = xmlfile.read()
        
        return data


if __name__ == "__main__":
    unittest.main()
