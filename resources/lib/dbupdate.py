from builtins import str
from builtins import object
import glob
import time
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
import helper
from config import *
from gamedatabase import *
from pyscraper.scraper import AbstractScraper
from pyscraper.web_scraper import WebScraper
from pyscraper.matcher import Matcher
from pyscraper.nfo_scraper import NFO_Scraper

from nfowriter import NfoWriter
from rcbexceptions import *

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

    def add_entry(self, gamename, filename=None, pathtype=None):
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

    def updateDB(self, gdb, gui, romCollections, isRescrape):
        self.gdb = gdb
        self._gui = gui

        log.info("Start Update DB")

        #at start, check if we need to create any artwork directories
        if not helper.createArtworkDirectories(romCollections):
            #32010: Error: Could not create artwork directory.
            return False, util.localize(32010)

        log.info("Iterating Rom Collections")
        rccount = 1

        # always do full reimports when in rescrape-mode
        enableFullReimport = isRescrape or __addon__.getSetting(util.SETTING_RCB_ENABLEFULLREIMPORT).upper() == 'TRUE'
        log.info("enableFullReimport: {0}".format(enableFullReimport))

        continueUpdate = True
        # Added variable to allow user to continue on errors
        ignoreErrors = False

        for romCollection in list(romCollections.values()):

            # timestamp1 = time.clock()

            # check if import was canceled
            if not continueUpdate:
                log.info("Game import canceled")
                break

            # prepare Header for ProgressDialog
            # 32122 = Importing Rom Collection
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
                    if monitor.abortRequested():
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

                    # 32123 = Importing Game
                    msg = "%s: %s" %(util.localize(32123), gamenameFromFile)
                    continueUpdate = self._gui.writeMsg(msg, fileidx + 1)
                    if not continueUpdate:
                        log.info("Game import canceled by user")
                        break

                    # check if this file already exists in DB
                    continueUpdate, isUpdate, gameId = self.checkRomfileAlreadyExists(filename, enableFullReimport)
                    if not continueUpdate:
                        continue

                    foldername = self.getFoldernameFromRomFilename(filename)

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
                    if monitor.abortRequested():
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
                        #32124 = Continue
                        #32125 = Continue and Ignore Errors
                        #32126 = Cancel
                        #32127 = First 10 games could not be imported.
                        options = [util.localize(32124), util.localize(32125), util.localize(32126)]
                        answer = xbmcgui.Dialog().select(util.localize(32127), options)
                        if answer == 1:
                            # Continue and ignore errors
                            ignoreErrors = True
                        elif answer == 2:
                            # Cancel
                            #32128 = Import canceled.
                            #32129 = Please check kodi.log for details.
                            message = "%s[CR]%s" % (util.localize(32128), util.localize(32129))
                            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
                            continueUpdate = False
                            break

                except ScraperExceededAPIQuoteException:
                    #32128 = Import canceled.
                    #32043 = API quota for current scraper exceeded.
                    xbmcgui.Dialog().ok(util.localize(32128), util.localize(32043))
                    # Abort the scraping entirely
                    break
                except Exception as exc:
                    log.warn(u"An error occurred while adding game %s: %s" % (gamenameFromFile, exc))
                    self.missingDescFile.add_entry(gamenameFromFile)

                    continue

        # timestamp2 = time.clock()
        # diff = (timestamp2 - timestamp1) * 1000
        # print "load %i games in %d ms" % (self.getListSize(), diff)

        self._gui.writeMsg("Done.", self._gui.itemCount)
        log.info("Update finished")
        return True, ''

    def getRomFilesByRomCollection(self, romCollection, enableFullReimport):

        log.info("Rom path: %s" % romCollection.romPaths)

        log.info("Reading rom files")
        files = []
        for romPath in romCollection.romPaths:
            log.info("Reading rom files in path: %s" % romPath)
            files = self.walkDownPath(files, str(romPath), romCollection.maxFolderDepth)

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

        for directory in dirs:
            newRomPath = util.joinPath(dirname, directory, filemask)
            maxFolderDepth = maxFolderDepth - 1
            if maxFolderDepth > 0:
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
            log.debug("Before merging results: %s vs %s" % (list(results.items()), list(newResults.items())))
            # Retain any existing key values that aren't an empty list, overwrite all others
            z = dict(list(newResults.items()) + list(dict((k, v) for k, v in list(results.items()) if len(v) > 0).items()))
            log.debug("After merging results: %s" % list(z.items()))
            return z
        except Exception as e:
            # Return original results without doing anything
            log.warn("Error when merging results: %s" % e)
            return results

    def useSingleScrapers(self, romCollection, romFile, gamenameFromFile, progDialogRCHeader, fileCount):
        """Scrape site for game metadata

        Args:
            romCollection:
            romFile:
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

        scraperSite = None

        #search for default scraper if there are more than one
        for site in romCollection.scraperSites:
            if site.default:
                scraperSite = site
                break

        #if no default site was found, just use the first one
        if not scraperSite:
            if len(romCollection.scraperSites) >= 1:
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
                #set path to desc file (only useful for offline scrapers)
                newscraper.path = scraperSite.path

            log.info("Using scraper: %s" % newscraper.name)
            # 32123 = Importing Game
            # 32131 = downloading info
            msg = "%s: %s[CR]%s: %s" %(util.localize(32123), gamenameFromFile, newscraper.name, util.localize(32131))
            self._gui.writeMsg(msg, fileCount)

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

    def insertGameFromDesc(self, gamedescription, gamename_from_file, romCollection, romfiles, foldername, isUpdate, gameId):

        log.info("insertGameFromDesc")

        if gamedescription is not None:
            game = self.resolveParseResult(gamedescription, 'Game')
        else:
            game = ''

        # if no game name has been scraped we expect that no results have been found
        if game == '':
            self.missingDescFile.add_entry(gamename_from_file)

            if __addon__.getSetting(util.SETTING_RCB_IGNOREGAMEWITHOUTDESC).upper() == 'TRUE':
                log.warn("No description found for game '%s'. Game will not be imported." % gamename_from_file)
                return None
            gamedescription = {}

        game_row = self.convert_parseresult_to_gamerow(gamedescription, gamename_from_file)
        game_row[Game.COL_romCollectionId] = romCollection.id
        gamename = game_row[Game.COL_NAME]
        publisher = self.resolveParseResult(gamedescription, 'Publisher')
        developer = self.resolveParseResult(gamedescription, 'Developer')

        artWorkFound, artworkfiles, artworkurls = self.getArtworkForGame(romCollection, gamename, gamename_from_file,
                                                                gamedescription, foldername, publisher, developer)

        #add artwork filenames to game_row
        for filetype, filenames in list(artworkfiles.items()):
            for filename in filenames:
                prop = 'COL_fileType%s' % filetype.id
                index = getattr(Game, prop)
                game_row[index] = filename

        gameId = self.insertGame(game_row, isUpdate, gameId, romCollection.allowUpdate, )

        if gameId is None:
            return None

        genreIds = self.insertForeignKeyItemList(gamedescription, 'Genre', Genre(self.gdb))
        self.add_genres_to_db(genreIds, gameId)

        self.add_romfiles_to_db(romfiles, gameId)

        self.gdb.commit()

        # Create Nfo file with game properties
        try:
            # Read game from db as nfowriter expects GameView db row
            gamerow = GameView(self.gdb).getGameById(gameId)
            writer = NfoWriter()
            writer.createNfoFromDesc(gamerow, romCollection.name, romfiles[0], gamename_from_file, artworkfiles, artworkurls)
        except Exception as e:
            log.warn(u"Unable to write NFO file for game %s: %s" % (gamename, e))

        return gameId


    def convert_parseresult_to_gamerow(self, parseresult, gamename_from_file):

        #init list with Null values
        game_row = [None]*len(Game.FIELDNAMES)

        game_row[Game.COL_yearId] = self.insertForeignKeyItem(parseresult, 'ReleaseYear', Year(self.gdb))
        game_row[Game.COL_publisherId] = self.insertForeignKeyItem(parseresult, 'Publisher', Publisher(self.gdb))
        game_row[Game.COL_developerId] = self.insertForeignKeyItem(parseresult, 'Developer', Developer(self.gdb))

        game_row[Game.COL_region] = self.resolveParseResult(parseresult, 'Region')
        game_row[Game.COL_media] = self.resolveParseResult(parseresult, 'Media')
        game_row[Game.COL_controllerType] = self.resolveParseResult(parseresult, 'Controller')
        game_row[Game.COL_maxPlayers] = self.resolveParseResult(parseresult, 'Players')
        game_row[Game.COL_rating] = self.resolveParseResult(parseresult, 'Rating')
        game_row[Game.COL_numVotes] = self.resolveParseResult(parseresult, 'Votes')
        game_row[Game.COL_numVotes] = self.resolveParseResult(parseresult, 'URL')
        game_row[Game.COL_perspective] = self.resolveParseResult(parseresult, 'Perspective')
        game_row[Game.COL_originalTitle] = self.resolveParseResult(parseresult, 'OriginalTitle')
        game_row[Game.COL_alternateTitle] = self.resolveParseResult(parseresult, 'AlternateTitle')
        game_row[Game.COL_translatedBy] = self.resolveParseResult(parseresult, 'TranslatedBy')
        game_row[Game.COL_version] = self.resolveParseResult(parseresult, 'Version')
        game_row[Game.COL_description] = self.resolveParseResult(parseresult, 'Description')
        isFavorite = self.resolveParseResult(parseresult, 'IsFavorite')
        if isFavorite == '':
            isFavorite = '0'
        game_row[Game.COL_isFavorite] = isFavorite
        launchCount = self.resolveParseResult(parseresult, 'LaunchCount')
        if launchCount == '':
            launchCount = '0'
        game_row[Game.COL_launchCount] = launchCount

        if parseresult is not None:
            gamename = self.resolveParseResult(parseresult, 'Game')
            if gamename != gamename_from_file:
                self.possibleMismatchFile.add_entry(gamename, gamename_from_file)

            if gamename == "":
                gamename = gamename_from_file
        else:
            gamename = gamename_from_file
        game_row[DataBaseObject.COL_NAME] = gamename

        return game_row

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

    """
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

        for fileType, fileNames in artworkfiles.items():
            for filename in fileNames:
                log.info("Importing artwork file %s = %s" % (fileType.type, filename))
                self.insertFile(filename, gameId, fileType, romCollection.id, publisherId, developerId)

        gameId = self.insertGame(gamename, plot, romCollection.id, publisherId, developerId, reviewerId, yearId,
                                 players, rating, votes, url, region, media, perspective, controller, originalTitle,
                                 alternateTitle, translatedBy, version, isFavorite, launchCount, isUpdate, gameId,
                                 romCollection.allowUpdate, )

        del plot, players, rating, votes, url, region, media, perspective, controller, originalTitle, alternateTitle, translatedBy, version

        if gameId is None:
            return None

        self.add_genres_to_db(genreIds, gameId)

        self.add_romfiles_to_db(romFiles, gameId)

        self.gdb.commit()
        return gameId
    """

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
            else:
                self.missingArtworkFile.add_entry(gamename, gamenameFromFile, path.fileType.name)

            artworkfiles[path.fileType] = files

        return artWorkFound, artworkfiles, artworkurls

    # FIXME TODO Can we create a game object and set the vars on it rather than pass in a million values
    def insertGame(self, game_row, isUpdate, gameId, allowUpdate):

        #HACK: delete first element as we do not want to insert or update the id
        del game_row[0]

        # Check if exists and insert/update as appropriate; move this functionality to the Game object
        try:
            if not isUpdate:
                log.info(u"Game does not exist in database. Insert game: %s" % game_row[DataBaseObject.COL_NAME])
                Game(self.gdb).insert(game_row)
                return self.gdb.cursor.lastrowid
            else:
                if allowUpdate:
                    # check if we are allowed to update with null values
                    allowOverwriteWithNullvalues = __addon__.getSetting(
                        util.SETTING_RCB_ALLOWOVERWRITEWITHNULLVALUES).upper() == 'TRUE'
                    log.info("allowOverwriteWithNullvalues: {0}".format(allowOverwriteWithNullvalues))

                    log.info(u"Game does exist in database. Update game: %s" % game_row[DataBaseObject.COL_NAME])
                    #remove id from column list
                    columns = Game.FIELDNAMES[1:]
                    Game(self.gdb).update(columns, game_row, gameId, allowOverwriteWithNullvalues)
                else:
                    log.info(
                        u"Game does exist in database but update is not allowed for current rom collection. game: %s" % game_row[DataBaseObject.COL_NAME])

                return gameId
        except Exception as exc:
            log.error(u"An error occured while adding game '%s'. Error: %s" % (game_row[DataBaseObject.COL_NAME], exc))
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

        for directory in dirsLocal:
            if isinstance(directory, str):
                dirs.append(util.convertToUnicodeString(directory))
            else:
                dirs.append(directory)

        for localfile in filesLocal:
            if fnmatch.fnmatch(localfile, filemask):
                # allFiles = [f.decode(sys.getfilesystemencoding()).encode('utf-8') for f in glob.glob(newRomPath)]
                if isinstance(localfile, str):
                    localfile = util.convertToUnicodeString(localfile)
                localfile = util.joinPath(dirname, localfile)
                # return unicode filenames so relating scraping actions can handle them correctly
                files.append(localfile)

        return dirs, files, dirname, filemask

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
        for f in allFiles:
            if pathname.lower() == f.lower():
                log.warn("Found path '%s' by search with ignore case." % pathname)
                files.append(f)

        return files

    def resolveParseResult(self, result, itemName):

        resultValue = u''

        try:
            resultValue = result[itemName][0]
            if (isinstance(resultValue, str)):
                resultValue = resultValue.strip()
                resultValue = util.convertToUnicodeString(resultValue)
        except Exception as exc:
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
            except Exception:
                log.warn("Error inserting into database: %s" % fileName)
        else:
            log.info("File already exists in database: %s" % fileName)

    def download_thumb(self, thumburl, destfilename):
        log.info("begin download_thumb using requests module: thumburl = %s" % thumburl)

        # Download file to tmp folder
        tmp = util.joinPath(util.getTempDir(), os.path.basename(destfilename))

        log.info("download_thumb: start downloading to temp file: %s" % tmp)
        response = requests.get(thumburl, headers=WebScraper._headers, stream=True)
        log.info("download_thumb: status code = %s" % response.status_code)
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

            log.info("File %s does not exist, starting download" % fileName)
            # Dialog Status Art Download

            # Update progress dialog to state we are downloading art
            try:
                #32123 = Importing Game
                #32210 = downloading artwork
                msg = "%s: %s[CR]%s: %s" % (util.localize(32123), self._guiDict["gameNameKey"],
                                            self._guiDict["scraperSiteKey"][thumbKey], util.localize(32210))
                self._gui.writeMsg(msg, self._guiDict["fileCountKey"])
            except KeyError:
                log.warn("Unable to retrieve key from GUI dict")

            try:
                self.download_thumb(thumbUrl, fileName)

            except Exception as exc:
                log.error("Could not create file: '%s'. Error message: '%s'" % (fileName, exc))
                # xbmcgui.Dialog().ok(util.localize(32012), util.localize(32011))
                return False, artworkurls

            Logutil.log("Download finished.", util.LOG_LEVEL_INFO)

        except Exception as exc:
            log.warn("Error in getThumbFromOnlineSource: %s" % exc)

        return True, artworkurls
