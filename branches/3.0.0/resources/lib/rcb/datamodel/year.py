
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class Year(DataBaseObject):
    
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


    def __init__(self, gdb):        
        self._gdb = gdb
        self._tableName = "Year"
        
        self.id = None
        self.name = ''
        
    
    def fromDb(self, row):
        
        if(not row):
            return None
        
        year = Year(self._gdb)
        
        year.id = row[util.ROW_ID]
        year.name = row[util.ROW_NAME]
        
        return year

    
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
            print count
            if (count[0] < 2):
                util.Logutil.log("Delete Year with id %s" % str(yearId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.yearDeleteQuery, (yearId,))
