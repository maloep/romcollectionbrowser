

import os, sys

#taken from apple movie trailer script (thanks to Nuka1195 and others)
# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

from pysqlite2 import dbapi2 as sqlite

CURRENT_SCRIPT_VERSION = "V0.4"


class GameDataBase:	
	
	def __init__(self, databaseDir):
		self.databaseDir = databaseDir
		self.dataBasePath = os.path.join(self.databaseDir, 'MyGames.db')		
		self.connect()
		
		#TODO check if db exists
		#TODO check DB Update (ALTER Tables)
		#self.checkDBStructure()
		self.createTables()
		self.commit()
		self.close()
		
	def connect( self ):		
		self.connection = sqlite.connect(self.dataBasePath)
		self.cursor = self.connection.cursor()
		
	def commit( self ):		
		try:
			self.connection.commit()
			return True
		except: return False

	def close( self ):
		print "close Connection"
		self.connection.close()
	
	def executeSQLScript(self, scriptName):
		sqlCreateFile = open(scriptName, 'r')
		sqlCreateString = sqlCreateFile.read()						
		self.connection.executescript(sqlCreateString)		
	
	def createTables(self):
		print "Create Tables"
		self.executeSQLScript(os.path.join(self.databaseDir, 'SQL_CREATE.txt'))
		
	def dropTables(self):
		print "Drop Tables"
		self.executeSQLScript(os.path.join(self.databaseDir, 'SQL_DROP_ALL.txt'))

	
	def checkDBStructure(self):				
		
		print "checkDBStructure"
		dbVersion = ""
		try:
			rcbSettingRows = RCBSetting(self).getAll()
			if(rcbSettingRows == None or len(rcbSettingRows) != 1):	
				print "return no rows"
				return
			rcbSetting = rcbSettingRows[0]
			dbVersion = rcbSetting[10]
			
		except  Exception, (exc): 
			print "return exc: " +str(exc)
			return
		
		print dbVersion
		print CURRENT_SCRIPT_VERSION
		
		#Alter Table
		if(dbVersion != CURRENT_SCRIPT_VERSION):
			alterTableScript = "SQL_ALTER_%(old)s_%(new)s.txt" %{'old': dbVersion, 'new':CURRENT_SCRIPT_VERSION}
			print alterTableScript
			self.executeSQLScript(str(os.path.join(self.databaseDir, alterTableScript)))
			
	
	

class DataBaseObject:
	
	def __init__(self, gdb, tableName):
		self.gdb = gdb
		self.tableName = tableName
	
	def insert(self, args):		
		paramsString = ( "?, " * len(args))
		paramsString = paramsString[0:len(paramsString)-2]
		insertString = "Insert INTO %(tablename)s VALUES (NULL, %(args)s)" % {'tablename':self.tableName, 'args': paramsString }		
		self.gdb.cursor.execute(insertString, args)
		
		#print("Insert INTO %(tablename)s VALUES (%(args)s)" % {'tablename':self.tableName, 'args': ( "?, " * len(args)) })
		
	
	def update(self, columns, args, id):
		
		if(len(columns) != len(args)):
			#TODO raise Exception?			
			return
			
		updateString = "Update %s SET " %self.tableName
		for i in range(0, len(columns)):
			updateString += columns[i] +  " = ?"
			if(i < len(columns) -1):
				updateString += ", "
				
		updateString += " WHERE id = " +str(id)		
		self.gdb.cursor.execute(updateString, args)
		
	
	def deleteAll(self):
		self.gdb.cursor.execute("DELETE FROM '%s'" % self.tableName)		
	
	
	def getAll(self):
		self.gdb.cursor.execute("SELECT * FROM '%s'" % self.tableName)
		allObjects = self.gdb.cursor.fetchall()
		return allObjects
		
		
	def getAllOrdered(self):
		self.gdb.cursor.execute("SELECT * FROM '%s' ORDER BY name" % self.tableName)
		allObjects = self.gdb.cursor.fetchall()
		return allObjects
		
		
	def getOneByName(self, name):			
		self.gdb.cursor.execute("SELECT * FROM '%s' WHERE name = ?" % self.tableName, (name,))
		object = self.gdb.cursor.fetchone()
		return object
		
	def getObjectById(self, id):
		self.gdb.cursor.execute("SELECT * FROM '%s' WHERE id = ?" % self.tableName, (id,))
		object = self.gdb.cursor.fetchone()		
		return object	
	
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

	def getObjectByQuery(self, query, args):		
		self.gdb.cursor.execute(query, args)
		object = self.gdb.cursor.fetchone()		
		return object


class Game(DataBaseObject):	
	filterQuery = "Select * From Game WHERE \
					(RomCollectionId IN (Select Id From RomCollection Where ConsoleId = ?) OR (0 = ?)) AND \
					(Id IN (Select GameId From GenreGame Where GenreId = ?) OR (0 = ?)) AND \
					(YearId = ? OR (0 = ?)) AND \
					(PublisherId = ? OR (0 = ?)) \
					ORDER BY name"
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Game"
		
	def getFilteredGames(self, consoleId, genreId, yearId, publisherId):
		args = (consoleId, genreId, yearId, publisherId)
		games = self.getObjectsByWildcardQuery(self.filterQuery, args)
		return games


class Console(DataBaseObject):	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Console"


class RCBSetting(DataBaseObject):	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "RCBSetting"


class RomCollection(DataBaseObject):	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "RomCollection"


class Genre(DataBaseObject):
	
	filteGenreByGameId = "SELECT * FROM Genre WHERE Id IN (Select GenreId From GenreGame Where GameId = ?)"
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Genre"
		
	def getGenresByGameId(self, gameId):
		genres = self.getObjectsByQuery(self.filteGenreByGameId, (gameId,))
		return genres


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
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Year"


class Publisher(DataBaseObject):	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Publisher"
		

class Developer(DataBaseObject):
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Developer"
		
class Reviewer(DataBaseObject):
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Reviewer"


class FileType(DataBaseObject):	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "FileType"
		
		
class FileTypeForControl(DataBaseObject):
	filterQueryByKey = "Select * from FileTypeForControl \
					where romCollectionId = ? AND \
					fileTypeId = (select id from filetype where name = ?) AND \
					control = ? AND \
					priority = ?"
					
	filterQueryByKeyNoPrio = "Select * from FileTypeForControl \
					where romCollectionId = ? AND \
					control = ? \
					ORDER BY priority"
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "FileTypeForControl"
		
	def getFileTypeForControlByKey(self, romCollectionId, fileType, control, priority):
		fileType = self.getObjectByQuery(self.filterQueryByKey, (romCollectionId, fileType, control, priority))
		return fileType
		
	def getFileTypesForControlByKey(self, romCollectionId, control):
		fileTypes = self.getObjectsByQuery(self.filterQueryByKeyNoPrio, (romCollectionId, control))
		return fileTypes


class File(DataBaseObject):	
	filterQueryByGameIdAndFileType = "Select name from File \
					where gameId = ? AND \
					filetypeid = (select id from filetype where name = ?)"
					
	filterQueryByNameAndType = "Select * from File \
					where name = ? AND \
					filetypeid = (select id from filetype where name = ?)"
					
	filterQueryByGameIdAndTypeId = "Select * from File \
					where gameId = ? AND \
					filetypeid = ?"
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "File"
			
	def getFileByNameAndType(self, name, type):
		file = self.getObjectByQuery(self.filterQueryByNameAndType, (name, type))
		return file
		
	def getFilesByNameAndType(self, name, type):
		files = self.getObjectsByQuery(self.filterQueryByNameAndType, (name, type))
		return files
		
	def getFilesByFileGameIdAndTypeId(self, gameId, fileTypeId):
		files = self.getObjectsByQuery(self.filterQueryByGameIdAndTypeId, (gameId, fileTypeId))
		return files
		
	def getIngameScreenshotByGameId(self, gameId):
		file = self.getObjectByQuery(self.filterQueryByGameIdAndFileType, (gameId, 'screenshotingame'))
		if file == None:
			return ""		
		return file[0]
		
	def getIngameScreenshotsByGameId(self, gameId):
		files = self.getObjectsByQuery(self.filterQueryByGameIdAndFileType, (gameId, 'screenshotingame'))		
		return files
		
	def getTitleScreenshotsByGameId(self, gameId):
		files = self.getObjectsByQuery(self.filterQueryByGameIdAndFileType, (gameId, 'screenshottitle'))		
		return files
		
	def getCartridgesByGameId(self, gameId):
		files = self.getObjectsByQuery(self.filterQueryByGameIdAndFileType, (gameId, 'cartridge'))	
		return files
		
	def getIngameVideosByGameId(self, gameId):
		files = self.getObjectsByQuery(self.filterQueryByGameIdAndFileType, (gameId, 'ingamevideo'))
		return files
		
	def getCoverByGameId(self, gameId):
		file = self.getObjectByQuery(self.filterQueryByGameIdAndFileType, (gameId, 'cover'))
		if file == None:
			return ""		
		return file[0]
		
	def getCoversByGameId(self, gameId):
		files = self.getObjectsByQuery(self.filterQueryByGameIdAndFileType, (gameId, 'cover'))			
		return files
		
	def getRomsByGameId(self, gameId):
		files = self.getObjectsByQuery(self.filterQueryByGameIdAndFileType, (gameId, 'rom'))
		return files
		

class Path(DataBaseObject):	
	filterQueryByRomCollectionIdAndFileType = "Select name from Path \
					where romCollectionId = ? AND \
					filetypeid = (select id from filetype where name = ?)"
					
	filterQueryByNameAndType = "Select name from Path \
					where name = ? AND \
					filetypeid = (select id from filetype where name = ?)"
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Path"
		
	def getPathByNameAndType(self, name, type):
		file = self.getObjectByQuery(self.filterQueryByNameAndType, (name, type))
		return file
		
	def getRomPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'rom'))
		return path
		
	def getDescriptionPathByRomCollectionId(self, romCollectionId):
		path = self.getObjectByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'description'))
		if path == None:
			return ""	
		return path[0]
		
	def getIngameScreenshotPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'screenshotingame'))
		return path
		
	def getTitleScreenshotPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'screenshottitle'))
		return path
		
	def getCoverPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'cover'))
		return path
		
	def getCartridgePathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'cartridge'))
		return path
		
	def getManualPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'manual'))
		return path
		
	def getIngameVideoPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'ingamevideo'))
		return path
		
	def getTrailerPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'trailer'))
		return path
		
	def getConfigurationPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery(self.filterQueryByRomCollectionIdAndFileType, (romCollectionId, 'configuration'))
		return path
		
