
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
                        
        mediaDict = helper.cacheMediaPathsForSelection(1, None, conf)
        self.assertTrue(len(mediaDict) == 1, 'len(mediaDict) should have been 1 but was %i' %len(mediaDict))
        
        mediaPathsDict = mediaDict['1']
        self.assertTrue(len(mediaPathsDict) == 3, 'len(mediaPathsDict) should have been 3 but was %i' %len(mediaPathsDict))
        self.assertTrue(len(mediaPathsDict['boxfront']) == 2, 'len(mediaPathsDict[boxfront]) should have been 2 but was %i' %len(mediaPathsDict['boxfront']))
        self.assertTrue(len(mediaPathsDict['screenshot']) == 2, 'len(mediaPathsDict[screenshot]) should have been 2 but was %i' %len(mediaPathsDict['screenshot']))
        self.assertTrue(len(mediaPathsDict['gameplay']) == 2, 'len(mediaPathsDict[gameplay]) should have been 2 but was %i' %len(mediaPathsDict['gameplay']))
        
        self.assertTrue(mediaPathsDict['boxfront'][0] == 'testdata\\artwork\\Atari 2600\\boxfront\\Adventure (1980) (Atari).png', 'wrong boxfront image in cache')
        self.assertTrue(mediaPathsDict['boxfront'][1] == 'testdata\\artwork\\Atari 2600\\boxfront\\Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).png', 'wrong boxfront image in cache')
        
        self.assertTrue(mediaPathsDict['screenshot'][0] == 'testdata\\artwork\\Atari 2600\\screenshot\\Adventure (1980) (Atari).jpg', 'wrong screenshot image in cache')
        self.assertTrue(mediaPathsDict['screenshot'][1] == 'testdata\\artwork\\Atari 2600\\screenshot\\Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).gif', 'wrong screenshot image in cache')
        
        self.assertTrue(mediaPathsDict['gameplay'][0] == 'testdata\\artwork\\Atari 2600\\video\\Adventure (1980) (Atari).wmv', 'wrong gameplay video in cache')
        self.assertTrue(mediaPathsDict['gameplay'][1] == 'testdata\\artwork\\Atari 2600\\video\\Air-Sea Battle (32 in 1) (1988) (Atari) (PAL).mp4', 'wrong gameplay video in cache')
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()