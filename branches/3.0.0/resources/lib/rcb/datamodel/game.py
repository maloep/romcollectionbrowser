
import databaseobject
from databaseobject import DataBaseObject
from platform import Platform

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

class Game(DataBaseObject):
    __filterQuery = "Select * From Game WHERE \
                    (romCollectionId = ? OR (0 = ?)) AND \
                    (Id IN (Select GameId From GenreGame Where GenreId = ?) OR (0 = ?)) AND \
                    (YearId = ? OR (0 = ?)) AND \
                    (PublisherId = ? OR (0 = ?)) AND \
                    (isFavorite = ? OR (0 = ?)) \
                    AND %s \
                    ORDER BY name COLLATE NOCASE"
                    
    __filterByNameAndRomCollectionId = "SELECT * FROM Game WHERE name = ? and romCollectionId = ?"
    
    __filterMostPlayedGames = "Select * From Game Where launchCount > 0 Order by launchCount desc Limit "    
    
    
    def __init__(self, gdb):
        self._gdb = gdb
        self._tableName = "Game"
        
        self.id = None
        self.name = ''
        self.releases = []
        self.genres = []

        
    def fromDb(self, row):
        if(not row):
            return None
        
        game = Game(self._gdb)
        
        game.id = row[databaseobject.DBINDEX_id]
        game.name = row[databaseobject.DBINDEX_name]
        
        return game
    
    
    def toDbDict(self, game):
        gamedict = {}
        gamedict['id'] = game.id
        gamedict['name'] = game.name
        
        
    def getFilteredGames(self, romCollectionId, genreId, yearId, publisherId, isFavorite, likeStatement):
        args = (romCollectionId, genreId, yearId, publisherId, isFavorite)
        filterQuery = self.__filterQuery %likeStatement
        util.Logutil.log('searching games with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)
        util.Logutil.log('searching games with args: romCollectionId = %s, genreId = %s, yearId = %s, publisherId = %s, isFavorite = %s, characterFilter = %s' %(str(romCollectionId), str(genreId), str(yearId), str(publisherId), str(isFavorite), likeStatement), util.LOG_LEVEL_DEBUG)
        games = self.getObjectsByWildcardQuery(filterQuery, args)        
        return games
        
    def getGameByNameAndRomCollectionId(self, name, romCollectionId):
        game = self.getObjectByQuery(self.__filterByNameAndRomCollectionId, (name, romCollectionId))
        return game
        
    def getMostPlayedGames(self, count):
        if(str.isdigit(str(count))):
            filter = self.__filterMostPlayedGames +str(count)
        else:
            filter = self.__filterMostPlayedGames +str(10)
        games = self.getObjectsByQuery(filter, [])
        return games
        
        