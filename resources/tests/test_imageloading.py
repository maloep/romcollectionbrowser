
from builtins import filter
from builtins import str
from builtins import object
import os, sys, re, time, shutil
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

from gamedatabase import GameDataBase, GameView
from artworkupdater import ArtworkUpdater


import helper
from config import Config, RomCollection

class RCBMockGui(object):
    itemCount = 0
    def writeMsg(self, msg1, msg2, count=0):
        return True

class Test(unittest.TestCase):

    @classmethod
    def get_testdata_path(cls):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata')

    @classmethod
    def setUp(cls):
        # Open the DB
        db_path = os.path.join(cls.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        shutil.copyfile(os.path.join(db_path, 'MyGames_current_12_games.db'), os.path.join(db_path, 'MyGames.db'))

        cls.gdb = GameDataBase(db_path)
        cls.gdb.connect()

    @classmethod
    def tearDown(cls):
        # Cleanup
        cls.gdb.close()
        os.remove(os.path.join(os.path.join(cls.get_testdata_path(), 'database'), 'MyGames.db'))


    def test_cache_artwork_1_rom_collection_1_artworktype_add_artwork(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        # image should be missing at start
        game = GameView(self.gdb).getGameById(5)
        self.assertIsNone(game[GameView.COL_fileType1], "fileType1 expected to be missing before update artwork cache")

        rcid = 1
        artwork_type = 1

        ArtworkUpdater(RCBMockGui(), self.gdb, conf).update_artwork_cache(rcid, artwork_type)

        # image should be available now
        game = GameView(self.gdb).getGameById(5)
        self.assertEquals("./testdata/artwork/Amiga/boxfront/Eliminator.png", game[GameView.COL_fileType1])

    def test_cache_artwork_1_rom_collection_1_artworktype_remove_artwork(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        # image should be present at start
        game = GameView(self.gdb).getGameById(9)
        self.assertIsNotNone(game[GameView.COL_fileType4], "fileType4 expected to be present before update artwork cache")

        rcid = 2
        artwork_type = 4

        ArtworkUpdater(RCBMockGui(), self.gdb, conf).update_artwork_cache(rcid, artwork_type)

        # image should be removed now
        game = GameView(self.gdb).getGameById(9)
        self.assertIsNone(game[GameView.COL_fileType4], "fileType4 expected to be removed after update artwork cache")
        #other artwork types should be unchanged
        self.assertEquals("./testdata/artwork/Atari 2600/video/Asteroids (1981) (Atari) [no copyright].png",
                          game[GameView.COL_fileType6])
        #available artwork should still be present
        game = GameView(self.gdb).getGameById(7)
        self.assertEquals("./testdata/artwork/Atari 2600/screenshot/Adventure (1980) (Atari).jpg",
                          game[GameView.COL_fileType4])
        game = GameView(self.gdb).getGameById(8)
        self.assertEquals("./testdata/artwork/Atari 2600/screenshot/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).gif",
                          game[GameView.COL_fileType4])

    def test_cache_artwork_1_rom_collection_n_artworktypes_add_artwork(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        # image should be missing at start
        game = GameView(self.gdb).getGameById(5)
        self.assertIsNone(game[GameView.COL_fileType1], "fileType1 expected to be missing before update artwork cache")
        self.assertIsNone(game[GameView.COL_fileType4], "fileType1 expected to be missing before update artwork cache")

        rcid = 1
        artwork_type = 0

        ArtworkUpdater(RCBMockGui(), self.gdb, conf).update_artwork_cache(rcid, artwork_type)

        # image should be available now
        game = GameView(self.gdb).getGameById(5)
        self.assertEquals("./testdata/artwork/Amiga/boxfront/Eliminator.png", game[GameView.COL_fileType1])
        self.assertEquals("./testdata/artwork/Amiga/screenshot/Eliminator.png", game[GameView.COL_fileType4])

    def test_cache_artwork_n_rom_collections_n_artworktypes_add_remove_artwork(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        #check for correct startup values
        game = GameView(self.gdb).getGameById(5)
        self.assertIsNone(game[GameView.COL_fileType1], "fileType1 expected to be missing before update artwork cache")
        self.assertIsNone(game[GameView.COL_fileType4], "fileType4 expected to be missing before update artwork cache")
        game = GameView(self.gdb).getGameById(9)
        self.assertIsNotNone(game[GameView.COL_fileType4], "fileType4 expected to be present before update artwork cache")

        rcid = 0
        artwork_type = 0

        ArtworkUpdater(RCBMockGui(), self.gdb, conf).update_artwork_cache(rcid, artwork_type)

        # image should be available now
        game = GameView(self.gdb).getGameById(5)
        self.assertEquals("./testdata/artwork/Amiga/boxfront/Eliminator.png", game[GameView.COL_fileType1])
        self.assertEquals("./testdata/artwork/Amiga/screenshot/Eliminator.png", game[GameView.COL_fileType4])

        # image should be removed now
        game = GameView(self.gdb).getGameById(9)
        self.assertIsNone(game[GameView.COL_fileType4], "fileType4 expected to be removed after update artwork cache")
        self.assertIsNone(game[GameView.COL_fileType6], "fileType6 expected to be removed after update artwork cache")
        #available artwork should still be present
        game = GameView(self.gdb).getGameById(7)
        self.assertEquals("./testdata/artwork/Atari 2600/screenshot/Adventure (1980) (Atari).jpg",
                          game[GameView.COL_fileType4])
        game = GameView(self.gdb).getGameById(8)
        self.assertEquals("./testdata/artwork/Atari 2600/screenshot/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).gif",
                          game[GameView.COL_fileType4])



    @unittest.skip("to be reimplemented")
    def testCacheMediaPaths_1RomCollection(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcId = 1

        mediaDict = helper.cacheMediaPathsForSelection(rcId, None, conf)
        self.assertTrue(len(mediaDict) == 1, 'len(mediaDict) should have been 1 but was %i' %len(mediaDict))

        mediaPathsDict = mediaDict[str(rcId)]
        self.assertTrue(len(mediaPathsDict) == 3, 'len(mediaPathsDict) should have been 3 but was %i' %len(mediaPathsDict))
        self.assertTrue(len(mediaPathsDict['boxfront']) == 3, 'len(mediaPathsDict[boxfront]) should have been 3 but was %i' %len(mediaPathsDict['boxfront']))
        self.assertTrue(len(mediaPathsDict['screenshot']) == 2, 'len(mediaPathsDict[screenshot]) should have been 2 but was %i' %len(mediaPathsDict['screenshot']))
        self.assertTrue(len(mediaPathsDict['gameplay']) == 2, 'len(mediaPathsDict[gameplay]) should have been 2 but was %i' %len(mediaPathsDict['gameplay']))

        #FIXME TODO: this test might fail on non-Windows systems
        self.assertTrue(mediaPathsDict['boxfront'][0] == 'testdata\\artwork\\Atari 2600\\boxfront\\Adventure (1980) (Atari).png', 'wrong boxfront image in cache')
        self.assertTrue(mediaPathsDict['boxfront'][1] == 'testdata\\artwork\\Atari 2600\\boxfront\\Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).png', 'wrong boxfront image in cache')
        self.assertTrue(mediaPathsDict['boxfront'][2] == 'testdata\\artwork\\Atari 2600\\boxfront\\Asteroids (1981) (Atari) [no copyright].png', 'wrong boxfront image in cache')

        self.assertTrue(mediaPathsDict['screenshot'][0] == 'testdata\\artwork\\Atari 2600\\screenshot\\Adventure (1980) (Atari).jpg', 'wrong screenshot image in cache')
        self.assertTrue(mediaPathsDict['screenshot'][1] == 'testdata\\artwork\\Atari 2600\\screenshot\\Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).gif', 'wrong screenshot image in cache')

        self.assertTrue(mediaPathsDict['gameplay'][0] == 'testdata\\artwork\\Atari 2600\\video\\Adventure (1980) (Atari).wmv', 'wrong gameplay video in cache')
        self.assertTrue(mediaPathsDict['gameplay'][1] == 'testdata\\artwork\\Atari 2600\\video\\Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).mp4', 'wrong gameplay video in cache')

    @unittest.skip("to be reimplemented")
    def testCacheMediaPaths_1RomCollection_FoldernameAsGamename(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcId = 2

        mediaDict = helper.cacheMediaPathsForSelection(rcId, None, conf)
        self.assertTrue(len(mediaDict) == 1, 'len(mediaDict) should have been 1 but was %i' %len(mediaDict))

        mediaPathsDict = mediaDict[str(rcId)]

        self.assertTrue(len(mediaPathsDict) == 2, 'len(mediaPathsDict) should have been 2 but was %i' %len(mediaPathsDict))

        # with foldername as gamename option RCB adds all files inside the game folder to the dict. So it contains boxfront and screenshot files.
        self.assertTrue(len(mediaPathsDict['boxfront']) == 4, 'len(mediaPathsDict[boxfront]) should have been 2 but was %i' %len(mediaPathsDict['boxfront']))
        self.assertTrue(len(mediaPathsDict['screenshot']) == 4, 'len(mediaPathsDict[screenshot]) should have been 2 but was %i' %len(mediaPathsDict['screenshot']))

        self.assertTrue(mediaPathsDict['boxfront'][0] == 'testdata\\artwork\\SNES\\Chrono Trigger\\boxfront.png', 'wrong boxfront image in cache')
        self.assertTrue(mediaPathsDict['boxfront'][1] == 'testdata\\artwork\\SNES\\Chrono Trigger\\screenshot.png', 'wrong boxfront image in cache')
        self.assertTrue(mediaPathsDict['boxfront'][2] == "testdata\\artwork\\SNES\\Madden NFL '97\\boxfront.png", 'wrong boxfront image in cache')
        self.assertTrue(mediaPathsDict['boxfront'][3] == "testdata\\artwork\\SNES\\Madden NFL '97\\screenshot.png", 'wrong boxfront image in cache')

        self.assertTrue(mediaPathsDict['screenshot'][0] == 'testdata\\artwork\\SNES\\Chrono Trigger\\boxfront.png', 'wrong screenshot image in cache')
        self.assertTrue(mediaPathsDict['screenshot'][1] == 'testdata\\artwork\\SNES\\Chrono Trigger\\screenshot.png', 'wrong screenshot image in cache')
        self.assertTrue(mediaPathsDict['screenshot'][2] == "testdata\\artwork\\SNES\\Madden NFL '97\\boxfront.png", 'wrong screenshot image in cache')
        self.assertTrue(mediaPathsDict['screenshot'][3] == "testdata\\artwork\\SNES\\Madden NFL '97\\screenshot.png", 'wrong screenshot image in cache')

    @unittest.skip("to be reimplemented")
    def testCacheMediaPaths_2RomCollections(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        mediaDict = helper.cacheMediaPathsForSelection(0, None, conf)
        self.assertTrue(len(mediaDict) == 2, 'len(mediaDict) should have been 2 but was %i' %len(mediaDict))

        mediaPathsDict = mediaDict['1']
        self.assertTrue(len(mediaPathsDict) == 3, 'len(mediaPathsDict) should have been 3 but was %i' %len(mediaPathsDict))

        mediaPathsDict = mediaDict['2']
        self.assertTrue(len(mediaPathsDict) == 2, 'len(mediaPathsDict) should have been 2 but was %i' %len(mediaPathsDict))

    @unittest.skip("to be reimplemented")
    def testFileForControl_DB(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rc_id = 1
        rom_collection = conf.romCollections[str(rc_id)]

        game = GameView(self.gdb).getGameById(28)

        file = helper.get_file_for_control_from_db(rom_collection.imagePlacingMain.fileTypesForGameList, game)

        print (file)

    @unittest.skip("to be reimplemented")
    def testFileForControl(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        rcId = 1

        mediaDict = helper.cacheMediaPathsForSelection(rcId, None, conf)

        romCollection = conf.romCollections[str(rcId)]
        mediaPathsDict = mediaDict[str(rcId)]

        gamenameFromFile = 'Adventure (1980) (Atari)'
        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/Atari 2600/boxfront/Adventure (1980) (Atari).png'
        #HACK: for some reason getFileForControl seems to return a list and not a string
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))

        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/Atari 2600/screenshot/Adventure (1980) (Atari).jpg'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))

        filetypeGameplay, errorMsg = conf.get_filetype_by_name('gameplay', conf.tree)
        filename = helper.get_file_for_control((filetypeGameplay,), romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/Atari 2600/video/Adventure (1980) (Atari).wmv'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))


        gamenameFromFile = 'Air-Sea Battle (32 in 1) (1988) (Atari) (PAL)'
        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/Atari 2600/boxfront/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).png'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))

        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/Atari 2600/screenshot/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).gif'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))

        filename = helper.get_file_for_control((filetypeGameplay,), romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/Atari 2600/video/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).mp4'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))


        gamenameFromFile = 'Asteroids (1981) (Atari) [no copyright]'
        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/Atari 2600/boxfront/Asteroids (1981) (Atari) [no copyright].png'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))

        #this should return the fallback boxfront image as there is no screenshot image available
        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/Atari 2600/boxfront/Asteroids (1981) (Atari) [no copyright].png'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))

    @unittest.skip("to be reimplemented")
    def testFileForControl_FoldernameAsGamename(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()
        
        rcId = 2
        
        mediaDict = helper.cacheMediaPathsForSelection(rcId, None, conf)
        
        romCollection = conf.romCollections[str(rcId)]
        mediaPathsDict = mediaDict[str(rcId)]
        
        gamenameFromFile = 'Chrono Trigger'
        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/SNES/Chrono Trigger/boxfront.png'
        #HACK: for some reason getFileForControl seems to return a list and not a string
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = './testdata/artwork/SNES/Chrono Trigger/screenshot.png'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        
        gamenameFromFile = "Madden NFL '97"
        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = "./testdata/artwork/SNES/Madden NFL '97/boxfront.png"
        #HACK: for some reason getFileForControl seems to return a list and not a string
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        filename = helper.get_file_for_control(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile),
        filenameExpected = "./testdata/artwork/SNES/Madden NFL '97/screenshot.png"
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))

    @unittest.skip("to be reimplemented")
    def testFileForControlRegularExpression(self):
                
        imagelist = [os.path.normpath('testdata\artwork\SNES\Game 1.png'),
                     os.path.normpath('testdata\artwork\SNES\Game 2 (USA).png'),
                     os.path.normpath('testdata\artwork\SNES\Game 3 [V1].jpg'),
                     os.path.normpath('testdata\artwork\SNES\Game 4.gif')]
                
        image = self._matchImagePattern(imagelist, 'Game 1')
        self.assertTrue(image == 'testdata\artwork\SNES\Game 1.png', 'Wrong image: %s' %image)
        
        image = self._matchImagePattern(imagelist, 'Game 2 (USA)')
        self.assertTrue(image == 'testdata\artwork\SNES\Game 2 (USA).png', 'Wrong image: %s' %image)
        
        image = self._matchImagePattern(imagelist, 'Game 3 [V1]')
        self.assertTrue(image == 'testdata\artwork\SNES\Game 3 [V1].jpg', 'Wrong image: %s' %image)
        
        image = self._matchImagePattern(imagelist, 'Game 4')
        self.assertTrue(image == 'testdata\artwork\SNES\Game 4.gif', 'Wrong image: %s' %image)

    def _matchImagePattern(self, imagelist, gamenameFromFile):
        
        mediaPath = 'testdata\artwork\SNES\%GAME%.*'
        pathnameFromFile = mediaPath.replace("%GAME%", gamenameFromFile)
        pathToSearch = re.escape(os.path.normpath(pathnameFromFile.replace('.*', '')))
        foundImage = ''
                
        timestamp1 = time.clock()
        pattern = re.compile('%s\..*$' %re.escape(gamenameFromFile))
        for image in imagelist:
            match = pattern.search(image)
            if match:
                foundImage = image
                
        timestamp2 = time.clock()
        diff = (timestamp2 - timestamp1) * 1000
        print ('pattern.search took %s ms' %diff)
        
        return foundImage

    def _matchImageFilter(self, imagelist, gamenameFromFile):
        
        mediaPath = 'testdata\artwork\SNES\%GAME%.*'
        pathnameFromFile = mediaPath.replace("%GAME%", gamenameFromFile)
        pathToSearch = re.escape(os.path.normpath(pathnameFromFile.replace('.*', '')))
        foundImage = ''
        
        timestamp1 = time.clock()
        pattern = re.compile('%s\..*$' %pathToSearch)
        foundImage = list(filter(pattern.match, imagelist))
        timestamp2 = time.clock()
        diff = (timestamp2 - timestamp1) * 1000
        print ('filter took %s ms' %diff)
                
        return foundImage[0]
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()