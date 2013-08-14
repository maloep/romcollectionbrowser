
import databaseobject
from databaseobject import DataBaseObject
from platform import Platform
from company import Company
from namedentities import Year

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


"""
DB Index
"""
DBINDEX_description = 2
DBINDEX_gameCmd = 3
DBINDEX_alternateGameCmd = 4
DBINDEX_mobyRank = 5
DBINDEX_mobyScore = 6
DBINDEX_mobyScoreVotes = 7
DBINDEX_thegamesdbScore = 8
DBINDEX_thegamesdbVotes = 9
DBINDEX_isFavorite = 10
DBINDEX_launchCount = 11
DBINDEX_version = 12
DBINDEX_completed = 13
DBINDEX_broken = 14
DBINDEX_dateAdded = 15
DBINDEX_dateModified = 16
DBINDEX_lastPlayed = 17
DBINDEX_gameId = 18
DBINDEX_platformId = 19
DBINDEX_romCollectionId = 20
DBINDEX_developerId = 21
DBINDEX_publisherId = 22
DBINDEX_yearId = 23
DBINDEX_ESRBRatingId = 24
DBINDEX_regionId = 25
DBINDEX_laguageId = 26
DBINDEX_mediaId = 27
DBINDEX_maxPlayersId = 28
DBINDEX_perspectiveId = 29
DBINDEX_controllerId = 30


class Release(DataBaseObject):
    filterQuery = "Select * From ReleaseView WHERE \
                    (platformId = ? OR (0 = ?)) AND \
                    (gameId IN (Select gameId From LinkGenreGame Where genreId = ?) OR (0 = ?)) AND \
                    (YearId = ? OR (0 = ?)) AND \
                    (PublisherId = ? OR (0 = ?)) AND \
                    (isFavorite = ? OR (0 = ?)) \
                    AND %s \
                    ORDER BY name COLLATE NOCASE"
                    
    filterByNameAndRomCollectionId = "SELECT * FROM Release WHERE name = ? and romCollectionId = ?"
    
    filterMostPlayedGames = "Select * From Release Where launchCount > 0 Order by launchCount desc Limit "    
    
    
    def __init__(self):
        self.tableName = "Release"
        
        self.id = None
        self.gameId = None
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
        
        self.isFavorite = 0
        self.launchCount = 0
        self.completed = False
        self.broken = False
        self.dateAdded = ''
        self.lastPlayed = ''
        self.lastModified = ''        
                
        #referenced objects - complex
        self.platform = Platform()       
        self.publisher = Company()    
        self.developer = Company()
        self.persons = []
        self.characters = []
        
        #referenced objects - simple
        self.year = ''
        self.yearId = None
        self.region = ''
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
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        
        self.gameId = row[DBINDEX_gameId]
        self.description = row[DBINDEX_description]
        self.gameCmd = row[DBINDEX_gameCmd]
        self.alternateGameCmd = None
        self.isFavorite = row[DBINDEX_isFavorite]
        self.launchCount = row[DBINDEX_launchCount]
        #release.originalTitle = row[DBINDEX_originalTitle]
        self.version = row[DBINDEX_version]
                
        self.platform = Platform()
        self.platform.id = row[DBINDEX_platformId]
                
        self.publisher = Company()
        self.publisher.id = row[DBINDEX_publisherId]
        
        self.developer = Company()
        self.developer.id = row[DBINDEX_developerId]
        
        
        """
        release.romCollectionId = row[DBINDEX_romCollectionId]
        release.maxPlayers = row[DBINDEX_maxPlayers]
        release.rating = row[DBINDEX_rating]
        release.url = row[DBINDEX_url]
        release.region = row[DBINDEX_region]
        release.media = row[DBINDEX_media]
        release.perspective = row[DBINDEX_perspective]
        release.controller = row[DBINDEX_controllerType]
        release.alternateTitle = row[DBINDEX_alternateTitle]
        """
    
    
    def toDbDict(self):
        releasedict = {}
        releasedict['id'] = self.id
        releasedict['name'] = self.name
        releasedict['gameId'] = self.gameId 
        releasedict['description'] = self.description
        if(self.platform):
            releasedict['platformId'] = self.platform.id
        if(self.publisher):
            releasedict['publisherId'] = self.publisher.id
        if(self.developer):
            releasedict['developerId'] = self.developer.id
        
        releasedict['yearId'] = self.yearId
        releasedict['gameCmd'] = self.gameCmd
        releasedict['alternateGameCmd'] = self.alternateGameCmd
        releasedict['isFavorite'] = self.isFavorite
        releasedict['launchCount'] = self.launchCount
        releasedict['version'] = self.version
        
        
        """
        releasedict['romCollectionId'] = release.romCollection.id
        releasedict['maxPlayers'] = release.maxPlayers
        releasedict['rating'] = release.rating
        releasedict['numVotes'] = release.numVotes
        releasedict['url'] = release.url
        releasedict['region'] = release.region
        releasedict['media'] = release.media
        releasedict['perspective'] = release.perspective
        releasedict['controllerType'] = release.controllerType
        releasedict['alternateTitle'] = release.alternateTitle
        """
        return releasedict
        
    
    def insert(self, gdb, allowUpdate):
        
        if(self.name == ''):
            return
        
        #store objects that have to be stored before release because we need the ids
        if(self.platform):
            self.platform.insert(gdb, allowUpdate)
            
        if(self.developer):
            self.developer.insert(gdb, allowUpdate)
            
        if(self.publisher):
            self.publisher.insert(gdb, allowUpdate)
            
        if(self.year != ''):
            year = Year()
            year.name = self.year
            year.insert(gdb, allowUpdate)
            self.yearId = year.id
        
        #store self
        if(self.id):
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
        #store children that require releaseId        
        for person in self.persons:
            person.releaseId = self.id
            person.insert(gdb, allowUpdate)
        
        
    @staticmethod
    def getReleaseByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Release', name)
        release = Release()
        release.fromDb(dbRow)
        return release
    
    
    @staticmethod
    def getReleaseById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Release', id)
        release = Release()
        release.fromDb(dbRow)
        return release
        
       
    @staticmethod
    def getFilteredReleases(gdb, platformId, genreId, yearId, publisherId, isFavorite, likeStatement):
        args = (platformId, genreId, yearId, publisherId, isFavorite)
        filterQuery = Release.filterQuery %likeStatement
        util.Logutil.log('searching games with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)
        util.Logutil.log('searching games with args: platformId = %s, genreId = %s, yearId = %s, publisherId = %s, isFavorite = %s, characterFilter = %s' %(str(platformId), str(genreId), str(yearId), str(publisherId), str(isFavorite), likeStatement), util.LOG_LEVEL_DEBUG)
        dbRows = DataBaseObject.getByWildcardQuery(gdb, filterQuery, args)        
        objs = []
        for dbRow in dbRows:
            obj = Release()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
        
    """
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
    """
        