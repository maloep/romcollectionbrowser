

import os, sys

#taken from apple movie trailer script (thanks to Nuka1195 and others)
# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

from pysqlite2 import dbapi2 as sqlite


class GameDataBase:	
	
	def __init__(self, databaseDir):
		self.databaseDir = databaseDir
		self.dataBasePath = os.path.join(self.databaseDir, 'MyGames.db')		
		self.connect()
		#TODO check if db exists
		self.createTables()
		self.commit()
		self.close()
		
	def connect( self ):
		print "connect to " +self.dataBasePath
		self.connection = sqlite.connect(self.dataBasePath)
		self.cursor = self.connection.cursor()
		
	def commit( self ):
		print "commit"
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
		
	def insertTestData(self):
		print "Insert Test Data"
		self.executeSQLScript(os.path.join(self.databaseDir, 'SQL_INSERT_TEST_DATA.txt'))	
	
	def prepareTestDataBase(self):
		print "prepareTestDataBase"		
		self.dropTables()		
		self.createTables()		
		self.insertTestData()
		self.commit()
		print "Ready"		
	

class DataBaseObject:
	
	def __init__(self, gdb, tableName):
		self.gdb = gdb
		self.tableName = tableName
	
	def insert(self, args):		
		paramsString = ( "?, " * len(args))
		paramsString = paramsString[0:len(paramsString)-2]
		insertString = "Insert INTO %(tablename)s VALUES (NULL, %(args)s)" % {'tablename':self.tableName, 'args': paramsString }
		print insertString
		self.gdb.cursor.execute(insertString, args)
		
		#print("Insert INTO %(tablename)s VALUES (%(args)s)" % {'tablename':self.tableName, 'args': ( "?, " * len(args)) })
	
	def getAll(self):
		self.gdb.cursor.execute("SELECT * FROM '%s'" % self.tableName)
		allObjects = self.gdb.cursor.fetchall()		
		return allObjects
		
	def getOneByName(self, name):			
		self.gdb.cursor.execute("SELECT * FROM '%s' WHERE name = ?" % self.tableName, (name,))
		object = self.gdb.cursor.fetchone()
		return object
	
	
	def getObjectsByWildcardQuery(self, args):		
		#double Args for WildCard-Comparison (0 = 0)
		newArgs = []
		for arg in args:
			newArgs.append(arg)
			newArgs.append(arg)
			
		return self.getObjectsByQuery(newArgs)		
		
	def getObjectsByQuery(self, args):		
		self.gdb.cursor.execute(self.filterQuery, args)
		allObjects = self.gdb.cursor.fetchall()		
		return allObjects

	def getObjectByQuery(self, args):		
		self.gdb.cursor.execute(self.filterQuery, args)
		object = self.gdb.cursor.fetchone()		
		return object
		
	def getObjectById(self, id):
		self.gdb.cursor.execute("SELECT * FROM '%s' WHERE id = ?" % self.tableName, (id,))
		object = self.gdb.cursor.fetchone()		
		return object


class Game(DataBaseObject):	
	filterQuery = "Select * From Game WHERE \
					(RomCollectionId IN (Select Id From RomCollection Where ConsoleId = ?) OR (0 = ?)) AND \
					(Id IN (Select GameId From GenreGame Where GenreId = ?) OR (0 = ?)) AND \
					(YearId = ? OR (0 = ?)) AND \
					(PublisherId = ? OR (0 = ?))"
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Game"
		
	def getFilteredGames(self, consoleId, genreId, yearId, publisherId):
		args = (consoleId, genreId, yearId, publisherId)
		games = self.getObjectsByWildcardQuery(args)
		return games


class Console(DataBaseObject):	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Console"


class RomCollection(DataBaseObject):	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "RomCollection"


class Genre(DataBaseObject):	
	#GetByFilter = "SELECT * FROM Genre WHERE Id IN \
	#				(SELECT Genreid From GenreGame WHERE GameId IN \
	#					(Select Id From Game Where EmulatorId IN \
	#						(Select EmulatorId From EmulatorConsole Where ConsoleId = 1)))"
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Genre"


class Year(DataBaseObject):
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Year"


class Publisher(DataBaseObject):	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Publisher"


class File(DataBaseObject):	
	filterQuery = "Select name from File \
					where gameId = ? AND \
					filetypeid = (select id from filetype where name = ?)"
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "File"
		
	def getIngameScreenshotByGameId(self, gameId):
		file = self.getObjectByQuery((gameId, 'screenshotingame'))
		if file == None:
			return ""		
		return file[0]
		
	def getCoverByGameId(self, gameId):
		file = self.getObjectByQuery((gameId, 'cover'))
		if file == None:
			return ""		
		return file[0]
		
	def getRomsByGameId(self, gameId):
		files = self.getObjectsByQuery((gameId, 'rom'))
		return files
		

class Path(DataBaseObject):	
	filterQuery = "Select name from Path \
					where romCollectionId = ? AND \
					filetypeid = (select id from filetype where name = ?)"
	
	def __init__(self, gdb):		
		self.gdb = gdb
		self.tableName = "Path"
		
	def getRomPathByRomCollectionId(self, romCollectionId):
		path = self.getObjectByQuery((romCollectionId, 'rom'))
		if path == None:
			return ""	
		return path[0]
		
	def getDescriptionPathByRomCollectionId(self, romCollectionId):
		path = self.getObjectByQuery((romCollectionId, 'description'))
		if path == None:
			return ""	
		return path[0]
		
	def getIngameScreenshotPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery((romCollectionId, 'screenshotingame'))
		return path
		
	def getTitleScreenshotPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery((romCollectionId, 'screenshottitle'))
		return path
		
	def getCoverPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery((romCollectionId, 'cover'))
		return path
		
	def getCartridgePathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery((romCollectionId, 'cartridge'))
		return path
		
	def getManualPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery((romCollectionId, 'manual'))
		return path
		
	def getIngameVideoPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery((romCollectionId, 'ingamevideo'))
		return path
		
	def getTrailerPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery((romCollectionId, 'trailer'))
		return path
		
	def getConfigurationPathsByRomCollectionId(self, romCollectionId):
		path = self.getObjectsByQuery((romCollectionId, 'configuration'))
		return path
		
