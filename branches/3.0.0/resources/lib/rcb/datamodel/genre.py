
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class Genre(DataBaseObject):
    
    #obsolete: atm genres are only filtered by console
    __filterQuery = "SELECT * FROM Genre WHERE Id IN (Select GenreId From GenreGame Where GameId IN ( \
                        Select Id From Game WHERE \
                        (romCollectionId = ? OR (0 = ?)) AND \
                        (YearId = ? OR (0 = ?)) AND \
                        (PublisherId = ? OR (0 = ?)) \
                        AND %s)) \
                        ORDER BY name COLLATE NOCASE"
                        
    filterGenreByConsole = "SELECT * FROM Genre WHERE Id IN (Select GenreId From GenreGame Where GameId IN ( \
                        Select Id From Game WHERE \
                        (romCollectionId = ? OR (0 = ?)))) \
                        ORDER BY name COLLATE NOCASE"
    
    filteGenreByGameId = "SELECT * FROM Genre WHERE Id IN (Select GenreId From GenreGame Where GameId = ?)"
    
    filteGenreIdByGameId = "SELECT GenreId From GenreGame Where GameId = ?"
    
    genreIdCountQuery = "SELECT g.genreid, count(*) 'genreIdCount' \
                    from genregame g \
                    inner join genregame g2 \
                    on g.genreid=g2.genreid \
                    where g.gameid = ? \
                    group by g.genreid"
    
    genreDeleteQuery = "DELETE FROM Genre WHERE id = ?"
    
    genreGameDeleteQuery = "DELETE FROM GenreGame WHERE gameId = ?"
    
    def __init__(self, gdb):        
        self._gdb = gdb
        self._tableName = "Genre"
        
        self.id = None
        self.name = ''
        
    
    def fromDb(self, row):
        genre = Genre(self._gdb)
        
        if(not row):
            return genre
        
        genre.id = row[util.ROW_ID]
        genre.name = row[util.ROW_NAME]
        
        return genre
    
        
    def getFilteredGenres(self, romCollectionId, yearId, publisherId, likeStatement):
        args = (romCollectionId, yearId, publisherId)
        filterQuery = self.__filterQuery %likeStatement
        util.Logutil.log('searching genres with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)
        genres = self.getObjectsByWildcardQuery(filterQuery, args)
        return genres
    
    def getFilteredGenresByConsole(self, romCollectionId):
        genres = self.getObjectsByWildcardQuery(self.filterGenreByConsole, (romCollectionId,))
        return genres
        
    def getGenresByGameId(self, gameId):
        genres = self.getObjectsByQuery(self.filteGenreByGameId, (gameId,))
        return genres

    def getGenreIdByGameId(self, gameId):
        genreId = self.getObjectsByQuery(self.filteGenreIdByGameId, (gameId,))
        return genreId
        
    def delete(self, gameId):
        #genreId = self.getGenreIdByGameId(gameId)
        self._gdb.cursor.execute(self.genreIdCountQuery, (gameId,))    
        object = self._gdb.cursor.fetchall()
        if(object != None):
            for items in object:    
                if (items[1] < 2):
                    util.Logutil.log("Delete Genre with id %s" % str(items[0]), util.LOG_LEVEL_INFO)
                    self.deleteObjectByQuery(self.genreDeleteQuery, (items[0],))
        util.Logutil.log("Delete GenreGame with gameId %s" % str(gameId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.genreGameDeleteQuery, (gameId,))