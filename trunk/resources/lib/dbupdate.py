
import os, sys
import getpass, string, glob
import codecs
import zipfile
import zlib
import time
import difflib
from pysqlite2 import dbapi2 as sqlite

from config import *
from gamedatabase import *
from pyparsing import *
from descriptionparserfactory import *
import util
from util import *
from settings import *




class DBUpdate:		
	
	def __init__(self):
		pass
	
	rcbSettings = RCBSettingsXml()
	
	def updateDB(self, gdb, gui):
		self.gdb = gdb
		
		config = Config()
		statusOk, errorMsg = config.readXml()
		if(statusOk == False):
			return False, errorMsg
		
		Logutil.log("Start Update DB", util.LOG_LEVEL_INFO)
		
		Logutil.log("Iterating Rom Collections", util.LOG_LEVEL_INFO)
		rccount = 1
		for romCollection in config.romCollections:
			
			#prepare Header for ProgressDialog
			progDialogRCHeader = "Importing Rom Collection (%i / %i): %s" %(rccount, len(config.romCollections), romCollection.name)
			rccount = rccount + 1
			
			Logutil.log("current Rom Collection: " +romCollection.name, util.LOG_LEVEL_INFO)

			#Read settings for current Rom Collection
			Logutil.log("ignoreOnScan: " +str(romCollection.ignoreOnScan), util.LOG_LEVEL_INFO)
			if(romCollection.ignoreOnScan):
				Logutil.log("current Rom Collection will be ignored.", util.LOG_LEVEL_INFO)
				continue
									
			Logutil.log("using one description file per game: " +str(romCollection.descFilePerGame), util.LOG_LEVEL_INFO)						
			Logutil.log("update is allowed for current rom collection: " +str(romCollection.allowUpdate), util.LOG_LEVEL_INFO)			
			Logutil.log("search game by CRC: " +str(romCollection.searchGameByCRC), util.LOG_LEVEL_INFO)			
			Logutil.log("ignore rom filename when searching game by CRC: " +str(romCollection.searchGameByCRCIgnoreRomName), util.LOG_LEVEL_INFO)
						
			Logutil.log("use foldername as CRC: " +str(romCollection.useFoldernameAsCRC), util.LOG_LEVEL_INFO)			
			Logutil.log("use filename as CRC: " +str(romCollection.useFilenameAsCRC), util.LOG_LEVEL_INFO)
								
			Logutil.log("ignore games without description: " +str(romCollection.ignoreGameWithoutDesc), util.LOG_LEVEL_INFO)						
			Logutil.log("max folder depth: " +str(romCollection.maxFolderDepth), util.LOG_LEVEL_INFO)
			
			#check if we can find any roms with this configuration
			if(romCollection.searchGameByCRCIgnoreRomName and not romCollection.searchGameByCRC and not romCollection.descFilePerGame):
				Logutil.log("Configuration error: descFilePerGame = false, searchGameByCRCIgnoreRomName = true, searchGameByCRC = false." \
				"You won't find any description with this configuration!", util.LOG_LEVEL_ERROR)
				continue			
			
					
			files = self.getRomFilesByRomCollection(romCollection.romPaths, romCollection.maxFolderDepth)				
								
			lastgamenameFromFile = ""
			lastgamename = ""
			foldername = ''
			
			filecrcDict = {}
			fileGamenameDict = {}
			fileFoldernameDict = {}
			
			#always remember the crc of the first rom of multi rom games
			crcOfFirstGame = {}
			
			#itemCount is used for percentage in ProgressDialogGUI
			gui.itemCount = len(files) +1
			fileCount = 1
			
			Logutil.log("Start building file crcs", util.LOG_LEVEL_INFO)
			for filename in files:				
				gui.writeMsg(progDialogRCHeader, "Checking file crcs...", "", fileCount)
				fileCount = fileCount +1
				
				gamename = self.getGamenameFromFilename(filename, romCollection)
				
				#check if we are handling one of the additional disks of a multi rom game
				isMultiRomGame = self.checkRomfileIsMultirom(gamename, lastgamename, lastgamenameFromFile, filename)
				
				#lastgamename may be overwritten by parsed gamename
				lastgamenameFromFile = gamename
				lastgamename = gamename				
				
				gamename = gamename.strip()
				gamename = gamename.lower()
				
				#build dictionaries (key=gamename, filecrc or foldername; value=filenames) for later game search
				fileGamenameDict = self.buildFilenameDict(fileGamenameDict, isMultiRomGame, filename, gamename, fileGamenameDict, gamename, True)
					
				if(romCollection.searchGameByCRC):
					filecrc = self.getFileCRC(filename)
					#use crc of first rom if it is a multirom game
					if(not isMultiRomGame):
						try:
							crcOfFirstGame[gamename] = filecrc
							Logutil.log('Adding crc to crcOfFirstGame-dict: %s:%s' %(gamename, filecrc), util.LOG_LEVEL_DEBUG)
						except:							
							pass
					else:
						try:
							filecrc = crcOfFirstGame[gamename]
							Logutil.log('Read crc from crcOfFirstGame-dict: %s:%s' %(gamename, filecrc), util.LOG_LEVEL_DEBUG)
						except Exception, (exc):							
							pass
						
					filecrcDict = self.buildFilenameDict(filecrcDict, isMultiRomGame, filename, filecrc, fileGamenameDict, gamename, False)
				
				#Folder name of game may be used as crc value in description files					
				if(romCollection.useFoldernameAsCRC):
					foldername = self.getCRCFromFolder(filename)
					foldername = foldername.strip()
					foldername = foldername.lower()
					fileFoldernameDict = self.buildFilenameDict(fileFoldernameDict, isMultiRomGame, filename, foldername, fileGamenameDict, gamename, False)

			Logutil.log("Building file crcs done", util.LOG_LEVEL_INFO)																																														
			
			if(not romCollection.descFilePerGame and len(romCollection.scraperSites) > 0):
				Logutil.log("Searching for game in parsed results:", util.LOG_LEVEL_INFO)
				
				try:						
					fileCount = 1
					
					#first scraper must be the one for multiple games					
					if(len(romCollection.scraperSites[0].scrapers) == 0):
						Logutil.log('Configuration error: Configured scraper site does not contain any scrapers', util.LOG_LEVEL_ERROR)
						continue
						
					scraper = romCollection.scraperSites[0].scrapers[0]					
					Logutil.log("using parser file: " +scraper.parseInstruction, util.LOG_LEVEL_INFO)
					Logutil.log("using game descriptions: " +scraper.source, util.LOG_LEVEL_INFO)
											
					parser = DescriptionParserFactory.getParser(str(scraper.parseInstruction)) 										
					
					#parse description
					for result in parser.scanDescription(scraper.source, str(scraper.parseInstruction)):
						
						filenamelist, foldername, filecrc = self.findFilesByGameDescription(result, romCollection, filecrcDict, fileFoldernameDict, fileGamenameDict)

						if(filenamelist != None and len(filenamelist) > 0):								
							gamenameFromFile = self.getGamenameFromFilename(filenamelist[0], romCollection)
							gamenameFromDesc = result['Game'][0]
							gui.writeMsg(progDialogRCHeader, "Import game: " +str(gamenameFromDesc), "", fileCount)
							fileCount = fileCount +1
							
							#use additional scrapers
							if(len(romCollection.scraperSites) > 1):
								for i in range(1, len(romCollection.scraperSites)):
									scraperSite = romCollection.scraperSites[i]
									urlsFromPreviousScrapers = []
									for scraper in scraperSite.scrapers:
										results, urlsFromPreviousScrapers, doContinue = self.scrapeResults(result, scraper, urlsFromPreviousScrapers, gamenameFromFile, foldername, filecrc)
										if(doContinue):
											continue
						else:
							gamename = ''
							gamenameFromFile = ''								
							
						self.insertGameFromDesc(result, lastgamename, gamenameFromFile, romCollection, filenamelist, foldername)
							
				except Exception, (exc):
					Logutil.log("an error occured while adding game " +gamename.encode('iso-8859-15'), util.LOG_LEVEL_WARNING)
					Logutil.log("Error: " +str(exc), util.LOG_LEVEL_WARNING)
					return None
			else:	
				fileCount = 1										
				
				for filename in files:						
					gamenameFromFile = self.getGamenameFromFilename(filename, romCollection)						
					
					gui.writeMsg(progDialogRCHeader, "Import game: " +gamenameFromFile, "", fileCount)
					fileCount = fileCount +1
					
					foldername = os.path.dirname(filename)
					filecrc = self.getFileCRC(filename)																		
					
					results = {}										
					
					for scraperSite in romCollection.scraperSites:
						urlsFromPreviousScrapers = []
						for scraper in scraperSite.scrapers:							
							results, urlsFromPreviousScrapers, doContinue = self.scrapeResults(results, scraper, urlsFromPreviousScrapers, gamenameFromFile, foldername, filecrc)
							if(doContinue):
								continue						
					
					#print results
					if(len(results) == 0):
						lastgamename = ""
						gamedescription = None
					else:
						gamedescription = results
						
					filenamelist = []
					filenamelist.append(filename)
												
					self.insertGameFromDesc(gamedescription, lastgamename, gamenameFromFile, romCollection, filenamelist, foldername)													
					
		gui.writeMsg("Done.", "", "", gui.itemCount)
		self.exit()
		return True, ''
					
	
	def scrapeResults(self, results, scraper, urlsFromPreviousScrapers, gamenameFromFile, foldername, filecrc):		
		Logutil.log("using parser file: " +scraper.parseInstruction, util.LOG_LEVEL_INFO)		
		Logutil.log("using game description: " +scraper.source, util.LOG_LEVEL_INFO)
		
		#url to scrape may be passed from the previous scraper
		if(scraper.source.isdigit()):
			if(len(urlsFromPreviousScrapers) == 0):
				Logutil.log("Configuration error: scraper source is numeric and there is no previous scraper that returned an url to scrape.", util.LOG_LEVEL_ERROR)
				return results, urlsFromPreviousScrapers, True			
			if(len(urlsFromPreviousScrapers) < int(scraper.source)):
				Logutil.log("Configuration error: no url found at index " +str(scraper.source), util.LOG_LEVEL_ERROR)
				return results, urlsFromPreviousScrapers, True
			
			url = urlsFromPreviousScrapers[int(scraper.source) -1]
			Logutil.log("using url from previous scraper: " +str(url), util.LOG_LEVEL_INFO)
			scraperSource = url
														
		tempResults = self.parseDescriptionFile(scraper, gamenameFromFile, foldername, filecrc)
		if(tempResults == None):
			return results, urlsFromPreviousScrapers, True
		
		if(scraper.returnUrl):			
			try:								
				tempUrl = self.resolveParseResult(tempResults, 'url')
				urlsFromPreviousScrapers.append(tempUrl)
				Logutil.log("pass url to next scraper: " +str(tempUrl), util.LOG_LEVEL_INFO)
				return results, urlsFromPreviousScrapers, True
			except:
				Logutil.log("Should pass url to next scraper, but url is empty.", util.LOG_LEVEL_WARNING)
				return results, urlsFromPreviousScrapers, True
			
		if(tempResults != None):
			for resultKey in tempResults.keys():
				Logutil.log("resultKey: " +resultKey, util.LOG_LEVEL_INFO)
				try:
					resultValueOld = results[resultKey]																	
				except Exception, (exc):										
					resultValueOld = []
					
				try:
					resultValueNew = tempResults[resultKey]																	
				except Exception, (exc):										
					resultValueNew = []
																						
				if(len(resultValueOld) == 0):
					results[resultKey] = resultValueNew
					
				Logutil.log("resultValue: " +str(results[resultKey]), util.LOG_LEVEL_INFO)
					
		return results, urlsFromPreviousScrapers, False
	
	
	def getRomFilesByRomCollection(self, romPaths, maxFolderDepth):
				
		Logutil.log("Rom path: " +str(romPaths), util.LOG_LEVEL_INFO)
				
		Logutil.log("Reading rom files", util.LOG_LEVEL_INFO)
		files = []
		for romPath in romPaths:
			files = self.walkDownPath(files, romPath, maxFolderDepth)
			
		files.sort()
			
		Logutil.log("Files read: " +str(files), util.LOG_LEVEL_INFO)
		
		return files
		
		
	def walkDownPath(self, files, romPath, maxFolderDepth):
		
		Logutil.log("walkDownPath romPath: " +romPath, util.LOG_LEVEL_INFO)						
		
		dirname = os.path.dirname(romPath)
		Logutil.log("dirname: " +dirname, util.LOG_LEVEL_INFO)
		basename = os.path.basename(romPath)
		Logutil.log("basename: " +basename, util.LOG_LEVEL_INFO)						
				
		Logutil.log("checking sub directories", util.LOG_LEVEL_INFO)
		for walkRoot, walkDirs, walkFiles in self.walklevel(dirname.encode('utf-8'), maxFolderDepth):
			Logutil.log( "root: " +str(walkRoot), util.LOG_LEVEL_DEBUG)
			Logutil.log( "walkDirs: " +str(walkDirs), util.LOG_LEVEL_DEBUG)
			Logutil.log( "walkFiles: " +str(walkFiles), util.LOG_LEVEL_DEBUG)
									
			newRomPath = os.path.join(walkRoot, basename)
			Logutil.log( "newRomPath: " +str(newRomPath), util.LOG_LEVEL_DEBUG)
			
			#glob is same as "os.listdir(romPath)" but it can handle wildcards like *.adf
			allFiles = glob.glob(newRomPath)
			Logutil.log( "all files in newRomPath: " +str(allFiles), util.LOG_LEVEL_DEBUG)
		
			#did not find appendall or something like this
			for file in allFiles:
				files.append(file)							
		
		return files
	
	
	def walklevel(self, some_dir, level=1):
		some_dir = some_dir.rstrip(os.path.sep)
		assert os.path.isdir(some_dir)
		num_sep = len([x for x in some_dir if x == os.path.sep])
		for root, dirs, files in os.walk(some_dir):
			yield root, dirs, files
			num_sep_this = len([x for x in root if x == os.path.sep])
			if num_sep + level <= num_sep_this:
				del dirs[:]
		
		
	def getGamenameFromFilename(self, filename, romCollection):
		subrom = False
					
		Logutil.log("current rom file: " +str(filename), util.LOG_LEVEL_INFO)

		#build friendly romname
		gamename = os.path.basename(filename)
		Logutil.log("gamename (file): " +gamename, util.LOG_LEVEL_INFO)
				
		dpIndex = gamename.lower().find(romCollection.diskPrefix.lower())
		if dpIndex > -1:
			gamename = gamename[0:dpIndex]
		else:
			gamename = os.path.splitext(gamename)[0]					
		
		Logutil.log("gamename (friendly): " +gamename, util.LOG_LEVEL_INFO)		
		
		return gamename
		
		
	def checkRomfileIsMultirom(self, gamename, lastgamename, lastgamenameFromFile, filename):		
	
		#XBOX Hack: rom files will always be named default.xbe: always detected as multi rom without this hack
		if(gamename == lastgamenameFromFile and lastgamenameFromFile.lower() != 'default'):		
			Logutil.log("handling multi rom game: " +lastgamename, util.LOG_LEVEL_INFO)			
			return True
		return False
		
		
	def buildFilenameDict(self, dict, isMultiRomGame, filename, key, fileGamenameDict, gamename, appendToGamenameDict):				
		
		try:											
			if(not isMultiRomGame):
				filenamelist = []
				filenamelist.append(filename)
				dict[key] = filenamelist
				Logutil.log("Add filename %s with key %s" %(filename, key), util.LOG_LEVEL_DEBUG)
			else:
				filenamelist = fileGamenameDict[gamename]
				if(appendToGamenameDict):
					filenamelist.append(filename)
				dict[key] = filenamelist
				Logutil.log("Add filename %s to multirom game with key %s" %(filename, key), util.LOG_LEVEL_DEBUG)
		except:
			pass
			
		return dict
		
		
	def getFileCRC(self, filename):
		#get crc value of the rom file - this can take a long time for large files, so it is configurable
		filecrc = ''		
		if (zipfile.is_zipfile(str(filename))):
			try:
				Logutil.log("handling zip file", util.LOG_LEVEL_INFO)
				zip = zipfile.ZipFile(str(filename), 'r')
				zipInfos = zip.infolist()
				if(len(zipInfos) > 1):
					Logutil.log("more than one file in zip archive is not supported! Checking CRC of first entry.", util.LOG_LEVEL_WARNING)
				filecrc = "%0.8X" %(zipInfos[0].CRC & 0xFFFFFFFF)
				Logutil.log("crc in zipped file: " +filecrc, util.LOG_LEVEL_INFO)
			except:
				Logutil.log("Error while creating crc from zip file!", util.LOG_LEVEL_ERROR)
		else:						
			prev = 0
			for eachLine in open(str(filename),"rb"):
				prev = zlib.crc32(eachLine, prev)					
			filecrc = "%0.8X"%(prev & 0xFFFFFFFF)
			Logutil.log("crc for current file: " +str(filecrc), util.LOG_LEVEL_INFO)
				
		filecrc = filecrc.strip()
		filecrc = filecrc.lower()
		return filecrc
		
		
	def getCRCFromFolder(self, filename):
		crcFromFolder = ''
		dirname = os.path.dirname(filename)		
		if(dirname != None):
			pathTuple = os.path.split(dirname)			
			if(len(pathTuple) == 2):
				crcFromFolder = pathTuple[1]				
				
		return crcFromFolder


	def findFilesByGameDescription(self, result, romCollection, filecrcDict, fileFoldernameDict, fileGamenameDict):
		gamedesc = result['Game'][0]
		Logutil.log("game name in parsed result: " +str(gamedesc), util.LOG_LEVEL_DEBUG)				
		
		foldername = ''
		filecrc = ''
		
		#find by filename
		#there is an option only to search by crc (maybe there are games with the same name but different crcs)
		if(not romCollection.searchGameByCRCIgnoreRomName):
			try:
				gamedesc = gamedesc.lower()
				gamedesc = gamedesc.strip()
				filename = fileGamenameDict[gamedesc]
			except:
				filename = None
				
			if (filename != None):
				Logutil.log("result found by filename: " +gamedesc, util.LOG_LEVEL_INFO)				
				return filename, foldername, filecrc
		
		#find by crc
		if(romCollection.searchGameByCRC or romCollection.useFoldernameAsCRC or romCollection.useFilenameAsCRC):
			try:
				resultFound = False
				resultcrcs = result['crc']
				for resultcrc in resultcrcs:
					Logutil.log("crc in parsed result: " +resultcrc, util.LOG_LEVEL_DEBUG)
					resultcrc = resultcrc.lower()
					resultcrc = resultcrc.strip()
					try:
						filename = filecrcDict[resultcrc]
						filecrc = resultcrc
					except:
						filename = None
					if(filename != None):
						Logutil.log("result found by crc: " +gamedesc, util.LOG_LEVEL_INFO)						
						return filename, foldername, filecrc
						
					#search for folder
					if(romCollection.useFoldernameAsCRC):
						Logutil.log("using foldername as crc value", util.LOG_LEVEL_DEBUG)						
						try:
							filename = fileFoldernameDict[resultcrc]
							foldername = resultcrc
						except:
							filename = None
						if(filename != None):
							Logutil.log("result found by foldername crc: " +gamedesc, util.LOG_LEVEL_INFO)							
							return filename, foldername, filecrc
							
					Logutil.log("using filename as crc value", util.LOG_LEVEL_DEBUG)										
					try:
						filename = fileGamenameDict[resultcrc]
					except:
						filename = None
					if(filename != None):
						Logutil.log("result found by filename crc: " +gamedesc, util.LOG_LEVEL_INFO)						
						return filename, foldername, filecrc
						
			except Exception, (exc):
				Logutil.log("Error while checking crc results: " +str(exc), util.LOG_LEVEL_ERROR)
		
		return None, foldername, filecrc
		
		
	def insertGameFromDesc(self, gamedescription, lastgamename, gamename, romCollection, filenamelist, foldername):								
		if(gamedescription != None):
			game = self.resolveParseResult(gamedescription, 'Game')
		else:
			game = ''
						
		if(filenamelist == None or len(filenamelist) == 0):
			lastgamename = ""			
			Logutil.log("game " +game +" was found in parsed results but not in your rom collection.", util.LOG_LEVEL_WARNING)
			return
		else:
			lastgamename = game
		
		#get Console Name to import images via %CONSOLE%
		self.insertData(gamedescription, gamename, romCollection, filenamelist, foldername)
	
	
	def parseDescriptionFile(self, scraper, gamenameFromFile, foldername, crc):
		descriptionfile = scraper.source.replace("%GAME%", gamenameFromFile)

		if(not descriptionfile.startswith('http://') and not os.path.exists(descriptionfile)):
			Logutil.log("description file for game " +gamenameFromFile +" could not be found. "\
			"Check if this path exists: " +descriptionfile, util.LOG_LEVEL_WARNING)
			return None
		
		Logutil.log("Parsing game description: " +descriptionfile, util.LOG_LEVEL_INFO)			
			
		try:
			replaceTokens = ['%FILENAME%', '%FOLDERNAME%', '%CRC%']
			for key in util.API_KEYS.keys():
				replaceTokens.append(key)
				
			replaceValues = [gamenameFromFile, foldername, crc]
			for value in util.API_KEYS.values():
				replaceValues.append(value)
				
			for i in range(0, len(replaceTokens)):
				descriptionfile = descriptionfile.replace(replaceTokens[i], replaceValues[i])
				
			#replace configurable tokens
			#TODO move from Scraper to RomCollection?				
			replaceKeys = scraper.replaceKeyString.split(',')
			Logutil.log("replaceKeys: " +str(replaceKeys), util.LOG_LEVEL_INFO)						
			replaceValues = scraper.replaceValueString.split(',')
			Logutil.log("replaceValues: " +str(replaceValues), util.LOG_LEVEL_INFO)
			
			if(len(replaceKeys) != len(replaceValues)):
				Logutil.log("Configuration error: replaceKeyString (%s) and replaceValueString(%s) does not have the same number of ','-separated items." %(scraper.replaceKeyString, scraper.replaceValueString), util.LOG_LEVEL_ERROR)
				return None
			
			for i in range(0, len(replaceKeys)):
				descriptionfile = descriptionfile.replace(replaceKeys[i], replaceValues[i])
				
			parser = DescriptionParserFactory.getParser(str(scraper.parseInstruction))
			Logutil.log("description file (tokens replaced): " +descriptionfile, util.LOG_LEVEL_INFO)
			results = parser.parseDescription(str(descriptionfile))
		except Exception, (exc):
			Logutil.log("an error occured while parsing game description: " +descriptionfile, util.LOG_LEVEL_WARNING)
			Logutil.log("Parser complains about: " +str(exc), util.LOG_LEVEL_WARNING)
			return None			
					
		if (results != None and len(results) == 1):
			return results[0]
		elif(results != None and len(results) > 1):
			#find best matching result
			bestIndex = 0
			highestRatio = 0
			for i in range(0, len(results)):
				result = results[i]
				try:
					searchKey = self.resolveParseResult(result, 'SearchKey')
					#TODO gamenameFromFile is not always correct
					ratio = difflib.SequenceMatcher(None, gamenameFromFile, searchKey).ratio()
					if(ratio > highestRatio):
						highestRatio = ratio
						bestIndex = i
				except Exception, (exc):
					Logutil.log("parseDescription returned more than 1 result. An error occured while matching the best result: " +str(exc), util.LOG_LEVEL_WARNING)
			return results[bestIndex]
		else:
			return None
					
			
			
			
	def insertData(self, gamedescription, gamenameFromFile, romCollection, romFiles, foldername):
		Logutil.log("Insert data", util.LOG_LEVEL_INFO)
				
		publisherId = None
		developerId = None
		publisher = None
		developer = None
				
		if(gamedescription != None):
			
			publisher = self.resolveParseResult(gamedescription, 'Publisher')
			developer = self.resolveParseResult(gamedescription, 'Developer')
			
			yearId = self.insertForeignKeyItem(gamedescription, 'ReleaseYear', Year(self.gdb))
			genreIds = self.insertForeignKeyItemList(gamedescription, 'Genre', Genre(self.gdb))		
			publisherId = self.insertForeignKeyItem(gamedescription, 'Publisher', Publisher(self.gdb))
			developerId = self.insertForeignKeyItem(gamedescription, 'Developer', Developer(self.gdb))
			reviewerId = self.insertForeignKeyItem(gamedescription, 'Reviewer', Reviewer(self.gdb))	
			
			region = self.resolveParseResult(gamedescription, 'Region')		
			media = self.resolveParseResult(gamedescription, 'Media')
			controller = self.resolveParseResult(gamedescription, 'Controller')
			players = self.resolveParseResult(gamedescription, 'Players')		
			rating = self.resolveParseResult(gamedescription, 'Rating')
			votes = self.resolveParseResult(gamedescription, 'Votes')
			url = self.resolveParseResult(gamedescription, 'URL')
			perspective = self.resolveParseResult(gamedescription, 'Perspective')
			originalTitle = self.resolveParseResult(gamedescription, 'OriginalTitle')
			alternateTitle = self.resolveParseResult(gamedescription, 'AlternateTitle')
			translatedBy = self.resolveParseResult(gamedescription, 'TranslatedBy')
			version = self.resolveParseResult(gamedescription, 'Version')
					
			gamename = self.resolveParseResult(gamedescription, 'Game')
			if(gamename == ""):
				gamename = gamenameFromFile
			plot = self.resolveParseResult(gamedescription, 'Description')
						
			gameId = self.insertGame(gamename, plot, romCollection.console.id, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version, romCollection.allowUpdate, )
				
			for genreId in genreIds:
				genreGame = GenreGame(self.gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
				if(genreGame == None):
					GenreGame(self.gdb).insert((genreId, gameId))
		else:
			gamename = gamenameFromFile
			gameId = self.insertGame(gamename, None, romCollection.console.id, None, None, None, None, 
					None, None, None, None, None, None, None, None, None, None, None, None, romCollection.allowUpdate)			
			
		for romFile in romFiles:
			fileType = FileType()
			fileType.id = 0
			fileType.name = "rcb_rom"
			fileType.parent = "game"
			self.insertFile(romFile, gameId, fileType, None, None, None)
		
				
		for path in romCollection.mediaPaths:
						
			Logutil.log("FileType: " +str(path.fileType.name), util.LOG_LEVEL_INFO)			
			
			#TODO replace %CONSOLE%, %PUBLISHER%, ... 
			fileName = path.path.replace("%GAME%", gamenameFromFile)
			self.getThumbFromOnlineSource(gamedescription, path.fileType.name, fileName)
			
			Logutil.log("Additional data path: " +str(path.path), util.LOG_LEVEL_INFO)
			files = self.resolvePath((path.path,), gamename, gamenameFromFile, foldername, romCollection.console.name, publisher, developer)
			Logutil.log("Importing files: " +str(files), util.LOG_LEVEL_INFO)					
			
			self.insertFiles(files, gameId, path.fileType, romCollection.console.id, publisherId, developerId)								
				
		self.gdb.commit()
				
		
		
	def insertGame(self, gameName, description, consoleId, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version, allowUpdate):
		# TODO unique by name an RC
		gameRow = Game(self.gdb).getGameByNameAndConsoleId(gameName, consoleId)
		if(gameRow == None):
			Logutil.log("Game does not exist in database. Insert game: " +gameName.encode('iso-8859-15'), util.LOG_LEVEL_INFO)
			Game(self.gdb).insert((gameName, description, None, None, consoleId, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, 0, 0, originalTitle, alternateTitle, translatedBy, version))
			return self.gdb.cursor.lastrowid
		else:	
			if(allowUpdate):
				Logutil.log("Game does exist in database. Update game: " +gameName, util.LOG_LEVEL_INFO)
				Game(self.gdb).update(('name', 'description', 'consoleId', 'publisherId', 'developerId', 'reviewerId', 'yearId', 'maxPlayers', 'rating', 'numVotes',
					'url', 'region', 'media', 'perspective', 'controllerType', 'originalTitle', 'alternateTitle', 'translatedBy', 'version'),
					(gameName, description, consoleId, publisherId, developerId, reviewerId, yearId, players, rating, votes, url, region, media, perspective, controller,
					originalTitle, alternateTitle, translatedBy, version),
					gameRow[0])
			else:
				Logutil.log("Game does exist in database but update is not allowed for current rom collection. game: " +gameName.encode('iso-8859-15'), util.LOG_LEVEL_INFO)
			
			return gameRow[0]
		
	
	def insertForeignKeyItem(self, result, itemName, gdbObject):
		
		item = self.resolveParseResult(result, itemName)
		#TODO 
		if(itemName == 'ReleaseYear' and item != None):
			if(type(item) is time.struct_time):
				item = str(item[0])
			elif(len(item) > 4):
				item = item[0:4]
						
		if(item != "" and item != None):
			itemRow = gdbObject.getOneByName(item)
			if(itemRow == None):	
				Logutil.log(itemName +" does not exist in database. Insert: " +item.encode('iso-8859-15'), util.LOG_LEVEL_INFO)
				gdbObject.insert((item,))
				itemId = self.gdb.cursor.lastrowid
			else:
				itemId = itemRow[0]
		else:
			itemId = None
			
		return itemId
		
	
	def insertForeignKeyItemList(self, result, itemName, gdbObject):
		idList = []				
				
		try:
			itemList = result[itemName]
			Logutil.log("Result " +itemName +" = " +str(itemList), util.LOG_LEVEL_INFO)
		except:
			Logutil.log("Error while resolving item: " +itemName, util.LOG_LEVEL_WARNING)
			return idList				
		
		for item in itemList:
			itemRow = gdbObject.getOneByName(item)
			if(itemRow == None):
				Logutil.log(itemName +" does not exist in database. Insert: " +item.encode('iso-8859-15'), util.LOG_LEVEL_INFO)
				gdbObject.insert((item,))
				idList.append(self.gdb.cursor.lastrowid)
			else:
				idList.append(itemRow[0])
				
		return idList
		
		
	def resolvePath(self, paths, gamename, gamenameFromFile, foldername, consoleName, publisher, developer):		
		resolvedFiles = []				
				
		for path in paths:
			files = []
			Logutil.log("resolve path: " +path, util.LOG_LEVEL_INFO)
			
			if(path.find("%GAME%") > -1):
				pathnameFromGameName = path.replace("%GAME%", gamename)
				Logutil.log("resolved path from game name: " +pathnameFromGameName, util.LOG_LEVEL_INFO)				
				files = self.getFilesByWildcard(pathnameFromGameName)
				
				pathnameFromFile = path.replace("%GAME%", gamenameFromFile)
				if(gamename != gamenameFromFile and len(files) == 0):					
					Logutil.log("resolved path from rom file name: " +pathnameFromFile, util.LOG_LEVEL_INFO)					
					files = self.getFilesByWildcard(pathnameFromFile)
					
				pathnameFromFolder = path.replace("%GAME%", foldername)
				if(gamename != foldername and len(files) == 0):					
					Logutil.log("resolved path from rom folder name: " +pathnameFromFolder, util.LOG_LEVEL_INFO)					
					files = self.getFilesByWildcard(pathnameFromFolder)								
				
				#one last try with case insensitive search (on Linux we don't get files with case mismatches)
				if(len(files) == 0):
					files = self.getFilesByGameNameIgnoreCase(pathnameFromGameName)
				if(len(files) == 0):
					files = self.getFilesByGameNameIgnoreCase(pathnameFromFile)
				if(len(files) == 0):
					files = self.getFilesByGameNameIgnoreCase(pathnameFromFolder)
				
				
			#TODO could be done only once per RomCollection
			if(path.find("%CONSOLE%") > -1 and consoleName != None and len(files) == 0):
				pathnameFromConsole = path.replace("%CONSOLE%", consoleName)
				Logutil.log("resolved path from console name: " +pathnameFromConsole, util.LOG_LEVEL_INFO)
				files = self.getFilesByWildcard(pathnameFromConsole)				
				
			if(path.find("%PUBLISHER%") > -1 and publisher != None and len(files) == 0):
				pathnameFromPublisher = path.replace("%PUBLISHER%", publisher)
				Logutil.log("resolved path from publisher name: " +pathnameFromPublisher, util.LOG_LEVEL_INFO)
				files = self.getFilesByWildcard(pathnameFromPublisher)				
				
			if(path.find("%DEVELOPER%") > -1 and developer != None and len(files) == 0):
				pathnameFromDeveloper = path.replace("%DEVELOPER%", developer)
				Logutil.log("resolved path from developer name: " +pathnameFromDeveloper, util.LOG_LEVEL_INFO)
				files = self.getFilesByWildcard(pathnameFromDeveloper)													
				
			if(len(files) == 0):
				Logutil.log("No files found for game %s at path %s. Make sure that file names are matching." %(gamename, path), util.LOG_LEVEL_WARNING)
			for file in files:
				if(os.path.exists(file)):
					resolvedFiles.append(file)
					
		return resolvedFiles
	
	
	def getFilesByWildcard(self, pathName):
		
		files = []
		
		try:
			# try glob with * wildcard
			files = glob.glob(pathName)
		except Exception, (exc):
			Logutil.log("Error using glob function in resolvePath " +str(exc), util.LOG_LEVEL_WARNING)
		
		# glob can't handle []-characters - try it with listdir
		if(len(files)  == 0):
			try:				
				if(os.path.isfile(pathName)):
					files.append(pathName)
				else:
					files = os.listdir(pathName)					
			except:
				pass
		return files
		Logutil.log("resolved files: " +str(files), util.LOG_LEVEL_INFO)
		
		
	def getFilesByGameNameIgnoreCase(self, pathname):
		
		files = []
		
		dirname = os.path.dirname(pathname)
		basename = os.path.basename(pathname)
		
		#search all Files that start with the first character of game name
		newpath = os.path.join(dirname, basename[0].upper() +'*')
		filesUpper = glob.glob(newpath)
		newpath = os.path.join(dirname, basename[0].lower() +'*')
		filesLower = glob.glob(newpath)
		
		allFiles = filesUpper + filesLower
		for file in allFiles:
			if(pathname.lower() == file.lower()):
				Logutil.log("Found path %s by search with ignore case." %pathname, util.LOG_LEVEL_WARNING)
				files.append(file)
				
		return files
		
		
	def resolveParseResult(self, result, itemName):
		
		resultValue = ""
		
		try:			
			resultValue = result[itemName][0]
			
			#replace and remove HTML tags
			resultValue = self.stripHTMLTags(resultValue)
			
			#TODO: use sqlite.register_adapter?
			try:
				resultValue	= resultValue.decode('iso-8859-15')
			except:
				try:
					resultValue	= resultValue.decode('utf-8')
				except:
					pass
			
									
		except Exception, (exc):
			Logutil.log("Error while resolving item: " +itemName +" : " +str(exc), util.LOG_LEVEL_WARNING)
						
		try:
			Logutil.log("Result " +itemName +" = " +resultValue.encode('iso-8859-15'), util.LOG_LEVEL_INFO)
		except:
			pass
				
		return resultValue
	
	
	def stripHTMLTags(self, inputString):
		
		#TODO there must be a function available to do this 
		inputString = inputString.replace('&nbsp;', ' ')
		inputString = inputString.replace('&quot;', '"')
		inputString = inputString.replace('&amp;', '&')
		inputString = inputString.replace('&lt;', '<')
		inputString = inputString.replace('&gt;', '>')
				
		#remove html tags and double spaces
		intag = [False]
		lastSpace = [False]
		def chk(c):
			if intag[0]:
				intag[0] = (c != '>')
				lastSpace[0] = (c == ' ')
				return False
			elif c == '<':
				intag[0] = True
				lastSpace[0] = (c == ' ')
				return False
			if(c == ' ' and lastSpace[0]):
				lastSpace[0] = (c == ' ')
				return False
			lastSpace[0] = (c == ' ')
			return True
		
		return ''.join(c for c in inputString if chk(c))

	
	
	def insertFiles(self, fileNames, gameId, fileType, consoleId, publisherId, developerId):
		for fileName in fileNames:
			self.insertFile(fileName, gameId, fileType, consoleId, publisherId, developerId)
			
		
	def insertFile(self, fileName, gameId, fileType, consoleId, publisherId, developerId):
		Logutil.log("Begin Insert file: " +fileName, util.LOG_LEVEL_DEBUG)										
		
		parentId = None
		
		#TODO console and romcollection could be done only once per RomCollection			
		#fileTypeRow[3] = parent
		if(fileType.parent == 'game'):
			Logutil.log("Insert file with parent game", util.LOG_LEVEL_INFO)
			parentId = gameId
		elif(fileType.parent == 'console'):
			Logutil.log("Insert file with parent console", util.LOG_LEVEL_INFO)
			parentId = consoleId		
		elif(fileType.parent == 'publisher'):
			Logutil.log("Insert file with parent publisher", util.LOG_LEVEL_INFO)
			parentId = publisherId
		elif(fileType.parent == 'developer'):
			Logutil.log("Insert file with parent developer", util.LOG_LEVEL_INFO)
			parentId = developerId
			
		fileRow = File(self.gdb).getFileByNameAndTypeAndParent(fileName, fileType.id, parentId)
		if(fileRow == None):
			Logutil.log("File does not exist in database. Insert file: " +fileName, util.LOG_LEVEL_INFO)
			File(self.gdb).insert((str(fileName), fileType.id, parentId))
				

	def getThumbFromOnlineSource(self, gamedescription, fileType, fileName):
		Logutil.log("Get thumb from online source", util.LOG_LEVEL_INFO)
		try:			
			#maybe we got a thumb url from desc parser
			thumbKey = 'Filetype' +fileType
			Logutil.log("using key: " +thumbKey, util.LOG_LEVEL_INFO)
			thumbUrl = self.resolveParseResult(gamedescription, thumbKey)
			Logutil.log("Get thumb from url: " +str(thumbUrl), util.LOG_LEVEL_INFO)
			if(thumbUrl == ''):
				return
			
			rootExtFile = os.path.splitext(fileName)
			rootExtUrl = os.path.splitext(thumbUrl)
			
			if(len(rootExtUrl) == 2 and len(rootExtFile) != 0):
				fileName = rootExtFile[0] + rootExtUrl[1]
			
			#TODO check if folder exists
			Logutil.log("check if file exists: " +str(fileName), util.LOG_LEVEL_INFO)			
			if (not os.path.isfile(fileName)):
				Logutil.log("File does not exist. Starting download.", util.LOG_LEVEL_INFO)				
				# fetch thumbnail and save to filepath
				urllib.urlretrieve( thumbUrl, str(fileName))
				# cleanup any remaining urllib cache
				urllib.urlcleanup()
				Logutil.log("Download finished.", util.LOG_LEVEL_INFO)
		except Exception, (exc):
			Logutil.log("Error in getThumbFromOnlineSource: " +str(exc), util.LOG_LEVEL_WARNING)						
		
		

	def exit(self):
		Logutil.log("Update finished", util.LOG_LEVEL_INFO)		
