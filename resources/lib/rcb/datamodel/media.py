import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

"""
DB Index
"""
DBINDEX_description = 2


class Media(DataBaseObject):
    
    
    def __init__(self):
        self.tableName = "Media"
        self.id = None
        self.name = ''
        self.description = ''
        
    
    def fromDb(self, row):
        if(not row):
            return
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        self.description = row[DBINDEX_description]
        
        
    def toDbDict(self):
        dbdict = {}
        dbdict['id'] = self.id
        dbdict['name'] = self.name
        dbdict['description'] = self.description
        return dbdict
    
    
    def insert(self, gdb, allowUpdate):
        if(self.name == ''):
            return
        
        obj = Media.getMediaByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    @staticmethod
    def getAllMedias(gdb):
        dblist = DataBaseObject.getAll(gdb, 'Media')
        objs = []
        for dbRow in dblist:
            obj = Media()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
            
            
    @staticmethod
    def getMediaByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Media', name)
        obj = Media()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getMediaById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Media', id)
        obj = Media()
        obj.fromDb(dbRow)
        return obj