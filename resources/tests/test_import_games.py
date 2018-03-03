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
        # Load a config file with 2 valid RomCollections
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_importtests.xml')
        conf = Config(config_xml_file)
        conf.readXml()
        
        rcs = {}
        rcs[1] = conf.romCollections['1']
        
        self.register_responses()
        
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

    
    def register_responses(self):
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
        
        
    def loadXmlFromFile(self, filename):
        f = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata',
                         'scraper_web_responses', 'importtests', filename)        

        with open(f) as xmlfile:
            data = xmlfile.read()
        
        return data


if __name__ == "__main__":
    unittest.main()
