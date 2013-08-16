import os
import unittest
import inspect
import time

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

from resources.lib.rcb.datamodel.gamedatabase import GameDataBase
from resources.lib.rcb.datamodel.databaseobject import DataBaseObject
from resources.lib.rcb.datamodel.release import Release
from resources.lib.rcb.datamodel.releaseview import ReleaseView

class TestReleaseView(unittest.TestCase):

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
            
            
    """
    def test_getReleases(self):
        self._gdb = GameDataBase(self._databasedir, 'MyGamesRead.db')
        self._gdb.connect()
        query = "SELECT [R.name] FROM ReleaseView"
        #args = ("Super Mario Kart", 5)
        args = []
        results = DataBaseObject.getByQuery(self._gdb, query, args)
        print results
    """
                

                
    def test_getFilteredReleases(self):
        self.gdb = GameDataBase(self._databasedir, 'MyGamesRead.db')
        self.gdb.connect()
        
        releases = ReleaseView.getFilteredReleases(self.gdb, 1, 0, 0, 0, '0', '0=0')
        
        print releases
    
        
        