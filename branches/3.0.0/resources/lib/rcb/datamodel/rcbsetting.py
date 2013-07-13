
from databaseobject import DataBaseObject
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class RCBSetting(DataBaseObject):    
    def __init__(self, gdb):   
        self._gdb = gdb
        self._tableName = "RCBSetting"
        
        self.id = None
        self.lastSelectedView = None
        self.lastSelectedConsoleIndex = None
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
        
        rcbsetting.id = row[util.ROW_ID]
        rcbsetting.lastSelectedView = row[util.RCBSETTING_lastSelectedView]
        rcbsetting.lastSelectedConsoleIndex = row[util.RCBSETTING_lastSelectedConsoleIndex]
        rcbsetting.lastSelectedGenreIndex = row[util.RCBSETTING_lastSelectedGenreIndex]
        rcbsetting.lastSelectedPublisherIndex = row[util.RCBSETTING_lastSelectedPublisherIndex]
        rcbsetting.lastSelectedYearIndex = row[util.RCBSETTING_lastSelectedYearIndex]
        rcbsetting.lastSelectedGameIndex = row[util.RCBSETTING_lastSelectedGameIndex]
        rcbsetting.autoexecBackupPath = row[util.RCBSETTING_autoexecBackupPath]
        rcbsetting.dbVersion = row[util.RCBSETTING_dbVersion]
        rcbsetting.lastFocusedControlMainView = row[util.RCBSETTING_lastFocusedControlMainView]
        rcbsetting.lastFocusedControlGameInfoView = row[util.RCBSETTING_lastFocusedControlGameInfoView]
        rcbsetting.lastSelectedCharacterIndex = row[util.RCBSETTING_lastSelectedCharacterIndex]
        
        return rcbsetting
    
    