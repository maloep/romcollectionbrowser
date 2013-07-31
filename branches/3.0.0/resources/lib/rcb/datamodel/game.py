
import databaseobject
from databaseobject import DataBaseObject
from platform import Platform

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *
from resources.lib.rcb.datamodel.links import LinkGenreGame

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
    
    #releases = []
    
    def __init__(self, gdb):
        self.gdb = gdb
        self.tableName = "Game"
        
        self.id = None
        self.name = ''
        self.releases = []
        self.genres = []

        
    def fromDb(self, row):
        if(not row):
            return
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
    
    
    def toDbDict(self):
        gamedict = {}
        gamedict['id'] = self.id
        gamedict['name'] = self.name
        return gamedict
        
            
    def insert(self, allowUpdate):
        
        if(self.id):
            if(allowUpdate):
                self.updateAllColumns(False)
        else:
            self.id = DataBaseObject.insert(self)
        
        for release in self.releases:
            release.gameId = self.id
            release.insert(allowUpdate)
            
        for genre in self.genres:
            genre.releaseId = self.id
            genre.insert(allowUpdate)
            
            linkGenreGame = LinkGenreGame(self.gdb)
            linkGenreGame.genreId = genre.id
            linkGenreGame.gameId = self.id
            linkGenreGame.insert(allowUpdate)
                            
    
    @staticmethod
    def getGameByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Game', name)
        game = Game(gdb)
        game.fromDb(dbRow)
        return game
    
    
    @staticmethod
    def getGameById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Game', id)
        game = Game(gdb)
        game.fromDb(dbRow)
        return game
    
    
    @staticmethod
    def getAllGames(gdb):
        gamelist = DataBaseObject.getAll(gdb, 'Game')
        games = []
        for dbRow in gamelist:
            game = Game(gdb)
            game.fromDb(dbRow)
            games.append(game)
        return games
            
    
    @staticmethod
    def getFilteredGames(gdb, romCollectionId, genreId, yearId, publisherId, isFavorite, likeStatement):
        args = (romCollectionId, genreId, yearId, publisherId, isFavorite)
        filterQuery = Game.__filterQuery %likeStatement
        util.Logutil.log('searching games with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)
        util.Logutil.log('searching games with args: romCollectionId = %s, genreId = %s, yearId = %s, publisherId = %s, isFavorite = %s, characterFilter = %s' %(str(romCollectionId), str(genreId), str(yearId), str(publisherId), str(isFavorite), likeStatement), util.LOG_LEVEL_DEBUG)
        dbRows = DataBaseObject.getByWildcardQuery(gdb, filterQuery, args)        
        games = []
        for dbRow in dbRows:
            game = Game(gdb)
            game.fromDb(dbRow)
            games.append(game)
        return games
        
    
    @staticmethod
    def getGameByNameAndRomCollectionId(gdb, name, romCollectionId):
        dbRow = DataBaseObject.getOneByQuery(gdb, Game.__filterByNameAndRomCollectionId, (name, romCollectionId))
        game = Game(gdb)
        game.fromDb(dbRow)
        return game
        
    
    @staticmethod
    def getMostPlayedGames(gdb, count):
        if(str.isdigit(str(count))):
            filter = Game.__filterMostPlayedGames +str(count)
        else:
            filter = Game.__filterMostPlayedGames +str(10)
        dbRows = DataBaseObject.getByQuery(gdb, filter, [])
        games = []
        for dbRow in dbRows:
            game = Game(gdb)
            game.fromDb(dbRow)
            games.append(game)
        return games
        
        