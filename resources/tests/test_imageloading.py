
import os
import unittest


from resources.lib import helper
from resources.lib.config import Config, RomCollection

class Test(unittest.TestCase):

    @classmethod
    def setUp(cls):
        pass

    
    @classmethod
    def tearDown(cls):
        pass

    
    def testCacheMediaPaths_1RomCollection(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()
                        
        rcId = 1
                        
        mediaDict = helper.cacheMediaPathsForSelection(rcId, None, conf)
        self.assertTrue(len(mediaDict) == 1, 'len(mediaDict) should have been 1 but was %i' %len(mediaDict))
        
        mediaPathsDict = mediaDict[str(rcId)]
        self.assertTrue(len(mediaPathsDict) == 3, 'len(mediaPathsDict) should have been 3 but was %i' %len(mediaPathsDict))
        self.assertTrue(len(mediaPathsDict['boxfront']) == 3, 'len(mediaPathsDict[boxfront]) should have been 2 but was %i' %len(mediaPathsDict['boxfront']))
        self.assertTrue(len(mediaPathsDict['screenshot']) == 2, 'len(mediaPathsDict[screenshot]) should have been 2 but was %i' %len(mediaPathsDict['screenshot']))
        self.assertTrue(len(mediaPathsDict['gameplay']) == 2, 'len(mediaPathsDict[gameplay]) should have been 2 but was %i' %len(mediaPathsDict['gameplay']))
        
        self.assertTrue(mediaPathsDict['boxfront'][0] == 'testdata\\artwork\\Atari 2600\\boxfront\\Adventure (1980) (Atari).png', 'wrong boxfront image in cache')
        self.assertTrue(mediaPathsDict['boxfront'][1] == 'testdata\\artwork\\Atari 2600\\boxfront\\Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).png', 'wrong boxfront image in cache')
        self.assertTrue(mediaPathsDict['boxfront'][2] == 'testdata\\artwork\\Atari 2600\\boxfront\\Asteroids (1981) (Atari) [no copyright].png', 'wrong boxfront image in cache')
        
        self.assertTrue(mediaPathsDict['screenshot'][0] == 'testdata\\artwork\\Atari 2600\\screenshot\\Adventure (1980) (Atari).jpg', 'wrong screenshot image in cache')
        self.assertTrue(mediaPathsDict['screenshot'][1] == 'testdata\\artwork\\Atari 2600\\screenshot\\Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).gif', 'wrong screenshot image in cache')
        
        self.assertTrue(mediaPathsDict['gameplay'][0] == 'testdata\\artwork\\Atari 2600\\video\\Adventure (1980) (Atari).wmv', 'wrong gameplay video in cache')
        self.assertTrue(mediaPathsDict['gameplay'][1] == 'testdata\\artwork\\Atari 2600\\video\\Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).mp4', 'wrong gameplay video in cache')
        
        
    def testCacheMediaPaths_1RomCollection_FoldernameAsGamename(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'romcollections_imageloading.xml')
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
        
        
    def testCacheMediaPaths_2RomCollections(self):
        # Load a config file with 2 valid RomCollections and all FileTypes and ImagePlacings
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()
                        
        mediaDict = helper.cacheMediaPathsForSelection(0, None, conf)
        self.assertTrue(len(mediaDict) == 2, 'len(mediaDict) should have been 2 but was %i' %len(mediaDict))
        
        mediaPathsDict = mediaDict['1']
        self.assertTrue(len(mediaPathsDict) == 3, 'len(mediaPathsDict) should have been 3 but was %i' %len(mediaPathsDict))
        
        mediaPathsDict = mediaDict['2']
        self.assertTrue(len(mediaPathsDict) == 2, 'len(mediaPathsDict) should have been 2 but was %i' %len(mediaPathsDict))
        
        
    def testFileForControl(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()
        
        rcId = 1
        
        mediaDict = helper.cacheMediaPathsForSelection(rcId, None, conf)
        
        romCollection = conf.romCollections[str(rcId)]
        mediaPathsDict = mediaDict[str(rcId)]
        
        gamenameFromFile = 'Adventure (1980) (Atari)'
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = './testdata/artwork/Atari 2600/boxfront/Adventure (1980) (Atari).png'
        #HACK: for some reason getFileForControl seems to return a list and not a string
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = './testdata/artwork/Atari 2600/screenshot/Adventure (1980) (Atari).jpg'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        filetypeGameplay, errorMsg = conf.readFileType('gameplay', conf.tree)
        filename = helper.getFileForControl((filetypeGameplay,), romCollection, mediaPathsDict, gamenameFromFile, True),        
        filenameExpected = './testdata/artwork/Atari 2600/video/Adventure (1980) (Atari).wmv'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        
        gamenameFromFile = 'Air-Sea Battle (32 in 1) (1988) (Atari) (PAL)'
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = './testdata/artwork/Atari 2600/boxfront/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).png'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = './testdata/artwork/Atari 2600/screenshot/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).gif'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        filename = helper.getFileForControl((filetypeGameplay,), romCollection, mediaPathsDict, gamenameFromFile, True),        
        filenameExpected = './testdata/artwork/Atari 2600/video/Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).mp4'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        

        gamenameFromFile = 'Asteroids (1981) (Atari) [no copyright]'
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = './testdata/artwork/Atari 2600/boxfront/Asteroids (1981) (Atari) [no copyright].png'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        #this should return the fallback boxfront image as there is no screenshot image available
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = './testdata/artwork/Atari 2600/boxfront/Asteroids (1981) (Atari) [no copyright].png'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        
    def testFileForControl_FoldernameAsGamename(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()
        
        rcId = 2
        
        mediaDict = helper.cacheMediaPathsForSelection(rcId, None, conf)
        
        romCollection = conf.romCollections[str(rcId)]
        mediaPathsDict = mediaDict[str(rcId)]
        
        gamenameFromFile = 'Chrono Trigger'
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = './testdata/artwork/SNES/Chrono Trigger/boxfront.png'
        #HACK: for some reason getFileForControl seems to return a list and not a string
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = './testdata/artwork/SNES/Chrono Trigger/screenshot.png'
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        
        gamenameFromFile = "Madden NFL '97"
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = "./testdata/artwork/SNES/Madden NFL '97/boxfront.png"
        #HACK: for some reason getFileForControl seems to return a list and not a string
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        
        filename = helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile, False),        
        filenameExpected = "./testdata/artwork/SNES/Madden NFL '97/screenshot.png"
        self.assertTrue(filename[0] == filenameExpected, 'Artwork file should have been %s but was %s' %(filenameExpected, filename))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()