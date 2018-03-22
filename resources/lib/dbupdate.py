import getpass, glob
import time
import urllib2
import io
import requests

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
from pyscraper.scraper import AbstractScraper
from pyscraper.matcher import Matcher
from pyscraper.nfo_scraper import NFO_Scraper

from nfowriter import NfoWriter
from rcbexceptions import *

# HACK: zlib isn't shipped with some linux distributions
try:
    import zlib
except:
    Logutil.log(
        "Error while loading zlib library. You won't be able to import games using crc values (only used when importing offline game descriptions).",
        util.LOG_LEVEL_WARNING)


monitor = xbmc.Monitor()


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
            fh.write('\n~~~~~~~~~~~~~~~~~~~~~~~~\n%s\n~~~~~~~~~~~~~~~~~~~~~~~~\n' % rcname)

    def add_entry(self, gamename, filename=None):
        if filename is None:
            msg = u'%s\n' % gamename
        else:
            msg = u'%s, %s\n' % (gamename, filename)
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
            msg = u'--> No artwork found for game "%s". Game will not be imported.\n' % gamename
        else:
            msg = u'%s (filename: %s) (%s)\n' % (gamename, filename, pathtype)

        with io.open(self.fname, mode='a', encoding='utf-8') as fh:
            fh.write(msg)


class MismatchLogFile(UpdateLogFile):
    _fname = u'scrapeResult_possibleMismatches.txt'
    _header = u'Possible Mismatches\n===================\n\n'

    def add_header(self, rcname):
        with open(self.fname, mode='w') as fh:
            fh.write('~~~~~~~~~~~~~~~~~~~~~~~~\n%s\n~~~~~~~~~~~~~~~~~~~~~~~~\n' % rcname)
            fh.write('gamename, filename\n')


class DBUpdate(object):
    _guiDict = {}  # Dict for logging to screen
    _gui = None  # Only retained for displaying message dialog

    def __init__(self):
        Logutil.log("init DBUpdate", util.LOG_LEVEL_INFO)

        # self.scrapeResultsFile = ScrapeResultsLogFile()
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

        # always do full reimports when in rescrape-mode
        enableFullReimport = isRescrape or __addon__.getSetting(util.SETTING_RCB_ENABLEFULLREIMPORT).upper() == 'TRUE'
        log.info("enableFullReimport: {0}".format(enableFullReimport))

        continueUpdate = True
        # Added variable to allow user to continue on errors
        ignoreErrors = False

        for romCollection in romCollections.values():

            # timestamp1 = time.clock()

            # check if import was canceled
            if not continueUpdate:
                log.info("Game import canceled")
                break

            # prepare Header for ProgressDialog
            progDialogRCHeader = util.localize(32122) + " (%i / %i): %s" % (
            rccount, len(romCollections), romCollection.name)
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
                    #Give kodi a chance to interrupt the process
                    #HACK: we should use monitor.abortRequested() or monitor.waitForAbort()
                    #but for some reason only xbmc.abortRequested returns True
                    if monitor.abortRequested() or xbmc.abortRequested:
                        log.info("Kodi requests abort. Cancel Update.")
                        break

                    log.info("Scraping for %s" % filename)
                    gamenameFromFile = romCollection.getGamenameFromFilename(filename)

                    # check if we are handling one of the additional disks of a multi rom game
                    isMultiRomGame = (gamenameFromFile == lastgamename)
                    lastgamename = gamenameFromFile

                    if isMultiRomGame:
                        # Add this entry as a file under the game ID and move on
                        log.info("Detected %s as a multirom game (previous game was %s)" % (filename, lastgamename))
                        if lastGameId is None:
                            log.error("Game detected as multi rom game, but lastGameId is None.")
                            continue
                        fileType = FileType()
                        fileType.id, fileType.name, fileType.parent = 0, "rcb_rom", "game"
                        self.insertFile(filename, lastGameId, fileType, None, None, None)
                        self.gdb.commit()
                        del fileType
                        continue

                    log.info("Start scraping info for game: %s" % gamenameFromFile)

                    continueUpdate = self._gui.writeMsg(progDialogRCHeader,
                                                        util.localize(32123) + ": " + gamenameFromFile, "", fileidx + 1)
                    if not continueUpdate:
                        log.info("Game import canceled by user")
                        break

                    # check if this file already exists in DB
                    continueUpdate, isUpdate, gameId = self.checkRomfileAlreadyExists(filename, enableFullReimport)
                    if not continueUpdate:
                        continue

                    results = {}
                    foldername = self.getFoldernameFromRomFilename(filename)

                    artScrapers = {}
                    results, artScrapers = self.useSingleScrapers(romCollection, filename, gamenameFromFile,
                                                                      progDialogRCHeader, fileidx + 1)

                    if len(results) == 0:
                        # lastgamename = ""
                        results = None

                    # Variables to process Art Download Info
                    self._guiDict.update({'dialogHeaderKey': progDialogRCHeader, 'gameNameKey': gamenameFromFile,
                                          'scraperSiteKey': artScrapers, 'fileCountKey': (fileidx + 1)})
                    del artScrapers

                    #Give kodi a chance to interrupt the process
                    #HACK: we should use monitor.abortRequested() or monitor.waitForAbort()
                    #but for some reason only xbmc.abortRequested returns True
                    if monitor.abortRequested() or xbmc.abortRequested:
                        log.info("Kodi requests abort. Cancel Update.")
                        break

                    # Add 'gui' and 'dialogDict' parameters to function
                    lastGameId = self.insertGameFromDesc(results, gamenameFromFile, romCollection, [filename],
                                                         foldername, isUpdate, gameId)
                    del results, foldername

                    if lastGameId is not None:
                        log.info("Successfully added %s" % gamenameFromFile)
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
                    log.warn(u"An error occurred while adding game %s: %s" % (gamenameFromFile, exc))
                    self.missingDescFile.add_entry(gamenameFromFile)

                    continue

        # timestamp2 = time.clock()
        # diff = (timestamp2 - timestamp1) * 1000
        # print "load %i games in %d ms" % (self.getListSize(), diff)

        self._gui.writeMsg("Done.", "", "", self._gui.itemCount)
        log.info("Update finished")
        return True, ''

    def getRomFilesByRomCollection(self, romCollection, enableFullReimport):

        log.info("Rom path: %s" % romCollection.romPaths)

        log.info("Reading rom files")
        files = []
        for romPath in romCollection.romPaths:
            log.info("Reading rom files in path: %s" % romPath)
            files = self.walkDownPath(files, unicode(romPath), romCollection.maxFolderDepth)

        # only use files that are not already present in database
        if enableFullReimport == False:
            inDBFiles = DataBaseObject(self.gdb, '').getFileAllFilesByRCId(romCollection.id)
            files = [f for f in files if not f in inDBFiles]

        files.sort()
        log.info("Files read: %s" % files)

        return files

    def walkDownPath(self, files, romPath, maxFolderDepth):

        log.info("alkDownPath romPath: %s" % romPath)

        files = self.walkDown(files, romPath, maxFolderDepth)
        log.info("files after walkDown = %s" % files)

        return files

    def walkDown(self, files, romPath, maxFolderDepth):
        log.info("Running walkdown on: %s" % romPath)

        dirs, newFiles, dirname, filemask = self.getFilesByWildcardExt(romPath)
        files.extend(newFiles)

        for dir in dirs:
            newRomPath = util.joinPath(dirname, dir, filemask)
            maxFolderDepth = maxFolderDepth - 1
            if (maxFolderDepth > 0):
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

        log.info("searching for Key: %s" % key)

        try:
            filename = fileDict[key]
            log.info("result found: %s" % filename)
        except KeyError:
            filename = None

        return filename

    def checkRomfileAlreadyExists(self, filename, enableFullReimport):

        isUpdate = False
        gameId = None
        log.debug("Checking if file already exists in DB: %s" % filename)
        romFile = File(self.gdb).getFileByNameAndType(filename, 0)
        if romFile is not None:
            isUpdate = True
            gameId = romFile[3]  # FIXME TODO Replace with FILE_parentId
            log.info("File '%s' already exists in database." % filename)
            log.info("Always rescan imported games = {0}".format(enableFullReimport))
            if enableFullReimport is False:
                log.info("Won't scrape this game again. Set 'Always rescan imported games' to True to force scraping.")
                return False, isUpdate, gameId
        else:
            log.debug("Couldn't find file in DB")

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
            log.debug("Before merging results: %s vs %s" % (results.items(), newResults.items()))
            # Retain any existing key values that aren't an empty list, overwrite all others
            z = dict(newResults.items() + dict((k, v) for k, v in results.iteritems() if len(v) > 0).items())
            log.debug("After merging results: %s" % z.items())
            return z
        except Exception as e:
            # Return original results without doing anything
            log.warn("Error when merging results: %s" % e)
            return results

    def useSingleScrapers(self, romCollection, romFile, gamenameFromFile, progDialogRCHeader, fileCount):
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
        gameresult = {}
        artScrapers = {}

        scraperSite = romCollection.scraperSites[0]

        try:
            #first check if a local nfo file is available
            nfoscraper = NFO_Scraper()
            nfofile = nfoscraper.get_nfo_path(gamenameFromFile, romCollection.name, romFile)
            if xbmcvfs.exists(nfofile) and __addon__.getSetting(util.SETTING_RCB_PREFERLOCALNFO).upper() == 'TRUE':
                log.info("Found local nfo file. Using this to scrape info.")
                newscraper = nfoscraper
            else:
                newscraper = AbstractScraper().get_scraper_by_name(scraperSite.name)

            results = newscraper.search(gamenameFromFile, romCollection.name)
            log.debug(u"Searching for %s - found %s results: %s" % (gamenameFromFile, len(results), results))
        except ScraperExceededAPIQuoteException as ke:
            # API key is invalid - we need to stop scraping
            log.error("Scraper exceeded API key, stopping scraping")
            raise
        except Exception as e:
            log.error("Error searching for %s using scraper %s - %s %s" % (
            gamenameFromFile, scraperSite.name, type(e), e))
            return gameresult, artScrapers

        if results == []:
            log.warn("No search results found for %s using scraper %s" % (gamenameFromFile, scraperSite.name))
            return gameresult, artScrapers

        matched = Matcher().getBestResults(results, gamenameFromFile)
        if matched is None:
            log.error("No matches found for %s, skipping" % gamenameFromFile)
            return gameresult, artScrapers
        log.debug("After matching: %s" % matched)

        try:
            retrievedresult = newscraper.retrieve(matched['id'], romCollection.name)
            log.debug(u"Retrieving %s - found %s" % (matched['id'], retrievedresult))
        except Exception as e:
            # FIXME TODO Catch exceptions specifically
            log.error("Error retrieving %s - %s %s" % (matched['id'], type(e), e))
            return gameresult, artScrapers

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

        log.debug(u"After scraping, result = %s, artscrapers = %s" % (gameresult, artScrapers))
        return gameresult, artScrapers

    def insertGameFromDesc(self, gamedescription, gamename, romCollection, filenamelist, foldername, isUpdate, gameId):

        log.info("insertGameFromDesc")

        if gamedescription is not None:
            game = self.resolveParseResult(gamedescription, 'Game')
        else:
            game = ''

        # if no game name has been scraped we expect that no results have been found
        if game == '':
            self.missingDescFile.add_entry(gamename)

            if __addon__.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTDESC).upper() == 'TRUE':
                log.warn("No description found for game '%s'. Game will not be imported." % gamename)
                return None
            gamedescription = {}

        gameId = self.insertData(gamedescription, gamename, romCollection, filenamelist, foldername, isUpdate, gameId)
        return gameId

    def add_genres_to_db(self, genreIds, gameId):
        # If the genre-game link doesn't exist in the DB, create it
        for genreId in genreIds:
            genreGame = GenreGame(self.gdb).getGenreGameByGenreIdAndGameId(genreId, gameId)
            if genreGame is None:
                log.debug("Inserting link between game %s and genre %s" % (str(gameId), str(genreId)))
                GenreGame(self.gdb).insert((genreId, gameId))
            del genreGame

    def add_romfiles_to_db(self, romFiles, gameId):
        for romFile in romFiles:
            log.debug("Adding romfile to DB: %s" % romFile)
            fileType = FileType()
            fileType.id, fileType.name, fileType.parent = 0, "rcb_rom", "game"
            self.insertFile(romFile, gameId, fileType, None, None, None)
            del fileType

    def insertData(self, gamedescription, gamenameFromFile, romCollection, romFiles, foldername, isUpdate, gameId):
        log.info("Insert data")

        publisher = self.resolveParseResult(gamedescription, 'Publisher')
        developer = self.resolveParseResult(gamedescription, 'Developer')
        year = self.resolveParseResult(gamedescription, 'ReleaseYear')

        yearId = self.insertForeignKeyItem(gamedescription, 'ReleaseYear', Year(self.gdb))
        genreIds = self.insertForeignKeyItemList(gamedescription, 'Genre', Genre(self.gdb))
        reviewerId = self.insertForeignKeyItem(gamedescription, 'Reviewer', Reviewer(self.gdb))
        publisherId = self.insertForeignKeyItem(gamedescription, 'Publisher', Publisher(self.gdb))
        developerId = self.insertForeignKeyItem(gamedescription, 'Developer', Developer(self.gdb))

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

        artWorkFound, artworkfiles, artworkurls = self.getArtworkForGame(romCollection, gamename, gamenameFromFile,
                                                                         gamedescription, foldername, publisher,
                                                                         developer)

        # Create Nfo file with game properties
        try:
            genreList = gamedescription.get('Genre', [])
            writer = NfoWriter()
            writer.createNfoFromDesc(gamename, plot, romCollection.name, publisher, developer, year,
                                     players, rating, votes, url, region, media, perspective, controller,
                                     originalTitle, alternateTitle, version, genreList, isFavorite, launchCount,
                                     romFiles[0], gamenameFromFile, artworkfiles, artworkurls)
        except Exception as e:
            log.warn(u"Unable to write NFO file for game %s: %s" % (gamename, e))

        del publisher, developer, year

        gameId = self.insertGame(gamename, plot, romCollection.id, publisherId, developerId, reviewerId, yearId,
                                 players, rating, votes, url, region, media, perspective, controller, originalTitle,
                                 alternateTitle, translatedBy, version, isFavorite, launchCount, isUpdate, gameId,
                                 romCollection.allowUpdate, )

        del plot, players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version

        if gameId is None:
            return None

        self.add_genres_to_db(genreIds, gameId)

        self.add_romfiles_to_db(romFiles, gameId)

        for fileType, fileNames in artworkfiles.iteritems():
            for filename in fileNames:
                log.info("Importing artwork file %s = %s" % (fileType.type, filename))
                self.insertFile(filename, gameId, fileType, romCollection.id, publisherId, developerId)

        self.gdb.commit()
        return gameId

    def getArtworkForGame(self, romCollection, gamename, gamenameFromFile, gamedescription, foldername, publisher,
                          developer):
        artWorkFound = False
        artworkfiles = {}
        artworkurls = {}
        for path in romCollection.mediaPaths:

            log.info("FileType: {0}".format(path.fileType.name))

            # TODO replace %ROMCOLLECTION%, %PUBLISHER%, ...
            fileName = path.path.replace("%GAME%", gamenameFromFile)

            continueUpdate, artworkurls = self.getThumbFromOnlineSource(gamedescription, path.fileType.name,
                                                                        fileName, artworkurls)
            if not continueUpdate:
                return False, {}, {}

            log.debug("Additional data path: %s" % path.path)
            files = self.resolvePath((path.path,), gamename, gamenameFromFile, foldername, romCollection.name,
                                     publisher, developer)
            if len(files) > 0:
                artWorkFound = True

                # HACK: disable static image check as a preparation for new default image handling (this code has problems with [] in rom names)
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
                   players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle,
                   translatedBy, version, isFavorite, launchCount, isUpdate, gameId, allowUpdate):
        # Check if exists and insert/update as appropriate; move this functionality to the Game object
        try:
            if not isUpdate:
                log.info(u"Game does not exist in database. Insert game: %s" % gameName)
                Game(self.gdb).insert(
                    (gameName, description, None, None, romCollectionId, publisherId, developerId, reviewerId, yearId,
                     players, rating, votes, url, region, media, perspective, controller, int(isFavorite),
                     int(launchCount), originalTitle, alternateTitle, translatedBy, version))
                return self.gdb.cursor.lastrowid
            else:
                if allowUpdate:

                    # check if we are allowed to update with null values
                    allowOverwriteWithNullvalues = __addon__.getSetting(
                        util.SETTING_RCB_ALLOWOVERWRITEWITHNULLVALUES).upper() == 'TRUE'
                    log.info("allowOverwriteWithNullvalues: {0}".format(allowOverwriteWithNullvalues))

                    log.info(u"Game does exist in database. Update game: %s" % gameName)
                    Game(self.gdb).update(('name', 'description', 'romCollectionId', 'publisherId', 'developerId',
                                           'reviewerId', 'yearId', 'maxPlayers', 'rating', 'numVotes',
                                           'url', 'region', 'media', 'perspective', 'controllerType', 'originalTitle',
                                           'alternateTitle', 'translatedBy', 'version', 'isFavorite', 'launchCount'),
                                          (gameName, description, romCollectionId, publisherId, developerId, reviewerId,
                                           yearId, players, rating, votes, url, region, media, perspective, controller,
                                           originalTitle, alternateTitle, translatedBy, version, int(isFavorite),
                                           int(launchCount)),
                                          gameId, allowOverwriteWithNullvalues)
                else:
                    log.info(
                        u"Game does exist in database but update is not allowed for current rom collection. game: %s" % gameName)

                return gameId
        except Exception, (exc):
            log.error(u"An error occured while adding game '%s'. Error: %s" % (gameName, exc))
            return None

    def insertForeignKeyItem(self, result, itemName, gdbObject):

        item = self.resolveParseResult(result, itemName)

        if item != "" and item is not None:
            itemRow = gdbObject.getOneByName(item)
            if itemRow is None:
                log.info("%s does not exist in database. Insert: %s" % (itemName, item.encode('utf-8')))

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
            log.info("Result %s = %s" % (itemName, itemList))
        except KeyError:
            log.warn("Error while resolving item: %s" % itemName)
            return idList

        for item in itemList:
            itemRow = gdbObject.getOneByName(item)
            if itemRow is None:
                log.info("%s does not exist in database. Insert: %s" % (itemName, item.encode('utf-8')))

                gdbObject.insert((item,))
                idList.append(self.gdb.cursor.lastrowid)
            else:
                idList.append(itemRow[0])

        return idList

    def resolvePath(self, paths, gamename, gamenameFromFile, foldername, romCollectionName, publisher, developer):
        resolvedFiles = []

        for path in paths:
            files = []
            log.info("resolve path: %s" % path)

            if path.find("%GAME%") > -1:

                pathnameFromFile = path.replace("%GAME%", gamenameFromFile)
                log.info("resolved path from rom file name: %s" % pathnameFromFile)
                files = self.getFilesByWildcard(pathnameFromFile)
                if len(files) == 0:
                    files = self.getFilesByGameNameIgnoreCase(pathnameFromFile)

                if gamename != gamenameFromFile and len(files) == 0:
                    pathnameFromGameName = path.replace("%GAME%", gamename)
                    log.info("resolved path from game name: %s" % pathnameFromGameName)
                    files = self.getFilesByWildcard(pathnameFromGameName)
                    if len(files) == 0:
                        files = self.getFilesByGameNameIgnoreCase(pathnameFromGameName)

                if gamename != foldername and len(files) == 0:
                    pathnameFromFolder = path.replace("%GAME%", foldername)
                    log.info("resolved path from rom folder name: %s" % pathnameFromFolder)
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
                log.info("resolved path from publisher name: %s" % pathnameFromPublisher)
                files = self.getFilesByWildcard(pathnameFromPublisher)

            if path.find("%DEVELOPER%") > -1 and developer is not None and len(files) == 0:
                pathnameFromDeveloper = path.replace("%DEVELOPER%", developer)
                log.info("resolved path from developer name: %s" % pathnameFromDeveloper)
                files = self.getFilesByWildcard(pathnameFromDeveloper)

            if path.find("%GAME%") == -1 & path.find("%ROMCOLLECTION%") == -1 & path.find(
                    "%PUBLISHER%") == -1 & path.find("%DEVELOPER%") == -1:
                pathnameFromStaticFile = path
                log.info("using static defined media file from path: %s" % pathnameFromStaticFile)
                files = self.getFilesByWildcard(pathnameFromStaticFile)

            if len(files) == 0:
                log.warn("No files found for game '%s' at path '%s'. Make sure that file names are matching." % (
                gamename, path))
            for f in files:
                if xbmcvfs.exists(f):
                    resolvedFiles.append(f)

        return resolvedFiles

    def getFilesByWildcard(self, pathName):
        dirs, files, dirname, filemask = self.getFilesByWildcardExt(pathName)
        return files

    def getFilesByWildcardExt(self, pathName):

        log.info("Begin getFilesByWildcard. pathName = %s" % pathName)
        files = []
        dirs = []

        dirname = os.path.dirname(pathName)
        log.info("dirname: %s" % dirname)
        filemask = os.path.basename(pathName)
        # HACK: escape [] for use with fnmatch
        filemask = filemask.replace('[', '[[]')
        filemask = filemask.replace(']', '[]]')
        # This might be stupid but it was late...
        filemask = filemask.replace('[[[]]', '[[]')
        log.info("filemask: %s" % filemask)

        dirsLocal, filesLocal = xbmcvfs.listdir(dirname)
        log.info("xbmcvfs dirs: %s" % dirs)
        log.info("xbmcvfs files: %s" % filesLocal)

        for dir in dirsLocal:
            if type(dir) == str:
                dirs.append(dir.decode('utf-8'))
            else:
                dirs.append(dir)

        for file in filesLocal:
            if fnmatch.fnmatch(file, filemask):
                # allFiles = [f.decode(sys.getfilesystemencoding()).encode('utf-8') for f in glob.glob(newRomPath)]
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
                log.warn("Found path '%s' by search with ignore case." % pathname)
                files.append(file)

        return files

    def resolveParseResult(self, result, itemName):

        resultValue = u''

        try:
            resultValue = result[itemName][0].strip()

            if type(resultValue) == str:
                resultValue = resultValue.decode('utf-8')

        except Exception, (exc):
            log.warn(u"Error while resolving item: %s: %s" % (itemName, exc))

        try:
            log.debug(u"Result %s = %s" % (itemName, resultValue))
        except:
            pass

        return resultValue

    def insertFile(self, fileName, gameId, fileType, romCollectionId, publisherId, developerId):
        log.debug("Begin Insert file: %s" % fileName)

        parentId = None

        # TODO console and romcollection could be done only once per RomCollection
        # fileTypeRow[3] = parent
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
            log.info("File does not exist in database. Insert file: %s" % fileName)
            f = File(self.gdb)
            try:
                f.insert((fileName, fileType.id, parentId))
            except Exception, (exc):
                log.warn("Error inserting into database: %s" % fileName)
        else:
            log.info("File already exists in database: %s" % fileName)


    def download_thumb(self, thumburl, destfilename):
        log.info("begin download_thumb using requests module: thumburl = %s" % thumburl)

        # Download file to tmp folder
        tmp = util.joinPath(util.getTempDir(), os.path.basename(destfilename))

        log.info("download_thumb: start downloading to temp file: %s" % tmp)
        response = requests.get(thumburl, stream=True)
        log.info("download_thumb: status code = %s" %response.status_code)
        if response.status_code != 200:
            log.info("download_thumb: invalid response status code. Can't download image.")
            return

        with open(tmp, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

        log.info("download_thumb: copy from temp file to final destination: %s" % destfilename)

        # Copy from the tmp folder to the target location
        xbmcvfs.copy(tmp, destfilename)
        xbmcvfs.delete(tmp)
        log.info("end download_thumb")


    def getThumbFromOnlineSource(self, gamedescription, fileType, fileName, artworkurls):
        log.info("Get thumb from online source")

        try:
            # maybe we got a thumb url from desc parser
            thumbKey = 'Filetype' + fileType
            log.info("using key: %s" % thumbKey)
            thumbUrl = self.resolveParseResult(gamedescription, thumbKey)
            if thumbUrl == '':
                return True, artworkurls

            artworkurls[fileType] = thumbUrl

            log.info("Get thumb from url: %s" % thumbUrl)

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
            log.debug("Checking for artwork directory %s" % dirname)
            if KodiVersions.getKodiVersion() >= KodiVersions.KRYPTON:
                exists = xbmcvfs.exists(dirname)
            else:
                exists = os.path.exists(dirname)
            if not exists:
                log.info("Artwork directory %s doesn't exist, creating it" % dirname)
                success = xbmcvfs.mkdirs(dirname)
                log.info("Directory successfully created: %s" %success)
                if not success:
                    #HACK: check if directory was really not created.
                    directoryExists = xbmcvfs.exists(dirname)
                    log.info("Directory exists: %s" %directoryExists)
                    if not directoryExists:
                        log.error("Could not create artwork directory: '%s'" % dirname)
                        xbmcgui.Dialog().ok(util.localize(32010), util.localize(32011))
                        del dirname
                        return False, artworkurls

            log.info("File %s does not exist, starting download" % fileName)
            # Dialog Status Art Download

            # Update progress dialog to state we are downloading art
            try:
                msg = "%s: %s" % (util.localize(32123), self._guiDict["gameNameKey"])
                submsg = "%s - downloading art" % self._guiDict["scraperSiteKey"][thumbKey]
                self._gui.writeMsg(self._guiDict["dialogHeaderKey"], msg, submsg, self._guiDict["fileCountKey"])
            except KeyError:
                log.warn("Unable to retrieve key from GUI dict")

            try:
                self.download_thumb(thumbUrl, fileName)

            except Exception, (exc):
                log.error("Could not create file: '%s'. Error message: '%s'" % (fileName, exc))
                # xbmcgui.Dialog().ok(util.localize(32012), util.localize(32011))
                return False, artworkurls

            Logutil.log("Download finished.", util.LOG_LEVEL_INFO)

        except Exception, (exc):
            log.warn("Error in getThumbFromOnlineSource: %s" % exc)

        return True, artworkurls
