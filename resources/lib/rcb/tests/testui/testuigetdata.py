import unittest

from resources.lib.rcb.datamodel.gamedatabase import GameDataBase
from resources.lib.rcb.datamodel.releaseview import ReleaseView
from resources.lib.rcb.datamodel.file import File
from resources.lib.rcb.utils import util
from resources.lib.rcb.gameimport import gamescraper
from resources.lib.rcb.configuration import config
from resources.lib.rcb.configuration.config import *

from resources.lib.heimdall.src.heimdall.predicates import *
from resources.lib.heimdall.src.heimdall.core import Subject


class TestUIGetData(unittest.TestCase):

    def setUp(self):
        util.RCBHOME = os.path.join(os.getcwd(), '..', '..', '..', '..', '..')
        util.ISTESTRUN = True

        Logutil.currentLogLevel = util.LOG_LEVEL_INFO
        self._databasedir = os.path.join( os.getcwd(), 'TestDataBase')
        self.gdb = None
        
    
    def tearDown(self):
        if(self.gdb):
            self.gdb.close()
            time.sleep(1.0)
            
            
    def test_getResolveArtwork(self):
        
        self.gdb = GameDataBase(self._databasedir, 'MyGames.db')
        self.gdb.connect()
        
        myConfig = Config('config.xml')
        statusOk, errorMsg = myConfig.readXml()
        romCollection = myConfig.romCollections['3']
        
        timestamp1 = time.clock()
        releases = ReleaseView.getFilteredReleasesTest(self.gdb, 3, 0, 0, 0, 0, '0=0')
        timestamp2 = time.clock()
        diff = (timestamp2 - timestamp1) * 1000
        print "load %i games from db in %d ms" % (len(releases), diff)
           
        
        timestamp1 = time.clock()   
        fileDict = File.getFileDictForGamelist(self.gdb)
                
        for release in releases:
            files = release.getMediaFiles(self.gdb, ('boxfront', 'screenshot'), fileDict, myConfig)
            files2 = release.getMediaFiles(self.gdb, ('boxfront', 'screenshot'), fileDict, myConfig)
            if(len(files) > 0):
                print files[0]
            if(len(files2) > 0):
                print files2[0]
        
        timestamp2 = time.clock()    
        diff = (timestamp2 - timestamp1) * 1000
        print "load artwork for %i games in %d ms" % (len(releases), diff)
        


class RCBMock:
    
    itemCount = 0
    
    def writeMsg(self, msg1, msg2, msg3, count=0):
        return True
