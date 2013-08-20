import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *



class FileType(DataBaseObject):
        
    fileTypeDict = None
        
    
    def __init__(self):
        self.tableName = "FileType"
        
        self.id = None
        self.name = ''
        
        
    def fromDb(self, row):
        if(not row):
            return
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        
    
    def insert(self, gdb, allowUpdate):
        
        if(self.name == ''):
            return
        
        obj = FileType.getFileTypeByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    @staticmethod
    def getFileTypeByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'FileType', name)
        obj = FileType()
        obj.fromDb(dbRow)
        return obj
            
            
    @staticmethod
    def getAllFileTypes(gdb):
        dblist = DataBaseObject.getAll(gdb, 'FileType')
        objs = []
        for dbRow in dblist:
            obj = FileType()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
    
    
    @staticmethod
    def cacheFileTypes(gdb):
        if(FileType.fileTypeDict):
            return FileType.fileTypeDict
        
        FileType.fileTypeDict = {}
        fileTypes = FileType.getAllFileTypes(gdb)
        for fileType in fileTypes:
            FileType.fileTypeDict[fileType.name] = fileType
        
        return FileType.fileTypeDict
    
    
    @staticmethod
    def getCachedFileType(gdb, fileTypeName):
        if(FileType.fileTypeDict == None):
            FileType.cacheFileTypes(gdb)
            
        try:
            return FileType.fileTypeDict[fileTypeName]
        except KeyError:
            Logutil.log("fileType %s not found in fileTypeDict" %fileTypeName, util.LOG_LEVEL_ERROR)
            
        return None
                            