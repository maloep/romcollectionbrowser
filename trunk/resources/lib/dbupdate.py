
import os, sys
import getpass, string, glob
import codecs
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *

from pyparsing import *
from descriptionparser import *

DEBUG = True

class DBUpdate:
	
	logFilePath = os.path.join(os.getcwd(), 'update.log')
	logFile = None
	
	def __init__(self):			
		self.logFile = open(self.logFilePath, 'w')
	
	def updateDB(self, gdb):		
		self.gdb = gdb
		
		self.log("Start Update DB")
		
		self.log("Reading Rom Collections from database")
		romCollectionRows = RomCollection(self.gdb).getAll()
		if(romCollectionRows == None):
			self.log("ERROR: There are no Rom Collections in database. Make sure you import settings first.")
			self.exit()
			return
		self.log(str(len(romCollectionRows)) +" Rom Collections read")		
		
		for romCollectionRow in romCollectionRows:
			self.log("current Rom Collection: " +romCollectionRow[1])
						
			descParserFile = romCollectionRow[6]
			self.log("using parser file: " +descParserFile)
			descriptionPath = Path(self.gdb).getDescriptionPathByRomCollectionId(romCollectionRow[0])				
			self.log("using game descriptions: " +descriptionPath)
			
			self.log("using one description file per game: " +romCollectionRow[9])
			#romCollectionRow[9] = descFilePerGame
			if(romCollectionRow[9] == 'False'):
				self.log("Start parsing description file")
				results = self.parseDescriptionFile(str(descriptionPath), str(descParserFile), '')
				if(results == None):
					self.log("ERROR: There was an error parsing the description file. Please see xbmc log file")
					self.exit()
					return
				
				if(DEBUG):
					for result in results:
						self.log(result.asDict())
			
			#romCollectionRow[8] = startWithDescFile
			self.log("using start with description file: " +romCollectionRow[8])
			if(romCollectionRow[8] == 'True'):
				exit()
				return
			else:		
				self.log("Reading configured paths from database")
				romPath = Path(self.gdb).getRomPathByRomCollectionId(romCollectionRow[0])
				self.log("Rom path: " +str(romPath))
				ingameScreenshotPaths = Path(self.gdb).getIngameScreenshotPathsByRomCollectionId(romCollectionRow[0])				
				self.log("ingame screen path: " +str(ingameScreenshotPaths))
				titleScreenshotPaths = Path(self.gdb).getTitleScreenshotPathsByRomCollectionId(romCollectionRow[0])
				self.log("title screen  path: " +str(titleScreenshotPaths))
				coverPaths = Path(self.gdb).getCoverPathsByRomCollectionId(romCollectionRow[0])				
				self.log("cover path: " +str(coverPaths))
				cartridgePaths = Path(self.gdb).getCartridgePathsByRomCollectionId(romCollectionRow[0])				
				self.log("cartridge path: " +str(cartridgePaths))
				manualPaths = Path(self.gdb).getManualPathsByRomCollectionId(romCollectionRow[0])			
				self.log("manual path: " +str(manualPaths))
				ingameVideoPaths = Path(self.gdb).getIngameVideoPathsByRomCollectionId(romCollectionRow[0])				
				self.log("ingame video path: " +str(ingameVideoPaths))
				trailerPaths = Path(self.gdb).getTrailerPathsByRomCollectionId(romCollectionRow[0])				
				self.log("trailer path: " +str(trailerPaths))
				configurationPaths = Path(self.gdb).getConfigurationPathsByRomCollectionId(romCollectionRow[0])
				self.log("configuration path: " +str(configurationPaths))
						
				self.log("Reading rom files")
				# read ROMs from disk
				if os.path.isdir(os.path.dirname(romPath)):
					#glob is same as "os.listdir(romPath)" but it can handle wildcards like *.adf
					files = glob.glob(romPath)
					files.sort()
				else:
					files = []
					
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
					
					if(gamename == lastgamename):
						self.log("handling multi rom game: " +lastgamename)
						gameRow = Game(self.gdb).getOneByName(gamename)
						if(gameRow == None):
							self.log("WARNING: multi rom game could not be read from database. "\
								"This usually happens if game name in description file differs from game name in rom file name.")
							continue
						self.insertFile(str(filename), gameRow[0], "rom")
						continue
						
					lastgamename = gamename
									
					self.log("Resolving paths")
					ingameScreenFiles = self.resolvePath(ingameScreenshotPaths, gamename)
					self.log("ingame screen files: " +str(ingameScreenFiles))
					titleScreenFiles = self.resolvePath(titleScreenshotPaths, gamename)
					self.log("title screen files: " +str(titleScreenFiles))
					coverFiles = self.resolvePath(coverPaths, gamename)
					self.log("cover files: " +str(titleScreenFiles))
					cartridgeFiles = self.resolvePath(cartridgePaths, gamename)
					self.log("cartridge files: " +str(titleScreenFiles))
					manualFiles = self.resolvePath(manualPaths, gamename)
					self.log("manual files: " +str(titleScreenFiles))
					ingameVideoFiles = self.resolvePath(ingameVideoPaths, gamename)
					self.log("ingame video files: " +str(titleScreenFiles))
					trailerFiles = self.resolvePath(trailerPaths, gamename)
					self.log("trailer files: " +str(titleScreenFiles))
					configurationFiles = self.resolvePath(configurationPaths, gamename)
					self.log("configuration files: " +str(titleScreenFiles))

					gamedescription = Empty()

					#romCollectionRow[9] = descFilePerGame
					if(romCollectionRow[9] == 'False'):
						#TODO Hash with gamename?
						self.log("Searching for game in parsed results:")
						for result in results:
							gamedesc = result['Game'][0]
							self.log("game name in parsed result: " +gamedesc)
							
							if (gamedesc.strip() == gamename.strip()):
								self.log("result found: " +gamedesc)
								gamedescription = result
						if(gamedescription == Emty()):
							self.log("WARNING: game " +gamename +" could not be found in parsed results")
							continue
					else:
						self.log("Parsing game description")
						results = self.parseDescriptionFile(str(descriptionPath), str(descParserFile), gamename)
						if(results == None):							
							lastgamename = ""
							continue
						else:
							gamedescription = results[0]
					
					self.insertData(gamedescription, romCollectionRow[0], filename, ingameScreenFiles, titleScreenFiles, coverFiles, cartridgeFiles,
						manualFiles, ingameVideoFiles, trailerFiles, configurationFiles)
		exit()
		
	
	def resolvePath(self, paths, gamename):		
		resolvedFiles = []
				
		for path in paths:
			pathname = path[0].replace("%GAME%", gamename)
			files = glob.glob(pathname)
			for file in files:
				if(os.path.exists(file)):
					resolvedFiles.append(file)		
		return resolvedFiles
		
	
	def parseDescriptionFile(self, descriptionPath, descParserFile, gamename):
		descriptionfile = descriptionPath.replace("%GAME%", gamename)
							
		if(os.path.exists(descriptionfile)):
			dp = DescriptionParser()
			results = dp.parseDescription(descriptionfile, descParserFile, gamename)
				
			#TODO delete objects?
			del dp
			
			return results
			
		else:
			self.log("WARNING: description file for game " +gamename +" could not be found. "\
				"Check if this path exists: " +descriptionfile)
			return None
			
			
	def insertData(self, gamedescription, romCollectionId, romFile, ingameScreenFiles, titleScreenFiles, coverFiles, cartridgeFiles,
						manualFiles, ingameVideoFiles, trailerFiles, configurationFiles):
		self.log("Insert data")
		self.log("Result game (form Parser) = " +str(gamedescription.Game))
		self.log("Result desc (form Parser) = " +str(gamedescription.Description))
		self.log("Result year (form Parser) = " +str(gamedescription.ReleaseYear))
		self.log("Result genre (form Parser) = " +str(gamedescription.Genre))
		self.log("Result publisher (form Parser) = " +str(gamedescription.Publisher))
		
		
		year = gamedescription.ReleaseYear[0].strip()
		self.log("Result year (as string) = " +year)
		yearRow = Year(self.gdb).getOneByName(year)
		if(yearRow == None):				
			Year(self.gdb).insert((year,))
			yearId = self.gdb.cursor.lastrowid
		else:
			yearId = yearRow[0]
			
		genres = gamedescription.Genre
		genreIds = []
		
		for genreItem in genres:
			genreItem = genreItem.strip()
			self.log("Result genre (as string) = " +genreItem)
			genreRow = Genre(self.gdb).getOneByName(genreItem)
			if(genreRow == None):
				Genre(self.gdb).insert((genreItem,))				
				genreIds.append(self.gdb.cursor.lastrowid)
			else:
				genreIds.append(genreRow[0])
				
		publisher = gamedescription.Publisher[0].strip()
		self.log("Result publisher (as string) = " +publisher)
		publisherRow = Publisher(self.gdb).getOneByName(publisher)
		print publisherRow
		if(publisherRow == None):				
			Publisher(self.gdb).insert((publisher,))
			publisherId = self.gdb.cursor.lastrowid
		else:
			publisherId = publisherRow[0]
		
		
		game = gamedescription.Game[0].strip()
		self.log("Result game (as string) = " +game)
		gameRow = Game(self.gdb).getOneByName(game)
		print gameRow
		if(gameRow == None):			
			Game(self.gdb).insert((game, gamedescription.Description[0], '', '', romCollectionId, publisherId, yearId))
			gameId = self.gdb.cursor.lastrowid
		else:
			gameId = gameRow[0]
		
		for genreId in genreIds:
			genreGame = GenreGame(self.gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
			if(genreGame == None):
				GenreGame(self.gdb).insert((genreId, gameId))
		
		self.insertFile(romFile, gameId, "rom")
		self.insertFiles(ingameScreenFiles, gameId, "screenshotingame")
		self.insertFiles(titleScreenFiles, gameId, "screenshottitle")
		self.insertFiles(coverFiles, gameId, "cover")
		self.insertFiles(cartridgeFiles, gameId, "cartridge")
		self.insertFiles(manualFiles, gameId, "manual")
		self.insertFiles(ingameVideoFiles, gameId, "ingamevideo")
		self.insertFiles(trailerFiles, gameId, "trailer")
		self.insertFiles(configurationFiles, gameId, "configuration")
		
		#TODO Transaction (per game or complete update?)
		self.gdb.commit()
		
	
	
	def insertFiles(self, fileNames, gameId, fileType):
		for fileName in fileNames:
			self.insertFile(fileName, gameId, fileType)
			
		
	def insertFile(self, fileName, gameId, fileType):
		self.log("Insert file: " +fileName)
		fileRow = File(self.gdb).getFileByNameAndType(fileName, fileType)
		fileTypeRow = FileType(self.gdb).getOneByName(fileType)
		if(fileRow == None):
			File(self.gdb).insert((str(fileName), fileTypeRow[0], gameId))
			

	def log(self, message):
		if(DEBUG):
			self.logFile.write(message +"\n")
		
	def exit(self):
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