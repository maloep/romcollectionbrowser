
import os, sys
import getpass, string, glob
import codecs
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *

from pyparsing import *
from descriptionparser import *


class DBUpdate:
	
	def updateDB(self, gdb):
		
		self.gdb = gdb
		
		romCollectionRows = RomCollection(self.gdb).getAll()
		
		for romCollectionRow in romCollectionRows:
			print str(romCollectionRow)
						
			descParserFile = romCollectionRow[6]
			print descParserFile
			descriptionPath = Path(self.gdb).getDescriptionPathByRomCollectionId(romCollectionRow[0])				
			print descriptionPath
			
			print romCollectionRow[9]
			#romCollectionRow[9] = descFilePerGame
			if(romCollectionRow[9] == 'False'):				
				results = self.parseDescriptionFile(str(descriptionPath), str(descParserFile), '')
				
				#for result in results:
				#	print result.asDict()
			
			#romCollectionRow[8] = startWithDescFile
			if(romCollectionRow[8] == 'True'):
				print "start with desc file"
				pass
			else:				
				romPath = Path(self.gdb).getRomPathByRomCollectionId(romCollectionRow[0])				
				ingameScreenshotPaths = Path(self.gdb).getIngameScreenshotPathsByRomCollectionId(romCollectionRow[0])				
				titleScreenshotPaths = Path(self.gdb).getTitleScreenshotPathsByRomCollectionId(romCollectionRow[0])				
				coverPaths = Path(self.gdb).getCoverPathsByRomCollectionId(romCollectionRow[0])				
				cartridgePaths = Path(self.gdb).getCartridgePathsByRomCollectionId(romCollectionRow[0])				
				manualPaths = Path(self.gdb).getManualPathsByRomCollectionId(romCollectionRow[0])			
				ingameVideoPaths = Path(self.gdb).getIngameVideoPathsByRomCollectionId(romCollectionRow[0])				
				trailerPaths = Path(self.gdb).getTrailerPathsByRomCollectionId(romCollectionRow[0])				
				configurationPaths = Path(self.gdb).getConfigurationPathsByRomCollectionId(romCollectionRow[0])
							
				print romPath
				# read ROMs from disk
				if os.path.isdir(os.path.dirname(romPath)):
					#glob is same as "os.listdir(romPath)" but it can handle wildcards like *.adf
					files = glob.glob(romPath)
					files.sort()
				else:
					files = []
					
				lastgamename = ""				
					
				for filename in files:
					subrom = False
			
					#build friendly romname
					gamename = os.path.basename(filename)
					#romCollectionRow[10] = DiskPrefix
					dpIndex = gamename.lower().find(romCollectionRow[10].lower())
					if dpIndex > -1:
						gamename = gamename[0:dpIndex]
					else:
						gamename = os.path.splitext(gamename)[0]					
					
					if(gamename == lastgamename):
						print gamename
						gameRow = Game(self.gdb).getOneByName(gamename)						
						self.insertFile(str(filename), gameRow[0], "rom")
						continue
						
					lastgamename = gamename
										
					ingameScreenFiles = self.resolvePath(ingameScreenshotPaths, gamename)
					titleScreenFiles = self.resolvePath(titleScreenshotPaths, gamename)
					coverFiles = self.resolvePath(coverPaths, gamename)
					cartridgeFiles = self.resolvePath(cartridgePaths, gamename)
					manualFiles = self.resolvePath(manualPaths, gamename)
					ingameVideoFiles = self.resolvePath(ingameVideoPaths, gamename)
					trailerFiles = self.resolvePath(trailerPaths, gamename)
					configurationFiles = self.resolvePath(configurationPaths, gamename)


					#romCollectionRow[9] = descFilePerGame
					if(romCollectionRow[9] == 'False'):
						#TODO Hash with gamename?
						for result in results:
							gamedesc = result['Game'][0]
							
							if (gamedesc.strip() == gamename.strip()):								
								gamedescription = result
					else:
						gamedescription = self.parseDescriptionFile(descriptionPath, descParserFile, gamename)
					
					self.insertData(gamedescription, romCollectionRow[0], filename, ingameScreenFiles, titleScreenFiles, coverFiles, cartridgeFiles,
						manualFiles, ingameVideoFiles, trailerFiles, configurationFiles)
						
	
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
			
			print results
				
			#TODO delete objects?
			del dp
			
			return results
			
			
	def insertData(self, gamedescription, romCollectionId, romFile, ingameScreenFiles, titleScreenFiles, coverFiles, cartridgeFiles,
						manualFiles, ingameVideoFiles, trailerFiles, configurationFiles):
		
		print "Result game = " +str(gamedescription.Game)
		print "Result desc = " +str(gamedescription.Description)
		print "Result year = " +str(gamedescription.ReleaseYear)
		print "Result genre = " +str(gamedescription.Genre)
		print "Result publisher = " +str(gamedescription.Publisher)
		print "rom File = " +str(romFile)
		print "Ingame Screenshots = " +str(ingameScreenFiles)
		print "Title Screenshots = " +str(titleScreenFiles)
		print "Cover = " +str(coverFiles)
		print "Cartridge = " +str(cartridgeFiles)
		print "Manual = " +str(manualFiles)
		print "Ingame Video = " +str(ingameVideoFiles)
		print "Trailer = " +str(trailerFiles)
		print "ConfigurationFiles = " +str(configurationFiles)
		
		
		year = gamedescription.ReleaseYear[0].strip()
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
			genreRow = Genre(self.gdb).getOneByName(genreItem)
			if(genreRow == None):
				Genre(self.gdb).insert((genreItem,))				
				genreIds.append(self.gdb.cursor.lastrowid)
			else:
				genreIds.append(genreRow[0])
				
		publisher = gamedescription.Publisher[0].strip()
		publisherRow = Publisher(self.gdb).getOneByName(publisher)
		print publisherRow
		if(publisherRow == None):				
			Publisher(self.gdb).insert((publisher,))
			publisherId = self.gdb.cursor.lastrowid
		else:
			publisherId = publisherRow[0]
		
		
		game = gamedescription.Game[0].strip()
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
		print fileName
		fileRow = File(self.gdb).getFileByNameAndType(fileName, fileType)
		fileTypeRow = FileType(self.gdb).getOneByName(fileType)
		if(fileRow == None):
			File(self.gdb).insert((str(fileName), fileTypeRow[0], gameId))
			


def main():
	gdb = GameDataBase(os.path.join(os.getcwd(), '..', 'database'))
	dbupdate = DBUpdate()
	gdb.connect()
	dbupdate.updateDB(gdb)
	gdb.close()
	del dbupdate
	del gdb
	
	
#main()