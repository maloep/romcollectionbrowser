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
        shutil.copyfile(os.path.join(db_path, 'MyGames_2.2.0_empty.db'), os.path.join(db_path, 'MyGames.db'))

        cls.gdb = GameDataBase(db_path)
        cls.gdb.connect()
        

    @responses.activate
    def test_import_initial_accurate_gameswithoutdesc(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()
        
        rcs = {}
        rcs[1] = conf.romCollections['1']
        
        self.register_responses_Amiga()
        
        #adjust settings        
        xbmcaddon._settings['rcb_createNfoWhileScraping'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'false'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Accurate'
        
        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)
        
        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(1, 0, 0, 0, 0, likeStmnt)
        
        self.assertEquals(len(games), 4)
        
        airborneRanger = games[0]
        self.assertEquals(airborneRanger.name, 'Airborne Ranger')
        self.assertEquals(airborneRanger.year, '1989')
        self.assertTrue(airborneRanger.plot.startswith('In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger.'))
        self.assertEquals(airborneRanger.genre, 'Action, Adventure')
        self.assertEquals(airborneRanger.publisher, 'MicroProse')
        self.assertEquals(airborneRanger.developer, 'Imagitec')
        self.assertEquals(airborneRanger.maxPlayers, '1')
        roms = File(self.gdb).getRomsByGameId(airborneRanger.id)
        self.assertEquals(len(roms), 1)
        
        chuckRock = games[1]
        self.assertEquals(chuckRock.name, 'Chuck Rock')
        self.assertEquals(chuckRock.year, '1991')
        self.assertTrue(chuckRock.plot.startswith("Chuck Rock hasn't been the same since his long-time rival in love, the evil Gary Gritter, kidnapped his wife, the beautiful Ophelia."))
        self.assertEquals(chuckRock.genre, 'Platform')
        self.assertEquals(chuckRock.publisher, 'Core Design')
        self.assertEquals(chuckRock.developer, 'Core Design')
        self.assertEquals(chuckRock.maxPlayers, '1')
        self.assertEquals(chuckRock.rating, '8')
        roms = File(self.gdb).getRomsByGameId(chuckRock.id)
        self.assertEquals(len(roms), 1)
        
        eliminator = games[2]
        self.assertEquals(eliminator.name, 'Eliminator')
        self.assertEquals(eliminator.year, None)
        roms = File(self.gdb).getRomsByGameId(eliminator.id)
        self.assertEquals(len(roms), 1)
        
        formulaOne = games[3]
        self.assertEquals(formulaOne.name, 'MicroProse Formula One Grand Prix')
        self.assertEquals(formulaOne.year, '1991')
        self.assertTrue(formulaOne.plot.startswith("MicroProse Formula One Grand Prix is a racing simulator released in 1991 by MicroProse and created by game designer Geoff Crammond."))
        self.assertEquals(formulaOne.genre, 'Racing, Sports')
        self.assertEquals(formulaOne.publisher, 'MicroProse')
        self.assertEquals(formulaOne.developer, None)
        self.assertEquals(formulaOne.maxPlayers, '1')
        roms = File(self.gdb).getRomsByGameId(formulaOne.id)
        self.assertEquals(len(roms), 4)
        
    
    @responses.activate
    def test_import_initial_guessmatches_nogameswithoutdesc(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()
        
        rcs = {}
        rcs[2] = conf.romCollections['2']
        
        self.register_responses_Atari()
        
        #adjust settings        
        xbmcaddon._settings['rcb_createNfoWhileScraping'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'true'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Guess Matches'
        
        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)
        
        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(2, 0, 0, 0, 0, likeStmnt)
        
        self.assertEquals(len(games), 3)
        
        adventure = games[0]
        self.assertEquals(adventure.name, 'Adventure')
        self.assertEquals(adventure.year, '1978')
        self.assertTrue(adventure.plot.startswith('Adventure was the first action-adventure game on a video console'))
        self.assertEquals(adventure.genre, 'Adventure')
        self.assertEquals(adventure.publisher, 'Atari')
        self.assertEquals(adventure.developer, 'Atari')
        roms = File(self.gdb).getRomsByGameId(adventure.id)
        self.assertEquals(len(roms), 1)
        
        airSeaBattle = games[1]
        self.assertEquals(airSeaBattle.name, 'Air-Sea Battle (Target Fun)')
        self.assertEquals(airSeaBattle.year, '1978')
        self.assertTrue(airSeaBattle.plot.startswith('There are six basic types of game available in Air-Sea Battle'))
        self.assertEquals(airSeaBattle.genre, 'Action')
        self.assertEquals(airSeaBattle.maxPlayers, '2')
        self.assertEquals(airSeaBattle.publisher, 'Atari')
        self.assertEquals(airSeaBattle.developer, 'Atari')
        roms = File(self.gdb).getRomsByGameId(airSeaBattle.id)
        self.assertEquals(len(roms), 1)
        
        asteroids = games[2]
        self.assertEquals(asteroids.name, 'Asteroids')
        self.assertEquals(asteroids.year, '1979')
        self.assertTrue(asteroids.plot.startswith('The objective of Asteroids is to score as many points'))
        self.assertEquals(asteroids.genre, 'Shooter')
        self.assertEquals(asteroids.maxPlayers, '2')
        self.assertEquals(asteroids.publisher, 'Atari')
        self.assertEquals(asteroids.developer, 'Atari')
        roms = File(self.gdb).getRomsByGameId(asteroids.id)
        self.assertEquals(len(roms), 1)
        
    
    @responses.activate
    def test_import_initial_special_characters(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()
        
        rcs = {}
        rcs[3] = conf.romCollections['3']
        
        self.register_responses_N64()
        
        #adjust settings        
        xbmcaddon._settings['rcb_createNfoWhileScraping'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'true'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Guess Matches'
        
        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)
        
        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(3, 0, 0, 0, 0, likeStmnt)
        
        self.assertEquals(len(games), 1)
        snowboarding = games[0]
        self.assertEquals(snowboarding.name, '1080 Snowboarding')
        #TODO check for description with special characters
        #self.assertTrue(snowboarding.plot.startswith(u"You’re taking a Tahoe 155 snowboard down a steep, bumpy incline at night and you’re about to top off an Indy Nosebone with a 360° Air"))
        self.assertEquals(snowboarding.year, '1998')
        self.assertEquals(snowboarding.genre, 'Sports')
        self.assertEquals(snowboarding.publisher, 'Nintendo')
        self.assertEquals(snowboarding.developer, 'Nintendo EAD')
        roms = File(self.gdb).getRomsByGameId(snowboarding.id)
        self.assertEquals(len(roms), 1)

    @responses.activate
    def test_import_multirompath_multidisc(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcs = {}
        rcs[4] = conf.romCollections['4']

        self.register_responses_PSX()

        # adjust settings
        xbmcaddon._settings['rcb_createNfoWhileScraping'] = 'false'
        xbmcaddon._settings['rcb_ignoreGamesWithoutDesc'] = 'true'
        xbmcaddon._settings['rcb_scrapingMode'] = 'Automatic: Guess Matches'

        dbu = DBUpdate()
        dbu.updateDB(self.gdb, RCBMockGui(), rcs, False)

        likeStmnt = '0 = 0'
        games = Game(self.gdb).getGamesByFilter(4, 0, 0, 0, 0, likeStmnt)

        self.assertEquals(len(games), 2)

        bushido = games[0]
        self.assertEquals(bushido.name, 'Bushido Blade')
        self.assertEquals(bushido.year, '1997')
        self.assertTrue(bushido.plot.startswith('"Bushido" is the soul of Japan - an ancient honor code deeply followed by samurai warriors for centuries'))
        self.assertEquals(bushido.genre, 'Fighting')
        self.assertEquals(bushido.maxPlayers, '2')
        self.assertEquals(bushido.publisher, 'Square, SCEA')
        self.assertEquals(bushido.developer, 'Light Weight')
        roms = File(self.gdb).getRomsByGameId(bushido.id)
        self.assertEquals(len(roms), 1)

        silenthill = games[1]
        self.assertEquals(silenthill.name, 'Silent Hill')
        self.assertEquals(silenthill.year, '1999')
        self.assertTrue(silenthill.plot.startswith('Silent Hill is a 1999 survival horror video game for the PlayStation.'))
        self.assertEquals(silenthill.genre, 'Action, Horror')
        self.assertEquals(silenthill.maxPlayers, '1')
        self.assertEquals(silenthill.publisher, 'Konami Digital Entertainment')
        self.assertEquals(silenthill.developer, 'Team Silent, Konami')
        roms = File(self.gdb).getRomsByGameId(silenthill.id)
        self.assertEquals(len(roms), 2)

    
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
        
        
    def register_responses_Atari(self):
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Atari+2600&name=Adventure+%281980%29+%28Atari%29',
                body=self.loadXmlFromFile('thegamesdb_Atari_Adventure_search.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGame.php?id=2570',
                body=self.loadXmlFromFile('thegamesdb_Atari_Adventure_result.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Atari+2600&name=Air-Sea+Battle+%2832+in+1%29+%281988%29+%28Atari%29+%28PAL%29',
                body=self.loadXmlFromFile('thegamesdb_Atari_Air-Sea Battle_search.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGame.php?id=5296',
                body=self.loadXmlFromFile('thegamesdb_Atari_Air-Sea Battle_result.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Atari+2600&name=Air-Sea+Battle+%2832+in+1%29+%281988%29+%28Atari%29+%28PAL%29',
                body=self.loadXmlFromFile('thegamesdb_Atari_Asteroids_search.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGame.php?id=1342',
                body=self.loadXmlFromFile('thegamesdb_Atari_Asteroids_result.xml'), 
                status=200)
        
        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Atari+2600&name=Unknown',
                body=self.loadXmlFromFile('thegamesdb_Atari_Unknown_search.xml'), 
                status=200)
        
        
    def register_responses_N64(self):

        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Nintendo+64&name=1080%C2%B0+Snowboarding',
                body=self.loadXmlFromFile('thegamesdb_N64_1080 Snowboarding_search.xml'),
                status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGame.php?id=237',
                      body=self.loadXmlFromFile('thegamesdb_N64_1080 Snowboarding_result.xml'),
                      status=200)

    def register_responses_PSX(self):

        responses.add(responses.GET, 
                'http://thegamesdb.net/api/GetGamesList.php?platform=Sony+Playstation&name=Bushido+Blade',
                body=self.loadXmlFromFile('thegamesdb_PSX_Bushido Blade_search.xml'),
                status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGame.php?id=8375',
                      body=self.loadXmlFromFile('thegamesdb_PSX_Bushido Blade_result.xml'),
                      status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGamesList.php?platform=Sony+Playstation&name=Silent+Hill+%28Disc+1+of+2%29',
                      body=self.loadXmlFromFile('thegamesdb_PSX_Silent Hill_search.xml'),
                      status=200)

        responses.add(responses.GET,
                      'http://thegamesdb.net/api/GetGame.php?id=1014',
                      body=self.loadXmlFromFile('thegamesdb_PSX_Silent Hill_result.xml'),
                      status=200)

        
        
    def loadXmlFromFile(self, filename):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'importtests', filename)        

        with open(f) as xmlfile:
            data = xmlfile.read()
        
        return data


if __name__ == "__main__":
    unittest.main()
