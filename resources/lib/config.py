from builtins import next
from builtins import str
from builtins import object
import os, sys, re
import util
import xbmcvfs
from util import *
from rcbxmlreaderwriter import RcbXmlReaderWriter
from xml.etree.ElementTree import *
from util import Logutil as log

#friendly name : db column, missing filter statement
gameproperties = {'Title': ['name', "name = ''"],
                  'Description': ['description', "description = ''"],
                  'Genre': ['genre', "Id NOT IN (SELECT GameId From GenreGame)"],
                  'Developer': ['developerId', "developerId is NULL"],
                  'Publisher': ['publisherId', "publisherId is NULL"],
                  'Reviewer': ['reviewerId', "reviewerId is NULL"],
                  'Release Year': ['yearId', "yearId is NULL"],
                  'Rating': ['rating', "rating = ''"],
                  'Votes': ['numVotes', "numVotes is NULL"],
                  'Region': ['region', "region = ''"],
                  'Media': ['media', "media = ''"],
                  'Max. Players': ['maxPlayers', "maxPlayers = ''"],
                  'Controller': ['controllerType', "controllerType = ''"],
                  'Perspective': ['perspective', "perspective = ''"],
                  'Original Title': ['originalTitle', "originalTitle = ''"],
                  'Alternate Title': ['alternateTitle', "alternateTitle = ''"],
                  'Translated By': ['translatedBy', "translatedBy = ''"],
                  'Version': ['version', "version = ''"],
                  'Url': ['url', "url = ''"]
                  }

imagePlacingDict = {'gameinfobig': 'one big',
                    'gameinfobigVideo': 'one big or video',
                    'gameinfosmall': 'four small',
                    'gameinfosmallVideo': 'three small + video',
                    'gameinfomamemarquee': 'MAME: marquee in list',
                    'gameinfomamecabinet': 'MAME: cabinet in list'}


class FileType(object):
    """
    This config object is defined in config_template.xml in element FileTypes.

    name: In the case of MAME, this will be either: boxfront, cabinet, marquee, action, title.
          For all other emulators: boxfront, boxback, cartridge, screenshot, fanart.
    id: Unique identifier for the FileType, defined in config_template.xml, and used in the File table in the database.
    type: The filetype, either image or video.
    parent: The class that this file pertains to. Current supported values: game, romcollection, developer, publisher.
    """

    def __init__(self, **kwargs):
        self.name = ''
        self.id = -1
        self.type = ''
        self.parent = ''

        """ Set any variables explicitly passed """
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __repr__(self):
        return "<FileType: %s>" % self.__dict__


class ImagePlacing(object):
    """This class controls how images should be displayed, based on whether it is a 'gameinfobig' or 'gameinfosmall'
    (or other options defined in the imagePlacingDict).

    For each category, there will be one or more entries defined in the config.xml; the first is the one
    selected, with subsequent entries others as fallback if the collection hasn't set up a corresponding path.

    Each class attribute is a list of FileType
    """

    def __init__(self):
        # name of the image placing - this is a key in the imagePlacingDict
        self.name = ''

        # List of FileType to be displayed as an icon in the game list, particularly the Info or Thumbs view
        self.fileTypesForGameList = None
        # List of FileType to be displayed as a thumb in the game list when a game is selected
        self.fileTypesForGameListSelected = None

        self.fileTypesForMainView1 = None
        self.fileTypesForMainView2 = None
        self.fileTypesForMainView3 = None

        # Image to be displayed as background when a game is selected
        self.fileTypesForMainViewBackground = None

        # Used for gameinfobig - List of FileType to be displayed as the big image when a game is selected
        self.fileTypesForMainViewGameInfoBig = None

        # Used for gameinfosmall - Lists of FileType to be displayed as the 4 small images when a game is selected
        self.fileTypesForMainViewGameInfoUpperLeft = None
        self.fileTypesForMainViewGameInfoUpperRight = None
        self.fileTypesForMainViewGameInfoLowerLeft = None
        self.fileTypesForMainViewGameInfoLowerRight = None

        # Used for MAME marquee and cabinet view when a game is selected
        self.fileTypesForMainViewGameInfoUpper = None
        self.fileTypesForMainViewGameInfoLower = None
        self.fileTypesForMainViewGameInfoLeft = None
        self.fileTypesForMainViewGameInfoRight = None

        self.fileTypesForMainViewVideoWindowBig = None
        self.fileTypesForMainViewVideoWindowSmall = None
        self.fileTypesForMainViewVideoFullscreen = None

    def __repr__(self):
        return "<ImagePlacing: %s>" % self.__dict__

    # The following properties are aligned with the artwork name used in the skins so that we can reference
    # them by name
    @property
    def icon(self):
        return self.fileTypesForGameList

    @property
    def thumb(self):
        return self.fileTypesForGameListSelected

    @property
    def background(self):
        return self.fileTypesForMainViewBackground

    @property
    def gameinfobig(self):
        return self.fileTypesForMainViewGameInfoBig

    @property
    def gameinfoupperleft(self):
        return self.fileTypesForMainViewGameInfoUpperLeft

    @property
    def gameinfoupperright(self):
        return self.fileTypesForMainViewGameInfoUpperRight

    @property
    def gameinfolowerleft(self):
        return self.fileTypesForMainViewGameInfoLowerLeft

    @property
    def gameinfolowerright(self):
        return self.fileTypesForMainViewGameInfoLowerRight

    @property
    def gameinfolower(self):
        return self.fileTypesForMainViewGameInfoLower


class MediaPath(object):
    """
    A RomCollection has multiple MediaPaths, each one representing different artwork
    e.g. boxfront, boxback, etc. The fileType is a FileType object.

    Note MediaPath can also be used for RomCollections, Publishers and Developers.

    path: The filesystem path to the Media
    fileType: The FileType object referenced by the path
    """

    def __init__(self):
        self.path = ''
        self.fileType = None

    def __repr__(self):
        return "<MediaPath: %s>" % self.__dict__


class Site(object):
    """
    A site is a reference to the scraper class used to retrieve game metadata. These are defined in config_template.xml.

    NOTE that this class will be deprecated in the future.

    name: The name of the site
    path: path to offline game description
    """

    def __init__(self, **kwargs):
        self.name = ''
        self.path = ''
        self.default = False

        """ Set any variables explicitly passed """
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __repr__(self):
        return "<Site: %s>" % self.__dict__


class MissingFilter(object):
    def __init__(self):
        self.andGroup = []
        self.orGroup = []

    def __repr__(self):
        return "<MissingFilter: %s>" % self.__dict__


class RomCollection(object):
    """
    useBuiltinEmulator: Use Kodi's libretro core, rather than an external emulator
    gameclient: Select libretro gameclient manually
    emulatorCmd: The OS command to launch the emulator
    preCmd: The OS command to execute before the emulatorCmd
    postCmd: The OS command to execute after the emulatorCmd
    emulatorParams: List of command-line parameters appended to the emulatorCmd
    romPaths: List of path + masks containing the roms for this collection, including wildcard match, e.g.
        /path/to/rom/files/*.zip, /path/to/rom/files/*.smc. Note we can only have 1 path but multiple wildcard masks

    scraperSites: List of Site objects applicable to this collection
    imagePlacingMain: ImagePlacing (Image configuration) used on the main window
    imagePlacingInfo: ImagePlacing (Image configuration) used on the game info window
    ignoreOnScan: Whether to skip this rom collection when scanning
    allowUpdate: Allows overwriting an existing rom in the collection with details from a more recent scan
    useEmuSolo: Whether to shutdown/restart Kodi while running the external emulator using the scripts in
        scriptfiles/
    usePopen: Use Python subprocess popen
    maxFolderDepth: How many directories to recurse from the romPath looking for matching roms
    useFoldernameAsGamename:
    doNotExtractZipFiles: If the rom is a zip file, extract it to a temporary local directory. Used in
        cases of unsupported zip files (usually .7z)
    makeLocalCopy: Whether to copy the rom to a temporary local directory and use that in the launch. Used
        primarily to workaround SMB issues
    diskPrefix: String used to assist in identifying whether a romset has multiple files (representing a
        multi-disk game).
    """

    def __init__(self):
        self.id = -1
        self.name = ''

        self.useBuiltinEmulator = False
        self.gameclient = ''
        self.emulatorCmd = ''
        self.preCmd = ''
        self.postCmd = ''
        self.emulatorParams = ''
        self.romPaths = []
        self.saveStatePath = ''
        self.saveStateParams = ''
        self.mediaPaths = []
        self.scraperSites = []
        self.imagePlacingMain = None
        self.imagePlacingInfo = None
        self.autoplayVideoMain = True
        self.autoplayVideoInfo = True
        self.ignoreOnScan = False
        self.allowUpdate = True
        self.useEmuSolo = False
        self.usePopen = False
        self.maxFolderDepth = 99
        self.useFoldernameAsGamename = False
        self.doNotExtractZipFiles = False
        self.makeLocalCopy = False
        self.diskPrefix = '_Disk.*'

    @property
    def pathRoms(self):
        """
        Returns:
            A list of paths containing romfiles supported by this emulator, e.g. [/path/to/roms1, /path/to/roms2]
        """
        paths = []
        for rompath in self.romPaths:
            # Skip if the path has already been added
            if rompath in paths:
                continue
            paths.append(os.path.dirname(rompath))
        return paths

    @property
    def maskRomPaths(self):
        """
        Returns:
            A list of suffixes supported by this emulator, e.g. [*.smc, *.zip]
        """
        exts = []
        for rompath in self.romPaths:
            exts.append(os.path.basename(rompath))
        return exts

    @property
    def pathSaveState(self):
        saveStatePath = ''

        try:
            saveStatePath = os.path.split(self.saveStatePath)[0]
        except IndexError:
            pass

        return saveStatePath

    @property
    def maskSaveState(self):
        saveStateMask = ''

        try:
            saveStateMask = os.path.split(self.saveStatePath)[1]
        except IndexError:
            pass

        return saveStateMask

    @property
    def imagePlacingNameGameList(self):
        return self.imagePlacingMain.name

    @property
    def imagePlacingNameGameInfo(self):
        return self.imagePlacingInfo.name

    def __repr__(self):
        return "<RomCollection: %s>" % self.__dict__

    def getMediaPathByTypeName(self, name):
        """ Returns the mediaPath object matching where the FileType's name matches e.g. type = boxfront

        If not found (i.e. the rom collection has not set a path for this type), will return an empty string
        """
        for path in self.mediaPaths:
            if path.fileType.name == name:
                return path.path
        return ''

    def getMediaPathByTypeId(self, typeid):
        """ Returns the mediaPath object matching where the FileType's name matches e.g. type = boxfront

        If not found (i.e. the rom collection has not set a path for this type), will return an empty string
        """
        for path in self.mediaPaths:
            if path.fileType.id == typeid:
                return path.path
        return ''

    def getScraperSiteByName(self, name):
        """ Returns the scraperSite object by name

        If not found, will return None
        """
        for scraper in self.scraperSites:
            if scraper.name == name:
                return scraper
        return None

    def getAvailableFileTypeForArt(self, attname, placing):
        """ Iterate over the list of <fileTypeForGameList> elements and return the first one found in the
        RomCollection's *available* media paths

        Args:
            attname: The art name used in either Kodi or the skin, e.g. 'icon', 'background', 'gameinfobig'
            placing: The ImagePlacing to find the FileType for - ImagePlacingMain or ImagePlacingInfo
        """
        fts = getattr(placing, attname)
        for ft in fts:
            if self.getMediaPathByTypeName(ft.name) != '':
                return ft

        return None

    def _getImagesForPlacing(self, placing):
        """ Returns a dict containing the filetype for each art property to be displayed. The dict key
        matches the ListItem.setArt key so it can be referenced in the skin

        Note that we should already have set the icon and thumb; these aren't retrieved here
        """
        fts = {}

        fts['background'] = self.getAvailableFileTypeForArt('background', placing)

        if placing.name == 'gameinfobig':
            fts['gameinfobig'] = self.getAvailableFileTypeForArt('gameinfobig', placing)

        elif placing.name == 'gameinfosmall':
            for arttype in ['gameinfoupperleft', 'gameinfoupperright', 'gameinfolowerleft', 'gameinfolowerright']:
                fts[arttype] = self.getAvailableFileTypeForArt(arttype, placing)

        elif placing.name == 'gameinfomamemarquee':
            for arttype in ['gameinfoleft', 'gameinfoupperright', 'gameinfolowerright']:
                fts[arttype] = self.getAvailableFileTypeForArt(arttype, placing)

        elif placing.name == 'gameinfomamecabinet':
            for arttype in ['gameinfoupperleft', 'gameinfoupperright', 'gameinfolower']:
                fts[arttype] = self.getAvailableFileTypeForArt(arttype, placing)

        else:
            print ('WARNING - Unsupported image placing type: ' + placing.name)

        return fts

    def getImagesForGameInfoView(self):
        """Returns a dict of FileTypes to be displayed in the GameInfoView"""
        return self._getImagesForPlacing(self.imagePlacingInfo)

    def getImagesForGameListViewSelected(self):
        """Returns a dict of FileTypes to be displayed in the GameListView, when selected"""
        return self._getImagesForPlacing(self.imagePlacingMain)

    def getImagesForGameListView(self):
        """Returns a dict of FileTypes to be displayed in the GameListView (typically just icon and thumb)"""
        fts = {}
        fts['icon'] = self.getAvailableFileTypeForArt('icon', self.imagePlacingMain)
        fts['thumb'] = self.getAvailableFileTypeForArt('thumb', self.imagePlacingMain)
        return fts

    def getGamenameFromFilename(self, filename):
        log.debug("current rom file: %s" % filename)

        # Build friendly romname
        if self.useFoldernameAsGamename:
            gamename = os.path.basename(os.path.dirname(filename))
        else:
            gamename = os.path.basename(filename)

        log.debug("gamename (file): %s" % gamename)

        # Use regular expression to find disk prefix like '(Disk 1)' etc.
        match = False
        if self.diskPrefix != '':
            match = re.search(self.diskPrefix.lower(), gamename.lower())

        if match:
            gamename = gamename[0:match.start()]
        else:
            gamename = os.path.splitext(gamename)[0]

        gamename = gamename.strip()

        log.debug("gamename (friendly): %s" % gamename)

        return gamename


class Config(RcbXmlReaderWriter):
    """
    romCollections: A dict of all the RomCollections added by the user, with key being the numeric ID cast as a string
    scraperSites: A list of all the available Sites/Scrapers
    fileTypeIdsForGamelist = None

    showHideOption: Default is 'ignore'
    missingFilterInfo:
    missingFilterArtwork:

    tree: XML tree containing the configuration
    configPath: This doesn't appear to be used
    configFile: Path to the XML tree
    """

    def __init__(self, configFile):
        self.romCollections = None
        self.scraperSites = None
        self.fileTypeIdsForGamelist = None

        self.showHideOption = 'ignore'
        self.missingFilterInfo = None
        self.missingFilterArtwork = None

        self.tree = None
        self.configPath = None

        log.info('Config() set path to %s' % configFile)
        self.configFile = configFile

    def __repr__(self):
        return "<Config: %s>" % self.__dict__

    def initXml(self):
        log.info('initXml')

        if not self.configFile:
            self.configFile = util.getConfigXmlPath()

        if (not xbmcvfs.exists(self.configFile)):
            log.error('File config.xml does not exist. Place a valid config file here: %s' % self.configFile)
            return False, util.localize(32003)

        # force utf-8
        tree = ElementTree()
        if sys.version_info >= (2, 7):
            parser = XMLParser(encoding='utf-8')
        else:
            parser = XMLParser()

        tree.parse(self.configFile, parser)
        if (tree == None):
            log.error('Could not read config.xml')
            return False, util.localize(32004)

        self.tree = tree

        return True, ''

    def checkRomCollectionsAvailable(self):
        log.info('checkRomCollectionsAvailable')

        if not self.tree:
            success, errorMsg = self.initXml()
            if not success:
                return False, errorMsg

        romCollectionRows = self.tree.findall('RomCollections/RomCollection')
        numRomCollections = len(romCollectionRows)
        log.info("Number of Rom Collections in config.xml: %i" % numRomCollections)

        return numRomCollections > 0, ''

    def readXml(self):
        log.info('readXml')

        if not self.tree:
            success, errorMsg = self.initXml()
            if not success:
                return False, errorMsg

        # Rom Collections
        romCollections, errorMsg = self.readRomCollections(self.tree)
        if romCollections is None:
            return False, errorMsg
        self.romCollections = romCollections

        self.fileTypeIdsForGamelist = self.getFileTypeIdsForGameList(self.tree, romCollections)

        # Missing filter settings
        missingFilter = self.tree.find('MissingFilter')

        if missingFilter is not None:
            self.showHideOption = missingFilter.findtext('showHideOption')

        self.missingFilterInfo = self.readMissingFilter('missingInfoFilter', missingFilter)
        self.missingFilterArtwork = self.readMissingFilter('missingArtworkFilter', missingFilter)

        return True, ''

    def readRomCollections(self, tree):
        """
        Parses the config XML tree and extract the RomCollection objects into a dict.

        Args:
            tree: XML tree parsed from config.xml in the user's addon directory

        Returns:
            A dict of the rom collections, with the id attribute as the key. If an error occurs
            parsing the tree, None is returned

        """
        log.info('Begin readRomCollections')

        romCollections = {}

        romCollectionRows = tree.findall('RomCollections/RomCollection')

        if len(romCollectionRows) == 0:
            log.error('Configuration error. config.xml does not contain any RomCollections')
            return None, 'Configuration error. See xbmc.log for details'

        for romCollectionRow in romCollectionRows:

            romCollection = RomCollection()
            romCollection.name = romCollectionRow.attrib.get('name')
            if romCollection.name is None:
                log.error('Configuration error. RomCollection must have an attribute name')
                return None, util.localize(32005)

            log.info('current Rom Collection: ' + str(romCollection.name))

            rcid = romCollectionRow.attrib.get('id', '')
            if rcid == '':
                log.error('Configuration error. RomCollection %s must have an id' % romCollection.name)
                return None, util.localize(32005)

            if rcid in romCollections:
                log.error('Error while adding RomCollection. Make sure that the id is unique.')
                return None, util.localize(32006)

            romCollection.id = rcid

            # romPath
            for romPathRow in romCollectionRow.findall('romPath'):
                log.info('Rom path: ' + romPathRow.text)
                if romPathRow.text is not None:
                    romCollection.romPaths.append(romPathRow.text)

            # mediaPath
            for mediaPathRow in romCollectionRow.findall('mediaPath'):
                mediaPath = MediaPath()
                if mediaPathRow.text is not None:
                    mediaPath.path = mediaPathRow.text
                log.info('Media path: ' + mediaPath.path)
                fileType, errorMsg = self.get_filetype_by_name(mediaPathRow.attrib.get('type'), tree)
                if fileType is None:
                    return None, errorMsg
                mediaPath.fileType = fileType
                romCollection.mediaPaths.append(mediaPath)

            #Scraper
            for scraperRow in romCollectionRow.findall('scraper'):
                if 'name' not in scraperRow.attrib:
                    log.error('Configuration error. RomCollection/scraper must have an attribute name')
                    return None, util.localize(32005)

                site = Site()
                site.name = scraperRow.attrib.get('name')
                site.path = scraperRow.attrib.get('path')
                default = scraperRow.attrib.get('default')
                if default:
                    site.default = default.upper() == 'TRUE'
                else:
                    site.default = False

                romCollection.scraperSites.append(site)

            # ImagePlacing - Main window
            romCollection.imagePlacingMain = ImagePlacing()
            imagePlacingRow = romCollectionRow.find('imagePlacingMain')
            if imagePlacingRow is not None:
                log.info('Image Placing name: ' + str(imagePlacingRow.text))
                fileTypeFor, errorMsg = self.readImagePlacing(imagePlacingRow.text, tree)
                if fileTypeFor is None:
                    return None, errorMsg

                romCollection.imagePlacingMain = fileTypeFor

            # ImagePlacing - Info window
            romCollection.imagePlacingInfo = ImagePlacing()
            imagePlacingRow = romCollectionRow.find('imagePlacingInfo')
            if imagePlacingRow is not None:
                log.info('Image Placing name: ' + str(imagePlacingRow.text))
                fileTypeFor, errorMsg = self.readImagePlacing(imagePlacingRow.text, tree)
                if fileTypeFor is None:
                    return None, errorMsg

                romCollection.imagePlacingInfo = fileTypeFor

            # RomCollection properties
            for var in ['gameclient', 'emulatorCmd', 'preCmd', 'postCmd', 'emulatorParams', 'saveStatePath',
                        'saveStateParams', 'diskPrefix']:
                romCollection.__setattr__(var, romCollectionRow.findtext(var, ''))

            # RomCollection int properties
            for var in ['maxFolderDepth']:
                romCollection.__setattr__(var, int(romCollectionRow.findtext(var, '')))

            # RomCollection bool properties
            for var in ['useBuiltinEmulator', 'ignoreOnScan', 'allowUpdate', 'useEmuSolo', 'usePopen',
                        'autoplayVideoMain', 'autoplayVideoInfo', 'useFoldernameAsGamename',
                        'doNotExtractZipFiles', 'makeLocalCopy']:
                romCollection.__setattr__(var, romCollectionRow.findtext(var, '').upper() == 'TRUE')

            # Add to dict
            romCollections[rcid] = romCollection

        return romCollections, ''

    def get_filetype_by_name(self, name, tree):
        fileTypeRows = tree.findall('FileTypes/FileType')

        fileTypeRow = next((element for element in fileTypeRows if element.attrib.get('name') == name), None)
        if fileTypeRow is None:
            log.error('Configuration error. FileType %s does not exist in config.xml' % name)
            return None, util.localize(32005)

        fileType = FileType()
        fileType.name = name

        try:
            fileType.id = fileTypeRow.attrib.get('id')
            fileType.type = fileTypeRow.find('type').text
            fileType.parent = fileTypeRow.find('parent').text
        except KeyError:
            log.error('Configuration error. FileType %s must have an id' % name)
            return None, util.localize(32005)
        except AttributeError:
            pass

        return fileType, ''

    def readImagePlacing(self, imagePlacingName, tree):

        #fileTypeForRow = None
        fileTypeForRows = tree.findall('ImagePlacing/fileTypeFor')

        fileTypeForRow = next(
            (element for element in fileTypeForRows if element.attrib.get('name') == imagePlacingName), None)
        if fileTypeForRow is None:
            log.error(
                'Configuration error. ImagePlacing/fileTypeFor %s does not exist in config.xml' % str(imagePlacingName))
            return None, util.localize(32005)

        imagePlacing = ImagePlacing()

        imagePlacing.name = imagePlacingName

        for attr in ['fileTypesForGameList', 'fileTypesForGameListSelected',
                     'fileTypesForMainView1', 'fileTypesForMainView2', 'fileTypesForMainView3',
                     'fileTypesForMainViewBackground', 'fileTypesForMainViewGameInfoBig',
                     'fileTypesForMainViewGameInfoUpperLeft', 'fileTypesForMainViewGameInfoUpperRight',
                     'fileTypesForMainViewGameInfoLowerLeft', 'fileTypesForMainViewGameInfoLowerRight',
                     'fileTypesForMainViewGameInfoLower', 'fileTypesForMainViewGameInfoUpper',
                     'fileTypesForMainViewGameInfoRight', 'fileTypesForMainViewGameInfoLeft',
                     'fileTypesForMainViewVideoWindowBig', 'fileTypesForMainViewVideoWindowSmall',
                     'fileTypesForMainViewVideoFullscreen']:
            # Hack - class attribute fileTypesForXXX doesn't match XML key fileTypeForXXX
            val = self.readFileTypeForElement(fileTypeForRow, attr.replace('fileTypesFor', 'fileTypeFor'), tree)
            log.debug("Reading imageplacing for {0}: {1}".format(attr, val))
            setattr(imagePlacing, attr, val)

        return imagePlacing, ''

    def readFileTypeForElement(self, fileTypeForRow, key, tree):
        fileTypeList = []
        fileTypesForControl = fileTypeForRow.findall(key)
        for fileTypeForControl in fileTypesForControl:

            fileType, errorMsg = self.get_filetype_by_name(fileTypeForControl.text, tree)
            if fileType is None:
                return None

            fileTypeList.append(fileType)

        return fileTypeList

    def readMissingFilter(self, filterName, tree):
        missingFilter = MissingFilter()

        if tree is not None:
            missingFilterRow = tree.find(filterName)
            if missingFilterRow is not None:
                missingFilter.andGroup = self.getMissingFilterItems(missingFilterRow, 'andGroup')
                missingFilter.orGroup = self.getMissingFilterItems(missingFilterRow, 'orGroup')

        return missingFilter

    def getMissingFilterItems(self, missingFilterRow, groupName):
        items = []
        groupRow = missingFilterRow.find(groupName)
        if groupRow is not None:
            itemRows = groupRow.findall('item')
            for element in itemRows:
                items.append(element.text)
        return items

    def getFileTypeIdsForGameList(self, tree, romCollections):

        fileTypeIds = []
        for romCollection in list(romCollections.values()):
            for fileType in romCollection.imagePlacingMain.fileTypesForGameList:
                if (fileTypeIds.count(fileType.id) == 0):
                    fileTypeIds.append(fileType.id)
            for fileType in romCollection.imagePlacingMain.fileTypesForGameListSelected:
                if (fileTypeIds.count(fileType.id) == 0):
                    fileTypeIds.append(fileType.id)

            #fullscreen video
            fileType, errorMsg = self.get_filetype_by_name('gameplay', tree)
            if fileType is not None:
                fileTypeIds.append(fileType.id)

        return fileTypeIds

    def get_filetypes(self):
        filetypes = []

        filetype_rows = self.tree.findall('FileTypes/FileType')
        for filetype_row in filetype_rows:
            filetype = FileType()
            filetype.id = filetype_row.attrib.get('id')
            filetype.name = filetype_row.attrib.get('name')
            filetypes.append(filetype)

        return filetypes

    def getRomCollectionNames(self):
        """
        Returns: an alphabetically-sorted list of the Rom Collection names, suitable for a UI list

        """
        names = []
        for rckey, rcval in list(self.romCollections.items()):
            names.append(rcval.name)

        names.sort()

        return names

    def getRomCollectionById(self, rcid):
        """
        Find the matching Rom Collection by ID

        Args:
            rcid: the ID of the Rom Collection to be found (as a str)

        Returns:
            The Rom Collection with the matching ID, or None if not found

        """
        try:
            return self.romCollections.get(rcid)
        except KeyError:
            log.warn("Unable to find rom collection with ID {0}".format(rcid))
            return None

    def getRomCollectionByName(self, name):
        """
        Find the matching Rom Collection by Name

        Args:
            name: the name of the Rom Collection to be found

        Returns:
            The Rom Collection with the matching name, or None if not found

        """
        for rckey, rcval in list(self.romCollections.items()):
            if rcval.name == name:
                return rcval

        return None
