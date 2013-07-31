import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


DBINDEX_description = 2
DBINDEX_releaseYear = 3
DBINDEX_developerId = 4
DBINDEX_manufacturerId = 5
DBINDEX_cpu = 6
DBINDEX_ram = 7
DBINDEX_graphics = 8
DBINDEX_sound = 9
DBINDEX_display = 10
DBINDEX_mediaId = 11
DBINDEX_maxControllers = 12


class Platform(DataBaseObject):
    def __init__(self):
        self.tableName = "Platform"
        
        self.id = None
        self.name = ''
        self.description = ''
        self.manufacturer = None
        self.developer = None
        self.cpu = ''
        self.memory = ''
        self.graphics = ''
        self.sound = ''
        self.display = ''
        self.media = ''
        self.maxcontrollers = ''
        self.releasedate = ''
        self.hasonlinefeatures = ''
        self.originalprice = ''
        
        self.artworkurls = {}
        
        
    def fromDb(self, row):
        if(not row):
            return
                
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        
        
    def toDbDict(self):
        platformdict = {}
        platformdict['id'] = self.id
        platformdict['name'] = self.name 
        platformdict['description'] = self.description
        return platformdict
    
    
    def insert(self, gdb, allowUpdate):
        
        platform = Platform.getPlatformByName(gdb, self.name)
        if(platform.id):
            self.id = platform.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    
    @staticmethod
    def getPlatformByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Platform', name)
        platform = Platform()
        platform.fromDb(dbRow)
        return platform
    
    
    @staticmethod
    def getPlatformById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Platform', id)
        platform = Platform()
        platform.fromDb(dbRow)
        return platform