import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class Company(DataBaseObject):
    
    developerIdCountQuery = "SELECT count(developerId) 'developerIdCount' \
                    from Game \
                    where developerId = ? \
                    group by developerId"
    
    developerDeleteQuery = "DELETE FROM Company WHERE id = ?"


    def __init__(self):
        self.tableName = "Company"
        
        self.id = None
        self.name = ''
        
    
    def fromDb(self, row):
        
        if(not row):
            return
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        
        
    def toDbDict(self):
        dbdict = {}
        dbdict['id'] = self.id
        dbdict['name'] = self.name         
        return dbdict
    
    
    def insert(self, gdb, allowUpdate):
        
        if(self.name == ''):
            return
        
        obj = Company.getCompanyByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    @staticmethod
    def getCompanyByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Company', name)
        obj = Company()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getCompanyById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Company', id)
        obj = Company()
        obj.fromDb(dbRow)
        return obj
    
    
    def delete(self, developerId):
        if(developerId != None):
            object = self.getCountByQuery(self.developerIdCountQuery, (developerId,))
            if (object[0] < 2):
                util.Logutil.log("Delete Company with id %s" % str(developerId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.developerDeleteQuery, (developerId,))
