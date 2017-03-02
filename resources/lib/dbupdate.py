
import os, sys, re
import getpass, string, glob
import codecs
import zipfile
import time
import urllib2

import xbmcvfs
import fnmatch

import util, helper
from util import *
from util import KodiVersions
from config import *
from gamedatabase import *
from descriptionparserfactory import *
from pyscraper.pyscraper import PyScraper
import nfowriter
from nfowriter import *

#HACK: zlib isn't shipped with some linux distributions
try:
	import zlib
except:
	Logutil.log("Error while loading zlib library. You won't be able to import games using crc values (only used when importing offline game descriptions).", util.LOG_LEVEL_WARNING)


class UpdateLogFile(object):
	_fname = ''
	_header = ''

	def __init__(self):
		with open(self.fname, mode='w') as fh:
			fh.write("{0}\n".format(self._header))
		return

	@property
	def logfile_dir(self):
		return util.getAddonDataPath()

	@property
	def fname(self):
		return os.path.join(self.logfile_dir, self._fname)

	def add_header(self, rcname):
		with open(self.fname, mode='a') as fh:
			fh.write('\n~~~~~~~~~~~~~~~~~~~~~~~~\n{0}\n~~~~~~~~~~~~~~~~~~~~~~~~\n'.format(rcname))

	def add_entry(self, gamename, filename=None):
		if filename is None:
			msg = '{0}\n'.format(gamename)
		else:
			msg = '{0}, {1}\n'.format(gamename, filename)
		with open(self.fname, mode='a') as fh:
			fh.write(msg)


class ScrapeResultsLogFile(UpdateLogFile):
	_fname = u'scrapeResults.txt'
	_header = u'Scrape Results\n=============='


class MissingDescLogFile(UpdateLogFile):
	_fname = u'scrapeResult_missingDesc.txt'
	_header = u'Missing Descriptions\n===================='


class MissingArtworkLogFile(UpdateLogFile):
	_fname = u'scrapeResult_missingArtwork.txt'
	_header = u'Missing Artwork\n=============='

	def add_entry(self, gamename, filename=None, pathtype=None):
		if filename is None:
			msg = '--> No artwork found for game "{0}". Game will not be imported.\n'.format(gamename)
		else:
			msg = '{0} (filename: {1}) ({2})\n'.format(gamename, filename, pathtype)

		with open(self.fname, mode='a') as fh:
			fh.write(msg)


class MismatchLogFile(UpdateLogFile):
	_fname = u'scrapeResult_possibleMismatches.txt'
	_header = u'Possible Mismatches\n===================\n\n'

	def add_header(self, rcname):
		with open(self.fname, mode='w') as fh:
			fh.write('~~~~~~~~~~~~~~~~~~~~~~~~\n{0}\n~~~~~~~~~~~~~~~~~~~~~~~~\n'.format(rcname))
			fh.write('gamename, filename\n')


class DBUpdate:
	
	def __init__(self):
		Logutil.log("init DBUpdate", util.LOG_LEVEL_INFO)

		#self.scrapeResultsFile = ScrapeResultsLogFile()
		self.missingDescFile = MissingDescLogFile()
		self.missingArtworkFile = MissingArtworkLogFile()
		self.possibleMismatchFile = MismatchLogFile()

		pass

	def retrieve_settings(self):
		self.ignoreGameWithoutDesc = self.Settings.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTDESC).upper() == 'TRUE'
		self.ignoreGamesWithoutArtwork = self.Settings.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTARTWORK).upper() == 'TRUE'
		self.createNfoFile = self.Settings.getSetting(util.SETTING_RCB_CREATENFOFILE).upper() == 'TRUE'
		# Set the fuzzy factor before scraping
		matchingRatioIndex = self.Settings.getSetting(util.SETTING_RCB_FUZZYFACTOR)
		if matchingRatioIndex == '':
			matchingRatioIndex = 2
		Logutil.log("matchingRatioIndex: " +str(matchingRatioIndex), util.LOG_LEVEL_INFO)

		self.fuzzyFactor = util.FUZZY_FACTOR_ENUM[int(matchingRatioIndex)]
		Logutil.log("fuzzyFactor: " +str(self.fuzzyFactor), util.LOG_LEVEL_INFO)

	def updateDB(self, gdb, gui, updateOption, romCollections, settings, isRescrape):
		self.gdb = gdb
		self.Settings = settings

		self.retrieve_settings()
		
		Logutil.log("Start Update DB", util.LOG_LEVEL_INFO)
		
		Logutil.log("Iterating Rom Collections", util.LOG_LEVEL_INFO)
		rccount = 1
		
		#always do full reimports when in rescrape-mode 
		enableFullReimport = isRescrape or self.Settings.getSetting(util.SETTING_RCB_ENABLEFULLREIMPORT).upper() == 'TRUE'
		Logutil.log("enableFullReimport: " +str(enableFullReimport), util.LOG_LEVEL_INFO)
		
		continueUpdate = True
		#Added variable to allow user to continue on errors
		ignoreErrors = False
		
		for romCollection in romCollections.values():
			
			#timestamp1 = time.clock()
			
			#check if import was canceled
			if(not continueUpdate):
				Logutil.log('Game import canceled', util.LOG_LEVEL_INFO)
				break
							
			#prepare Header for ProgressDialog
			progDialogRCHeader = util.localize(32122) +" (%i / %i): %s" %(rccount, len(romCollections), romCollection.name)
			rccount = rccount + 1
			
			Logutil.log("current Rom Collection: " +romCollection.name, util.LOG_LEVEL_INFO)

			#Read settings for current Rom Collection
			Logutil.log("ignoreOnScan: " +str(romCollection.ignoreOnScan), util.LOG_LEVEL_INFO)
			if(romCollection.ignoreOnScan):
				Logutil.log("current Rom Collection will be ignored.", util.LOG_LEVEL_INFO)
				#self.scrapeResultsFile.write('Rom Collection will be ignored.\n')
				continue

			Logutil.log("update is allowed for current rom collection: " +str(romCollection.allowUpdate), util.LOG_LEVEL_INFO)
			Logutil.log("max folder depth: " +str(romCollection.maxFolderDepth), util.LOG_LEVEL_INFO)
			
			firstScraper = romCollection.scraperSites[0]
			
			#check if we are in local artwork mode
			if len(romCollection.scraperSites) == 1 and firstScraper.is_localartwork_scraper():
				Logutil.log("Forcing enableFullReimport because we are in local artwork mode", util.LOG_LEVEL_INFO)
				enableFullReimport = True
			
			files = self.getRomFilesByRomCollection(romCollection, enableFullReimport)
			if len(files) == 0:
				Logutil.log(u'No files found for rom collection {0}, skipping'.format (romCollection.name),
							util.LOG_LEVEL_INFO)
				continue
			else:
				Logutil.log(u'Found {0} game files for rom collection {1}'.format(len(files), romCollection.name),
							util.LOG_LEVEL_INFO)
			
			#itemCount is used for percentage in ProgressDialogGUI
			gui.itemCount = len(files) +1

			if firstScraper.is_multigame_scraper():
				#build file hash tables	(key = gamename or crc, value = romfiles)			
				Logutil.log("Start building file dict", util.LOG_LEVEL_INFO)
				fileDict = self.buildFileDict(gui, progDialogRCHeader, files, romCollection, firstScraper)
									
				try:
					fileCount = 0
					gamenameFromDesc = u''
					
					#TODO move to to check preconditions
					#first scraper must be the one for multiple games					
					if(len(firstScraper.scrapers) == 0):
						Logutil.log('Configuration error: Configured scraper site does not contain any scrapers', util.LOG_LEVEL_ERROR)
						continue
											
					scraper = firstScraper.scrapers[0]
					Logutil.log("Parsing with multi game scraper {0} using parser file {1} and game description {2}".format(firstScraper.name, scraper.parseInstruction, scraper.source), util.LOG_LEVEL_INFO)
											
					parser = DescriptionParserFactory.getParser(str(scraper.parseInstruction)) 										
					
					#parse description
					for result in parser.scanDescription(scraper.source, str(scraper.parseInstruction), scraper.encoding):
						try:
							gamenameFromDesc = result['Game'][0]
							
							#find parsed game in Rom Collection
							filenamelist = self.matchDescriptionWithRomfiles(firstScraper, result, fileDict, gamenameFromDesc)
							if filenamelist is None or len(filenamelist) == 0:
								Logutil.log(u'Game {0} was found in parsed results but not in your rom collection'.format(gamenameFromDesc),
											util.LOG_LEVEL_WARNING)
								continue
		
							artScrapers = {}

							gamenameFromFile = helper.getGamenameFromFilename(filenamelist[0], romCollection)
							foldername = self.getFoldernameFromRomFilename(filenamelist[0])

							fileCount = fileCount +1

							continueUpdate = gui.writeMsg(progDialogRCHeader, util.localize(32123) +": " +str(gamenameFromDesc), "", fileCount)
							if(not continueUpdate):
								Logutil.log('Game import canceled by user', util.LOG_LEVEL_INFO)
								break

							Logutil.log('Start scraping info for game: ' +str(gamenameFromFile), LOG_LEVEL_INFO)

							#check if this file already exists in DB
							continueUpdate, isUpdate, gameId = self.checkRomfileAlreadyExists(filenamelist[0], enableFullReimport, False)
							if(not continueUpdate):
								continue

							#use additional scrapers
							if(len(romCollection.scraperSites) > 1):
								result, artScrapers = self.useSingleScrapers(result, romCollection, 1, gamenameFromFile, foldername, filenamelist[0], updateOption, gui, progDialogRCHeader, fileCount)
							
							dialogDict = {'dialogHeaderKey':progDialogRCHeader, 'gameNameKey':gamenameFromFile, 'scraperSiteKey':artScrapers, 'fileCountKey':fileCount}
							gameId = self.insertGameFromDesc(result, gamenameFromFile, romCollection, filenamelist, foldername, isUpdate, gameId, gui, False, dialogDict)
							del artScrapers, gamenameFromFile, foldername, dialogDict
							
							#remove found files from file list
							if(gameId != None):
								Logutil.log("Successfully added {0}".format(gamenameFromDesc), util.LOG_LEVEL_INFO)
								files = [x for x in files if x not in filenamelist]
									
							del filenamelist
									
							#stop import if no files are left
							if(len(files) == 0):
								Logutil.log("All games are imported", util.LOG_LEVEL_INFO)
								break
						
						except Exception, (exc):
							Logutil.log("an error occured while adding game " +gamenameFromDesc, util.LOG_LEVEL_WARNING)
							Logutil.log("Error: " +str(exc), util.LOG_LEVEL_WARNING)
							continue
					
					#all files still available files-list, are missing entries
					for filename in files:
						gamenameFromFile = helper.getGamenameFromFilename(filename, romCollection)
						Logutil.log("Adding file {0} ({1}) to missing description file".format(filename, gamenameFromFile), util.LOG_LEVEL_WARNING)
						self.missingDescFile.add_entry(gamenameFromFile)
							
				except Exception, (exc):
					Logutil.log("an error occured while adding game " +gamenameFromDesc, util.LOG_LEVEL_WARNING)
					Logutil.log("Error: " +str(exc), util.LOG_LEVEL_WARNING)
					self.missingDescFile.add_entry(gamenameFromDesc)

					continue
			else:
				Logutil.log("{0} is not multigame scraper".format(firstScraper.name), util.LOG_LEVEL_INFO)
				successfulFiles = 0
				lastgamename = ''
				lastGameId = None
				
				for fileidx, filename in enumerate(files):
					
					try:
						Logutil.log("Scraping for {0}".format(filename), util.LOG_LEVEL_INFO)
						gamenameFromFile = helper.getGamenameFromFilename(filename, romCollection)
						
						#check if we are handling one of the additional disks of a multi rom game
						isMultiRomGame = self.checkRomfileIsMultirom(gamenameFromFile, lastgamename)
						lastgamename = gamenameFromFile
						
						if(isMultiRomGame):
							# Add this entry as a file under the game ID and move on
							Logutil.log("Detected {0} as a multirom game (previous game was {1}".format(filename, lastgamename), util.LOG_LEVEL_INFO)
							if lastGameId is None:
								Logutil.log('Game detected as multi rom game, but lastGameId is None.', util.LOG_LEVEL_ERROR)
								continue
							fileType = FileType()
							fileType.id = 0
							fileType.name = "rcb_rom"
							fileType.parent = "game"
							self.insertFile(filename, lastGameId, fileType, None, None, None)
							del fileType
							continue
						
						Logutil.log('Start scraping info for game: ' + gamenameFromFile, LOG_LEVEL_INFO)						
						
						continueUpdate = gui.writeMsg(progDialogRCHeader, util.localize(32123) +": " +gamenameFromFile, "", fileidx + 1)
						if(not continueUpdate):				
							Logutil.log('Game import canceled by user', util.LOG_LEVEL_INFO)
							break
						
						#check if this file already exists in DB
						continueUpdate, isUpdate, gameId = self.checkRomfileAlreadyExists(filename,
																						  enableFullReimport,
																						  firstScraper.is_localartwork_scraper())
						if(not continueUpdate):
							continue										
						
						results = {}
						foldername = self.getFoldernameFromRomFilename(filename)
																		
						artScrapers = {} 
						if not firstScraper.is_localartwork_scraper():
							results, artScrapers = self.useSingleScrapers(results, romCollection, 0, gamenameFromFile, foldername, filename, updateOption, gui, progDialogRCHeader, fileidx + 1)
												
						if(len(results) == 0):
							#lastgamename = ""
							results = None
	
						#Variables to process Art Download Info
						dialogDict = {'dialogHeaderKey':progDialogRCHeader, 'gameNameKey':gamenameFromFile, 'scraperSiteKey':artScrapers, 'fileCountKey': (fileidx + 1)}
						del artScrapers
												
						#Add 'gui' and 'dialogDict' parameters to function
						lastGameId = self.insertGameFromDesc(results, gamenameFromFile, romCollection, [filename], foldername, isUpdate, gameId, gui, firstScraper.is_localartwork_scraper(), dialogDict)
						del results, foldername, dialogDict
						
						if (lastGameId != None):
							Logutil.log("Successfully added {0}".format(gamenameFromFile), util.LOG_LEVEL_INFO)
							successfulFiles = successfulFiles + 1
	
						# Check if all first 10 games have errors - Modified to allow user to continue on errors
						if fileidx > 9 and successfulFiles == 0 and not ignoreErrors:
							options = [util.localize(32124), util.localize(32125), util.localize(32126)]
							answer = xbmcgui.Dialog().select(util.localize(32127), options)
							if(answer == 1):
								# Continue and ignore errors
								ignoreErrors = True
							elif(answer == 2):
								# Cancel
								xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32128), util.localize(32129))
								continueUpdate = False
								break
					
					except Exception, (exc):
						Logutil.log("an error occured while adding game " +gamenameFromFile, util.LOG_LEVEL_WARNING)
						Logutil.log("Error: " +str(exc), util.LOG_LEVEL_WARNING)
						self.missingDescFile.add_entry(gamenameFromFile)

						continue
					
					
			#timestamp2 = time.clock()
			#diff = (timestamp2 - timestamp1) * 1000		
			#print "load %i games in %d ms" % (self.getListSize(), diff)
					
		gui.writeMsg("Done.", "", "", gui.itemCount)
		self.exit()
		return True, ''
	
	
	def buildFileDict(self, gui, progDialogRCHeader, files, romCollection, firstScraper):
		
		lastgamename = ""
		crcOfFirstGame = {}
		
		fileDict = {}
		
		for idx, filename in enumerate(files):
			try:
				gui.writeMsg(progDialogRCHeader, util.localize(32130), "", idx + 1)

				gamename = helper.getGamenameFromFilename(filename, romCollection)
				#check if we are handling one of the additional disks of a multi rom game
				isMultiRomGame = self.checkRomfileIsMultirom(gamename, lastgamename)
				#lastgamename may be overwritten by parsed gamename
				lastgamename = gamename
				gamename = gamename.strip()
				gamename = gamename.lower()
				
				#Logutil.log('gamename in fileDict: ' +str(gamename), util.LOG_LEVEL_INFO)
									
				#build dictionaries (key=gamename, filecrc or foldername; value=filenames) for later game search
				if(firstScraper.useFoldernameAsCRC):
					Logutil.log('useFoldernameAsCRC = True', util.LOG_LEVEL_INFO)
					foldername = self.getFoldernameFromRomFilename(filename)
					foldername = foldername.strip()
					foldername = foldername.lower()
					fileDict = self.buildFilenameDict(fileDict, isMultiRomGame, filename, foldername)
				elif(firstScraper.useFilenameAsCRC):
					Logutil.log('useFilenameAsCRC = True', util.LOG_LEVEL_INFO)
					fileDict = self.buildFilenameDict(fileDict, isMultiRomGame, filename, gamename)
				elif(firstScraper.searchGameByCRC):
					Logutil.log('searchGameByCRC = True', util.LOG_LEVEL_INFO)
					filecrc = self.getFileCRC(filename)
					#use crc of first rom if it is a multirom game
					if(not isMultiRomGame):
						crcOfFirstGame[gamename] = filecrc
						Logutil.log('Adding crc to crcOfFirstGame-dict: %s: %s' %(gamename, filecrc), util.LOG_LEVEL_INFO)
					else:
						filecrc = crcOfFirstGame[gamename]
						Logutil.log('Read crc from crcOfFirstGame-dict: %s: %s' %(gamename, filecrc), util.LOG_LEVEL_INFO)
						
					fileDict = self.buildFilenameDict(fileDict, isMultiRomGame, filename, filecrc)
				else:						
					fileDict = self.buildFilenameDict(fileDict, isMultiRomGame, filename, gamename)
			except Exception, (exc):
				Logutil.log("an error occured while building file list", util.LOG_LEVEL_WARNING)
				Logutil.log("Error: " +str(exc), util.LOG_LEVEL_WARNING)
				continue
		
		return fileDict
		
		
	
	
	def getRomFilesByRomCollection(self, romCollection, enableFullReimport):
				
		Logutil.log("Rom path: " +str(romCollection.romPaths), util.LOG_LEVEL_INFO)
				
		Logutil.log("Reading rom files", util.LOG_LEVEL_INFO)
		files = []
		for romPath in romCollection.romPaths:
			Logutil.log("Reading rom files in path: {0}".format(romPath), util.LOG_LEVEL_INFO)
			files = self.walkDownPath(files, unicode(romPath), romCollection.maxFolderDepth)
		
		#only use files that are not already present in database
		if enableFullReimport == False:
			inDBFiles = DataBaseObject(self.gdb, '').getFileAllFilesByRCId(romCollection.id)
			files = [f for f in files if not f in inDBFiles]
		
		files.sort()
		Logutil.log("Files read: " +str(files), util.LOG_LEVEL_INFO)
		
		return files
		
		
	def walkDownPath(self, files, romPath, maxFolderDepth):
		
		Logutil.log("walkDownPath romPath: " +romPath, util.LOG_LEVEL_INFO)
		
		files = self.walkDown(files, romPath, maxFolderDepth)
		Logutil.log("files after walkDown = %s" %files, util.LOG_LEVEL_INFO)
		
		return files
	
	
	def walkDown(self, files, romPath, maxFolderDepth):
		Logutil.log("Running walkdown on: %s" %romPath, util.LOG_LEVEL_INFO)
				
		dirs, newFiles, dirname, filemask = self.getFilesByWildcardExt(romPath)
		files.extend(newFiles)
		
		for dir in dirs:
			newRomPath = util.joinPath(dirname, dir, filemask)
			maxFolderDepth = maxFolderDepth -1
			if(maxFolderDepth > 0):
				self.walkDown(files, newRomPath, maxFolderDepth)
					
		return files
			
		
	def checkRomfileIsMultirom(self, gamename, lastgamename):
	
		Logutil.log("checkRomfileIsMultirom. gamename = %s, lastgamename = %s" %(gamename, lastgamename), util.LOG_LEVEL_INFO)
	
		#XBOX Hack: rom files will always be named default.xbe: always detected as multi rom without this hack
		if(gamename == lastgamename and lastgamename.lower() != 'default'):		
			Logutil.log("handling multi rom game: " +lastgamename, util.LOG_LEVEL_INFO)			
			return True
		return False
		
		
	def buildFilenameDict(self, result, isMultiRomGame, filename, key):

		try:											
			if isMultiRomGame:
				result[key].append(filename)
				Logutil.log('Add filename "%s" to multirom game with key "%s"' %(filename, key), util.LOG_LEVEL_DEBUG)
			else:
				result[key] = [filename]
				Logutil.log('Add filename "%s" with key "%s"' %(filename, key), util.LOG_LEVEL_DEBUG)
		except Exception, (exc):
			Logutil.log('Error occured in buildFilenameDict: ' +str(exc), util.LOG_LEVEL_WARNING)
			
		return result
		
		
	def getFileCRC(self, filename):
		
		try:
			#get crc value of the rom file - this can take a long time for large files, so it is configurable
			filecrc = ''		
			if (zipfile.is_zipfile(str(filename))):			
					Logutil.log("handling zip file", util.LOG_LEVEL_INFO)
					zip = zipfile.ZipFile(str(filename), 'r')
					zipInfos = zip.infolist()
					del zip
					if(len(zipInfos) > 1):
						Logutil.log("more than one file in zip archive is not supported! Checking CRC of first entry.", util.LOG_LEVEL_WARNING)
					filecrc = "%0.8X" %(zipInfos[0].CRC & 0xFFFFFFFF)
					Logutil.log("crc in zipped file: " +filecrc, util.LOG_LEVEL_INFO)			
			else:						
				prev = 0
				for eachLine in open(str(filename),"rb"):
					prev = zlib.crc32(eachLine, prev)					
				filecrc = "%0.8X"%(prev & 0xFFFFFFFF)
				Logutil.log("crc for current file: " +str(filecrc), util.LOG_LEVEL_INFO)
			
			filecrc = filecrc.strip()
			filecrc = filecrc.lower()
		except Exception, (exc):
			Logutil.log("Error while creating crc: " +str(exc), util.LOG_LEVEL_ERROR)
			return "000000"
		
		return filecrc
		
		
	def getFoldernameFromRomFilename(self, filename):
		Logutil.log("Begin getFoldernameFromRomFilename: %s" +filename, util.LOG_LEVEL_INFO)		
		foldername = ''
		dirname = os.path.dirname(filename)
		Logutil.log("dirname: %s" %dirname, util.LOG_LEVEL_INFO)
		if(dirname != None):
			pathTuple = os.path.split(dirname)
			if(len(pathTuple) == 2):
				foldername = pathTuple[1]				
				
		return foldername


	def matchDescriptionWithRomfiles(self, firstScraper, result, fileDict, gamenameFromDesc):
			
		filenamelist = []
		
		if(firstScraper.searchGameByCRC or firstScraper.useFoldernameAsCRC or firstScraper.useFilenameAsCRC):
			resultcrcs = result['crc']
			for resultcrc in resultcrcs:
				Logutil.log("crc in parsed result: " +resultcrc, util.LOG_LEVEL_DEBUG)
				resultcrc = resultcrc.lower()
				resultcrc = resultcrc.strip()
				filenamelist = self.findFilesByGameDescription(resultcrc, fileDict)
				if(filenamelist != None):
					break
		else:
			Logutil.log("game name in parsed result: " +gamenameFromDesc, util.LOG_LEVEL_INFO)
			gamenameFromDesc = gamenameFromDesc.lower()
			gamenameFromDesc = gamenameFromDesc.strip()
			filenamelist = self.findFilesByGameDescription(gamenameFromDesc, fileDict)
		
		return filenamelist


	def findFilesByGameDescription(self, key, fileDict):
		
		Logutil.log("searching for Key: " +str(key), util.LOG_LEVEL_INFO)
			
		try:
			filename = fileDict[key]
			Logutil.log("result found: " +str(filename), util.LOG_LEVEL_INFO)
		except:
			filename = None

		return filename
	
	
	def checkRomfileAlreadyExists(self, filename, enableFullReimport, isLocalArtwork):
		
		isUpdate = False
		gameId = None
		Logutil.log("Checking if file already exists in DB: {0}".format(str(filename)), util.LOG_LEVEL_DEBUG)
		romFile = File(self.gdb).getFileByNameAndType(filename, 0)
		if(romFile != None):
			isUpdate = True
			gameId = romFile[3]
			Logutil.log('File "%s" already exists in database.' %filename, util.LOG_LEVEL_INFO)
			Logutil.log('Always rescan imported games = ' +str(enableFullReimport), util.LOG_LEVEL_INFO)
			Logutil.log('scraper == "local artwork": ' +str(isLocalArtwork), util.LOG_LEVEL_INFO)
			if(enableFullReimport == False and not isLocalArtwork):
				Logutil.log('Won\'t scrape this game again. Set "Always rescan imported games" to True to force scraping.', util.LOG_LEVEL_INFO)
				return False, isUpdate, gameId
		else:
			Logutil.log("Couldn't find file in DB", util.LOG_LEVEL_DEBUG)
			if(isLocalArtwork):
				Logutil.log('scraper == "local artwork": ' +str(isLocalArtwork), util.LOG_LEVEL_INFO)
				Logutil.log('Can\'t use "local artwork" scraper if game is not already imported. Use another scraper first.', util.LOG_LEVEL_INFO)
				return False, isUpdate, gameId
		
		return True, isUpdate, gameId
		
				
	def useSingleScrapers(self, result, romCollection, startIndex, gamenameFromFile, foldername, firstRomfile, updateOption, gui, progDialogRCHeader, fileCount):
		
		filecrc = ''
		artScrapers = {}
		
		for idx, scraperSite in enumerate(romCollection.scraperSites):
			
			gui.writeMsg(progDialogRCHeader, util.localize(32123) +": " +gamenameFromFile, scraperSite.name + " - " +util.localize(32131), fileCount)
			Logutil.log('Using site {0} with {1} scrapers'.format(scraperSite.name, len(scraperSite.scrapers)), util.LOG_LEVEL_INFO)
			
			if(scraperSite.searchGameByCRC and filecrc == ''):
				filecrc = self.getFileCRC(firstRomfile)
			
			urlsFromPreviousScrapers = []
			doContinue = False
			for scraper in scraperSite.scrapers:
				Logutil.log('Retrieving results for scraper {0} - {1}'.format(idx, scraper.source), util.LOG_LEVEL_DEBUG)
				pyScraper = PyScraper()
				result, urlsFromPreviousScrapers, doContinue = pyScraper.scrapeResults(result, scraper, urlsFromPreviousScrapers, gamenameFromFile, foldername, filecrc, firstRomfile, self.fuzzyFactor, updateOption, romCollection, self.Settings)
				del pyScraper
			Logutil.log('Completed site {0}'.format(scraperSite.name), util.LOG_LEVEL_DEBUG)
			if(doContinue):
				continue
									
			#Find Filetypes and Scrapers for Art Download
			if(len(result) > 0):
				for path in romCollection.mediaPaths:
					thumbKey = 'Filetype' + path.fileType.name 
					if(len(self.resolveParseResult(result, thumbKey)) > 0):
						if((thumbKey in artScrapers) == 0):
							artScrapers[thumbKey] = scraperSite.name			
						
		return result, artScrapers
				
				
	def insertGameFromDesc(self, gamedescription, gamename, romCollection, filenamelist, foldername, isUpdate, gameId, gui, isLocalArtwork, dialogDict=''):
		
		Logutil.log("insertGameFromDesc", util.LOG_LEVEL_INFO)
		
		if(gamedescription != None):
			game = self.resolveParseResult(gamedescription, 'Game')
		else:
			if(not isLocalArtwork):
				self.missingDescFile.add_entry(gamename)

				if self.ignoreGameWithoutDesc:
					Logutil.log('No description found for game "%s". Game will not be imported.' %gamename, util.LOG_LEVEL_WARNING)
					return None
			game = ''
			gamedescription = {}
					
		gameId = self.insertData(gamedescription, gamename, romCollection, filenamelist, foldername, isUpdate, gameId, gui, isLocalArtwork, dialogDict)
		return gameId

	def add_genres_to_db(self, genreIds, gameId):
		# If the genre-game link doesn't exist in the DB, create it
		for genreId in genreIds:
			genreGame = GenreGame(self.gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
			if genreGame is None:
				Logutil.log("Inserting link between game {0} and genre {1}".format(str(gameId), str(genreId)), util.LOG_LEVEL_DEBUG)
				GenreGame(self.gdb).insert((genreId, gameId))
			del genreGame

	def add_romfiles_to_db(self, romFiles, gameId):
		for romFile in romFiles:
			Logutil.log("Adding romfile to DB: {0}".format(str(romFile)), util.LOG_LEVEL_DEBUG)
			fileType = FileType()
			fileType.id = 0
			fileType.name = "rcb_rom"
			fileType.parent = "game"
			self.insertFile(romFile, gameId, fileType, None, None, None)
			del fileType
			
	def insertData(self, gamedescription, gamenameFromFile, romCollection, romFiles, foldername, isUpdate, gameId, gui, isLocalArtwork, dialogDict=''):
		Logutil.log("Insert data", util.LOG_LEVEL_INFO)
		
		publisher = self.resolveParseResult(gamedescription, 'Publisher')
		developer = self.resolveParseResult(gamedescription, 'Developer')
		year = self.resolveParseResult(gamedescription, 'ReleaseYear')
		
		yearId = self.insertForeignKeyItem(gamedescription, 'ReleaseYear', Year(self.gdb))
		genreIds = self.insertForeignKeyItemList(gamedescription, 'Genre', Genre(self.gdb))
		reviewerId = self.insertForeignKeyItem(gamedescription, 'Reviewer', Reviewer(self.gdb))
			
		publisherId = -1
		developerId = -1
			
		#read current properties for local artwork scraper
		if(not isLocalArtwork):
			publisherId = self.insertForeignKeyItem(gamedescription, 'Publisher', Publisher(self.gdb))
			developerId = self.insertForeignKeyItem(gamedescription, 'Developer', Developer(self.gdb))
		else:
			gameRow = Game(self.gdb).getObjectById(gameId)
			if(gameRow != None):
				publisherId = gameRow[GAME_publisherId]
				publisherRow = Publisher(self.gdb).getObjectById(gameId)
				if(publisherRow != None):
					publisher = publisherRow[util.ROW_NAME]  			
				developerId = gameRow[GAME_developerId]
				del gameRow
				developerRow = Developer(self.gdb).getObjectById(gameId)
				if(developerRow != None):
					developer = developerRow[util.ROW_NAME]
					del developerRow
		
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
		plot = self.resolveParseResult(gamedescription, 'Description')
		isFavorite = self.resolveParseResult(gamedescription, 'IsFavorite')
		if(isFavorite == ''):
			isFavorite = '0'
		launchCount = self.resolveParseResult(gamedescription, 'LaunchCount')
		if(launchCount == ''):
			launchCount = '0'
		
		if(gamedescription != None):
			gamename = self.resolveParseResult(gamedescription, 'Game')
			if(gamename != gamenameFromFile):
				self.possibleMismatchFile.add_entry(gamename, gamenameFromFile)

			if(gamename == ""):
				gamename = gamenameFromFile
		else:
			gamename = gamenameFromFile
		
		artWorkFound, artworkfiles, artworkurls = self.getArtworkForGame(romCollection, gamename, gamenameFromFile, gamedescription, gui, dialogDict, foldername, publisher, developer, isLocalArtwork)
				
		if not artWorkFound and self.ignoreGamesWithoutArtwork:
			Logutil.log('No artwork found for game "%s". Game will not be imported.' %gamenameFromFile, util.LOG_LEVEL_WARNING)
			self.missingArtworkFile.add_entry(gamename)

			return None

			
		# Create Nfo file with game properties
		if self.createNfoFile and gamedescription != None:
			try:
				genreList = gamedescription['Genre']
			except:
				genreList = []
			nfowriter.NfoWriter().createNfoFromDesc(gamename, plot, romCollection.name, publisher, developer, year, 
				players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, version, genreList, isFavorite, launchCount, romFiles[0], gamenameFromFile, artworkfiles, artworkurls)
			del genreList
					
		del publisher, developer, year		
						
		if(not isLocalArtwork):
			gameId = self.insertGame(gamename, plot, romCollection.id, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version, isFavorite, launchCount, isUpdate, gameId, romCollection.allowUpdate, )
		
			del plot, players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version
		
			if(gameId == None):
				return None

			self.add_genres_to_db(genreIds, gameId)

			self.add_romfiles_to_db(romFiles, gameId)

		for fileType, fileNames in artworkfiles.iteritems():
			for filename in fileNames:
				Logutil.log("Importing artwork file {0} = {1}".format(fileType.type, str(filename)), util.LOG_LEVEL_INFO)
				self.insertFile(filename, gameId, fileType, romCollection.id, publisherId, developerId)
				
		self.gdb.commit()
		return gameId

	def getArtworkForGame(self, romCollection, gamename, gamenameFromFile, gamedescription, gui, dialogDict, foldername, publisher, developer, isLocalArtwork):
		artWorkFound = False
		artworkfiles = {}
		artworkurls = {}
		for path in romCollection.mediaPaths:
						
			Logutil.log("FileType: " +str(path.fileType.name), util.LOG_LEVEL_INFO)			
			
			#TODO replace %ROMCOLLECTION%, %PUBLISHER%, ... 
			fileName = path.path.replace("%GAME%", gamenameFromFile)
									
			if(not isLocalArtwork):
				continueUpdate, artworkurls = self.getThumbFromOnlineSource(gamedescription, path.fileType.name, fileName, gui, dialogDict, artworkurls)
				if(not continueUpdate):
					return None, False
			
			Logutil.log("Additional data path: " +str(path.path), util.LOG_LEVEL_DEBUG)
			files = self.resolvePath((path.path,), gamename, gamenameFromFile, foldername, romCollection.name, publisher, developer)
			if(len(files) > 0):
				artWorkFound = True
				
				#HACK: disable static image check as a preparation for new default image handling (this code has problems with [] in rom names)				
				"""
				imagePath = str(self.resolvePath((path.path,), gamename, gamenameFromFile, foldername, romCollection.name, publisher, developer))
				staticImageCheck = imagePath.upper().find(gamenameFromFile.upper())
				
				#make sure that it was no default image that was found here
				if(staticImageCheck != -1):
					artWorkFound = True
				"""					
			else:
				self.missingArtworkFile.add_entry(gamename, gamenameFromFile, path.fileType.name)
			
			artworkfiles[path.fileType] = files
		
		return artWorkFound, artworkfiles, artworkurls
		
	# FIXME TODO Can we create a game object and set the vars on it rather than pass in a million values
	def insertGame(self, gameName, description, romCollectionId, publisherId, developerId, reviewerId, yearId, 
				players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version, isFavorite, launchCount, isUpdate, gameId, allowUpdate):
		# Check if exists and insert/update as appropriate; move this functionality to the Game object
		try:
			if(not isUpdate):
				Logutil.log("Game does not exist in database. Insert game: " +gameName, util.LOG_LEVEL_INFO)
				Game(self.gdb).insert((gameName, description, None, None, romCollectionId, publisherId, developerId, reviewerId, yearId, 
					players, rating, votes, url, region, media, perspective, controller, int(isFavorite), int(launchCount), originalTitle, alternateTitle, translatedBy, version))				
				return self.gdb.cursor.lastrowid
			else:	
				if(allowUpdate):
					
					#check if we are allowed to update with null values
					allowOverwriteWithNullvalues = self.Settings.getSetting(util.SETTING_RCB_ALLOWOVERWRITEWITHNULLVALUES).upper() == 'TRUE'
					Logutil.log("allowOverwriteWithNullvalues: " +str(allowOverwriteWithNullvalues), util.LOG_LEVEL_INFO)
										
					Logutil.log("Game does exist in database. Update game: " +gameName, util.LOG_LEVEL_INFO)
					Game(self.gdb).update(('name', 'description', 'romCollectionId', 'publisherId', 'developerId', 'reviewerId', 'yearId', 'maxPlayers', 'rating', 'numVotes',
						'url', 'region', 'media', 'perspective', 'controllerType', 'originalTitle', 'alternateTitle', 'translatedBy', 'version', 'isFavorite', 'launchCount'),
						(gameName, description, romCollectionId, publisherId, developerId, reviewerId, yearId, players, rating, votes, url, region, media, perspective, controller,
						originalTitle, alternateTitle, translatedBy, version, int(isFavorite), int(launchCount)),
						gameId, allowOverwriteWithNullvalues)
				else:
					Logutil.log("Game does exist in database but update is not allowed for current rom collection. game: " +gameName, util.LOG_LEVEL_INFO)
								
				return gameId
		except Exception, (exc):
			Logutil.log("An error occured while adding game '%s'. Error: %s" %(gameName, str(exc)), util.LOG_LEVEL_ERROR)
			return None
			
		
	
	def insertForeignKeyItem(self, result, itemName, gdbObject):
		
		item = self.resolveParseResult(result, itemName)
						
		if(item != "" and item != None):
			itemRow = gdbObject.getOneByName(item)
			if(itemRow == None):	
				try:
					Logutil.log(itemName +" does not exist in database. Insert: " +item, util.LOG_LEVEL_INFO)
				except:
					pass
				gdbObject.insert((item,))
				del item
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
			item = self.stripHTMLTags(item)
			
			itemRow = gdbObject.getOneByName(item)
			if(itemRow == None):
				try:
					Logutil.log(itemName +" does not exist in database. Insert: " +item, util.LOG_LEVEL_INFO)
				except:
					pass
				gdbObject.insert((item,))
				idList.append(self.gdb.cursor.lastrowid)
			else:
				idList.append(itemRow[0])
				
		return idList
		
		
	def resolvePath(self, paths, gamename, gamenameFromFile, foldername, romCollectionName, publisher, developer):		
		resolvedFiles = []				
				
		for path in paths:
			files = []
			Logutil.log("resolve path: " +path, util.LOG_LEVEL_INFO)
			
			if(path.find("%GAME%") > -1):
				
				pathnameFromFile = path.replace("%GAME%", gamenameFromFile)									
				Logutil.log("resolved path from rom file name: " +pathnameFromFile, util.LOG_LEVEL_INFO)					
				files = self.getFilesByWildcard(pathnameFromFile)
				if(len(files) == 0):
					files = self.getFilesByGameNameIgnoreCase(pathnameFromFile)
				
				if(gamename != gamenameFromFile and len(files) == 0):
					pathnameFromGameName = path.replace("%GAME%", gamename)
					Logutil.log("resolved path from game name: " +pathnameFromGameName, util.LOG_LEVEL_INFO)				
					files = self.getFilesByWildcard(pathnameFromGameName)
					if(len(files) == 0):
						files = self.getFilesByGameNameIgnoreCase(pathnameFromGameName)								
									
				if(gamename != foldername and len(files) == 0):
					pathnameFromFolder = path.replace("%GAME%", foldername)					
					Logutil.log("resolved path from rom folder name: " +pathnameFromFolder, util.LOG_LEVEL_INFO)					
					files = self.getFilesByWildcard(pathnameFromFolder)
					if(len(files) == 0):
						files = self.getFilesByGameNameIgnoreCase(pathnameFromFolder)
				
				
			#TODO could be done only once per RomCollection
			if(path.find("%ROMCOLLECTION%") > -1 and romCollectionName != None and len(files) == 0):
				pathnameFromRomCollection = path.replace("%ROMCOLLECTION%", romCollectionName)
				Logutil.log("resolved path from rom collection name: " +pathnameFromRomCollection, util.LOG_LEVEL_INFO)
				files = self.getFilesByWildcard(pathnameFromRomCollection)				
				
			if(path.find("%PUBLISHER%") > -1 and publisher != None and len(files) == 0):
				pathnameFromPublisher = path.replace("%PUBLISHER%", publisher)
				Logutil.log("resolved path from publisher name: " +pathnameFromPublisher, util.LOG_LEVEL_INFO)
				files = self.getFilesByWildcard(pathnameFromPublisher)				
				
			if(path.find("%DEVELOPER%") > -1 and developer != None and len(files) == 0):
				pathnameFromDeveloper = path.replace("%DEVELOPER%", developer)
				Logutil.log("resolved path from developer name: " +pathnameFromDeveloper, util.LOG_LEVEL_INFO)
				files = self.getFilesByWildcard(pathnameFromDeveloper)													
			
			if(path.find("%GAME%") == -1 & path.find("%ROMCOLLECTION%") == -1 & path.find("%PUBLISHER%") == -1 & path.find("%DEVELOPER%") == -1):
				pathnameFromStaticFile = path
				Logutil.log("using static defined media file from path: " + pathnameFromStaticFile, util.LOG_LEVEL_INFO)
				files = self.getFilesByWildcard(pathnameFromStaticFile)			
				
			if(len(files) == 0):
				Logutil.log('No files found for game "%s" at path "%s". Make sure that file names are matching.' %(gamename, path), util.LOG_LEVEL_WARNING)
			for file in files:
				if(xbmcvfs.exists(file)):
					resolvedFiles.append(file)
					
		return resolvedFiles
	
	
	def getFilesByWildcard(self, pathName):
		dirs, files, dirname, filemask = self.getFilesByWildcardExt(pathName)
		return files
	
	
	def getFilesByWildcardExt(self, pathName):
		
		Logutil.log('Begin getFilesByWildcard. pathName = %s' %pathName, util.LOG_LEVEL_INFO)
		files = []
		dirs = []
		
		dirname = os.path.dirname(pathName)
		Logutil.log("dirname: " +dirname, util.LOG_LEVEL_INFO)
		filemask = os.path.basename(pathName)
		#HACK: escape [] for use with fnmatch
		filemask = filemask.replace('[', '[[]')
		filemask = filemask.replace(']', '[]]')
		#This might be stupid but it was late...
		filemask = filemask.replace('[[[]]', '[[]')
		Logutil.log("filemask: " +filemask, util.LOG_LEVEL_INFO)
		
		dirsLocal, filesLocal = xbmcvfs.listdir(dirname)
		Logutil.log("xbmcvfs dirs: %s" %dirs, util.LOG_LEVEL_INFO)
		Logutil.log("xbmcvfs files: %s" %filesLocal, util.LOG_LEVEL_INFO)
		
		for dir in dirsLocal:
			if (type(dir) == str):
				dirs.append(dir.decode('utf-8'))
			else:
				dirs.append(dir)
			
		for file in filesLocal:
			if(fnmatch.fnmatch(file, filemask)):
			#allFiles = [f.decode(sys.getfilesystemencoding()).encode('utf-8') for f in glob.glob(newRomPath)]
				if (type(file) == str):
					file = file.decode('utf-8')
				file = util.joinPath(dirname, file)
				# return unicode filenames so relating scraping actions can handle them correctly				
				files.append(file)
				
		return dirs, files, dirname, filemask
		
		"""
		try:
			# try glob with * wildcard
			files = glob.glob(pathName)
			Logutil.log('files after glob.glob: %s' %files, util.LOG_LEVEL_INFO)
		except Exception, (exc):
			Logutil.log("Error using glob function in resolvePath " +str(exc), util.LOG_LEVEL_WARNING)
			
		if(len(files) == 0):
			#HACK: removed \s from regular expression. previous version was '\s\[.*\]' 
			squares = re.findall('\[.*\]',pathName)
			if(squares != None and len(squares) >= 1):
				Logutil.log('Replacing [...] with *', util.LOG_LEVEL_INFO)
				for square in squares:						
					pathName = pathName.replace(square, '*')
			
				Logutil.log('new pathname: ' +str(pathName), util.LOG_LEVEL_INFO)
				try:
					files = glob.glob(pathName)
				except Exception, (exc):
					Logutil.log("Error using glob function in resolvePath " +str(exc), util.LOG_LEVEL_WARNING)
		
		# glob can't handle []-characters - try it with listdir
		if(len(files)  == 0):
			try:
				if(xbmcvfs.exists(pathName)):
					files.append(pathName)
				else:
					files = xbmcvfs.listdir(pathName)					
			except:
				pass
		Logutil.log("resolved files: " +str(files), util.LOG_LEVEL_INFO)
		return files
		"""	
		
		
	def getFilesByGameNameIgnoreCase(self, pathname):
		
		files = []
		
		dirname = os.path.dirname(pathname)
		basename = os.path.basename(pathname)
		
		#search all Files that start with the first character of game name
		newpath = util.joinPath(dirname, basename[0].upper() +'*')
		filesUpper = glob.glob(newpath)
		newpath = util.joinPath(dirname, basename[0].lower() +'*')
		filesLower = glob.glob(newpath)
		
		allFiles = filesUpper + filesLower
		for file in allFiles:
			if(pathname.lower() == file.lower()):
				Logutil.log('Found path "%s" by search with ignore case.' %pathname, util.LOG_LEVEL_WARNING)
				files.append(file)
				
		return files
		
		
	def resolveParseResult(self, result, itemName):
		
		resultValue = u''
		
		try:			
			resultValue = result[itemName][0]
			
			if(itemName == 'ReleaseYear' and resultValue != None):
				if(type(resultValue) is time.struct_time):
					resultValue = str(resultValue[0])
				elif(len(resultValue) > 4):
					resultValueOrig = resultValue
					resultValue = resultValue[0:4]
					try:
						#year must be numeric
						int(resultValue)
					except:
						resultValue = resultValueOrig[len(resultValueOrig) -4:]
						try:
							int(resultValue)
						except:
							resultValue = u''
							
			#replace and remove HTML tags
			resultValue = self.stripHTMLTags(resultValue)
			resultValue = resultValue.strip()
			if (type(resultValue) == str):
				resultValue = resultValue.decode('utf-8')
									
		except Exception, (exc):
			Logutil.log("Error while resolving item: " +itemName +" : " +str(exc), util.LOG_LEVEL_WARNING)
						
		try:
			Logutil.log("Result " +itemName +" = " +resultValue, util.LOG_LEVEL_DEBUG)
		except:
			pass
				
		return resultValue
	
	
	def stripHTMLTags(self, inputString):
				
		inputString = util.html_unescape(inputString)
		
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
			
		
	def insertFile(self, fileName, gameId, fileType, romCollectionId, publisherId, developerId):
		Logutil.log("Begin Insert file: " +fileName, util.LOG_LEVEL_DEBUG)										
		
		parentId = None
		
		#TODO console and romcollection could be done only once per RomCollection			
		#fileTypeRow[3] = parent
		if(fileType.parent == 'game'):
			parentId = gameId
		elif(fileType.parent == 'romcollection'):
			parentId = romCollectionId
		elif(fileType.parent == 'publisher'):
			parentId = publisherId
		elif(fileType.parent == 'developer'):
			parentId = developerId

		Logutil.log("Inserting file with parent {0} (type {1})".format(parentId, fileType.parent), util.LOG_LEVEL_INFO)
			
		fileRow = File(self.gdb).getFileByNameAndTypeAndParent(fileName, fileType.id, parentId)
		if(fileRow == None):
			Logutil.log("File does not exist in database. Insert file: " +fileName, util.LOG_LEVEL_INFO)
			f = File(self.gdb)
			try:
				f.insert((fileName, fileType.id, parentId))
			except Exception, (exc):
				Logutil.log("Error inserting into database: " +fileName, util.LOG_LEVEL_WARNING)
		else:
			Logutil.log("File already exists in database: " +fileName, util.LOG_LEVEL_INFO)
				

	def download_thumb(self, thumburl, destfilename):
		# Download file to tmp folder
		tmp = util.joinPath(util.getTempDir(), os.path.basename(destfilename))

		req = urllib2.Request(thumburl)
		req.add_unredirected_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31')
		f = open(tmp, 'wb')
		f.write(urllib2.urlopen(req).read())
		f.close()

		# Copy from the tmp folder to the target location
		xbmcvfs.copy(tmp, destfilename)
		xbmcvfs.delete(tmp)

	def getThumbFromOnlineSource(self, gamedescription, fileType, fileName, gui, dialogDict, artworkurls):
		Logutil.log("Get thumb from online source", util.LOG_LEVEL_INFO)
		
		try:
			#maybe we got a thumb url from desc parser
			thumbKey = 'Filetype' +fileType
			Logutil.log("using key: " +thumbKey, util.LOG_LEVEL_INFO)
			thumbUrl = self.resolveParseResult(gamedescription, thumbKey)			
			if(thumbUrl == ''):
				return True, artworkurls
			
			artworkurls[fileType] = thumbUrl
			
			Logutil.log("Get thumb from url: " +str(thumbUrl), util.LOG_LEVEL_INFO)
			
			rootExtFile = os.path.splitext(fileName)
			rootExtUrl = os.path.splitext(thumbUrl)
			
			files = []
			if(len(rootExtUrl) == 2 and len(rootExtFile) != 0):
				fileName = rootExtFile[0] + rootExtUrl[1]
				gameName = rootExtFile[0] + ".*"
				files = self.getFilesByWildcard(gameName)
			del rootExtFile, rootExtUrl

			if len(files) > 0:
				Logutil.log("File already exists. Won't download again.", util.LOG_LEVEL_INFO)
				return True, artworkurls

			# Create folder if it doesn't already exist
			dirname = os.path.join(os.path.dirname(fileName), '')	# Add the trailing slash that xbmcvfs.exists expects
			Logutil.log("Checking for artwork directory {0}".format(dirname), util.LOG_LEVEL_DEBUG)
			if KodiVersions.getKodiVersion() >= KodiVersions.KRYPTON:
				exists = xbmcvfs.exists(dirname)
			else:
				exists = os.path.exists(dirname)
			if not exists:
				Logutil.log("Artwork directory {0} doesn't exist, creating it".format(dirname), util.LOG_LEVEL_INFO)
				success = xbmcvfs.mkdirs(dirname)
				if not success:
					Logutil.log("Could not create artwork directory: '%s'" %(dirname), util.LOG_LEVEL_ERROR)
					xbmcgui.Dialog().ok(util.localize(32010), util.localize(32011))
					del dirname
					return False, artworkurls

			Logutil.log("File {0} does not exist, starting download".format(fileName), util.LOG_LEVEL_INFO)
			#Dialog Status Art Download
			try:
				if(dialogDict != ''):
					progDialogRCHeader = dialogDict["dialogHeaderKey"]
					gamenameFromFile = dialogDict["gameNameKey"]
					scraperSiteName = dialogDict["scraperSiteKey"]
					fileCount = dialogDict["fileCountKey"]
					gui.writeMsg(progDialogRCHeader, util.localize(32123) +": " +gamenameFromFile, str(scraperSiteName[thumbKey]) + " - downloading art", fileCount)
					del thumbKey, progDialogRCHeader, gamenameFromFile, scraperSiteName, fileCount
			except:
				pass

			try:
				self.download_thumb(thumbUrl, fileName)

			except Exception, (exc):
				Logutil.log("Could not create file: '%s'. Error message: '%s'" %(str(fileName), str(exc)), util.LOG_LEVEL_ERROR)
				#xbmcgui.Dialog().ok(util.localize(32012), util.localize(32011))
				return False, artworkurls

			Logutil.log("Download finished.", util.LOG_LEVEL_INFO)

		except Exception, (exc):
			Logutil.log("Error in getThumbFromOnlineSource: " +str(exc), util.LOG_LEVEL_WARNING)

		return True, artworkurls

	def exit(self):
		Logutil.log("Update finished", util.LOG_LEVEL_INFO)
