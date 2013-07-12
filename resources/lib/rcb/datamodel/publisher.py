
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class Publisher(DataBaseObject):
    
    __filterQuery = "SELECT * FROM Publisher WHERE Id IN (Select PublisherId From Game WHERE \
                        (romCollectionId = ? OR (0 = ?)) AND \
                        (YearId = ? OR (0 = ?)) \
                        AND id IN \
                        (SELECT GameId From GenreGame Where GenreId = ? OR (0 = ?)) \
                        AND %s) \
                        ORDER BY name COLLATE NOCASE"
                        
    filterPublishersByConsole = "SELECT * FROM Publisher WHERE Id IN (Select PublisherId From Game WHERE \
                        (romCollectionId = ? OR (0 = ?))) \
                        ORDER BY name COLLATE NOCASE"
    
    publisherIdCountQuery = "SELECT count(publisherId) 'publisherIdCount' \
                    from Game \
                    where publisherId = ? \
                    group by publisherId"
    
    publisherDeleteQuery = "DELETE FROM Publisher WHERE id = ?"


    def __init__(self, gdb):        
        self._gdb = gdb
        self._tableName = "Publisher"
        
        self.id = None
        self.name = ''
        
    
    def fromDb(self, row):
        publisher = Publisher(self._gdb)
        
        if(not row):
            return publisher
        
        publisher.id = row[util.ROW_ID]
        publisher.name = row[util.ROW_NAME]
        
        return publisher
        
        
    def getFilteredPublishers(self, romCollectionId, genreId, yearId, likeStatement):
        args = (romCollectionId, yearId, genreId)
        filterQuery = self.__filterQuery %likeStatement
        util.Logutil.log('searching publishers with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)        
        publishers = self.getObjectsByWildcardQuery(filterQuery, args)
        return publishers
    
    def getFilteredPublishersByConsole(self, romCollectionId):
        publishers = self.getObjectsByWildcardQuery(self.filterPublishersByConsole, (romCollectionId,))
        return publishers
    
    def delete(self, publisherId):
        if(publisherId != None):
            object = self.getCountByQuery(self.publisherIdCountQuery, (publisherId,))
            if (object[0] < 2):
                util.Logutil.log("Delete Publisher with id %s" % str(publisherId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.publisherDeleteQuery, (publisherId,))