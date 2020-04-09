from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
import os, shutil
from sqlite3 import dbapi2 as sqlite

from util import *
import util

Logutil.log("Loading sqlite3 as DB engine", util.LOG_LEVEL_INFO)


class GameDataBase(object):

    def __init__(self, databaseDir):
        self.dataBasePath = os.path.join(databaseDir, 'MyGames.db')
        sqlite.register_adapter(str, lambda s: util.convertToUnicodeString(s))
        #use scripts home for reading SQL files
        self.sqlDir = os.path.join(util.RCBHOME, 'resources', 'database')

    def connect(self):
        print (self.dataBasePath)
        self.connection = sqlite.connect(self.dataBasePath, check_same_thread=False)

        # Use row factory so we can retrieve values by column name
        self.connection.row_factory = sqlite.Row

        self.cursor = self.connection.cursor()
        #set cache size to 20000 pages (default is 2000)
        self.cursor.execute("PRAGMA cache_size = 20000")

    def commit(self):
        try:
            self.connection.commit()
            return True
        except:
            return False

    def close(self):
        print ("close Connection")
        self.connection.close()

    def compact(self):
        self.cursor.execute("VACUUM")

    def toMem(self):
        try:
            memDB = sqlite.connect(':memory:', check_same_thread=False)
            dump = os.linesep.join([line for line in self.connection.iterdump()])
            memDB.executescript(dump)
            self.connection.close()
            self.connection = memDB
            self.cursor = memDB.cursor()
            return True
        except Exception as e:
            util.Logutil.log("ERROR: %s" % str(e), util.LOG_LEVEL_INFO)
            return False

    def toDisk(self):
        try:
            self.connection.commit()
            os.remove(self.dataBasePath)
            diskDB = sqlite.connect(self.dataBasePath)
            dump = os.linesep.join([line for line in self.connection.iterdump()])
            diskDB.executescript(dump)
            self.connection.close()
            self.connection = diskDB
            self.cursor = diskDB.cursor()
            return True
        except Exception as e:
            util.Logutil.log("ERROR: %s" % str(e), util.LOG_LEVEL_INFO)
            return False

    def executeSQLScript(self, scriptName):
        sqlCreateFile = open(scriptName, 'r')
        sqlCreateString = sqlCreateFile.read()
        self.connection.executescript(sqlCreateString)

    def createTables(self):
        print ("Create Tables")
        self.executeSQLScript(os.path.join(self.sqlDir, 'SQL_CREATE.txt'))
        RCBSetting(self).insert((None, 0, 0, 0, 0, 0, None, util.CURRENT_DB_VERSION, None, None, 0, 0, 0, 0, None, None))

    def dropTables(self):
        print ("Drop Tables")
        self.executeSQLScript(os.path.join(self.sqlDir, 'SQL_DROP_ALL.txt'))

    def checkDBStructure(self):

        #returnValues: -1 error, 0=nothing, 1=import Games, 2=idLookupFile created

        dbVersion = ""
        try:
            rcbSettingRows = RCBSetting(self).getAll()
            if rcbSettingRows == None or len(rcbSettingRows) != 1:
                self.createTables()
                self.commit()
                return 1, ""
            rcbSetting = rcbSettingRows[0]

            dbVersion = rcbSetting[RCBSetting.COL_dbVersion]

        except Exception as exc:
            self.createTables()
            self.commit()
            return 1, ""

        #Upgrade to new db layout
        if dbVersion != util.CURRENT_DB_VERSION:

            #backup MyGames.db
            #newFileName = self.dataBasePath + '.backup ' + dbVersion
            newFileName = '{0}{1}{2}'.format(self.dataBasePath, '.backup ', dbVersion)

            if os.path.isfile(newFileName):
                #32030: Error: Cannot backup MyGames.db: Backup File exists.
                return -1, util.localize(32030)
            try:
                self.close()
                shutil.copy(str(self.dataBasePath), str(newFileName))
                self.connect()
            except Exception as exc:
                #32031: Error: Cannot backup MyGames.db
                return -1, util.localize(32031) + ": " + str(exc)

            #execute all upgrade scripts from old db version to current db version
            while True:
                alterTableScript = "SQL_UPGRADE_%s.txt" % dbVersion
                alterTableScript = str(os.path.join(self.sqlDir, alterTableScript))

                if os.path.isfile(alterTableScript):
                    self.executeSQLScript(alterTableScript)
                    self.commit()

                    rcbSettingRows = RCBSetting(self).getAll()
                    dbVersion = rcbSettingRows[0][RCBSetting.COL_dbVersion]

                    if dbVersion == util.CURRENT_DB_VERSION:
                        break
                else:
                    #32032: Error: No Update from version %s to %s.
                    return -1, util.localize(32032) % (dbVersion, util.CURRENT_DB_VERSION)

        # VACUUM database
        self.compact()

        count = Game(self).getCount()
        if (count == 0):
            return 1, ""

        return 0, ""


class DataBaseObject(object):

    COL_ID = 0
    COL_NAME = 1

    def __init__(self, gdb, tableName):
        self.gdb = gdb
        self.tableName = tableName

    def insert(self, args):
        paramsString = ("?, " * len(args))
        paramsString = paramsString[0:len(paramsString) - 2]
        insertString = "Insert INTO %(tablename)s VALUES (NULL, %(args)s)" % {'tablename': self.tableName,
                                                                              'args': paramsString}
        self.gdb.cursor.execute(insertString, args)
        if self.gdb.cursor.rowcount == 1:
            util.Logutil.log("inserted values " + str(args) + self.tableName, util.LOG_LEVEL_DEBUG)
        else:
            util.Logutil.log("failed to insert values " + str(args) + self.tableName, util.LOG_LEVEL_WARNING)

    #print("Insert INTO %(tablename)s VALUES (%(args)s)" % {'tablename':self.tableName, 'args': ( "?, " * len(args)) })

    def update(self, columns, argsOrig, obj_id, updateWithNullValues):

        if len(columns) != len(argsOrig):
            util.Logutil.log("len columns != len args in gdb.update()", util.LOG_LEVEL_WARNING)
            return

        args = []
        updateString = "Update %s SET " % self.tableName
        for i in range(0, len(columns)):

            #don't update with empty values
            if not updateWithNullValues and (argsOrig[i] == '' or argsOrig[i] == None):
                continue

            if i > 0:
                updateString += ", "

            args.append(argsOrig[i])
            updateString += columns[i] + " = ?"

        updateString += " WHERE id = " + str(obj_id)
        self.gdb.cursor.execute(updateString, args)

    def deleteAll(self):
        self.gdb.cursor.execute("DELETE FROM '%s'" % self.tableName)

    def deleteObjectByQuery(self, query, args):
        self.gdb.cursor.execute(query, args)

    def getCount(self):
        self.gdb.cursor.execute("SELECT count(*) From '%s'" % self.tableName)
        count = self.gdb.cursor.fetchall()
        return count[0][0]

    def getAll(self):
        self.gdb.cursor.execute("SELECT * FROM '%s'" % self.tableName)
        allObjects = self.gdb.cursor.fetchall()
        #newList = self.encodeUtf8(allObjects)
        return allObjects

    def getAllOrdered(self):
        self.gdb.cursor.execute("SELECT * FROM '%s' ORDER BY name COLLATE NOCASE" % self.tableName)
        allObjects = self.gdb.cursor.fetchall()
        #newList = self.encodeUtf8(allObjects)
        return allObjects

    def getOneByName(self, name):
        self.gdb.cursor.execute("SELECT * FROM '%s' WHERE name = ?" % self.tableName, (name,))
        obj = self.gdb.cursor.fetchone()
        return obj

    def getObjectById(self, obj_id):
        self.gdb.cursor.execute("SELECT * FROM '%s' WHERE id = ?" % self.tableName, (obj_id,))
        obj = self.gdb.cursor.fetchone()
        return obj

    def getObjectsByWildcardQuery(self, query, args):
        #double Args for WildCard-Comparison (0 = 0)
        newArgs = []
        for arg in args:
            newArgs.append(arg)
            newArgs.append(arg)

        return self.getObjectsByQuery(query, newArgs)

    def getObjectsByQuery(self, query, args):
        self.gdb.cursor.execute(query, args)
        allObjects = self.gdb.cursor.fetchall()
        return allObjects

    def getObjectsByQueryNoArgs(self, query):
        self.gdb.cursor.execute(query)
        allObjects = self.gdb.cursor.fetchall()
        return allObjects

    def getObjectByQuery(self, query, args):
        self.gdb.cursor.execute(query, args)
        obj = self.gdb.cursor.fetchone()
        return obj

    def getFileAllFilesByRCId(self, obj_id):
        self.gdb.cursor.execute(
            'select File.name from File, Game where Game.romcollectionid=? and File.parentId=Game.id and File.fileTypeId=0',
            (obj_id,))
        objects = self.gdb.cursor.fetchall()
        results = [r[0] for r in objects]
        return results

    def encodeUtf8(self, itemlist):
        newList = []
        for item in itemlist:
            newItem = []
            for param in item:
                if type(param).__name__ == 'str':
                    newItem.append(param.encode('utf-8'))
                else:
                    newItem.append(param)
            newList.append(newItem)
        return newList


class gameobj(object):
    """This class contains all the logic for the Game object, separate from the database implementation.
    """

    def __init__(self):
        """Set default values for specific fields"""
        self.name = ''
        self.id = -1
        self.romCollectionId = -1
        self.yearId = -1
        self.publisherId = -1
        self.developerId = -1
        self.reviewerId = -1

    def __repr__(self):
        return "<game: %s>" % self.__dict__

    #Property decorators are used to format the return data in some way, or to translate from a DB column
    #name to how it is actually used in the skin or the calling method

    @property
    def gameId(self):
        # Used to store the ID in the lists, where a unicode string is required rather than an integer
        return str(self.id)

    @property
    def isfavorite(self):
        if self.isFavorite == 1:
            return '1'
        else:
            return ''

    @property
    def plot(self):
        if self.description is None:
            return ''
        return util.html_to_kodi(self.description)

    @property
    def maxplayers(self):
        return str(self.maxPlayers)

    @property
    def votes(self):
        return str(self.numVotes)

    @property
    def playcount(self):
        return str(self.launchCount)

    @property
    def genre(self):
        return self.genres


class Game(DataBaseObject):
    #column index of table Game (for writing game data)
    COL_description = 2
    COL_gameCmd = 3
    COL_alternateGameCmd = 4
    COL_romCollectionId = 5
    COL_publisherId = 6
    COL_developerId = 7
    COL_yearId = 8
    COL_maxPlayers = 9
    COL_rating = 10
    COL_numVotes = 11
    COL_url = 12
    COL_region = 13
    COL_media = 14
    COL_perspective = 15
    COL_controllerType = 16
    COL_isFavorite = 17
    COL_launchCount = 18
    COL_originalTitle = 19
    COL_alternateTitle = 20
    COL_translatedBy = 21
    COL_version = 22
    COL_fileType1 = 23
    COL_fileType2 = 24
    COL_fileType3 = 25
    COL_fileType4 = 26
    COL_fileType5 = 27
    COL_fileType6 = 28
    COL_fileType7 = 29
    COL_fileType8 = 30
    COL_fileType9 = 31
    COL_fileType10 = 32
    COL_fileType11 = 33
    COL_fileType12 = 34
    COL_fileType13 = 35
    COL_fileType14 = 36
    COL_fileType15 = 37

    #this list uses the same order as the fields in table game
    #this way we can use game[Game.COL_fieldname] to get the correct field name (e.g. game[Game.COL_developer])
    FIELDNAMES = [
        'id',
        'name',
        'description',
        'gameCmd',
        'alternateGameCmd',
        'romCollectionId',
        'publisherId',
        'developerId',
        'yearId',
        'maxPlayers',
        'rating',
        'numVotes',
        'url',
        'region',
        'media',
        'perspective',
        'controllerType',
        'isFavorite',
        'launchCount',
        'originalTitle',
        'alternateTitle',
        'translatedBy',
        'version',
        'fileType1',
        'fileType2',
        'fileType3',
        'fileType4',
        'fileType5',
        'fileType6',
        'fileType7',
        'fileType8',
        'fileType9',
        'fileType10',
        'fileType11',
        'fileType12',
        'fileType13',
        'fileType14',
        'fileType15'
    ]

    deleteQuery = "DELETE FROM Game WHERE id = ?"

    def __init__(self, gdb):
        self.gdb = gdb
        self.tableName = "Game"

    def delete(self, gameId):
        self.deleteObjectByQuery(self.deleteQuery, (gameId,))


class GameView(DataBaseObject):

    #column index of GameView (for reading game data)
    COL_description = 2
    COL_gameCmd = 3
    COL_alternateGameCmd = 4
    COL_isFavorite = 5
    COL_launchCount = 6
    COL_version = 7
    COL_romCollectionId = 8
    COL_developerId = 9
    COL_developer = 10
    COL_publisherId = 11
    COL_publisher = 12
    COL_yearId = 13
    COL_year = 14
    COL_region = 15
    COL_maxPlayers = 16
    COL_rating = 17
    COL_numVotes = 18
    COL_url = 19
    COL_media = 20
    COL_controllerType = 21
    COL_originalTitle = 22
    COL_alternateTitle = 23
    COL_translatedBy = 24
    COL_perspective = 25
    COL_genre = 26
    COL_fileType1 = 27
    COL_fileType2 = 28
    COL_fileType3 = 29
    COL_fileType4 = 30
    COL_fileType5 = 31
    COL_fileType6 = 32
    COL_fileType7 = 33
    COL_fileType8 = 34
    COL_fileType9 = 35
    COL_fileType10 = 36
    COL_fileType11 = 37
    COL_fileType12 = 38
    COL_fileType13 = 39
    COL_fileType14 = 40
    COL_fileType15 = 41

    #this list uses the same order as the fields in Game View
    #this way we can use game[GameView.COL_fieldname] to get the correct field name (e.g. game[GameView.COL_developer])
    FIELDNAMES = [
        'id',
        'name',
        'description',
        'gameCmd',
        'alternateGameCmd',
        'isFavorite',
        'launchCount',
        'version',
        'romCollectionId',
        'developerId',
        'developer',
        'publisherId',
        'publisher',
        'yearId',
        'year',
        'region',
        'maxPlayers',
        'rating',
        'numVotes',
        'url',
        'media',
        'controllerType',
        'originalTitle',
        'alternateTitle',
        'translatedBy',
        'perspective',
        'genres',
        'fileType1',
        'fileType2',
        'fileType3',
        'fileType4',
        'fileType5',
        'fileType6',
        'fileType7',
        'fileType8',
        'fileType9',
        'fileType10',
        'fileType11',
        'fileType12',
        'fileType13',
        'fileType14',
        'fileType15'
    ]

    NUM_COLUMNS = 42

    filterQuery = "Select * From GameView WHERE \
                    (romCollectionId = ? OR (0 = ?)) AND \
                    (Id IN (Select GameId From GenreGame Where GenreId = ?) OR (0 = ?)) AND \
                    (YearId = ? OR (0 = ?)) AND \
                    (PublisherId = ? OR (0 = ?)) AND \
                    (DeveloperId = ? OR (0 = ?)) AND \
                    (isFavorite = ? OR (0 = ?)) AND \
                    (maxPlayers = ? OR (0 = ?)) AND \
                    (rating >= ? OR (0 = ?)) AND \
                    (region = ? OR (0 = ?)) AND \
                    %s \
                    %s \
                    %s"

    filterByGameByIdFromView = "SELECT * FROM GameView WHERE id = ?"

    filterByNameAndRomCollectionId = "SELECT * FROM GameView WHERE name = ? and romCollectionId = ?"

    filterMostPlayedGames = "Select * From GameView Where launchCount > 0 Order by launchCount desc Limit "

    filterQueryMaxPlayers = "SELECT DISTINCT maxPlayers FROM GameView WHERE \
                        (romCollectionId = ? OR (0 = ?)) AND \
                        (Id IN (Select GameId From GenreGame Where GenreId = ?) OR (0 = ?)) AND \
                        (YearId = ? OR (0 = ?)) AND \
                        (PublisherId = ? OR (0 = ?)) AND \
                        (DeveloperId = ? OR (0 = ?)) AND \
                        (rating >= ? OR (0 = ?)) AND \
                        (region = ? OR (0 = ?)) AND \
                        %s \
                        ORDER BY maxPlayers COLLATE NOCASE"

    filterQueryRegions = "SELECT DISTINCT region FROM GameView WHERE \
                            (romCollectionId = ? OR (0 = ?)) AND \
                            (Id IN (Select GameId From GenreGame Where GenreId = ?) OR (0 = ?)) AND \
                            (YearId = ? OR (0 = ?)) AND \
                            (PublisherId = ? OR (0 = ?)) AND \
                            (DeveloperId = ? OR (0 = ?)) AND \
                            (maxPlayers = ? OR (0 = ?)) AND \
                            (rating >= ? OR (0 = ?)) AND \
                            %s \
                            ORDER BY region COLLATE NOCASE"

    def __init__(self, gdb):
        self.gdb = gdb
        self.tableName = "GameView"

    def getFilteredGames(self, romCollectionId, genreId, yearId, publisherId, developerId, maxPlayers, rating, region,
                         isFavorite, likeStatement, order_by, maxNumGames=0):
        args = (romCollectionId, genreId, yearId, publisherId, developerId, isFavorite, maxPlayers, rating, region)
        limit = ""
        if int(maxNumGames) > 0:
            limit = "LIMIT %s" % str(maxNumGames)
        filterQuery = self.filterQuery % (likeStatement, order_by, limit)
        util.Logutil.log('searching games with query: ' + filterQuery, util.LOG_LEVEL_INFO)
        util.Logutil.log(
            'searching games with args: romCollectionId = %s, genreId = %s, yearId = %s, publisherId = %s, '
            'developerId = %s, maxPlayers = %s, rating = %s, region = %s, isFavorite = %s, likeStatement = %s, '
            'limit = %s' % (str(romCollectionId), str(genreId), str(yearId), str(publisherId), str(developerId),
                            maxPlayers, str(rating), region, str(isFavorite), likeStatement, limit),
            util.LOG_LEVEL_INFO)
        games = self.getObjectsByWildcardQuery(filterQuery, args)
        #newList = self.encodeUtf8(games)
        return games

    def getGameByNameAndRomCollectionId(self, name, romCollectionId):
        game = self.getObjectByQuery(self.filterByNameAndRomCollectionId, (name, romCollectionId))
        return game

    def getGamesByQuery(self, query, args):
        return self.getObjectsByQuery(query, args)

    def getGamesByQueryNoArgs(self, query):
        return self.getObjectsByQueryNoArgs(query)

    def getGameById(self, gameid):
        try:
            dbobj = self.getObjectByQuery(self.filterByGameByIdFromView, (gameid,))
        except Exception as e:
            print ('Error mapping game row to object: ' + e.message)
            return None
        return dbobj

    def getFilteredMaxPlayers(self, romCollectionId, genreId, yearId, publisherId, developerId, rating, region, likeStatement):
        args = (romCollectionId, genreId, yearId, publisherId, developerId, rating, region)
        filterQuery = self.filterQueryMaxPlayers % likeStatement
        util.Logutil.log('searching maxPlayers with query: ' + filterQuery, util.LOG_LEVEL_DEBUG)
        players = self.getObjectsByWildcardQuery(filterQuery, args)
        return players

    def getFilteredRegions(self, romCollectionId, genreId, yearId, publisherId, developerId, maxPlayers, rating, likeStatement):
        args = (romCollectionId, genreId, yearId, publisherId, developerId, maxPlayers, rating)
        filterQuery = self.filterQueryRegions % likeStatement
        util.Logutil.log('searching regions with query: ' + filterQuery, util.LOG_LEVEL_DEBUG)
        regions = self.getObjectsByWildcardQuery(filterQuery, args)
        return regions


class RCBSetting(DataBaseObject):
    #column index of table Rcbsetting
    COL_lastSelectedView = 1
    COL_lastSelectedConsoleId = 2
    COL_lastSelectedGenreId = 3
    COL_lastSelectedPublisherId = 4
    COL_lastSelectedDeveloperId = 5
    COL_lastSelectedYearId = 6
    COL_lastSelectedGameIndex = 7
    COL_dbVersion = 8
    COL_lastFocusedControlMainView = 9
    COL_lastFocusedControlGameInfoView = 10
    COL_lastSelectedCharacter = 11
    COL_lastSelectedMaxPlayers = 12
    COL_lastSelectedRating = 13
    COL_lastSelectedRegion = 14
    COL_sortMethod = 15
    COL_sortDirection = 16
    
    def __init__(self, gdb):
        self.gdb = gdb
        self.tableName = "RCBSetting"


class Genre(DataBaseObject):
    filterQuery = "SELECT * FROM Genre WHERE Id IN (Select GenreId From GenreGame Where GameId IN ( \
                        Select Id From Game WHERE \
                        (romCollectionId = ? OR (0 = ?)) AND \
                        (YearId = ? OR (0 = ?)) AND \
                        (PublisherId = ? OR (0 = ?)) AND \
                        (DeveloperId = ? OR (0 = ?)) AND \
                        (maxPlayers = ? OR (0 = ?)) AND \
                        (rating >= ? OR (0 = ?)) AND \
                        (region = ? OR (0 = ?)) AND \
                        %s)) \
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
        self.gdb = gdb
        self.tableName = "Genre"

    def getFilteredGenres(self, romCollectionId, yearId, publisherId, developerId, maxPlayers, rating, region, likeStatement):
        args = (romCollectionId, yearId, publisherId, developerId, maxPlayers, rating, region)
        filterQuery = self.filterQuery % likeStatement
        util.Logutil.log('searching genres with query: ' + filterQuery, util.LOG_LEVEL_DEBUG)
        genres = self.getObjectsByWildcardQuery(filterQuery, args)
        return genres

    def getGenresByGameId(self, gameId):
        genres = self.getObjectsByQuery(self.filteGenreByGameId, (gameId,))
        return genres

    def getGenresForGame(self, gameId):
        """As per getGenresByGameId, but this joins the genres together so we don't need to do it client-side"""
        genres = self.getObjectsByQuery(self.filteGenreByGameId, (gameId,))
        genrestring = ', '.join(g['name'] for g in genres)
        return genrestring

    def getGenreIdByGameId(self, gameId):
        genreId = self.getObjectsByQuery(self.filteGenreIdByGameId, (gameId,))
        return genreId

    def delete(self, gameId):
        #genreId = self.getGenreIdByGameId(gameId)
        self.gdb.cursor.execute(self.genreIdCountQuery, (gameId,))
        obj = self.gdb.cursor.fetchall()
        if obj != None:
            for items in obj:
                if items[1] < 2:
                    util.Logutil.log("Delete Genre with id %s" % str(items[0]), util.LOG_LEVEL_INFO)
                    self.deleteObjectByQuery(self.genreDeleteQuery, (items[0],))
        util.Logutil.log("Delete GenreGame with gameId %s" % str(gameId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.genreGameDeleteQuery, (gameId,))


class GenreGame(DataBaseObject):
    filterQueryByGenreIdAndGameId = "Select * from GenreGame \
                    where genreId = ? AND \
                    gameId = ?"

    def __init__(self, gdb):
        self.gdb = gdb
        self.tableName = "GenreGame"

    def getGenreGameByGenreIdAndGameId(self, genreId, gameId):
        genreGame = self.getObjectByQuery(self.filterQueryByGenreIdAndGameId, (genreId, gameId))
        return genreGame


class Year(DataBaseObject):
    yearIdByGameIdQuery = "SELECT yearId From Game Where Id = ?"


    filterQuery = "SELECT * FROM Year WHERE Id IN (Select YearId From Game WHERE \
                        (romCollectionId = ? OR (0 = ?)) AND \
                        id IN (SELECT GameId From GenreGame Where GenreId = ? OR (0 = ?)) AND \
                        (PublisherId = ? OR (0 = ?)) AND \
                        (DeveloperId = ? OR (0 = ?)) AND \
                        (maxPlayers = ? OR (0 = ?)) AND \
                        (rating >= ? OR (0 = ?)) AND \
                        (region = ? OR (0 = ?)) AND \
                        %s) \
                        ORDER BY name COLLATE NOCASE"

    yearIdCountQuery = "SELECT count(yearId) 'yearIdCount' \
                    from Game \
                    where yearId = ? \
                    group by yearId"

    yearDeleteQuery = "DELETE FROM Year WHERE id = ?"

    def __init__(self, gdb):
        self.gdb = gdb
        self.tableName = "Year"

    def getYear(self, yearid):
        year = self.getObjectById(yearid)
        if year is None:
            return '1900'
        else:
            return year['name']

    def getYearIdByGameId(self, gameId):
        yearId = self.getObjectByQuery(self.yearIdByGameIdQuery, (gameId,))
        if yearId == None:
            return None
        else:
            return yearId[0]

    def getFilteredYears(self, romCollectionId, genreId, publisherId, developerId, maxPlayers, rating, region, likeStatement):
        args = (romCollectionId, genreId, publisherId, developerId, maxPlayers, rating, region)
        filterQuery = self.filterQuery % likeStatement
        util.Logutil.log('searching years with query: ' + filterQuery, util.LOG_LEVEL_DEBUG)
        years = self.getObjectsByWildcardQuery(filterQuery, args)
        return years

    def delete(self, gameId):
        yearId = self.getYearIdByGameId(gameId)
        if yearId != None:
            obj = self.getObjectByQuery(self.yearIdCountQuery, (yearId,))
            if obj[0] < 2:
                util.Logutil.log("Delete Year with id %s" % str(yearId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.yearDeleteQuery, (yearId,))


class Publisher(DataBaseObject):
    publisherIdByGameIdQuery = "SELECT publisherId From Game Where Id = ?"

    filterQuery = "SELECT * FROM Publisher WHERE Id IN (Select PublisherId From Game WHERE \
                        (romCollectionId = ? OR (0 = ?)) AND \
                        id IN (SELECT GameId From GenreGame Where GenreId = ? OR (0 = ?)) AND \
                        (YearId = ? OR (0 = ?)) AND \
                        (DeveloperId = ? OR (0 = ?)) AND \
                        (maxPlayers = ? OR (0 = ?)) AND \
                        (rating >= ? OR (0 = ?)) AND \
                        (region = ? OR (0 = ?)) AND \
                        %s) \
                        ORDER BY name COLLATE NOCASE"

    publisherIdCountQuery = "SELECT count(publisherId) 'publisherIdCount' \
                    from Game \
                    where publisherId = ? \
                    group by publisherId"

    publisherDeleteQuery = "DELETE FROM Publisher WHERE id = ?"

    def __init__(self, gdb):
        self.gdb = gdb
        self.tableName = "Publisher"

    def getPublisherIdByGameId(self, gameId):
        publisherId = self.getObjectByQuery(self.publisherIdByGameIdQuery, (gameId,))
        if publisherId == None:
            return None
        else:
            return publisherId[0]

    def getPublisher(self, publisherid):
        publisher = self.getObjectById(publisherid)
        if publisher is None:
            return 'Unknown'
        else:
            return publisher['name']

    def getPublisherForGame(self, gameId):
        """ As per getPublisherIdByGameId, but this returns the publisher name so we don't need to do it client-side """
        publisherId = self.getObjectByQuery(self.publisherIdByGameIdQuery, (gameId,))
        if publisherId is None:
            print ('Unable to find publisher for game with id ' + gameId)
            return 'Unknown'
        publisher = self.getObjectById(publisherId['publisherId'])

        if publisher is None:
            print ('Unable to find publisher for id ' + publisherId['publisherId'])
            return 'Unknown'

        return publisher['name']

    def getFilteredPublishers(self, romCollectionId, genreId, yearId, developerId, maxPlayers, rating, region, likeStatement):
        args = (romCollectionId, genreId, yearId, developerId, maxPlayers, rating, region)
        filterQuery = self.filterQuery % likeStatement
        util.Logutil.log('searching publishers with query: ' + filterQuery, util.LOG_LEVEL_DEBUG)
        publishers = self.getObjectsByWildcardQuery(filterQuery, args)
        return publishers

    def delete(self, gameId):
        publisherId = self.getPublisherIdByGameId(gameId)
        if publisherId != None:
            obj = self.getObjectByQuery(self.publisherIdCountQuery, (publisherId,))
            if (obj[0] < 2):
                util.Logutil.log("Delete Publisher with id %s" % str(publisherId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.publisherDeleteQuery, (publisherId,))


class Developer(DataBaseObject):
    filterQuery = "SELECT * FROM Developer WHERE Id IN (Select DeveloperId From Game WHERE \
                            (romCollectionId = ? OR (0 = ?)) AND \
                            id IN (SELECT GameId From GenreGame Where GenreId = ? OR (0 = ?)) AND \
                            (YearId = ? OR (0 = ?)) AND \
                            (PublisherId = ? OR (0 = ?)) AND \
                            (maxPlayers = ? OR (0 = ?)) AND \
                            (rating >= ? OR (0 = ?)) AND \
                            (region = ? OR (0 = ?)) AND \
                            %s) \
                            ORDER BY name COLLATE NOCASE"

    developerIdByGameIdQuery = "SELECT developerId From Game Where Id = ?"

    developerIdCountQuery = "SELECT count(developerId) 'developerIdCount' \
                    from Game \
                    where developerId = ? \
                    group by developerId"

    developerDeleteQuery = "DELETE FROM Developer WHERE id = ?"

    def __init__(self, gdb):
        self.gdb = gdb
        self.tableName = "Developer"

    def getDeveloperIdByGameId(self, gameId):
        developerId = self.getObjectByQuery(self.developerIdByGameIdQuery, (gameId,))
        if developerId == None:
            return None
        else:
            return developerId[0]

    def getDeveloper(self, developerid):
        developer = self.getObjectById(developerid)
        if developer is None:
            return 'Unknown'
        else:
            return developer['name']

    def getFilteredDevelopers(self, romCollectionId, genreId, yearId, publisherId, maxPlayers, rating, region, likeStatement):
        args = (romCollectionId, genreId, yearId, publisherId, maxPlayers, rating, region)
        filterQuery = self.filterQuery % likeStatement
        util.Logutil.log('searching developers with query: ' + filterQuery, util.LOG_LEVEL_DEBUG)
        developers = self.getObjectsByWildcardQuery(filterQuery, args)
        return developers

    def getDeveloperForGame(self, gameId):
        """ As per getDeveloperIdByGameId, but this returns the publisher name so we don't need to do it client-side """
        developerId = self.getObjectByQuery(self.developerIdByGameIdQuery, (gameId,))

        if developerId is None:
            print ('Unable to find developer for game with id ' + gameId)
            return 'Unknown'
        developer = self.getObjectById(developerId['developerId'])

        if developer is None:
            print ('Unable to find developer for id ' + developerId['developerId'])
            return 'Unknown'

        return developer['name']

    def delete(self, gameId):
        developerId = self.getDeveloperIdByGameId(gameId)
        if developerId != None:
            obj = self.getObjectByQuery(self.developerIdCountQuery, (developerId,))
            if obj[0] < 2:
                util.Logutil.log("Delete Developer with id %s" % str(developerId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.developerDeleteQuery, (developerId,))


class File(DataBaseObject):
    COL_fileTypeId = 2
    COL_parentId = 3

    filterQueryByGameIdAndFileType = "Select name from File \
                    where parentId = ? AND \
                    filetypeid = ?"

    filterQueryByNameAndType = "Select * from File \
                    where name = ? AND \
                    filetypeid = ?"

    filterQueryByNameAndTypeAndParent = "Select * from File \
                    where name = ? AND \
                    filetypeid = ? AND \
                    parentId = ?"

    filterQueryByGameIdAndTypeId = "Select * from File \
                    where parentId = ? AND \
                    filetypeid = ?"

    filterFilesForGameList = "Select * from File Where FileTypeId in (%s)"

    filterQueryByParentIds = "Select * from File \
                    where parentId in (?, ?, ?, ?)"

    getFileList = "SELECT * FROM File WHERE filetypeid = 0"

    deleteQuery = "DELETE FROM File WHERE parentId= ?"

    deleteFileQuery = "DELETE FROM File WHERE Id= ?"

    def __init__(self, gdb):
        self.gdb = gdb
        self.tableName = "File"

    def getFileByNameAndType(self, name, filetype):
        f = self.getObjectByQuery(self.filterQueryByNameAndType, (name, filetype))
        return f

    def getFileByNameAndTypeAndParent(self, name, filetype, parentId):
        f = self.getObjectByQuery(self.filterQueryByNameAndTypeAndParent, (name, filetype, parentId))
        return f

    def getFilesByNameAndType(self, name, filetype):
        files = self.getObjectsByQuery(self.filterQueryByNameAndType, (name, filetype))
        return files

    def getFilesByGameIdAndTypeId(self, gameId, fileTypeId):
        files = self.getObjectsByQuery(self.filterQueryByGameIdAndTypeId, (gameId, fileTypeId))
        return files

    def getFilenameByGameIdAndTypeId(self, gameId, fileTypeId):
        """Get the filename (i.e. full path) for a game ID and filetype ID"""
        f = self.getObjectByQuery(self.filterQueryByGameIdAndTypeId, (gameId, fileTypeId))
        if f is None:
            return ''
        return f[DataBaseObject.COL_NAME]

    def getRomsByGameId(self, gameId):
        files = self.getObjectsByQuery(self.filterQueryByGameIdAndFileType, (gameId, 0))
        return files

    def getFilesForGamelist(self, fileTypeIds):
        files = self.getObjectsByQueryNoArgs(self.filterFilesForGameList % (','.join(fileTypeIds)))
        return files

    def getFilesByParentIds(self, gameId, romCollectionId, publisherId, developerId):
        files = self.getObjectsByQuery(self.filterQueryByParentIds, (gameId, romCollectionId, publisherId, developerId))
        return files

    def delete(self, gameId):
        util.Logutil.log("Delete Files with gameId %s" % str(gameId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.deleteQuery, (gameId,))

    def deleteByFileId(self, fileId):
        util.Logutil.log("Delete File with id %s" % str(fileId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.deleteFileQuery, (fileId,))

    def getFilesList(self):
        files = self.getObjectsByQueryNoArgs(self.getFileList)
        return files
