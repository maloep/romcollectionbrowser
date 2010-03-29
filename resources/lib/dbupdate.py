
import os, sys
import getpass, string, glob
import codecs
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *

from pyparsing import *
from descriptionparser import *
import zlib

DEBUG = True

class DBUpdate:
	
	logFilePath = os.path.join(os.getcwd(), 'update.log')
	logFile = None
	
	def __init__(self):
		try:
			self.logFile = open(self.logFilePath, 'w')
			self.logFileWritable = True
		except Exception, (exc):
			print("RCB WARNING: Cannot write log file update.log: " +str(exc))
			self.logFileWritable = False
			return
	
	def updateDB(self, gdb, gui):		
		self.gdb = gdb
		
		self.log("Start Update DB")
		
		self.log("Reading Rom Collections from database")
		romCollectionRows = RomCollection(self.gdb).getAll()
		if(romCollectionRows == None):
			gui.writeMsg("ERROR: There are no Rom Collections in database. Make sure to import settings first.")
			self.log("ERROR: There are no Rom Collections in database. Make sure to import settings first.")
			self.exit()
			return
		self.log(str(len(romCollectionRows)) +" Rom Collections read")		
		
		for romCollectionRow in romCollectionRows:
			gui.writeMsg("Importing Rom Collection: " +romCollectionRow[1])
			self.log("current Rom Collection: " +romCollectionRow[1])
						
			ignoreOnScan = romCollectionRow[13]
			self.log("ignoreOnScan: " +ignoreOnScan)
			if(ignoreOnScan == 'True'):
				self.log("current Rom Collection will be ignored.")
				continue
			
			descParserFile = romCollectionRow[6]
			self.log("using parser file: " +descParserFile)
			descriptionPath = Path(self.gdb).getDescriptionPathByRomCollectionId(romCollectionRow[0])				
			self.log("using game descriptions: " +descriptionPath)
			allowUpdate = romCollectionRow[12]
			self.log("update is allowed for current rom collection: " +allowUpdate)
			
			self.log("using one description file per game: " +romCollectionRow[9])
			#romCollectionRow[9] = descFilePerGame
			if(romCollectionRow[9] == 'False'):
				self.log("Start parsing description file")
				results = self.parseDescriptionFile(str(descriptionPath), str(descParserFile), '')
				if(results == None):
					gui.writeMsg("ERROR: There was an error parsing the description file. Please see log file for more information.")
					self.log("ERROR: There was an error parsing the description file. Please see log file for more information.")					
					
				
				if(DEBUG and results != None):
					for result in results:
						self.log(str(result.asDict()))
			
			#romCollectionRow[8] = startWithDescFile
			self.log("using start with description file: " +romCollectionRow[8])
			if(romCollectionRow[8] == 'True'):
				exit()
				return
			else:		
				self.log("Reading configured paths from database")
				romPaths = Path(self.gdb).getRomPathsByRomCollectionId(romCollectionRow[0])
				self.log("Rom path: " +str(romPaths))							
						
				self.log("Reading rom files")
				files = []
				for romPath in romPaths:				
					if os.path.isdir(os.path.dirname(romPath[0])):
						#glob is same as "os.listdir(romPath)" but it can handle wildcards like *.adf
						allFiles = glob.glob(romPath[0])
						#did not find appendall or slt
						for file in allFiles:							
							files.append(file)
				files.sort()
					
				self.log("Files read: " +str(files))
					
				lastgamename = ""				
					
				for filename in files:
					subrom = False
					
					self.log("current rom file: " +str(filename)	)
			
					#build friendly romname
					gamename = os.path.basename(filename)
					self.log("gamename (file): " +gamename)
					
					#romCollectionRow[10] = DiskPrefix
					dpIndex = gamename.lower().find(romCollectionRow[10].lower())
					if dpIndex > -1:
						gamename = gamename[0:dpIndex]
					else:
						gamename = os.path.splitext(gamename)[0]					
					
					self.log("gamename (friendly): " +gamename)
					gui.writeMsg("Importing Game: " +gamename)
					
					
					if(gamename == lastgamename):
						self.log("handling multi rom game: " +lastgamename)
						gameRow = Game(self.gdb).getOneByName(gamename)
						if(gameRow == None):
							self.log("WARNING: multi rom game could not be read from database. "\
								"This usually happens if game name in description file differs from game name in rom file name.")
							continue
						self.insertFile(str(filename), gameRow[0], "rcb_rom")
						self.gdb.commit()
						continue
						
					lastgamename = gamename							
					

					gamedescription = Empty()
					
					#get crc value of the rom file
					prev = 0
					for eachLine in open(filename,"rb"):
					    prev = zlib.crc32(eachLine, prev)					
					filecrc = "%X"%(prev & 0xFFFFFFFF)

					#romCollectionRow[9] = descFilePerGame
					if(romCollectionRow[9] == 'False'):
						#TODO Hash with gamename?
						self.log("Searching for game in parsed results:")
						if(results != None):
							for result in results:
								gamedesc = result['Game'][0]								
								self.log("game name in parsed result: " +gamedesc)								
								
								#find by filename
								if (gamedesc.strip() == gamename.strip()):
									self.log("result found by filename: " +gamedesc)
									gamedescription = result
									continue
								
								#find by crc
								try:
									resultcrcs = result['crc']
									for resultcrc in resultcrcs:										
										if(resultcrc.lower() == filecrc.lower()):
											self.log("result found by crc: " +gamedesc)
											gamedescription = result
											continue
											
								except:
									pass
								
								
							if(gamedescription == Empty()):
								self.log("WARNING: game " +gamename +" could not be found in parsed results. Importing game without description.")
						else:
							self.log("WARNING: game " +gamename +" has no gamedescription. Importing game without description.")
					else:						
						results = self.parseDescriptionFile(str(descriptionPath), str(descParserFile), gamename)
						if(results == None):
							self.log("WARNING: game description for game " +gamename +" could not be parsed. Importing game without description.")
							lastgamename = ""							
							#continue
						else:
							gamedescription = results[0]
					
					self.insertData(gamedescription, gamename, romCollectionRow[0], filename, allowUpdate)
		gui.writeMsg("Done.")
		self.exit()
		
		
	
	def parseDescriptionFile(self, descriptionPath, descParserFile, gamename):
		descriptionfile = descriptionPath.replace("%GAME%", gamename)

		if(os.path.exists(descriptionfile)):
			self.log("Parsing game description: " +descriptionfile)
			dp = DescriptionParser()
			
			try:
				results = dp.parseDescription(descriptionfile, descParserFile, gamename)
			except Exception, (exc):
				self.log("WARNING: an error occured while parsing game description: " +descriptionfile)
				self.log("Parser complains about: " +str(exc))
				return None
							
			del dp
			
			return results
			
		else:
			self.log("WARNING: description file for game " +gamename +" could not be found. "\
				"Check if this path exists: " +descriptionfile)
			return None
			
			
	def insertData(self, gamedescription, gamenameFromFile, romCollectionId, romFile, allowUpdate):
		self.log("Insert data")	
				
		if(gamedescription != Empty()):			
			yearId = self.insertForeignKeyItem(gamedescription.ReleaseYear, 'Year', Year(self.gdb))
			genreIds = self.insertForeignKeyItemList(gamedescription.Genre, 'Genre', Genre(self.gdb))		
			publisherId = self.insertForeignKeyItem(gamedescription.Publisher, 'Publisher', Publisher(self.gdb))
			developerId = self.insertForeignKeyItem(gamedescription.Developer, 'Developer', Developer(self.gdb))
			reviewerId = self.insertForeignKeyItem(gamedescription.Reviewer, 'Reviewer', Reviewer(self.gdb))		
			
			region = self.resolveParseResult(gamedescription.Region, 'Region')		
			media = self.resolveParseResult(gamedescription.Media, 'Media')
			controller = self.resolveParseResult(gamedescription.Controller, 'Controller')
			players = self.resolveParseResult(gamedescription.Players, 'Players')		
			rating = self.resolveParseResult(gamedescription.Rating, 'Rating')
			votes = self.resolveParseResult(gamedescription.Votes, 'Votes')
			url = self.resolveParseResult(gamedescription.URL, 'URL')
			perspective = self.resolveParseResult(gamedescription.Perspective, 'Perspective')		
		
			self.log("Result Game (from parser) = " +str(gamedescription.Game))
			gamename = gamedescription.Game[0].strip()
			
			self.log("Result Game (as string) = " +gamename)
			gameId = self.insertGame(gamename, gamedescription.Description[0], romCollectionId, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, allowUpdate)
				
			for genreId in genreIds:
				genreGame = GenreGame(self.gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
				if(genreGame == None):
					GenreGame(self.gdb).insert((genreId, gameId))
		else:
			gamename = gamenameFromFile
			gameId = self.insertGame(gamename, None, romCollectionId, None, None, None, None, 
					None, None, None, None, None, None, None, None, allowUpdate)				
			
		
		self.insertFile(romFile, gameId, "rcb_rom")
		
		
		allPathRows = Path(self.gdb).getPathsByRomCollectionId(romCollectionId)		
		for pathRow in allPathRows:
			self.log("Additional data path: " +str(pathRow))
			files = self.resolvePath((pathRow[1],), gamename, gamenameFromFile)
			self.log("Importing files: " +str(files))
			fileTypeRow = FileType(self.gdb).getObjectById(pathRow[2])
			self.log("FileType: " +str(fileTypeRow)) 
			if(fileTypeRow == None):
				continue
			self.insertFiles(files, gameId, fileTypeRow[1])
			
		
		
		manualPaths = Path(self.gdb).getManualPathsByRomCollectionId(romCollectionId)
		self.log("manual path: " +str(manualPaths))
		manualFiles = self.resolvePath(manualPaths, gamename, gamenameFromFile)
		self.log("manual files: " +str(manualFiles))
		self.insertFiles(manualFiles, gameId, "manual")
		
		configurationPaths = Path(self.gdb).getConfigurationPathsByRomCollectionId(romCollectionId)
		self.log("configuration path: " +str(configurationPaths))
		configurationFiles = self.resolvePath(configurationPaths, gamename, gamenameFromFile)
		self.log("configuration files: " +str(configurationFiles))
		self.insertFiles(configurationFiles, gameId, "configuration")
		
		
		#TODO Transaction?
		self.gdb.commit()
		
		
	def insertGame(self, gameName, description, romCollectionId, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, allowUpdate):
		gameRow = Game(self.gdb).getOneByName(gameName)
		if(gameRow == None):
			self.log("Game does not exist in database. Insert game: " +gameName)
			Game(self.gdb).insert((gameName, description, None, None, romCollectionId, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, 0, 0))
			return self.gdb.cursor.lastrowid
		else:	
			if(allowUpdate == 'True'):
				self.log("Game does exist in database. Update game: " +gameName)
				Game(self.gdb).update(('name', 'description', 'romCollectionId', 'publisherId', 'developerId', 'reviewerId', 'yearId', 'maxPlayers', 'rating', 'numVotes',
					'url', 'region', 'media', 'perspective', 'controllerType'),
					(gameName, description, romCollectionId, publisherId, developerId, reviewerId, yearId, players, rating, votes, url, region, media, perspective, controller),
					gameRow[0])
			else:
				self.log("Game does exist in database but update is not allowed for current rom collection. game: " +gameName)
			
			return gameRow[0]
		
	
	def insertForeignKeyItem(self, result, itemName, gdbObject):
		self.log("Result " +itemName +" (from Parser) = " +str(result))
		#if(result != Empty()):
		if(len(result) != 0):
			item = result[0].strip()
			self.log("Result "  +itemName +" (as string) = " +item)
			itemRow = gdbObject.getOneByName(item)
			if(itemRow == None):	
				self.log(itemName +" does not exist in database. Insert: " +item)
				gdbObject.insert((item,))
				itemId = self.gdb.cursor.lastrowid
			else:
				itemId = itemRow[0]
		else:
			itemId = None
			
		return itemId
		
	
	def insertForeignKeyItemList(self, resultList, itemName, gdbObject):	
		self.log("Result " +itemName +" (from Parser) = " +str(resultList))
		idList = []
		
		for resultItem in resultList:			
			item = resultItem.strip()
			self.log("Result " +itemName +" (as string) = " +item)
			itemRow = gdbObject.getOneByName(item)
			if(itemRow == None):
				self.log(itemName +" does not exist in database. Insert: " +item)
				gdbObject.insert((item,))
				idList.append(self.gdb.cursor.lastrowid)
			else:
				idList.append(itemRow[0])
				
		return idList
		
		
	def resolvePath(self, paths, gamename, gamenameFromFile):		
		resolvedFiles = []
				
		for path in paths:
			self.log("resolve path: " +path)
			pathnameFromGameName = path.replace("%GAME%", gamename)			
			self.log("resolved path from game name: " +pathnameFromGameName)
			files = glob.glob(pathnameFromGameName)
			
			if(gamename != gamenameFromFile):
				pathnameFromFile = path.replace("%GAME%", gamenameFromFile)
				self.log("resolved path from file name: " +pathnameFromFile)			
				files = glob.glob(pathnameFromFile)
			
			self.log("resolved files: " +str(files))
			for file in files:
				if(os.path.exists(file)):
					resolvedFiles.append(file)		
		return resolvedFiles
		
		
	def resolveParseResult(self, result, itemName):
		self.log("Result " +itemName +" (from Parser) = " +str(result))		
		if(len(result) != 0):
			item = result[0].strip()
		else:
			item = ""
		self.log("Result " +itemName +" (as string) = " +item)
		return item
	
	
	def insertFiles(self, fileNames, gameId, fileType):
		for fileName in fileNames:
			self.insertFile(fileName, gameId, fileType)
			
		
	def insertFile(self, fileName, gameId, fileType):
		self.log("Begin Insert file: " +fileName)
		fileRow = File(self.gdb).getFileByNameAndType(fileName, fileType)
		fileTypeRow = FileType(self.gdb).getOneByName(fileType)
		if(fileRow == None):
			self.log("File does not exist in database. Insert file: " +fileName)
			File(self.gdb).insert((str(fileName), fileTypeRow[0], gameId))
			

	def log(self, message):
		if(DEBUG and self.logFileWritable):
			self.logFile.write(message +"\n")			
				
		
	def exit(self):
		self.log("Update finished")
		self.logFile.close()


def main():
	gdb = GameDataBase(os.path.join(os.getcwd(), '..', 'database'))
	dbupdate = DBUpdate()
	gdb.connect()
	dbupdate.updateDB(gdb)
	gdb.close()
	del dbupdate
	del gdb
	
	
#main()