from __future__ import absolute_import
from builtins import str
from xml.etree.ElementTree import *

import helper
from configxmlwriter import *
from emulatorautoconfig.autoconfig import EmulatorAutoconfig
from rcbxmlreaderwriter import RcbXmlReaderWriter
from util import Logutil as log
import xbmc, xbmcgui, xbmcvfs
from pyscraper.web_scraper import WebScraper
from pyscraper.scraper import AbstractScraper

RETRIEVE_INFO_ONLINE_ARTWORK_ONLINE = 0  # Game description and artwork need to be downloaded
RETRIEVE_INFO_LOCAL_ARTWORK_LOCAL = 1  # Game description and artwork already exist locally
RETRIEVE_INFO_ONLINE_ARTWORK_LOCAL = 2  # Game description will be scraped online and artwork already exist locally

GAME_DESCRIPTION_PER_FILE = 0
GAME_DESCRIPTION_SINGLE_FILE = 1  # All game descriptions in a single file, e.g. MAME history.dat
GAME_DESCRIPTION_ONLINE = 2  # Game descriptions to be retrieved from online source


class ConfigXmlWizard(RcbXmlReaderWriter):

    # Called on first run
    def createConfigXml(self, configFile):

        rcId = 1
        #FIXME TODO move console dict to correct place
        consoleList = sorted(WebScraper().consoleDict.keys())

        success, romCollections = self.addRomCollections(rcId, None, consoleList, False)
        if not success:
            log.info("Action canceled. Config.xml will not be written")
            return False, util.localize(32172)

        configWriter = ConfigXmlWriter(True)
        success, message = configWriter.writeRomCollections(romCollections, False)

        #create artwork directories for all rom collections
        helper.createArtworkDirectories(romCollections)

        return success, message

    # Called by context menu
    def addRomCollection(self, configObj):
        Logutil.log("Begin addRomCollection", util.LOG_LEVEL_INFO)

        consoleList = sorted(WebScraper().consoleDict.keys())
        new_id = 1

        rcIds = list(configObj.romCollections.keys())
        rcIds.sort()
        #read existing rom collection ids and names
        for rcId in rcIds:

            #remove already configured consoles from the list
            if configObj.romCollections[rcId].name in consoleList:
                consoleList.remove(configObj.romCollections[rcId].name)
            #find highest id
            if int(rcId) > int(new_id):
                new_id = rcId

        new_id = int(new_id) + 1

        # Add new rom collections
        success, romCollections = self.addRomCollections(new_id, configObj, consoleList, True)
        if not success:
            log.info("Action canceled. Config.xml will not be written")
            return False, util.localize(32172)

        # Update config file
        configWriter = ConfigXmlWriter(False)
        success, message = configWriter.writeRomCollections(romCollections, False)

        #create artwork directories for all rom collections
        helper.createArtworkDirectories(romCollections)

        log.info("End addRomCollection")
        return success, message

    def promptEmulatorParams(self, defaultValue):
        """ Ask the user to enter emulator parameters """
        emuParams = xbmcgui.Dialog().input(util.localize(32179), defaultt=defaultValue, type=xbmcgui.INPUT_ALPHANUM)
        return emuParams

    def promptOtherConsoleName(self):
        """  Ask the user to enter a (other) console name """
        console = xbmcgui.Dialog().input(util.localize(32177), type=xbmcgui.INPUT_ALPHANUM)
        return console

    def promptEmulatorFileMasks(self):
        fileMaskInput = xbmcgui.Dialog().input(util.localize(32181), type=xbmcgui.INPUT_ALPHANUM)
        if fileMaskInput == '':
            return []
        return fileMaskInput.split(',')

    def promptRomPath(self, consolename):
        """ Prompt the user to browse to the rompath """
        dialog = xbmcgui.Dialog()
        # http://kodi.wiki/view/Add-on_unicode_paths
        romPath = util.convertToUnicodeString(dialog.browse(0, util.localize(32180) % consolename, 'files'))
        log.debug(u"rompath selected: {0}".format(romPath))

        return romPath

    def promptArtworkPath(self, console, startingDirectory):
        """ Prompt the user to browse to the artwork path """
        dialog = xbmcgui.Dialog()
        # http://kodi.wiki/view/Add-on_unicode_paths
        artworkPath = util.convertToUnicodeString(dialog.browse(0, util.localize(32193) % console, 'files', '', False, False,
                                    startingDirectory))
        log.debug(u"artworkPath selected: {0}".format(artworkPath))

        return artworkPath

    def addRomCollections(self, rcId, configObj, consoleList, isUpdate):

        romCollections = {}
        dialog = xbmcgui.Dialog()

        # Scraping scenario - game descriptions and artwork retrieved from online or available locally
        scenarioIndex = dialog.select(util.localize(32173),
                                      [util.localize(32174), util.localize(32175), util.localize(32207)])
        log.info("scenarioIndex: " + str(scenarioIndex))
        if scenarioIndex == -1:
            del dialog
            log.info("No scenario selected. Action canceled.")
            return False, romCollections

        autoconfig = EmulatorAutoconfig(util.getEmuAutoConfigPath())

        while True:

            fileTypeList, errorMsg = self.buildMediaTypeList(configObj, isUpdate)
            romCollection = RomCollection()
            if (errorMsg):
                log.warn("Error building Media Type List: {0}" % errorMsg)
                break

            # Console
            platformIndex = dialog.select(util.localize(32176), consoleList)
            log.info("platformIndex: " + str(platformIndex))
            if platformIndex == -1:
                log.info("No Platform selected. Action canceled.")
                break

            console = consoleList[platformIndex]
            if console == 'Other':
                console = self.promptOtherConsoleName()
                if console == '':
                    break

            else:
                consoleList.remove(console)
                log.info("Selected platform: " + console)

            romCollection.name = console
            romCollection.id = rcId
            rcId = rcId + 1

            # Check if we have general RetroPlayer support
            if helper.isRetroPlayerSupported():
                #32198 = Use RetroPlayer to launch games?
                romCollection.useBuiltinEmulator = bool(dialog.yesno(util.SCRIPTNAME, util.localize(32198)))

            # Only ask for emulator and params if we don't use builtin emulator
            if not romCollection.useBuiltinEmulator:

                # Maybe there is autoconfig support
                preconfiguredEmulator = None

                # Emulator
                if romCollection.name in ['Linux', 'Macintosh', 'Windows']:
                    # Check for standalone games
                    romCollection.emulatorCmd = '"%ROM%"'
                    log.info("emuCmd set to '%ROM%' for standalone games.")

                else:
                    emulist = []

                    log.info(u'Running on {0}. Trying to find emulator per autoconfig.'.format(util.current_os))
                    emulators = autoconfig.findEmulators(util.current_os, romCollection.name, True)
                    for emulator in emulators:
                        if emulator.isInstalled:
                            emulist.append(util.localize(32202) % emulator.name)
                        else:
                            emulist.append(emulator.name)

                    # Ask the user which one they want
                    if len(emulist) > 0:
                        try:
                            emuIndex = dialog.select(util.localize(32203), emulist)
                            if emuIndex >= 0:
                                preconfiguredEmulator = emulators[emuIndex]
                        except IndexError:
                            log.info("No Emulator selected.")
                            preconfiguredEmulator = None

                    if preconfiguredEmulator:
                        romCollection.emulatorCmd = preconfiguredEmulator.emuCmd
                    else:
                        consolePath = dialog.browse(1, util.localize(32178) % console, 'files')
                        Logutil.log('consolePath: ' + str(consolePath), util.LOG_LEVEL_INFO)
                        if consolePath == '':
                            log.info("No consolePath selected. Action canceled.")
                            break
                        romCollection.emulatorCmd = consolePath

                # Set emulator parameters
                if romCollection.name in ['Linux', 'Macintosh', 'Windows']:
                    romCollection.emulatorParams = ''
                    log.info("emuParams set to "" for standalone games.")
                else:
                    if preconfiguredEmulator:
                        defaultParams = preconfiguredEmulator.emuParams
                    else:
                        defaultParams = '"%ROM%"'

                    romCollection.emulatorParams = self.promptEmulatorParams(defaultParams)

            # Prompt for rompath
            romPath = self.promptRomPath(console)
            if romPath == '':
                log.info("No romPath selected. Action canceled.")
                break

            # Filemask
            fileMasks = self.promptEmulatorFileMasks()
            if fileMasks == []:
                break

            romCollection.romPaths = []
            for fileMask in fileMasks:
                romCollection.romPaths.append(util.joinPath(romPath, fileMask.strip()))

            # Specific MAME settings
            if romCollection.name == 'MAME':
                romCollection.imagePlacingMain = ImagePlacing()
                romCollection.imagePlacingMain.name = 'gameinfomamecabinet'

                # MAME zip files contain several files but they must be passed to the emu as zip file
                romCollection.doNotExtractZipFiles = True

            if scenarioIndex == RETRIEVE_INFO_ONLINE_ARTWORK_ONLINE:
                # Prompt for artwork path
                artworkPath = self.promptArtworkPath(console, romPath)
                if artworkPath == '':
                    log.info("No artworkPath selected. Action canceled.")
                    break

                romCollection.descFilePerGame = True

                # Media Paths
                romCollection.mediaPaths = []

                if romCollection.name == 'MAME':
                    mediaTypes = ['boxfront', 'action', 'title', 'cabinet', 'marquee', 'clearlogo', 'gameplay']
                else:
                    mediaTypes = ['boxfront', 'boxback', 'cartridge', 'screenshot', 'fanart', 'clearlogo', 'gameplay']
                for t in mediaTypes:
                    romCollection.mediaPaths.append(self.createMediaPath(t, artworkPath, scenarioIndex))
            else:
                romCollection.mediaPaths = []

                # Default to looking in the romPath for the first artwork path
                lastArtworkPath = romPath
                while True:
                    # Prompt the user for which artwork type we are selecting
                    fileTypeIndex = dialog.select(util.localize(32183), fileTypeList)
                    if fileTypeIndex == -1:
                        log.info("No fileTypeIndex selected.")
                        break

                    fileType = fileTypeList[fileTypeIndex]
                    fileTypeList.remove(fileType)

                    # Prompt user for path for existing artwork
                    artworkPath = util.convertToUnicodeString(dialog.browse(0, util.localize(32182) % (console, fileType), 'files', '', False,
                                                False, lastArtworkPath))
                    log.debug(u"artworkPath selected: {0}".format(artworkPath))
                    if artworkPath == '':
                        log.info("No artworkPath selected.")
                        break
                    lastArtworkPath = artworkPath

                    romCollection.mediaPaths.append(self.createMediaPath(fileType, artworkPath, scenarioIndex))

                    # Ask to add another artwork path
                    #32184 = Do you want to add another Artwork Path?
                    if not dialog.yesno(util.SCRIPTNAME, util.localize(32184)):
                        break

                #not used atm as we don't have any offline scrapers with descfile per game
                """
                # Ask user for source of game descriptions (description file per game or for all games)
                descIndex = dialog.select(util.localize(32185), [util.localize(32186), util.localize(32187)])
                log.debug("descIndex: " + str(descIndex))
                if descIndex == -1:
                    log.info("No descIndex selected. Action canceled.")
                    break

                romCollection.descFilePerGame = (descIndex != GAME_DESCRIPTION_SINGLE_FILE)
                """

                if scenarioIndex == RETRIEVE_INFO_LOCAL_ARTWORK_LOCAL:
                    offline_scrapers = AbstractScraper().get_available_offline_scrapers(console)
                    scraperIndex = dialog.select(util.localize(32206), offline_scrapers)
                    if scraperIndex == -1:
                        log.info("No Scraper type selected. Action canceled.")
                        break

                    selectedscraper = offline_scrapers[scraperIndex]
                    log.info("Selected scraper = {0}".format(selectedscraper))

                    #not used atm as we don't have any offline scrapers with descfile per game
                    """
                    if romCollection.descFilePerGame:
                        # Assume the files are in a single directory with the mask %GAME%.txt
                        # Prompt the user for the path
                        pathValue = dialog.browse(0, util.localize(32189) % console, 'files')
                        if pathValue == '':
                            break

                        # Prompt the user for the description file mask
                        filemask = xbmcgui.Dialog().input(util.localize(32190), defaultt='%GAME%.xml', type=xbmcgui.INPUT_ALPHANUM)
                        descPath = util.joinPath(pathValue, filemask.strip())
                    else:
                    """
                    descPath = dialog.browse(1, util.localize(32189) % console, 'files', '', False, False,
                                             lastArtworkPath)

                    log.info("descPath: " + str(descPath))
                    if descPath == '':
                        log.info("No descPath selected. Action canceled.")
                        break

                    # Create scraper
                    site = Site(name=selectedscraper, path=descPath, default=True)
                    romCollection.scraperSites = [site]

            log.debug("Created new rom collection: {0}".format(romCollection))

            romCollections[romCollection.id] = romCollection

            # Ask the user if they want to add another rom collection
            #32192 = Do you want to add another Rom Collection?
            if not dialog.yesno(util.SCRIPTNAME, util.localize(32192)):
                break

        del dialog

        return True, romCollections

    def buildMediaTypeList(self, configObj, isUpdate):
        #build fileTypeList
        fileTypeList = []

        if isUpdate:
            fileTypes = configObj.tree.findall('FileTypes/FileType')
        else:
            #build fileTypeList
            configFile = util.joinPath(util.getAddonInstallPath(), 'resources', 'database', 'config_template.xml')

            if not xbmcvfs.exists(configFile):
                log.error("File config_template.xml does not exist. Place a valid config file here: " + str(configFile))
                return None, util.localize(32040)

            tree = ElementTree().parse(configFile)
            fileTypes = tree.findall('FileTypes/FileType')

        for fileType in fileTypes:
            name = fileType.attrib.get('name')
            if name != None:
                mediaType = fileType.find('type')
                if mediaType != None and mediaType.text == 'video':
                    name = name + ' (video)'
                fileTypeList.append(name)

        return fileTypeList, ''

    def createMediaPath(self, mediatype, path, scenarioIndex):

        if mediatype == 'gameplay (video)':
            mediatype = 'gameplay'

        if mediatype in ['romcollection', 'developer', 'publisher']:
            fileMask = '%{0}%.*'.format(mediatype.upper())
        else:
            fileMask = '%GAME%.*'

        log.debug("media path type is {0}, filemask is {1}".format(mediatype, fileMask))

        fileType = FileType()
        fileType.name = mediatype

        mediaPath = MediaPath()
        mediaPath.fileType = fileType
        if scenarioIndex == RETRIEVE_INFO_ONLINE_ARTWORK_ONLINE:
            mediaPath.path = util.joinPath(path, mediatype, fileMask)
        else:
            mediaPath.path = util.joinPath(path, fileMask)

        return mediaPath
