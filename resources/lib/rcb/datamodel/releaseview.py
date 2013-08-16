
import databaseobject
from databaseobject import DataBaseObject
from release import Release
from platform import Platform
from company import Company
from namedentities import Year

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


"""
DB Index
"""
DBINDEX_id = 0
DBINDEX_name = 1
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
DBINDEX_nameFromFile = 18
DBINDEX_firstRomFile = 19
DBINDEX_gameId = 20
DBINDEX_platformId = 21
DBINDEX_platformName = 22
DBINDEX_developerId = 23
DBINDEX_developerName = 24
DBINDEX_publisherId = 25
DBINDEX_publisherName = 26
DBINDEX_romCollectionId = 27
DBINDEX_romCollectionName = 28
DBINDEX_yearId = 29
DBINDEX_yearName = 30
DBINDEX_ESRBRatingId = 31
DBINDEX_ESRBRatingName = 32
DBINDEX_regionId = 33
DBINDEX_regionName = 34
DBINDEX_languageId = 35
DBINDEX_languageName = 36
DBINDEX_mediaId = 37
DBINDEX_mediaName = 38
DBINDEX_maxPlayersId = 39
DBINDEX_maxPlayersName = 40
DBINDEX_perspectiveId = 41
DBINDEX_perspectiveName = 42
DBINDEX_controllerId = 43
DBINDEX_controllerName = 44


class ReleaseView(DataBaseObject):
    filterQuery = "Select * From ReleaseView WHERE \
                    (platformId = ? OR (0 = ?)) AND \
                    (gameId IN (Select gameId From LinkGenreGame Where genreId = ?) OR (0 = ?)) AND \
                    (yearId = ? OR (0 = ?)) AND \
                    (publisherId = ? OR (0 = ?)) AND \
                    (isFavorite = ? OR (0 = ?)) \
                    AND %s \
                    ORDER BY name COLLATE NOCASE"
    
    
    def __init__(self):
        self.tableName = "ReleaseView"
        
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
        self.firstRomFile = ''
        self.nameFromFile = ''
        self.romCollection = None
                        
        self.platformName = ''
        self.platformId = None
        self.publisherName = ''
        self.publisherId = None    
        self.developerName = ''
        self.developerId = None
        self.yearName = ''        
        self.yearId = None
        self.regionName = ''
        self.regionId = None
        self.maxPlayersName = ''
        self.maxPlayersId = None
        self.ESRBratingName = ''
        self.ESRBratingId = None
        self.languageName = ''
        self.languageId = None
        self.mediaName = ''
        self.mediaId = None
        self.perspectiveName = ''
        self.perspectiveId = None
        self.controllerName = ''
        self.controllerId = None
                
        self.persons = []
        self.characters = []
        self.alternateTitles = []
        self.detailurls = []        
        
        self.artworkurls = {}
        self.artworkfiles = {}
        self.romfiles = []
        
        
    def fromDb(self, row):
        
        if(not row):
            return None
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        
        self.gameId = row[DBINDEX_gameId]
        self.description = self.readSaveString(row, DBINDEX_description)
        self.gameCmd = self.readSaveString(row, DBINDEX_gameCmd)
        self.alternateGameCmd = None
        self.isFavorite = row[DBINDEX_isFavorite]
        self.launchCount = row[DBINDEX_launchCount]
        #release.originalTitle = row[DBINDEX_originalTitle]
        self.version = self.readSaveString(row, DBINDEX_version)
                
        self.platformName = self.readSaveString(row, DBINDEX_platformName)
        self.platformId = row[DBINDEX_platformId]
        self.yearName = self.readSaveString(row, DBINDEX_yearName)
        self.yearId = row[DBINDEX_yearId]
        self.publisherName = self.readSaveString(row, DBINDEX_publisherName)
        self.publisherId = row[DBINDEX_publisherId]
        self.developerName = self.readSaveString(row, DBINDEX_developerName)
        self.developerId = row[DBINDEX_developerId]
        
        self.maxPlayersName = self.readSaveString(row, DBINDEX_maxPlayersName)
        self.maxPlayersId = row[DBINDEX_maxPlayersId]
        self.ESRBratingName = self.readSaveString(row, DBINDEX_ESRBRatingName)
        self.ESRBratingId = row[DBINDEX_ESRBRatingId]
        self.regionId = row[DBINDEX_regionId]
        self.regionName = self.readSaveString(row, DBINDEX_regionName)
        self.mediaId = row[DBINDEX_mediaId]
        self.mediaName = self.readSaveString(row, DBINDEX_mediaName)
        self.perspectiveId = row[DBINDEX_perspectiveId]
        self.perspectiveName = self.readSaveString(row, DBINDEX_perspectiveName)
        self.controllerId = row[DBINDEX_controllerId]
        self.controllerName = self.readSaveString(row, DBINDEX_controllerName)
        
        """
        release.romCollectionId = row[DBINDEX_romCollectionId]
        release.alternateTitle = row[DBINDEX_alternateTitle]
        """
        
        
    def resolveMediaPath(self, fileType):
        
        fileName = ''
        try:
            fileName = self.artworkfiles[fileType]
            return fileName
        except KeyError:
            pass
        
        if(fileType == 'game'):
            fileName = fileName.replace("%GAME%", self.nameFromFile)
            fileName = fileName.replace("%PLATFORM%", self.platform.name)
            
            
    @staticmethod
    def getReleaseViewByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'ReleaseView', name)
        obj = ReleaseView()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getReleaseViewById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'ReleaseView', id)
        obj = ReleaseView()
        obj.fromDb(dbRow)
        return obj
        
        
    @staticmethod
    def getFilteredReleases(gdb, platformId, genreId, yearId, publisherId, isFavorite, likeStatement):
        args = (platformId, genreId, yearId, publisherId, isFavorite)
        filterQuery = ReleaseView.filterQuery %likeStatement
        util.Logutil.log('searching games with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)
        util.Logutil.log('searching games with args: platformId = %s, genreId = %s, yearId = %s, publisherId = %s, isFavorite = %s, characterFilter = %s' %(str(platformId), str(genreId), str(yearId), str(publisherId), str(isFavorite), likeStatement), util.LOG_LEVEL_DEBUG)
        dbRows = DataBaseObject.getByWildcardQuery(gdb, filterQuery, args)        
        objs = []
        for dbRow in dbRows:
            obj = ReleaseView()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
