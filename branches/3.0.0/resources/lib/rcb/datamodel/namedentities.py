import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class NamedEntity(DataBaseObject):

    def __init__(self):
        self.tableName = ""
        
        self.id = None
        self.name = ''
        
    
    def fromDb(self, row):
        if(not row):
            return None
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        
        
    def toDbDict(self):
        dbdict = {}
        dbdict['id'] = self.id
        dbdict['name'] = self.name         
        return dbdict


class Year(NamedEntity):
    
    #obsolete: atm years are only filtered by console
    __filterQuery = "SELECT * FROM Year WHERE Id IN (Select YearId From Game WHERE \
                        (romCollectionId = ? OR (0 = ?)) AND \
                        (PublisherId = ? OR (0 = ?)) \
                        AND id IN \
                        (SELECT GameId From GenreGame Where GenreId = ? OR (0 = ?)) \
                        AND %s) \
                        ORDER BY name COLLATE NOCASE"
                        
    filterYearByConsole = "SELECT * FROM Year WHERE Id IN (Select YearId From Game WHERE \
                        (romCollectionId = ? OR (0 = ?))) \
                        ORDER BY name COLLATE NOCASE"
    
    yearIdCountQuery = "SELECT count(yearId) 'yearIdCount' \
                    from Game \
                    where yearId = ? \
                    group by yearId"
    
    yearDeleteQuery = "DELETE FROM Year WHERE id = ?"


    def __init__(self):
        NamedEntity.__init__(self)
        self.tableName = "Year"
        
        
    def insert(self, gdb, allowUpdate):
        obj = Year.getYearByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    @staticmethod
    def getYearByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Year', name)
        obj = Year()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getYearById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Year', id)
        obj = Year()
        obj.fromDb(dbRow)
        return obj

    
    """
    def getFilteredYears(self, romCollectionId, genreId, publisherId, likeStatement):
        args = (romCollectionId, publisherId, genreId)
        filterQuery = self.__filterQuery %likeStatement
        util.Logutil.log('searching years with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)        
        years = self.getObjectsByWildcardQuery(filterQuery, args)
        return years
    
    def getFilteredYearsByConsole(self, romCollectionId):
        years = self.getObjectsByWildcardQuery(self.filterYearByConsole, (romCollectionId,))
        return years
    
    def delete(self, yearId):
        if(yearId != None):
            count = self.getCountByQuery(self.yearIdCountQuery, (yearId,))
            if (count[0] < 2):
                util.Logutil.log("Delete Year with id %s" % str(yearId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.yearDeleteQuery, (yearId,))
    """
                
                
class PersonRole(NamedEntity):
    
    deleteQuery = "DELETE FROM PersonRole WHERE id = ?"


    def __init__(self):
        NamedEntity.__init__(self)
        self.tableName = "PersonRole"

    
    def insert(self, gdb, allowUpdate):
        obj = PersonRole.getPersonRoleByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
        
        
    @staticmethod
    def getPersonRoleByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'PersonRole', name)
        personRole = PersonRole()
        personRole.fromDb(dbRow)
        return personRole
    
    
    @staticmethod
    def getPersonRoleById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'PersonRole', id)
        personRole = PersonRole()
        personRole.fromDb(dbRow)
        return personRole
        
    
    def delete(self, id):
        if(id != None):
            count = self.getCountByQuery(self.yearIdCountQuery, (id,))
            if (count[0] < 2):
                util.Logutil.log("Delete PersonRole with id %s" % str(id), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(PersonRole.deleteQuery, (id,))
