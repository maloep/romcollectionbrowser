import databaseobject
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
    
    filteGenreIdByGameId = "SELECT * From GenreGame Where GameId = ?"
    
    genreIdCountQuery = "SELECT g.genreid, count(*) 'genreIdCount' \
                    from genregame g \
                    inner join genregame g2 \
                    on g.genreid=g2.genreid \
                    where g.gameid = ? \
                    group by g.genreid"
    
    genreDeleteQuery = "DELETE FROM Genre WHERE id = ?"
    
    genreGameDeleteQuery = "DELETE FROM GenreGame WHERE gameId = ?"
    
    def __init__(self):
        self.tableName = "Genre"
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
        obj = Genre.getGenreByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    @staticmethod
    def getGenreByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Genre', name)
        obj = Genre()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getGenreById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Genre', id)
        obj = Genre()
        obj.fromDb(dbRow)
        return obj
        
    
    def getFilteredGenres(self, romCollectionId, yearId, publisherId, likeStatement):
        args = (romCollectionId, yearId, publisherId)
        filterQuery = self.__filterQuery %likeStatement
        util.Logutil.log('searching genres with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)
        genres = self.getByWildcardQuery(filterQuery, args)
        return genres
    
    def getFilteredGenresByConsole(self, romCollectionId):
        genres = self.getByWildcardQuery(self.filterGenreByConsole, (romCollectionId,))
        return genres
        
    def getGenresByGameId(self, gameId):
        genres = self.getByQuery(self.filteGenreByGameId, (gameId,))
        return genres

    def getGenreIdByGameId(self, gameId):
        genre = self.getByQuery(self.filteGenreIdByGameId, (gameId,))
        return genre.id
        
    def delete(self, gameId):
        #genreId = self.getGenreIdByGameId(gameId)
        gdb.cursor.execute(self.genreIdCountQuery, (gameId,))    
        object = gdb.cursor.fetchall()
        if(object != None):
            for items in object:    
                if (items[1] < 2):
                    util.Logutil.log("Delete Genre with id %s" % str(items[0]), util.LOG_LEVEL_INFO)
                    self.deleteObjectByQuery(self.genreDeleteQuery, (items[0],))
        util.Logutil.log("Delete GenreGame with gameId %s" % str(gameId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.genreGameDeleteQuery, (gameId,))