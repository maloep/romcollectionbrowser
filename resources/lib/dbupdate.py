
import getpass, glob
import time
import urllib2
import io

import xbmcvfs
import xbmcgui
import fnmatch

import util
from util import *
from util import KodiVersions
from util import Logutil as log
from util import __addon__
from config import *
from gamedatabase import *
from descriptionparserfactory import *
from pyscraper.scraper import AbstractScraper
from pyscraper.matcher import Matcher

from nfowriter import NfoWriter
from rcbexceptions import *

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
			msg = u'{0}\n'.format(gamename)
		else:
			msg = u'{0}, {1}\n'.format(gamename, filename)
		with io.open(self.fname, mode='a', encoding='utf-8') as fh:
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
			msg = u'--> No artwork found for game "{0}". Game will not be imported.\n'.format(gamename)
		else:
			msg = u'{0} (filename: {1}) ({2})\n'.format(gamename, filename, pathtype)

		with io.open(self.fname, mode='a', encoding='utf-8') as fh:
			fh.write(msg)


class MismatchLogFile(UpdateLogFile):
	_fname = u'scrapeResult_possibleMismatches.txt'
	_header = u'Possible Mismatches\n===================\n\n'

	def add_header(self, rcname):
		with open(self.fname, mode='w') as fh:
			fh.write('~~~~~~~~~~~~~~~~~~~~~~~~\n{0}\n~~~~~~~~~~~~~~~~~~~~~~~~\n'.format(rcname))
			fh.write('gamename, filename\n')


class DBUpdate(object):

	_guiDict = {}   # Dict for logging to screen
	_gui = None		# Only retained for displaying message dialog

	def __init__(self):
		Logutil.log("init DBUpdate", util.LOG_LEVEL_INFO)

		#self.scrapeResultsFile = ScrapeResultsLogFile()
		self.missingDescFile = MissingDescLogFile()
		self.missingArtworkFile = MissingArtworkLogFile()
		self.possibleMismatchFile = MismatchLogFile()

		pass

	def updateDB(self, gdb, gui, romCollections, isRescrape):
		self.gdb = gdb
		self._gui = gui

		log.info("Start Update DB")

		log.info("Iterating Rom Collections")
		rccount = 1

		#always do full reimports when in rescrape-mode
		enableFullReimport = isRescrape or __addon__.getSetting(util.SETTING_RCB_ENABLEFULLREIMPORT).upper() == 'TRUE'
		log.info("enableFullReimport: {0}".format(enableFullReimport))

		continueUpdate = True
		#Added variable to allow user to continue on errors
		ignoreErrors = False

		for romCollection in romCollections.values():

			# timestamp1 = time.clock()

			# check if import was canceled
			if not continueUpdate:
				log.info("Game import canceled")
				break

			# prepare Header for ProgressDialog
			progDialogRCHeader = util.localize(32122) + " (%i / %i): %s" % (rccount, len(romCollections), romCollection.name)
			rccount += 1

			log.info("current Rom Collection: {0}".format(romCollection.name))

			# Read settings for current Rom Collection
			log.info("ignoreOnScan: {0}".format(romCollection.ignoreOnScan))
			if romCollection.ignoreOnScan:
				log.info("current Rom Collection will be ignored.")
				# self.scrapeResultsFile.write('Rom Collection will be ignored.\n')
				continue

			log.info("update is allowed for current rom collection: {0}".format(romCollection.allowUpdate))
			log.info("max folder depth: {0}".format(romCollection.maxFolderDepth))

			firstScraper = romCollection.scraperSites[0]

			# check if we are in local artwork mode
			if len(romCollection.scraperSites) == 1 and firstScraper.is_localartwork_scraper():
				log.info("Forcing enableFullReimport because we are in local artwork mode")
				enableFullReimport = True

			files = self.getRomFilesByRomCollection(romCollection, enableFullReimport)
			if len(files) == 0:
				log.info(u"No files found for rom collection {0}, skipping".format(romCollection.name))
				continue

			log.info(u"Found {0} game files for rom collection {1}".format(len(files), romCollection.name))

			# itemCount is used for percentage in ProgressDialogGUI
			self._gui.itemCount = len(files) + 1

			successfulFiles = 0
			lastgamename = ''
			lastGameId = None

			for fileidx, filename in enumerate(files):

				try:
					log.info("Scraping for {0}".format(filename))
					gamenameFromFile = romCollection.getGamenameFromFilename(filename)

					# check if we are handling one of the additional disks of a multi rom game
					isMultiRomGame = (gamenameFromFile == lastgamename)
					lastgamename = gamenameFromFile

					if isMultiRomGame:
						# Add this entry as a file under the game ID and move on
						log.info("Detected {0} as a multirom game (previous game was {1}".format(filename, lastgamename))
						if lastGameId is None:
							log.error("Game detected as multi rom game, but lastGameId is None.")
							continue
						fileType = FileType()
						fileType.id, fileType.name, fileType.parent = 0, "rcb_rom", "game"
						self.insertFile(filename, lastGameId, fileType, None, None, None)
						del fileType
						continue

					log.info("Start scraping info for game: {0}".format(gamenameFromFile))

					continueUpdate = self._gui.writeMsg(progDialogRCHeader, util.localize(32123) + ": " + gamenameFromFile, "", fileidx + 1)
					if not continueUpdate:
						log.info("Game import canceled by user")
						break

					# check if this file already exists in DB
					continueUpdate, isUpdate, gameId = self.checkRomfileAlreadyExists(filename,
																					  enableFullReimport,
																					  firstScraper.is_localartwork_scraper())
					if not continueUpdate:
						continue

					results = {}
					foldername = self.getFoldernameFromRomFilename(filename)

					artScrapers = {}
					if not firstScraper.is_localartwork_scraper():
						results, artScrapers = self.useSingleScrapers(romCollection, gamenameFromFile, progDialogRCHeader, fileidx + 1)

					if len(results) == 0:
						#lastgamename = ""
						results = None

					# Variables to process Art Download Info
					self._guiDict.update({'dialogHeaderKey': progDialogRCHeader, 'gameNameKey': gamenameFromFile,
										  'scraperSiteKey': artScrapers, 'fileCountKey': (fileidx + 1)})
					del artScrapers

					# Add 'gui' and 'dialogDict' parameters to function
					lastGameId = self.insertGameFromDesc(results, gamenameFromFile, romCollection, [filename], foldername, isUpdate, gameId, firstScraper.is_localartwork_scraper())
					del results, foldername

					if lastGameId is not None:
						log.info("Successfully added {0}".format(gamenameFromFile))
						successfulFiles += 1

					# Check if all first 10 games have errors - Modified to allow user to continue on errors
					if fileidx > 9 and successfulFiles == 0 and not ignoreErrors:
						options = [util.localize(32124), util.localize(32125), util.localize(32126)]
						answer = xbmcgui.Dialog().select(util.localize(32127), options)
						if answer == 1:
							# Continue and ignore errors
							ignoreErrors = True
						elif answer == 2:
							# Cancel
							xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32128), util.localize(32129))
							continueUpdate = False
							break

				except ScraperExceededAPIQuoteException as ke:
					xbmcgui.Dialog().ok(util.localize(32128), "The API key for a scraper was exceeded")
					# Abort the scraping entirely
					break
				except Exception as exc:
					log.warn(u"An error occurred while adding game {0}: {1}".format(gamenameFromFile, exc))
					self.missingDescFile.add_entry(gamenameFromFile)

					continue

			#timestamp2 = time.clock()
			#diff = (timestamp2 - timestamp1) * 1000
			#print "load %i games in %d ms" % (self.getListSize(), diff)

		self._gui.writeMsg("Done.", "", "", self._gui.itemCount)
		self.exit()
		return True, ''

	def getRomFilesByRomCollection(self, romCollection, enableFullReimport):

		log.info("Rom path: {0}".format(romCollection.romPaths))

		log.info("Reading rom files")
		files = []
		for romPath in romCollection.romPaths:
			log.info("Reading rom files in path: {0}".format(romPath))
			files = self.walkDownPath(files, unicode(romPath), romCollection.maxFolderDepth)

		# only use files that are not already present in database
		if enableFullReimport == False:
			inDBFiles = DataBaseObject(self.gdb, '').getFileAllFilesByRCId(romCollection.id)
			files = [f for f in files if not f in inDBFiles]

		files.sort()
		log.info("Files read: {0}".format(files))

		return files

	def walkDownPath(self, files, romPath, maxFolderDepth):

		log.info("alkDownPath romPath: {0}".format(romPath))

		files = self.walkDown(files, romPath, maxFolderDepth)
		log.info("files after walkDown = {0}".format(files))

		return files

	def walkDown(self, files, romPath, maxFolderDepth):
		log.info("Running walkdown on: {0}".format(romPath))

		dirs, newFiles, dirname, filemask = self.getFilesByWildcardExt(romPath)
		files.extend(newFiles)

		for dir in dirs:
			newRomPath = util.joinPath(dirname, dir, filemask)
			maxFolderDepth = maxFolderDepth - 1
			if(maxFolderDepth > 0):
				self.walkDown(files, newRomPath, maxFolderDepth)

		return files

	def getFoldernameFromRomFilename(self, filename):
		"""
		Get the containing folder from a full path. For example, /Path/To/SNES/SNESGame.smc, return SNES

		If no path is specified (i.e. only a rom filename), then return ''
		"""
		d = os.path.dirname(filename)
		return os.path.basename(d)

	# FIXME TODO This is just a dict find; just do this where required, this function is redundant
	def findFilesByGameDescription(self, key, fileDict):

		log.info("searching for Key: {0}".format(key))

		try:
			filename = fileDict[key]
			log.info("result found: {0}".format(filename))
		except KeyError:
			filename = None

		return filename

	def checkRomfileAlreadyExists(self, filename, enableFullReimport, isLocalArtwork):

		isUpdate = False
		gameId = None
		log.debug("Checking if file already exists in DB: {0}".format(filename))
		romFile = File(self.gdb).getFileByNameAndType(filename, 0)
		if romFile is not None:
			isUpdate = True
			gameId = romFile[3]	 # FIXME TODO Replace with FILE_parentId
			log.info("File '{0}' already exists in database.".format(filename))
			log.info("Always rescan imported games = {0}".format(enableFullReimport))
			log.info("scraper == 'local artwork': {0}".format(isLocalArtwork))
			if enableFullReimport is False and not isLocalArtwork:
				log.info("Won't scrape this game again. Set 'Always rescan imported games' to True to force scraping.")
				return False, isUpdate, gameId
		else:
			log.debug("Couldn't find file in DB")
			if isLocalArtwork:
				log.info("scraper == 'local artwork': {0}".format(isLocalArtwork))
				log.info("Can't use 'local artwork' scraper if game is not already imported. Use another scraper first.")
				return False, isUpdate, gameId

		return True, isUpdate, gameId

	def addNewElements(self, results, newResults):
		""" Add fields from the results to the existing set of results, adding if new, replacing if empty. This allows
		us to add fields from subsequent site scrapes that were missing or not available in previous sites.

		Args:
			results: Existing results dict from previous scrapes
			newResults: Result dict from most recent scrape

		Returns:
			Updated dict of result fields
		"""
		try:
			log.debug("Before merging results: {0} vs {1}".format(results.items(), newResults.items()))
			# Retain any existing key values that aren't an empty list, overwrite all others
			z = dict(newResults.items() + dict((k, v) for k, v in results.iteritems() if len(v) > 0).items())
			log.debug("After merging results: {0}".format(z.items()))
			return z
		except Exception as e:
			# Return original results without doing anything
			log.warn("Error when merging results: {0}".format(e))
			return results

	def useSingleScrapers(self, romCollection, gamenameFromFile, progDialogRCHeader, fileCount):
		"""Scrape site for game metadata

		Args:
			romCollection:
			gamenameFromFile:
			progDialogRCHeader:
			fileCount:

		Returns:
			dict for the game result:
				{'SearchKey': ['Chrono Trigger'],
				 'Publisher': ['Squaresoft'],
				 'Description': ["The millennium. A portal is opened. The chain of time is broken...],
				 'Players': ['1'],
				 'Platform': ['Super Nintendo (SNES)'],
				 'Game': ['Chrono Trigger'],
				 'Filetypeboxfront': ['http://thegamesdb.net/banners/boxart/original/front/1255-1.jpg'],
				 'Filetypeboxback': ['http://thegamesdb.net/banners/boxart/original/back/1255-1.jpg'],
				 'Filetypescreenshot': ['http://thegamesdb.net/banners/screenshots/1255-1.jpg', 'http://thegamesdb.net/banners/screenshots/1255-2.jpg', 'http://thegamesdb.net/banners/screenshots/1255-3.jpg', 'http://thegamesdb.net/banners/screenshots/1255-4.jpg', 'http://thegamesdb.net/banners/screenshots/1255-5.jpg'],
				 'Filetypefanart': ['http://thegamesdb.net/banners/fanart/original/1255-1.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-10.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-11.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-2.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-3.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-4.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-5.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-6.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-7.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-8.jpg', 'http://thegamesdb.net/banners/fanart/original/1255-9.jpg'],
				 'Genre': ['Role-Playing'],
				 'Developer': ['Squaresoft']}
			dict for artwork urls:
				{'Filetypefanart': 'thegamesdb.net', 'Filetypeboxback': 'thegamesdb.net', 'Filetypescreenshot': 'thegamesdb.net', 'Filetypeboxfront': 'thegamesdb.net'}
				Note - this only contains entries for artwork that was found (i.e. is not empty list)
		"""
		artScrapers = {}
		gameresult = {}

		for idx, scraperSite in enumerate(romCollection.scraperSites):

			try:
				newscraper = AbstractScraper().get_scraper_by_name(scraperSite.name)
				results = newscraper.search(gamenameFromFile, romCollection.name)
				log.debug(u"Searching for {0} - found {1} results: {2}".format(gamenameFromFile, len(results), results))
			except ScraperExceededAPIQuoteException as ke:
				# API key is invalid - we need to stop scraping
				log.error("Scraper exceeded API key, stopping scraping")
				raise
			except Exception as e:
				log.error("Error searching for {0} using scraper {1} - {2} {3}".format(gamenameFromFile, scraperSite.name, type(e), e))
				continue

			if results == []:
				log.warn("No search results found for {0} using scraper {1}".format(gamenameFromFile, scraperSite.name))
				continue

			matched = Matcher().getBestResults(results, gamenameFromFile)
			if matched is None:
				log.error("No matches found for {0}, skipping".format(gamenameFromFile))
				continue
			log.debug("After matching: {0}".format(matched))

			try:
				retrievedresult = newscraper.retrieve(matched['id'])
				log.debug(u"Retrieving {0} - found {1}".format(matched['id'], retrievedresult))
			except Exception as e:
				# FIXME TODO Catch exceptions specifically
				log.error("Error retrieving {0} - {1} {2}".format(matched['id'], type(e), e))
				continue

			# Update the gameresult with any new fields
			gameresult = self.addNewElements(gameresult, retrievedresult)

			self._gui.writeMsg(progDialogRCHeader, util.localize(32123) + ": " + gamenameFromFile,
							   scraperSite.name + " - " + util.localize(32131), fileCount)

			# Find Filetypes and Scrapers for Art Download
			# FIXME TODO The following is kept to keep artwork downloading working as it currently is. We already have
			# the URLs and so could handle/download here, rather than deferring
			if len(gameresult) > 0:
				for path in romCollection.mediaPaths:
					thumbKey = 'Filetype' + path.fileType.name
					if len(self.resolveParseResult(gameresult, thumbKey)) > 0:
						if (thumbKey in artScrapers) == 0:
							artScrapers[thumbKey] = scraperSite.name

		log.debug(u"After scraping, result = {0}, artscrapers = {1}".format(gameresult, artScrapers))
		return gameresult, artScrapers

	def insertGameFromDesc(self, gamedescription, gamename, romCollection, filenamelist, foldername, isUpdate, gameId, isLocalArtwork):

		log.info("insertGameFromDesc")

		if gamedescription is not None:
			game = self.resolveParseResult(gamedescription, 'Game')

		#if no game name has been scraped we expect that no results have been found
		if game == '':
			if not isLocalArtwork:
				self.missingDescFile.add_entry(gamename)

				if __addon__.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTDESC).upper() == 'TRUE':
					log.warn("No description found for game '{0}'. Game will not be imported.".format(gamename))
					return None
			game = ''
			gamedescription = {}

		gameId = self.insertData(gamedescription, gamename, romCollection, filenamelist, foldername, isUpdate, gameId, isLocalArtwork)
		return gameId

	def add_genres_to_db(self, genreIds, gameId):
		# If the genre-game link doesn't exist in the DB, create it
		for genreId in genreIds:
			genreGame = GenreGame(self.gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
			if genreGame is None:
				log.debug("Inserting link between game {0} and genre {1}".format(str(gameId), str(genreId)))
				GenreGame(self.gdb).insert((genreId, gameId))
			del genreGame

	def add_romfiles_to_db(self, romFiles, gameId):
		for romFile in romFiles:
			log.debug("Adding romfile to DB: {0}".format(str(romFile)))
			fileType = FileType()
			fileType.id, fileType.name, fileType.parent = 0, "rcb_rom", "game"
			self.insertFile(romFile, gameId, fileType, None, None, None)
			del fileType

	def insertData(self, gamedescription, gamenameFromFile, romCollection, romFiles, foldername, isUpdate, gameId, isLocalArtwork):
		log.info("Insert data")

		publisher = self.resolveParseResult(gamedescription, 'Publisher')
		developer = self.resolveParseResult(gamedescription, 'Developer')
		year = self.resolveParseResult(gamedescription, 'ReleaseYear')

		yearId = self.insertForeignKeyItem(gamedescription, 'ReleaseYear', Year(self.gdb))
		genreIds = self.insertForeignKeyItemList(gamedescription, 'Genre', Genre(self.gdb))
		reviewerId = self.insertForeignKeyItem(gamedescription, 'Reviewer', Reviewer(self.gdb))

		publisherId = -1
		developerId = -1

		# read current properties for local artwork scraper
		if not isLocalArtwork:
			publisherId = self.insertForeignKeyItem(gamedescription, 'Publisher', Publisher(self.gdb))
			developerId = self.insertForeignKeyItem(gamedescription, 'Developer', Developer(self.gdb))
		else:
			gameRow = Game(self.gdb).getObjectById(gameId)
			if gameRow is not None:
				publisherId = gameRow[GAME_publisherId]
				publisherRow = Publisher(self.gdb).getObjectById(gameId)
				if publisherRow is not None:
					publisher = publisherRow[util.ROW_NAME]
				developerId = gameRow[GAME_developerId]
				del gameRow
				developerRow = Developer(self.gdb).getObjectById(gameId)
				if developerRow is not None:
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
		if isFavorite == '':
			isFavorite = '0'
		launchCount = self.resolveParseResult(gamedescription, 'LaunchCount')
		if launchCount == '':
			launchCount = '0'

		if gamedescription is not None:
			gamename = self.resolveParseResult(gamedescription, 'Game')
			if gamename != gamenameFromFile:
				self.possibleMismatchFile.add_entry(gamename, gamenameFromFile)

			if gamename == "":
				gamename = gamenameFromFile
		else:
			gamename = gamenameFromFile

		artWorkFound, artworkfiles, artworkurls = self.getArtworkForGame(romCollection, gamename, gamenameFromFile, gamedescription, foldername, publisher, developer, isLocalArtwork)

		if not artWorkFound and (__addon__.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTARTWORK).upper() == 'TRUE'):
			log.warn("No artwork found for game '{0}'. Game will not be imported.".format(gamenameFromFile))
			self.missingArtworkFile.add_entry(gamename)

			return None

		# Create Nfo file with game properties
		if (__addon__.getSetting(util.SETTING_RCB_CREATENFOFILE).upper() == 'TRUE') and gamedescription is not None:
			try:
				genreList = gamedescription.get('Genre', [])
				writer = NfoWriter()
				writer.createNfoFromDesc(gamename, plot, romCollection.name, publisher, developer, year,
					players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, version, genreList, isFavorite, launchCount, romFiles[0], gamenameFromFile, artworkfiles, artworkurls)
			except Exception as e:
				log.warn(u"Unable to write NFO file for game {0}: {1}".format(gamename, e))

		del publisher, developer, year

		if not isLocalArtwork:
			gameId = self.insertGame(gamename, plot, romCollection.id, publisherId, developerId, reviewerId, yearId,
				players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version, isFavorite, launchCount, isUpdate, gameId, romCollection.allowUpdate,)

			del plot, players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version

			if gameId is None:
				return None

			self.add_genres_to_db(genreIds, gameId)

			self.add_romfiles_to_db(romFiles, gameId)

		for fileType, fileNames in artworkfiles.iteritems():
			for filename in fileNames:
				log.info("Importing artwork file {0} = {1}".format(fileType.type, str(filename)))
				self.insertFile(filename, gameId, fileType, romCollection.id, publisherId, developerId)

		self.gdb.commit()
		return gameId

	def getArtworkForGame(self, romCollection, gamename, gamenameFromFile, gamedescription, foldername, publisher, developer, isLocalArtwork):
		artWorkFound = False
		artworkfiles = {}
		artworkurls = {}
		for path in romCollection.mediaPaths:

			log.info("FileType: {0}".format(path.fileType.name))

			# TODO replace %ROMCOLLECTION%, %PUBLISHER%, ...
			fileName = path.path.replace("%GAME%", gamenameFromFile)

			if not isLocalArtwork:
				continueUpdate, artworkurls = self.getThumbFromOnlineSource(gamedescription, path.fileType.name, fileName, artworkurls)
				if not continueUpdate:
					return False, {}, {}

			log.debug("Additional data path: {0}".format(path.path))
			files = self.resolvePath((path.path,), gamename, gamenameFromFile, foldername, romCollection.name, publisher, developer)
			if len(files) > 0:
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
			if not isUpdate:
				log.info(u"Game does not exist in database. Insert game: {0}".format(gameName))
				Game(self.gdb).insert((gameName, description, None, None, romCollectionId, publisherId, developerId, reviewerId, yearId,
					players, rating, votes, url, region, media, perspective, controller, int(isFavorite), int(launchCount), originalTitle, alternateTitle, translatedBy, version))
				return self.gdb.cursor.lastrowid
			else:
				if allowUpdate:

					#check if we are allowed to update with null values
					allowOverwriteWithNullvalues = __addon__.getSetting(util.SETTING_RCB_ALLOWOVERWRITEWITHNULLVALUES).upper() == 'TRUE'
					log.info("allowOverwriteWithNullvalues: {0}".format(allowOverwriteWithNullvalues))

					log.info(u"Game does exist in database. Update game: {0}".format(gameName))
					Game(self.gdb).update(('name', 'description', 'romCollectionId', 'publisherId', 'developerId', 'reviewerId', 'yearId', 'maxPlayers', 'rating', 'numVotes',
						'url', 'region', 'media', 'perspective', 'controllerType', 'originalTitle', 'alternateTitle', 'translatedBy', 'version', 'isFavorite', 'launchCount'),
						(gameName, description, romCollectionId, publisherId, developerId, reviewerId, yearId, players, rating, votes, url, region, media, perspective, controller,
						originalTitle, alternateTitle, translatedBy, version, int(isFavorite), int(launchCount)),
						gameId, allowOverwriteWithNullvalues)
				else:
					log.info(u"Game does exist in database but update is not allowed for current rom collection. game: {0}".format(gameName))

				return gameId
		except Exception, (exc):
			log.error(u"An error occured while adding game '{0}'. Error: {1}".format(gameName, exc))
			return None

	def insertForeignKeyItem(self, result, itemName, gdbObject):

		item = self.resolveParseResult(result, itemName)

		if item != "" and item is not None:
			itemRow = gdbObject.getOneByName(item)
			if itemRow is None:
				log.info("{0} does not exist in database. Insert: {1}".format(itemName, item.encode('utf-8')))

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
			log.info("Result {0} = {1}".format(itemName, itemList))
		except KeyError:
			log.warn("Error while resolving item: {0}".format(itemName))
			return idList

		for item in itemList:
			itemRow = gdbObject.getOneByName(item)
			if itemRow is None:
				log.info("{0} does not exist in database. Insert: {1}".format(itemName, item.encode('utf-8')))

				gdbObject.insert((item,))
				idList.append(self.gdb.cursor.lastrowid)
			else:
				idList.append(itemRow[0])

		return idList

	def resolvePath(self, paths, gamename, gamenameFromFile, foldername, romCollectionName, publisher, developer):
		resolvedFiles = []

		for path in paths:
			files = []
			log.info("resolve path: {0}".format(path))

			if path.find("%GAME%") > -1:

				pathnameFromFile = path.replace("%GAME%", gamenameFromFile)
				log.info("resolved path from rom file name: {0}".format(pathnameFromFile))
				files = self.getFilesByWildcard(pathnameFromFile)
				if len(files) == 0:
					files = self.getFilesByGameNameIgnoreCase(pathnameFromFile)

				if gamename != gamenameFromFile and len(files) == 0:
					pathnameFromGameName = path.replace("%GAME%", gamename)
					log.info("resolved path from game name: {0}".format(pathnameFromGameName))
					files = self.getFilesByWildcard(pathnameFromGameName)
					if len(files) == 0:
						files = self.getFilesByGameNameIgnoreCase(pathnameFromGameName)

				if gamename != foldername and len(files) == 0:
					pathnameFromFolder = path.replace("%GAME%", foldername)
					log.info("resolved path from rom folder name: {0}".format(pathnameFromFolder))
					files = self.getFilesByWildcard(pathnameFromFolder)
					if len(files) == 0:
						files = self.getFilesByGameNameIgnoreCase(pathnameFromFolder)


			# ODO could be done only once per RomCollection
			if path.find("%ROMCOLLECTION%") > -1 and romCollectionName is not None and len(files) == 0:
				pathnameFromRomCollection = path.replace("%ROMCOLLECTION%", romCollectionName)
				log.info("resolved path from rom collection name: {0}".format(pathnameFromRomCollection))
				files = self.getFilesByWildcard(pathnameFromRomCollection)

			if path.find("%PUBLISHER%") > -1 and publisher is not None and len(files) == 0:
				pathnameFromPublisher = path.replace("%PUBLISHER%", publisher)
				log.info("resolved path from publisher name: {0}".format(pathnameFromPublisher))
				files = self.getFilesByWildcard(pathnameFromPublisher)

			if path.find("%DEVELOPER%") > -1 and developer is not None and len(files) == 0:
				pathnameFromDeveloper = path.replace("%DEVELOPER%", developer)
				log.info("resolved path from developer name: {0}".format(pathnameFromDeveloper))
				files = self.getFilesByWildcard(pathnameFromDeveloper)

			if path.find("%GAME%") == -1 & path.find("%ROMCOLLECTION%") == -1 & path.find("%PUBLISHER%") == -1 & path.find("%DEVELOPER%") == -1:
				pathnameFromStaticFile = path
				log.info("using static defined media file from path: {0}".format(pathnameFromStaticFile))
				files = self.getFilesByWildcard(pathnameFromStaticFile)

			if len(files) == 0:
				log.warn("No files found for game '{0}' at path '{1}'. Make sure that file names are matching.".format(gamename, path))
			for f in files:
				if xbmcvfs.exists(f):
					resolvedFiles.append(f)

		return resolvedFiles

	def getFilesByWildcard(self, pathName):
		dirs, files, dirname, filemask = self.getFilesByWildcardExt(pathName)
		return files

	def getFilesByWildcardExt(self, pathName):

		log.info("Begin getFilesByWildcard. pathName = {0}".format(pathName))
		files = []
		dirs = []

		dirname = os.path.dirname(pathName)
		log.info("dirname: {0}".format(dirname))
		filemask = os.path.basename(pathName)
		# HACK: escape [] for use with fnmatch
		filemask = filemask.replace('[', '[[]')
		filemask = filemask.replace(']', '[]]')
		# This might be stupid but it was late...
		filemask = filemask.replace('[[[]]', '[[]')
		log.info("filemask: {0}".format(filemask))

		dirsLocal, filesLocal = xbmcvfs.listdir(dirname)
		log.info("xbmcvfs dirs: {0}".format(dirs))
		log.info("xbmcvfs files: {0}".format(filesLocal))

		for dir in dirsLocal:
			if type(dir) == str:
				dirs.append(dir.decode('utf-8'))
			else:
				dirs.append(dir)

		for file in filesLocal:
			if fnmatch.fnmatch(file, filemask):
			#allFiles = [f.decode(sys.getfilesystemencoding()).encode('utf-8') for f in glob.glob(newRomPath)]
				if type(file) == str:
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

		# search all Files that start with the first character of game name
		newpath = util.joinPath(dirname, basename[0].upper() + '*')
		filesUpper = glob.glob(newpath)
		newpath = util.joinPath(dirname, basename[0].lower() + '*')
		filesLower = glob.glob(newpath)

		allFiles = filesUpper + filesLower
		for file in allFiles:
			if pathname.lower() == file.lower():
				log.warn("Found path '{0}' by search with ignore case.".format(pathname))
				files.append(file)

		return files

	def resolveParseResult(self, result, itemName):

		resultValue = u''

		try:
			resultValue = result[itemName][0]

			if itemName == 'ReleaseYear' and resultValue is not None:
				if type(resultValue) is time.struct_time:
					resultValue = str(resultValue[0])
				elif len(resultValue) > 4:
					resultValueOrig = resultValue
					resultValue = resultValue[0:4]
					try:
						#year must be numeric
						int(resultValue)
					except:
						resultValue = resultValueOrig[len(resultValueOrig) - 4:]
						try:
							int(resultValue)
						except:
							resultValue = u''

			resultValue = resultValue.strip()
			if type(resultValue) == str:
				resultValue = resultValue.decode('utf-8')

		except Exception, (exc):
			log.warn(u"Error while resolving item: {0}: {1}".format(itemName, exc))

		try:
			log.debug(u"Result {0} = {1}".format(itemName, resultValue))
		except:
			pass

		return resultValue

	def insertFile(self, fileName, gameId, fileType, romCollectionId, publisherId, developerId):
		log.debug("Begin Insert file: {0}".format(fileName))

		parentId = None

		# TODO console and romcollection could be done only once per RomCollection
		#fileTypeRow[3] = parent
		if fileType.parent == 'game':
			parentId = gameId
		elif fileType.parent == 'romcollection':
			parentId = romCollectionId
		elif fileType.parent == 'publisher':
			parentId = publisherId
		elif fileType.parent == 'developer':
			parentId = developerId

		log.info("Inserting file with parent {0} (type {1})".format(parentId, fileType.parent))

		fileRow = File(self.gdb).getFileByNameAndTypeAndParent(fileName, fileType.id, parentId)
		if fileRow is None:
			log.info("File does not exist in database. Insert file: {0}".format(fileName))
			f = File(self.gdb)
			try:
				f.insert((fileName, fileType.id, parentId))
			except Exception, (exc):
				log.warn("Error inserting into database: {0}".format(fileName))
		else:
			log.info("File already exists in database: {0}".format(fileName))

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

	def getThumbFromOnlineSource(self, gamedescription, fileType, fileName, artworkurls):
		log.info("Get thumb from online source")

		try:
			# maybe we got a thumb url from desc parser
			thumbKey = 'Filetype' + fileType
			log.info("using key: {0}".format(thumbKey))
			thumbUrl = self.resolveParseResult(gamedescription, thumbKey)
			if thumbUrl == '':
				return True, artworkurls

			artworkurls[fileType] = thumbUrl

			log.info("Get thumb from url: {0}".format(thumbUrl))

			rootExtFile = os.path.splitext(fileName)
			rootExtUrl = os.path.splitext(thumbUrl)

			files = []
			if len(rootExtUrl) == 2 and len(rootExtFile) != 0:
				fileName = rootExtFile[0] + rootExtUrl[1]
				gameName = rootExtFile[0] + ".*"
				files = self.getFilesByWildcard(gameName)
			del rootExtFile, rootExtUrl

			if len(files) > 0:
				log.info("File already exists. Won't download again.")
				return True, artworkurls

			# Create folder if it doesn't already exist
			dirname = os.path.join(os.path.dirname(fileName), '')  # Add the trailing slash that xbmcvfs.exists expects
			log.debug("Checking for artwork directory {0}".format(dirname))
			if KodiVersions.getKodiVersion() >= KodiVersions.KRYPTON:
				exists = xbmcvfs.exists(dirname)
			else:
				exists = os.path.exists(dirname)
			if not exists:
				log.info("Artwork directory {0} doesn't exist, creating it".format(dirname))
				success = xbmcvfs.mkdirs(dirname)
				if not success:
					log.error("Could not create artwork directory: '{0}'".format(dirname))
					xbmcgui.Dialog().ok(util.localize(32010), util.localize(32011))
					del dirname
					return False, artworkurls

			log.info("File {0} does not exist, starting download".format(fileName))
			# Dialog Status Art Download

			# Update progress dialog to state we are downloading art
			try:
				msg = "{0}: {1}".format(util.localize(32123), self._guiDict["gameNameKey"])
				submsg = "{0} - downloading art".format(self._guiDict["scraperSiteKey"][thumbKey])
				self._gui.writeMsg(self._guiDict["dialogHeaderKey"], msg, submsg, self._guiDict["fileCountKey"])
			except KeyError:
				log.warn("Unable to retrieve key from GUI dict")

			try:
				self.download_thumb(thumbUrl, fileName)

			except Exception, (exc):
				log.error("Could not create file: '{0}'. Error message: '{1}'".format(fileName, exc))
				#xbmcgui.Dialog().ok(util.localize(32012), util.localize(32011))
				return False, artworkurls

			Logutil.log("Download finished.", util.LOG_LEVEL_INFO)

		except Exception, (exc):
			log.warn("Error in getThumbFromOnlineSource: {0}".format(exc))

		return True, artworkurls

	def exit(self):
		log.info("Update finished")
