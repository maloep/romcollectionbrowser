
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
        self.description = ''
        self.romCollectionId = None
        self.publisherId = None        
        self.developerId = None
        self.reviewerId = None
        self.yearId = None
        
        self.gameCmd = ''
        self.alternateGameCmd = ''
        self.maxPlayers = 0
        self.rating = ''
        self.numVotes = 0
        self.url = ''
        self.region = ''
        self.media = ''
        self.perspective = ''
        self.controllerType = ''
        self.isFavorite = 0
        self.launchCount = 0
        self.originalTitle = ''
        self.alternateTitle = ''
        self.translatedBy = ''
        self.version = ''
                
        self.platform = Platform(self._gdb)
        
        self.publisher = ''
        self.developer = ''
        self.year = ''
        self.reviewer = ''
        self.genre = []        
        self.artworkurls = {}

        
    def fromDb(self, row):
        
        if(not row):
            return None
        
        game = Game(self._gdb)
        
        game.id = row[util.ROW_ID]
        game.name = row[util.ROW_NAME]
        game.description = row[util.GAME_description]
        game.romCollectionId = row[util.GAME_romCollectionId]
        game.publisherId = row[util.GAME_publisherId]
        game.developerId = row[util.GAME_developerId]
        game.reviewerId = row[util.GAME_reviewerId]
        game.yearId = row[util.GAME_yearId]
        game.gameCmd = row[util.GAME_gameCmd]
        game.alternateGameCmd = None
        game.maxPlayers = row[util.GAME_maxPlayers]
        game.rating = row[util.GAME_rating]
        game.numVotes = row[util.GAME_numVotes]
        game.url = row[util.GAME_url]
        game.region = row[util.GAME_region]
        game.media = row[util.GAME_media]
        game.perspective = row[util.GAME_perspective]
        game.controllerType = row[util.GAME_controllerType]
        game.isFavorite = row[util.GAME_isFavorite]
        game.launchCount = row[util.GAME_launchCount]
        game.originalTitle = row[util.GAME_originalTitle]
        game.alternateTitle = row[util.GAME_alternateTitle]
        game.translatedBy = row[util.GAME_translatedBy]
        game.version = row[util.GAME_version]
        
        return game
    
    
    def toDbDict(self, game):
        gamedict = {}
        gamedict['id'] = game.id
        gamedict['name'] = game.name 
        gamedict['description'] = game.description
        gamedict['romCollectionId'] = game.romCollectionId
        gamedict['publisherId'] = game.publisherId
        gamedict['developerId'] = game.developerId
        gamedict['reviewerId'] = game.reviewerId
        gamedict['yearId'] = game.yearId
        gamedict['gameCmd'] = game.gameCmd
        gamedict['alternateGameCmd'] = game.alternateGameCmd
        gamedict['maxPlayers'] = game.maxPlayers
        gamedict['rating'] = game.rating
        gamedict['numVotes'] = game.numVotes
        gamedict['url'] = game.url
        gamedict['region'] = game.region
        gamedict['media'] = game.media
        gamedict['perspective'] = game.perspective
        gamedict['controllerType'] = game.controllerType
        gamedict['isFavorite'] = game.isFavorite
        gamedict['launchCount'] = game.launchCount
        gamedict['originalTitle'] = game.originalTitle
        gamedict['alternateTitle'] = game.alternateTitle
        gamedict['translatedBy'] = game.translatedBy
        gamedict['version'] = game.version
        
            
        
        
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
        
        