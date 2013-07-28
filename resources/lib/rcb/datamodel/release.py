
import databaseobject
from databaseobject import DataBaseObject
from platform import Platform

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


"""
DB Index
"""
DBINDEX_description = 2
DBINDEX_gameCmd = 3
DBINDEX_romCollectionId = 5
DBINDEX_publisherId = 6
DBINDEX_developerId = 7
DBINDEX_reviewerId = 8
DBINDEX_yearId = 9
DBINDEX_maxPlayers = 10
DBINDEX_rating = 11
DBINDEX_numVotes = 12
DBINDEX_url = 13
DBINDEX_region = 14
DBINDEX_media = 15
DBINDEX_perspective = 16
DBINDEX_controllerType = 17
DBINDEX_isFavorite = 18
DBINDEX_launchCount = 19
DBINDEX_originalTitle = 20
DBINDEX_alternateTitle = 21
DBINDEX_translatedBy = 22
DBINDEX_version = 23


class Release(DataBaseObject):
    __filterQuery = "Select * From Release WHERE \
                    (romCollectionId = ? OR (0 = ?)) AND \
                    (gameId IN (Select gameId From GenreGame Where genreId = ?) OR (0 = ?)) AND \
                    (YearId = ? OR (0 = ?)) AND \
                    (PublisherId = ? OR (0 = ?)) AND \
                    (isFavorite = ? OR (0 = ?)) \
                    AND %s \
                    ORDER BY name COLLATE NOCASE"
                    
    __filterByNameAndRomCollectionId = "SELECT * FROM Release WHERE name = ? and romCollectionId = ?"
    
    __filterMostPlayedGames = "Select * From Release Where launchCount > 0 Order by launchCount desc Limit "    
    
    
    def __init__(self, gdb):
        self._gdb = gdb
        self._tableName = "Release"
        
        self.id = None
        self.name = ''
        self.description = ''
        self.gameCmd = ''
        self.alternateGameCmd = ''
        self.originalTitle = ''
        self.version = ''
        self.mobyRank = ''
        self.mobyScore = ''
        self.mobyScoreVotes = ''
        self.thegamesdbScore = ''
        self.thegamesdbVotes = ''
        self.version = ''
        
        self.isFavorite = 0
        self.launchCount = 0
        self.completed = False
        self.broken = False
        self.dateAdded = ''
        self.lastPlayed = ''
        self.lastModified = ''        
                
        #referenced objects - complex
        self.platform = None        
        self.publisher = None        
        self.developer = None
        self.region = None
        self.persons = []
        
        #referenced objects - simple
        self.year = ''
        self.maxPlayers = ''
        self.ESRBrating = ''
        self.language = ''
        self.media = ''
        self.perspective = ''
        self.controller = ''
        self.alternateTitles = []
        self.detailurls = []
        self.romCollection = None
        
        self.artworkurls = {}

        
    def fromDb(self, row):
        
        if(not row):
            return None
        
        release = Release(self._gdb)
        
        release.id = row[databaseobject.DBINDEX_id]
        release.name = row[databaseobject.DBINDEX_name]
        release.description = row[DBINDEX_description]
        release.romCollectionId = row[DBINDEX_romCollectionId]
        release.publisherId = row[DBINDEX_publisherId]
        release.developerId = row[DBINDEX_developerId]
        release.reviewerId = row[DBINDEX_reviewerId]
        release.yearId = row[DBINDEX_yearId]
        release.gameCmd = row[DBINDEX_gameCmd]
        release.alternateGameCmd = None
        release.maxPlayers = row[DBINDEX_maxPlayers]
        release.rating = row[DBINDEX_rating]
        release.numVotes = row[DBINDEX_numVotes]
        release.url = row[DBINDEX_url]
        release.region = row[DBINDEX_region]
        release.media = row[DBINDEX_media]
        release.perspective = row[DBINDEX_perspective]
        release.controllerType = row[DBINDEX_controllerType]
        release.isFavorite = row[DBINDEX_isFavorite]
        release.launchCount = row[DBINDEX_launchCount]
        release.originalTitle = row[DBINDEX_originalTitle]
        release.alternateTitle = row[DBINDEX_alternateTitle]
        release.translatedBy = row[DBINDEX_translatedBy]
        release.version = row[DBINDEX_version]
        
        return release
    
    
    def toDbDict(self, release):
        releasedict = {}
        releasedict['id'] = release.id
        releasedict['name'] = release.name 
        releasedict['description'] = release.description
        releasedict['romCollectionId'] = release.romCollectionId
        releasedict['publisherId'] = release.publisherId
        releasedict['developerId'] = release.developerId
        releasedict['reviewerId'] = release.reviewerId
        releasedict['yearId'] = release.yearId
        releasedict['gameCmd'] = release.gameCmd
        releasedict['alternateGameCmd'] = release.alternateGameCmd
        releasedict['maxPlayers'] = release.maxPlayers
        releasedict['rating'] = release.rating
        releasedict['numVotes'] = release.numVotes
        releasedict['url'] = release.url
        releasedict['region'] = release.region
        releasedict['media'] = release.media
        releasedict['perspective'] = release.perspective
        releasedict['controllerType'] = release.controllerType
        releasedict['isFavorite'] = release.isFavorite
        releasedict['launchCount'] = release.launchCount
        releasedict['originalTitle'] = release.originalTitle
        releasedict['alternateTitle'] = release.alternateTitle
        releasedict['translatedBy'] = release.translatedBy
        releasedict['version'] = release.version
        
        
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
        
        