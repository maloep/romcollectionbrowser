

import os, sys, shutil

from databaseobject import DataBaseObject
from game import Game
from rcbsetting import RCBSetting
from resources.lib.rcb.utils.util import *
from resources.lib.rcb.utils import util


try:
	from sqlite3 import dbapi2 as sqlite
	Logutil.log("Loading sqlite3 as DB engine", util.LOG_LEVEL_INFO)
except:
	from pysqlite2 import dbapi2 as sqlite
	Logutil.log("Loading pysqlite2 as DB engine", util.LOG_LEVEL_INFO)


class GameDataBase:
	
	def __init__(self, databaseDir, databaseName):
		self.dataBasePath = os.path.join(databaseDir, databaseName)
		sqlite.register_adapter(str, lambda s:s.decode('utf-8'))
		#use scripts home for reading SQL files
		self.sqlDir = os.path.join(util.RCBHOME, 'resources', 'database')		
		
	def connect( self ):
		print self.dataBasePath
		self.connection = sqlite.connect(self.dataBasePath, check_same_thread = False)
		self.cursor = self.connection.cursor()
		
	def commit( self ):		
		try:
			self.connection.commit()
			return True
		except: return False

	def close( self ):
		print "close Connection"
		self.connection.close()
	
	def compact(self):
		self.cursor.execute("VACUUM")
		
	def toMem(self):
		try:
			memDB = sqlite.connect(':memory:', check_same_thread = False)
			dump = os.linesep.join([line for line in self.connection.iterdump()])
			memDB.executescript(dump)
			self.connection.close()
			self.connection = memDB
			self.cursor = memDB.cursor()
			return True
		except Exception, e: 
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
		except Exception, e: 
			util.Logutil.log("ERROR: %s" % str(e), util.LOG_LEVEL_INFO)
			return False
	
	def executeSQLScript(self, scriptName):
		sqlCreateFile = open(scriptName, 'r')
		sqlCreateString = sqlCreateFile.read()						
		self.connection.executescript(sqlCreateString)		
	
	def createTables(self):
		print "Create Tables"		
		self.executeSQLScript(os.path.join(self.sqlDir, 'SQL_CREATE.txt'))
		rcbsetting = RCBSetting(self).fromDb((None, None, None, None, None, None, None, None, util.CURRENT_DB_VERSION, None, None, None, None))
		RCBSetting(self).insert(rcbsetting)
		
	def dropTables(self):
		print "Drop Tables"
		self.executeSQLScript(os.path.join(self.sqlDir, 'SQL_DROP_ALL.txt'))

	
	def checkDBStructure(self):
		#returnValues: -1 error, 0=nothing, 1=import Games, 2=idLookupFile created
		
		dbVersion = ""
		try:
			rcbSettings = RCBSetting(self).getAll()
			if(rcbSettings == None or len(rcbSettings) != 1):	
				self.createTables()
				self.commit()
				return 1, ""
			rcbSetting = rcbSettings[0]
			
			#HACK: reflect changes in RCBSetting
			dbVersion = rcbSetting.dbVersion
			
		except  Exception, (exc):
			self.createTables()
			self.commit()
			return 1, ""
		
		#Alter Table
		if(dbVersion != util.CURRENT_DB_VERSION):
			alterTableScript = "SQL_ALTER_%(old)s_%(new)s.txt" %{'old': dbVersion, 'new':util.CURRENT_DB_VERSION}
			alterTableScript = str(os.path.join(self.sqlDir, alterTableScript))
			
			if os.path.isfile(alterTableScript):
				#backup MyGames.db				
				newFileName = self.dataBasePath +'.backup ' +dbVersion 
				
				if os.path.isfile(newFileName):
					return -1, util.localize(35030)				
				try:
					self.close()
					shutil.copy(str(self.dataBasePath), str(newFileName))
					self.connect()
				except Exception, (exc):					
					return -1, util.localize(35031) +": " +str(exc)
								
				self.executeSQLScript(alterTableScript)
				self.commit()
				return 0, ""
			else:
				return -1, util.localize(35032) %(dbVersion, util.CURRENT_DB_VERSION)
					
		count = Game(self).getCount()
		if(count == 0):
			return 1, ""
		
		return 0, ""


class GenreGame(DataBaseObject):
					
	filterQueryByGenreIdAndGameId = "Select * from GenreGame \
					where genreId = ? AND \
					gameId = ?"
	
	def __init__(self, gdb):		
		self._gdb = gdb
		self._tableName = "GenreGame"
		
		self.id = None
		self.genreId = None
		self.gameId = None
		
	def fromDb(self, row):
		
		if(not row):
			return None
		
		genreGame = GenreGame(self._gdb)

		genreGame.id = row[util.ROW_ID]
		genreGame.genreId = row[util.GENREGAME_genreId]
		genreGame.gameId = row[util.GENREGAME_gameId]

		return genreGame
		
	def getGenreGameByGenreIdAndGameId(self, genreId, gameId):
		genreGame = self.getObjectByQuery(self.filterQueryByGenreIdAndGameId, (genreId, gameId))
		return genreGame
		
		
class Reviewer(DataBaseObject):
	def __init__(self, gdb):		
		self._gdb = gdb
		self._tableName = "Reviewer"
		
		self.id = None
		self.name = ''


	def fromDb(self, row):
		if(not row):
			return None

		reviewer = Reviewer(self._gdb)

		reviewer.id = row[util.ROW_ID]
		reviewer.name = row[util.ROW_NAME]

		return reviewer
	
