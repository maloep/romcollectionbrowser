
import databaseobject
from databaseobject import DataBaseObject
from platform import Platform
from company import Company
from namedentities import Year
from file import File
from filetype import FileType

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


"""
DB Index
"""
DBINDEX_description = 2
DBINDEX_gameCmd = 3
DBINDEX_alternateGameCmd = 4
DBINDEX_isFavorite = 5
DBINDEX_launchCount = 6
DBINDEX_version = 7
DBINDEX_completed = 8
DBINDEX_broken = 9
DBINDEX_dateAdded = 10
DBINDEX_dateModified = 11
DBINDEX_lastPlayed = 12
DBINDEX_gameId = 13
DBINDEX_platformId = 14
DBINDEX_romCollectionId = 15
DBINDEX_developerId = 16
DBINDEX_publisherId = 17
DBINDEX_yearId = 18
DBINDEX_regionId = 19
DBINDEX_laguageId = 20
DBINDEX_maxPlayersId = 21
DBINDEX_perspectiveId = 22
DBINDEX_nameFromFile = 23
DBINDEX_firstRomFile = 24


class Release(DataBaseObject):
                    
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
        
        self.isFavorite = 0
        self.launchCount = 0
        self.completed = False
        self.broken = False
        self.dateAdded = ''
        self.lastPlayed = ''
        self.lastModified = ''
        self.firstRomFile = ''
        self.nameFromFile = ''
                
        #referenced objects - complex
        self.platform = None       
        self.publisher = None    
        self.developer = None
        self.persons = []
        self.characters = []
        
        #referenced objects - simple
        self.year = ''
        self.yearId = None
        self.region = ''
        self.maxPlayers = ''
        self.language = ''
        self.perspective = ''
        self.media = []
        self.controllers = []
        self.alternateTitles = []
        self.detailurls = []
        self.romCollection = None
        
        self.artworkurls = None
        self.mediaFiles = {}

        
    def fromDb(self, row):
        
        if(not row):
            return None
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        self.nameFromFile = row[DBINDEX_nameFromFile]
        self.firstRomFile = row[DBINDEX_firstRomFile]
        
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
        releasedict['nameFromFile'] = self.nameFromFile
        releasedict['firstRomFile'] = self.firstRomFile
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
        