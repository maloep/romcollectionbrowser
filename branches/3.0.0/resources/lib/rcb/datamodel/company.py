import databaseobject
from databaseobject import DataBaseObject
from file import File
from filetype import FileType

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class Company(DataBaseObject):
    
    
    filterQueryPublisher = "SELECT * FROM Company WHERE Id IN (Select PublisherId From Release WHERE \
                        (platformId = ? OR (0 = ?)) AND \
                        (YearId = ? OR (0 = ?)) \
                        AND id IN \
                        (SELECT GameId From LinkGenreGame Where GenreId = ? OR (0 = ?)) \
                        AND %s) \
                        ORDER BY name COLLATE NOCASE"
                        
    filterQueryDeveloper = "SELECT * FROM Company WHERE Id IN (Select DeveloperId From Release WHERE \
                        (platformId = ? OR (0 = ?)) AND \
                        (YearId = ? OR (0 = ?)) \
                        AND id IN \
                        (SELECT GameId From LinkGenreGame Where GenreId = ? OR (0 = ?)) \
                        AND %s) \
                        ORDER BY name COLLATE NOCASE"                    
    
    
    
    developerIdCountQuery = "SELECT count(developerId) 'developerIdCount' \
                    from Game \
                    where developerId = ? \
                    group by developerId"
    
    developerDeleteQuery = "DELETE FROM Company WHERE id = ?"


    def __init__(self):
        self.tableName = "Company"
        
        self.id = None
        self.name = ''
        
        self.mediaFiles = {}
        
    
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
    def getAllCompanies(gdb):
        dblist = DataBaseObject.getAll(gdb, 'Company')
        objs = []
        for dbRow in dblist:
            obj = Company()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
    
            
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
    
    
    @staticmethod
    def getFilteredPublishers(gdb, romCollectionId, genreId, yearId, likeStatement):
        args = (romCollectionId, yearId, genreId)
        filterQuery = Company.filterQueryPublisher %likeStatement
        util.Logutil.log('searching publishers with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)        
        
        dblist = DataBaseObject.getByWildcardQuery(gdb, filterQuery, args)
        objs = []
        for dbRow in dblist:
            obj = Company()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
    
    
    @staticmethod
    def getFilteredDevelopers(gdb, romCollectionId, genreId, yearId, likeStatement):
        args = (romCollectionId, yearId, genreId)
        filterQuery = Company.filterQueryDeveloper %likeStatement
        util.Logutil.log('searching developers with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)        
        
        dblist = DataBaseObject.getByWildcardQuery(gdb, filterQuery, args)
        objs = []
        for dbRow in dblist:
            obj = Company()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
    
    
    def delete(self, developerId):
        if(developerId != None):
            object = self.getCountByQuery(self.developerIdCountQuery, (developerId,))
            if (object[0] < 2):
                util.Logutil.log("Delete Company with id %s" % str(developerId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.developerDeleteQuery, (developerId,))
