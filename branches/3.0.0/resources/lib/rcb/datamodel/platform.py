import databaseobject
from databaseobject import DataBaseObject
from file import File
from filetype import FileType

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
DBINDEX_maxControllers = 11


class Platform(DataBaseObject):
    def __init__(self):
        self.tableName = "Platform"
        
        self.id = None
        self.name = ''
        self.description = ''
        self.manufacturerId = None
        self.developerId = None
        self.cpu = ''
        self.ram = ''
        self.graphics = ''
        self.sound = ''
        self.display = ''
        self.maxcontrollers = ''
        self.releaseyear = ''
        
        """
        self.hasonlinefeatures = ''
        self.originalprice = ''
        """
                
        self.mediaFiles = {}
        
        
    def fromDb(self, row):
        if(not row):
            return
                
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        
        self.description = row[DBINDEX_description]
        self.manufacturerId = row[DBINDEX_manufacturerId]
        self.developerId = row[DBINDEX_developerId]
        self.cpu = row[DBINDEX_cpu]
        self.ram = row[DBINDEX_ram]
        self.graphics = row[DBINDEX_graphics]
        self.sound = row[DBINDEX_sound]
        self.display = row[DBINDEX_display]
        self.maxcontrollers = row[DBINDEX_maxControllers]
        self.releaseyear = row[DBINDEX_releaseYear]
        
        
    def toDbDict(self):
        platformdict = {}
        platformdict['id'] = self.id
        platformdict['name'] = self.name 
        platformdict['description'] = self.description
        platformdict['manufacturerId'] = self.manufacturerId
        platformdict['developerId'] = self.developerId
        platformdict['cpu'] = self.cpu
        platformdict['ram'] = self.ram
        platformdict['graphics'] = self.graphics
        platformdict['sound'] = self.sound
        platformdict['display'] = self.display
        platformdict['maxcontrollers'] = self.maxcontrollers
        platformdict['releaseyear'] = self.releaseyear
        return platformdict
    
    
    def insert(self, gdb, allowUpdate):
        
        if(self.name == ''):
            return
        
        platform = Platform.getPlatformByName(gdb, self.name)
        if(platform.id):
            self.id = platform.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
        for fileTypeName in self.mediaFiles.keys():
            fileType = FileType()
            fileType.name = fileTypeName
            fileType.insert(gdb)
            
            file = File()
            file.name = self.mediaFiles[fileTypeName]
            file.parentId = self.id
            file.fileTypeId = fileType.id
            file.insert(gdb) 
            
                
    @staticmethod
    def getAllPlatforms(gdb):
        dblist = DataBaseObject.getAll(gdb, 'Platform')
        objs = []
        for dbRow in dblist:
            obj = Platform()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
            
    
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