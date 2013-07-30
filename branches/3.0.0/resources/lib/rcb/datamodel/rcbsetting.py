
import databaseobject
from databaseobject import DataBaseObject
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


"""
DB Index
"""
DBINDEX_lastSelectedView = 1
DBINDEX_lastSelectedPlatformIndex = 2
DBINDEX_lastSelectedGenreIndex = 3
DBINDEX_lastSelectedPublisherIndex = 4
DBINDEX_lastSelectedYearIndex = 5
DBINDEX_lastSelectedGameIndex = 6
DBINDEX_autoexecBackupPath = 7
DBINDEX_dbVersion = 8
DBINDEX_lastFocusedControlMainView = 9
DBINDEX_lastFocusedControlGameInfoView = 10
DBINDEX_lastSelectedCharacterIndex = 11


class RCBSetting(DataBaseObject):    
    def __init__(self, gdb):   
        self.gdb = gdb
        self.tableName = "RCBSetting"
        
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
            return
        
        self.id = row[databaseobject.DBINDEX_id]
        self.lastSelectedView = row[DBINDEX_lastSelectedView]
        self.lastSelectedPlatformIndex = row[DBINDEX_lastSelectedPlatformIndex]
        self.lastSelectedGenreIndex = row[DBINDEX_lastSelectedGenreIndex]
        self.lastSelectedPublisherIndex = row[DBINDEX_lastSelectedPublisherIndex]
        self.lastSelectedYearIndex = row[DBINDEX_lastSelectedYearIndex]
        self.lastSelectedGameIndex = row[DBINDEX_lastSelectedGameIndex]
        self.autoexecBackupPath = row[DBINDEX_autoexecBackupPath]
        self.dbVersion = row[DBINDEX_dbVersion]
        self.lastFocusedControlMainView = row[DBINDEX_lastFocusedControlMainView]
        self.lastFocusedControlGameInfoView = row[DBINDEX_lastFocusedControlGameInfoView]
        self.lastSelectedCharacterIndex = row[DBINDEX_lastSelectedCharacterIndex]
    
    
    def toDbDict(self):
        rcbsettingdict = {}
        rcbsettingdict['id'] = self.id
        
        rcbsettingdict['lastSelectedView'] = self.lastSelectedView
        rcbsettingdict['lastSelectedPlatformIndex'] = self.lastSelectedPlatformIndex
        rcbsettingdict['lastSelectedGenreIndex'] = self.lastSelectedGenreIndex
        rcbsettingdict['lastSelectedPublisherIndex'] = self.lastSelectedPublisherIndex
        rcbsettingdict['lastSelectedYearIndex'] = self.lastSelectedYearIndex
        rcbsettingdict['lastSelectedGameIndex'] = self.lastSelectedGameIndex
        rcbsettingdict['autoexecBackupPath'] = self.autoexecBackupPath
        rcbsettingdict['dbVersion'] = self.dbVersion
        rcbsettingdict['lastFocusedControlMainView'] = self.lastFocusedControlMainView
        rcbsettingdict['lastFocusedControlGameInfoView'] = self.lastFocusedControlGameInfoView
        rcbsettingdict['lastSelectedCharacterIndex'] = self.lastSelectedCharacterIndex
        
        return rcbsettingdict
    
    
    def insert(self):
        DataBaseObject.insert(self)
    