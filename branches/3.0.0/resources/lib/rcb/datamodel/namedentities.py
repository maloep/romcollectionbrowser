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
    
    #obsolete: atm years are only filtered by Platform
    filterQuery = "SELECT * FROM Year WHERE Id IN \
                    (Select YearId From Release WHERE (platformId = ? OR (0 = ?)) AND \
                    (PublisherId = ? OR (0 = ?)) \
                    AND id IN (SELECT GameId From LinkGenreGame Where GenreId = ? OR (0 = ?)) \
                    AND %s) \
                    ORDER BY name COLLATE NOCASE"
                        
    filterYearByPlatform = "SELECT * FROM Year WHERE Id IN (Select YearId From Game WHERE \
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
        if(self.name == ''):
            return
        
        obj = Year.getYearByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    @staticmethod
    def getAllYears(gdb):
        dblist = DataBaseObject.getAll(gdb, 'Year')
        objs = []
        for dbRow in dblist:
            obj = Year()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
            
            
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

    @staticmethod
    def getFilteredYears(gdb, romCollectionId, genreId, publisherId, likeStatement):
        args = (romCollectionId, publisherId, genreId)
        filterQuery = Year.filterQuery %likeStatement
        util.Logutil.log('searching years with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)        
        
        dblist = DataBaseObject.getByWildcardQuery(gdb, filterQuery, args)
        objs = []
        for dbRow in dblist:
            obj = Year()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
        
    
    """
    def getFilteredYearsByPlatform(self, romCollectionId):
        years = self.getObjectsByWildcardQuery(self.filterYearByPlatform, (romCollectionId,))
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
        if(self.name == ''):
            return
        
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
        
    
    """
    def delete(self, id):
        if(id != None):
            count = self.getCountByQuery(self.yearIdCountQuery, (id,))
            if (count[0] < 2):
                util.Logutil.log("Delete PersonRole with id %s" % str(id), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(PersonRole.deleteQuery, (id,))
    """
                
                
class Language(NamedEntity):
    
    deleteQuery = "DELETE FROM Language WHERE id = ?"


    def __init__(self):
        NamedEntity.__init__(self)
        self.tableName = "Language"

    
    def insert(self, gdb, allowUpdate):
        if(self.name == ''):
            return
        
        obj = Language.getLanguageByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
        
        
    @staticmethod
    def getLanguageByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Language', name)
        obj = Language()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getLanguageById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Language', id)
        obj = Language()
        obj.fromDb(dbRow)
        return obj
        
        
    @staticmethod
    def getAllLanguages(gdb):
        dblist = DataBaseObject.getAll(gdb, 'Language')
        objs = []
        for dbRow in dblist:
            obj = Language()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
    
    
    """
    def delete(self, id):
        if(id != None):
            count = self.getCountByQuery(self.yearIdCountQuery, (id,))
            if (count[0] < 2):
                util.Logutil.log("Delete Language with id %s" % str(id), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(Language.deleteQuery, (id,))
    """
                
                
class ESRBRating(NamedEntity):
    
    deleteQuery = "DELETE FROM ESRBRating WHERE id = ?"


    def __init__(self):
        NamedEntity.__init__(self)
        self.tableName = "ESRBRating"

    
    def insert(self, gdb, allowUpdate):
        if(self.name == ''):
            return
        
        obj = ESRBRating.getESRBRatingByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
        
        
    @staticmethod
    def getESRBRatingByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'ESRBRating', name)
        obj = Language()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getESRBRatingById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'ESRBRating', id)
        obj = Language()
        obj.fromDb(dbRow)
        return obj
        
        
    @staticmethod
    def getAllESRBRatings(gdb):
        dblist = DataBaseObject.getAll(gdb, 'ESRBRating')
        objs = []
        for dbRow in dblist:
            obj = Language()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
    
    
    """
    def delete(self, id):
        if(id != None):
            count = self.getCountByQuery(self.yearIdCountQuery, (id,))
            if (count[0] < 2):
                util.Logutil.log("Delete ESRBRating with id %s" % str(id), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(ESRBRating.deleteQuery, (id,))
    """
    
    
class MaxPlayers(NamedEntity):
    
    deleteQuery = "DELETE FROM MaxPlayers WHERE id = ?"


    def __init__(self):
        NamedEntity.__init__(self)
        self.tableName = "MaxPlayers"

    
    def insert(self, gdb, allowUpdate):
        if(self.name == ''):
            return
        
        obj = MaxPlayers.getMaxPlayersByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
        
        
    @staticmethod
    def getMaxPlayersByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'MaxPlayers', name)
        obj = MaxPlayers()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getMaxPlayersById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'MaxPlayers', id)
        obj = MaxPlayers()
        obj.fromDb(dbRow)
        return obj
        
        
    @staticmethod
    def getAllMaxPlayerss(gdb):
        dblist = DataBaseObject.getAll(gdb, 'MaxPlayers')
        objs = []
        for dbRow in dblist:
            obj = MaxPlayers()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
    
    
    """
    def delete(self, id):
        if(id != None):
            count = self.getCountByQuery(self.yearIdCountQuery, (id,))
            if (count[0] < 2):
                util.Logutil.log("Delete MaxPlayers with id %s" % str(id), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(MaxPlayers.deleteQuery, (id,))
    """