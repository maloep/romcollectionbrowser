
import databaseobject
from databaseobject import DataBaseObject
from release import Release
from platform import Platform
from company import Company
from namedentities import Year
from file import File 

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *
from resources.lib.rcb.gameimport import filewalker


"""
DB Index
"""
DBINDEX_id = 0
DBINDEX_name = 1
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
DBINDEX_nameFromFile = 13
DBINDEX_firstRomFile = 14
DBINDEX_gameId = 15
DBINDEX_platformId = 16
DBINDEX_platformName = 17
DBINDEX_developerId = 18
DBINDEX_developerName = 19
DBINDEX_publisherId = 20
DBINDEX_publisherName = 21
DBINDEX_romCollectionId = 22
DBINDEX_romCollectionName = 23
DBINDEX_yearId = 24
DBINDEX_yearName = 25
DBINDEX_regionId = 26
DBINDEX_regionName = 27
DBINDEX_languageId = 28
DBINDEX_languageName = 29
DBINDEX_mediaId = 30
DBINDEX_mediaName = 31
DBINDEX_maxPlayersId = 32
DBINDEX_maxPlayersName = 33
DBINDEX_perspectiveId = 34
DBINDEX_perspectiveName = 35
DBINDEX_controllerId = 36
DBINDEX_controllerName = 37


class ReleaseView(DataBaseObject):
    filterQuery = "Select * From ReleaseView WHERE \
                    (platformId = ? OR (0 = ?)) AND \
                    (gameId IN (Select gameId From LinkGenreGame Where genreId = ?) OR (0 = ?)) AND \
                    (yearId = ? OR (0 = ?)) AND \
                    (publisherId = ? OR (0 = ?)) AND \
                    (isFavorite = ? OR (0 = ?)) \
                    AND %s \
                    ORDER BY name COLLATE NOCASE"
                    
    #HACK: for some reason we need another syntax to get data from releaseview from python unit tests 
    filterQueryTest = "Select * From ReleaseView WHERE \
                    ([R.platformId] = ? OR (0 = ?)) AND \
                    ([R.gameId] IN (Select gameId From LinkGenreGame Where genreId = ?) OR (0 = ?)) AND \
                    ([R.yearId] = ? OR (0 = ?)) AND \
                    ([R.publisherId] = ? OR (0 = ?)) AND \
                    ([R.isFavorite] = ? OR (0 = ?)) \
                    AND %s \
                    ORDER BY [R.name] COLLATE NOCASE \
                    LIMIT 1000"
    
    
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
        
        self.artworkurls = None
        self.mediaFiles = None
        self.romFiles = []
        
        
    def fromDb(self, row):
        
        if(not row):
            return None
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        self.nameFromFile = row[DBINDEX_nameFromFile]
        self.firstRomFile = row[DBINDEX_firstRomFile]
        
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
        
    """
    def resolveMediaPath(self, config, fileType):
        Logutil.log("ReleaseView.resolveMediaPaths", util.LOG_LEVEL_DEBUG)
        
        if(self.mediaFiles == None):
            self.mediaFiles = {}
            
        for path in config.mediaPaths:
            
            if(path.type != fileType):
                continue
                        
            Logutil.log("FileType: %s" %str(path.type), util.LOG_LEVEL_DEBUG)
            fileName = path.path
                        
            if(path.parent == 'game'):
                fileName = fileName.replace("%GAME%", self.nameFromFile)
                fileName = fileName.replace("%PLATFORM%", self.platformName)
    
                rootExtFile = os.path.splitext(fileName)
                gameName = rootExtFile[0] + ".*"
                dirs, files, dirname, filemask = filewalker.getFilesByWildcard(gameName)
                if(len(files) > 0):
                    self.mediaFiles[path.type] = files[0]
    """
                        
                  
    def getMediaFiles(self, gdb, fileTypes, fileDict, config):
        Logutil.log("ReleaseView.getMediaFile", util.LOG_LEVEL_DEBUG)
                     
        mediaFiles = []
        for fileType in fileTypes:
            files = File.getCachedFiles(gdb, fileType, self.id, fileDict)
            if(files != None):
                for mediaPath in config.mediaPaths:
                    if(mediaPath.type == fileType):
                        path = mediaPath.path
                dir = os.path.dirname(path)
                dir = dir.replace('%PLATFORM%', self.platformName) 
                
                for file in files:
                    filename = os.path.join(dir, file.name)
                    mediaFiles.append(filename)
            
        return mediaFiles
                    
               
            
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
    
    
    @staticmethod
    def getFilteredReleasesTest(gdb, platformId, genreId, yearId, publisherId, isFavorite, likeStatement):
        args = (platformId, genreId, yearId, publisherId, isFavorite)
        filterQuery = ReleaseView.filterQueryTest %likeStatement
        util.Logutil.log('searching games with query: ' +filterQuery, util.LOG_LEVEL_DEBUG)
        util.Logutil.log('searching games with args: platformId = %s, genreId = %s, yearId = %s, publisherId = %s, isFavorite = %s, characterFilter = %s' %(str(platformId), str(genreId), str(yearId), str(publisherId), str(isFavorite), likeStatement), util.LOG_LEVEL_DEBUG)
        dbRows = DataBaseObject.getByWildcardQuery(gdb, filterQuery, args)        
        objs = []
        for dbRow in dbRows:
            obj = ReleaseView()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
