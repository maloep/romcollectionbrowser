
import databaseobject
from databaseobject import DataBaseObject
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


"""
DB Index
"""
lastSelectedView = 1
lastSelectedPlatformIndex = 2
lastSelectedGenreIndex = 3
lastSelectedPublisherIndex = 4
lastSelectedYearIndex = 5
lastSelectedGameIndex = 6
autoexecBackupPath = 7
dbVersion = 8
lastFocusedControlMainView = 9
lastFocusedControlGameInfoView = 10
lastSelectedCharacterIndex = 11


class RCBSetting(DataBaseObject):    
    def __init__(self, gdb):   
        self._gdb = gdb
        self._tableName = "RCBSetting"
        
        self.id = None
        self.lastSelectedView = None
        self.lastSelectedPlatformIndex = None
        self.lastSelectedGenreIndex = None
        self.lastSelectedPublisherIndex = None
        self.lastSelectedYearIndex = None
        self.lastSelectedGameIndex = None
        self.autoexecBackupPath = ''
        self.dbVersion = ''
        self.lastFocusedControlMainView = None
        self.lastFocusedControlGameInfoView = None
        self.lastSelectedCharacterIndex = None
        
    
    def fromDb(self, row):
        
        if(not row):
            return None
        
        rcbsetting = RCBSetting(self._gdb)
        
        rcbsetting.id = row[databaseobject.DBINDEX_id]
        rcbsetting.lastSelectedView = row[lastSelectedView]
        rcbsetting.lastSelectedPlatformIndex = row[lastSelectedPlatformIndex]
        rcbsetting.lastSelectedGenreIndex = row[lastSelectedGenreIndex]
        rcbsetting.lastSelectedPublisherIndex = row[lastSelectedPublisherIndex]
        rcbsetting.lastSelectedYearIndex = row[lastSelectedYearIndex]
        rcbsetting.lastSelectedGameIndex = row[lastSelectedGameIndex]
        rcbsetting.autoexecBackupPath = row[autoexecBackupPath]
        rcbsetting.dbVersion = row[dbVersion]
        rcbsetting.lastFocusedControlMainView = row[lastFocusedControlMainView]
        rcbsetting.lastFocusedControlGameInfoView = row[lastFocusedControlGameInfoView]
        rcbsetting.lastSelectedCharacterIndex = row[lastSelectedCharacterIndex]
        
        return rcbsetting
    
    