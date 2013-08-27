import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

"""
DB Index
"""
DBINDEX_description = 2


class Region(DataBaseObject):
    
    
    def __init__(self):
        self.tableName = "Region"
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
        
        obj = Region.getRegionByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    @staticmethod
    def getAllRegions(gdb):
        dblist = DataBaseObject.getAll(gdb, 'Region')
        objs = []
        for dbRow in dblist:
            obj = Region()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
            
            
    @staticmethod
    def getRegionByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Region', name)
        obj = Region()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getRegionById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Region', id)
        obj = Region()
        obj.fromDb(dbRow)
        return obj