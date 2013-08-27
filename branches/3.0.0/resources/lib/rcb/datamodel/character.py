import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

"""
DB Index
"""
DBINDEX_description = 2


class Character(DataBaseObject):
    
    
    def __init__(self):
        self.tableName = "Character"
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
        
        obj = Character.getCharacterByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    @staticmethod
    def getAllCharacters(gdb):
        dblist = DataBaseObject.getAll(gdb, 'Character')
        objs = []
        for dbRow in dblist:
            obj = Character()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
            
            
    @staticmethod
    def getCharacterByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Character', name)
        obj = Character()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getCharacterById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Character', id)
        obj = Character()
        obj.fromDb(dbRow)
        return obj