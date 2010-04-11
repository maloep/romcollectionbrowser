
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
			#TODO: correct handling of boolean values
			if(ignoreOnScan == 'True'):
				self.log("current Rom Collection will be ignored.")
				continue
			
			descParserFile = romCollectionRow[6]
			self.log("using parser file: " +descParserFile)
			descFilePerGame = romCollectionRow[9]
			self.log("using one description file per game: " +descFilePerGame)
			descriptionPath = Path(self.gdb).getDescriptionPathByRomCollectionId(romCollectionRow[0])
			self.log("using game descriptions: " +descriptionPath)
			allowUpdate = romCollectionRow[12]
			self.log("update is allowed for current rom collection: " +allowUpdate)
			searchGameByCRC = romCollectionRow[14]
			self.log("search game by CRC: " +searchGameByCRC)
			searchGameByCRCIgnoreRomName = romCollectionRow[15]
			self.log("ignore rom filename when searching game by CRC: " +searchGameByCRCIgnoreRomName)
			ignoreGameWithoutDesc = romCollectionRow[16]
			self.log("ignore games without description: " +ignoreGameWithoutDesc)
			
			#check if we can find any roms with this configuration
			if(searchGameByCRCIgnoreRomName == 'True' and searchGameByCRC == 'False' and descFilePerGame == 'False'):
				self.log("ERROR: Configuration error: descFilePerGame = false, searchGameByCRCIgnoreRomName = true, searchGameByCRC = false." \
				"You won't find any description with this configuration!")
				continue
				
			if(descFilePerGame == 'False'):
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
						#did not find appendall or something like this
						for file in allFiles:							
							files.append(file)
				files.sort()
					
				self.log("Files read: " +str(files))
					
				lastgamenameFromFile = ""
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
					
					
					#check if we are handling one of the additional disks of a multi rom game
					if(gamename == lastgamenameFromFile):
						self.log("handling multi rom game: " +lastgamename)
						gameRow = Game(self.gdb).getOneByName(lastgamename)
						if(gameRow == None):
							self.log("WARNING: multi rom game could not be read from database. "\
								"This usually happens if game name in description file differs from game name in rom file name.")
							continue
						self.insertFile(str(filename), gameRow[0], "rcb_rom", None, None, None, None)
						self.gdb.commit()
						continue
						
					#lastgamename may be overwritten by parsed gamename
					lastgamenameFromFile = gamename
					lastgamename = gamename
					

					gamedescription = Empty()
					
					#get crc value of the rom file - this can take a long time for large files, so it is configurable
					if(searchGameByCRC == 'True'):
						prev = 0
						for eachLine in open(str(filename),"rb"):
						    prev = zlib.crc32(eachLine, prev)					
						filecrc = "%X"%(prev & 0xFFFFFFFF)
						self.log("crc for current file: " +str(filecrc))

					#romCollectionRow[9] = descFilePerGame
					if(romCollectionRow[9] == 'False'):						
						self.log("Searching for game in parsed results:")
						if(results != None):
							for result in results:
								gamedesc = result['Game'][0]								
								self.log("game name in parsed result: " +gamedesc)								
								
								#find by filename
								#there is an option only to search by crc (maybe there are games with the same name but different crcs)
								if(searchGameByCRCIgnoreRomName == 'False'):
									if (gamedesc.strip() == gamename.strip()):
										self.log("result found by filename: " +gamedesc)
										gamedescription = result
										break
								
								#find by crc
								if(searchGameByCRC == 'True'):
									try:
										resultFound = False
										resultcrcs = result['crc']
										for resultcrc in resultcrcs:
											self.log("crc in parsed result: " +resultcrc)
											if(resultcrc.lower() == filecrc.lower()):
												self.log("result found by crc: " +gamedesc)
												gamedescription = result
												resultFound = True
												break
										if(resultFound):
											break
												
									except:
										pass								
								
							#if(gamedescription == Empty()):
							#	self.log("WARNING: game " +gamename +" could not be found in parsed results. Importing game without description.")
						#else:
						#	self.log("WARNING: game " +gamename +" has no gamedescription. Importing game without description.")
					else:						
						results = self.parseDescriptionFile(str(descriptionPath), str(descParserFile), gamename)
						if(results == None):
							gamedescription = Empty()
							
							lastgamename = ""
							#self.log("WARNING: game description for game " +gamename +" could not be parsed. Importing game without description.")							
							#continue
						else:
							gamedescription = results[0]
							
					if(gamedescription == Empty()):
						lastgamename = ""
						if(ignoreGameWithoutDesc == 'True'):
							self.log("WARNING: game " +gamename +" could not be found in parsed results. Game will not be imported.")
							continue
						else:
							self.log("WARNING: game " +gamename +" could not be found in parsed results. Importing game without description.")
					else:
						lastgamename = self.resolveParseResult(gamedescription.Game, 'Game')
					
					#get Console Name to import images via %CONSOLE%
					consoleId = romCollectionRow[2]									
					consoleRow = Console(self.gdb).getObjectById(consoleId)					
					if(consoleRow == None):						
						consoleName = None						
					else:
						consoleName = consoleRow[1]
					
					self.insertData(gamedescription, gamename, romCollectionRow[0], filename, allowUpdate, consoleId, consoleName)
					
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
			
			
	def insertData(self, gamedescription, gamenameFromFile, romCollectionId, romFile, allowUpdate, consoleId, consoleName):
		self.log("Insert data")	
				
		publisherId = None
		developerId = None
		publisher = None
		developer = None
				
		if(gamedescription != Empty()):
			
			publisher = self.resolveParseResult(gamedescription.Publisher, 'Publisher')
			developer = self.resolveParseResult(gamedescription.Developer, 'Developer')
			
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
			originalTitle = self.resolveParseResult(gamedescription.OriginalTitle, 'OriginalTitle')
			alternateTitle = self.resolveParseResult(gamedescription.AlternateTitle, 'AlternateTitle')
			translatedBy = self.resolveParseResult(gamedescription.TranslatedBy, 'TranslatedBy')
			version = self.resolveParseResult(gamedescription.Version, 'Version')
		
			self.log("Result Game (from parser) = " +str(gamedescription.Game))
			gamename = self.resolveParseResult(gamedescription.Game, 'Game')
			plot = self.resolveParseResult(gamedescription.Description, 'Description')
			
			self.log("Result Game (as string) = " +gamename)
			gameId = self.insertGame(gamename, plot, romCollectionId, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version, allowUpdate, )
				
			for genreId in genreIds:
				genreGame = GenreGame(self.gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
				if(genreGame == None):
					GenreGame(self.gdb).insert((genreId, gameId))
		else:
			gamename = gamenameFromFile
			gameId = self.insertGame(gamename, None, romCollectionId, None, None, None, None, 
					None, None, None, None, None, None, None, None, None, None, None, None, allowUpdate)			
			
		
		self.insertFile(romFile, gameId, "rcb_rom", None, None, None, None)
		
		
		allPathRows = Path(self.gdb).getPathsByRomCollectionId(romCollectionId)
		for pathRow in allPathRows:
			self.log("Additional data path: " +str(pathRow))
			files = self.resolvePath((pathRow[1],), gamename, gamenameFromFile, consoleName, publisher, developer)
			self.log("Importing files: " +str(files))
			fileTypeRow = FileType(self.gdb).getObjectById(pathRow[2])
			self.log("FileType: " +str(fileTypeRow)) 
			if(fileTypeRow == None):
				continue
			self.insertFiles(files, gameId, fileTypeRow[1], consoleId, publisherId, developerId, romCollectionId)
			
		
		
		manualPaths = Path(self.gdb).getManualPathsByRomCollectionId(romCollectionId)
		self.log("manual path: " +str(manualPaths))
		manualFiles = self.resolvePath(manualPaths, gamename, gamenameFromFile, None, None, None)
		self.log("manual files: " +str(manualFiles))
		self.insertFiles(manualFiles, gameId, "rcb_manual", None, None, None, None)
		
		configurationPaths = Path(self.gdb).getConfigurationPathsByRomCollectionId(romCollectionId)
		self.log("configuration path: " +str(configurationPaths))
		configurationFiles = self.resolvePath(configurationPaths, gamename, gamenameFromFile, None, None, None)
		self.log("configuration files: " +str(configurationFiles))
		self.insertFiles(configurationFiles, gameId, "rcb_configuration", None, None, None, None)
		
		
		#TODO Transaction?
		self.gdb.commit()
		
		
	def insertGame(self, gameName, description, romCollectionId, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version, allowUpdate):
		gameRow = Game(self.gdb).getOneByName(gameName)
		if(gameRow == None):
			self.log("Game does not exist in database. Insert game: " +gameName.encode('iso-8859-15'))
			Game(self.gdb).insert((gameName, description, None, None, romCollectionId, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, 0, 0, originalTitle, alternateTitle, translatedBy, version))
			return self.gdb.cursor.lastrowid
		else:	
			if(allowUpdate == 'True'):
				self.log("Game does exist in database. Update game: " +gameName)
				Game(self.gdb).update(('name', 'description', 'romCollectionId', 'publisherId', 'developerId', 'reviewerId', 'yearId', 'maxPlayers', 'rating', 'numVotes',
					'url', 'region', 'media', 'perspective', 'controllerType', 'originalTitle', 'alternateTitle', 'translatedBy', 'version'),
					(gameName, description, romCollectionId, publisherId, developerId, reviewerId, yearId, players, rating, votes, url, region, media, perspective, controller,
					originalTitle, alternateTitle, translatedBy, version),
					gameRow[0])
			else:
				self.log("Game does exist in database but update is not allowed for current rom collection. game: " +gameName.encode('iso-8859-15'))
			
			return gameRow[0]
		
	
	def insertForeignKeyItem(self, result, itemName, gdbObject):
		self.log("Result " +itemName +" (from Parser) = " +str(result))
		#if(result != Empty()):
		if(len(result) != 0):
			item = result[0].strip()
			self.log("Result "  +itemName +" (as string) = " +item.encode('iso-8859-15'))
			itemRow = gdbObject.getOneByName(item)
			if(itemRow == None):	
				self.log(itemName +" does not exist in database. Insert: " +item.encode('iso-8859-15'))
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
			self.log("Result " +itemName +" (as string) = " +item.encode('iso-8859-15'))
			itemRow = gdbObject.getOneByName(item)
			if(itemRow == None):
				self.log(itemName +" does not exist in database. Insert: " +item.encode('iso-8859-15'))
				gdbObject.insert((item,))
				idList.append(self.gdb.cursor.lastrowid)
			else:
				idList.append(itemRow[0])
				
		return idList
		
		
	def resolvePath(self, paths, gamename, gamenameFromFile, consoleName, publisher, developer):		
		resolvedFiles = []
				
		for path in paths:
			files = []
			self.log("resolve path: " +path)
			pathnameFromGameName = path.replace("%GAME%", gamename)			
			self.log("resolved path from game name: " +pathnameFromGameName)
			files = glob.glob(pathnameFromGameName)
			self.log("resolved files: " +str(files))
			
			if(gamename != gamenameFromFile and len(files) == 0):
				pathnameFromFile = path.replace("%GAME%", gamenameFromFile)
				self.log("resolved path from rom file name: " +pathnameFromFile)			
				files = glob.glob(pathnameFromFile)
				self.log("resolved files: " +str(files))
				
			#TODO could be done only once per RomCollection
			if(consoleName != None and len(files) == 0):
				pathnameFromConsole = path.replace("%CONSOLE%", consoleName)
				self.log("resolved path from console name: " +pathnameFromConsole)
				files = glob.glob(pathnameFromConsole)
				self.log("resolved files: " +str(files))
				
			if(publisher != None and len(files) == 0):
				pathnameFromPublisher = path.replace("%PUBLISHER%", publisher)
				self.log("resolved path from publisher name: " +pathnameFromPublisher)
				files = glob.glob(pathnameFromPublisher)
				self.log("resolved files: " +str(files))
				
			if(developer != None and len(files) == 0):
				pathnameFromDeveloper = path.replace("%DEVELOPER%", developer)
				self.log("resolved path from developer name: " +pathnameFromDeveloper)
				files = glob.glob(pathnameFromDeveloper)
				self.log("resolved files: " +str(files))
				
						
			if(len(files) == 0):
				self.log("WARNING: No files found for game %s. Make sure that rom name and file name are matching." %gamename)
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
		self.log("Result " +itemName +" (as string) = " +item.encode('iso-8859-15'))
		return item
	
	
	def insertFiles(self, fileNames, gameId, fileType, consoleId, publisherId, developerId, romCollectionId):
		for fileName in fileNames:
			self.insertFile(fileName, gameId, fileType, consoleId, publisherId, developerId, romCollectionId)
			
		
	def insertFile(self, fileName, gameId, fileType, consoleId, publisherId, developerId, romCollectionId):
		self.log("Begin Insert file: " +fileName)
				
		fileTypeRow = FileType(self.gdb).getOneByName(fileType)
		if(fileTypeRow == None):
			self.log("WARNING: No filetype found for %s. Please check your config.xml" %fileType)				
			
		parentId = None
		
		#TODO console and romcollection could be done only once per RomCollection			
		#fileTypeRow[3] = parent
		if(fileTypeRow[3] == 'game'):
			self.log("Insert file with parent game")
			parentId = gameId
		elif(fileTypeRow[3] == 'console'):
			self.log("Insert file with parent console")
			parentId = consoleId
		elif(fileTypeRow[3] == 'romcollection'):
			self.log("Insert file with parent rom collection")
			parentId = romCollectionId
		elif(fileTypeRow[3] == 'publisher'):
			self.log("Insert file with parent publisher")
			parentId = publisherId
		elif(fileTypeRow[3] == 'developer'):
			self.log("Insert file with parent developer")
			parentId = developerId
			
		fileRow = File(self.gdb).getFileByNameAndTypeAndParent(fileName, fileType, parentId)
		if(fileRow == None):
			self.log("File does not exist in database. Insert file: " +fileName)
			File(self.gdb).insert((str(fileName), fileTypeRow[0], parentId))
			

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