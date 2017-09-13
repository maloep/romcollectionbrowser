import os

import util
import urllib
import helper
from util import *
from xml.etree.ElementTree import *
from util import Logutil as log


#friendly name : db column, missing filter statement
gameproperties = {'Title' : ['name', "name = ''"],
				'Description' : ['description', "description = ''"],				
				'Genre' : ['genre', "Id NOT IN (SELECT GameId From GenreGame)"],
				'Developer' : ['developerId', "developerId is NULL"],
				'Publisher' : ['publisherId', "publisherId is NULL"],
				'Reviewer' : ['reviewerId', "reviewerId is NULL"],
				'Release Year' : ['yearId', "yearId is NULL"],
				'Rating' : ['rating', "rating = ''"],
				'Votes' : ['numVotes', "numVotes is NULL"],
				'Region' : ['region', "region = ''"],
				'Media' : ['media', "media = ''"],	
				'Max. Players' : ['maxPlayers', "maxPlayers = ''"],
				'Controller' : ['controllerType', "controllerType = ''"],
				'Perspective' : ['perspective', "perspective = ''"],
				'Original Title' : ['originalTitle', "originalTitle = ''"],
				'Alternate Title' : ['alternateTitle', "alternateTitle = ''"],
				'Translated By' : ['translatedBy', "translatedBy = ''"],
				'Version' : ['version', "version = ''"],
				'Url' : ['url', "url = ''"]
				}


consoleDict = {
			#name, mobygames-id, thegamesdb, archive vg
			'Other' : ['0', '', ''],
			'3DO' : ['35', '3DO', '3do'],
			'Amiga' : ['19', 'Amiga', 'amiga'],
			'Amiga CD32' : ['56', '', 'cd32'],
			'Amstrad CPC' : ['60', 'Amstrad CPC', 'cpc'],
			'Apple II' : ['31', '', 'appleii'],
			'Atari 2600' : ['28', 'Atari 2600', 'atari2600'],
			'Atari 5200' : ['33', 'Atari 5200', 'atari5200'],
			'Atari 7800' : ['34', 'Atari 7800', 'atari7800'],
			'Atari 8-bit' : ['39', '', 'atari8bit'],
			'Atari ST' : ['24', '', 'ast'],
			'BBC Micro' : ['92', '', 'bbc'],
			'BREW' : ['63', '', ''],
			'CD-i' : ['73', '', 'cdi'], 
			'Channel F' : ['76', '', 'channelf'],  
			'ColecoVision' : ['29', 'Colecovision', 'colecovision'],
			'Commodore 128' : ['61', '', ''],
			'Commodore 64' : ['27', 'Commodore 64', 'c64'],
			'Commodore PET/CBM' : ['77', '', 'pet'],  
			'DoJa' : ['72', '', ''],
			'DOS' : ['2', '', ''],
			'Dragon 32/64' : ['79', '', ''],  
			'Dreamcast' : ['8', 'Sega Dreamcast', 'dreamcast'],
			'Electron' : ['93', '', ''],
			'ExEn' : ['70', '', ''],
			'Game Boy' : ['10', 'Nintendo Gameboy', 'gameboy'],
			'Game Boy Advance' : ['12', 'Nintendo Game Boy Advance', 'gba'],  
			'Game Boy Color' : ['11', 'Nintendo Game Boy Color', 'gbc'],
			'GameCube' : ['14', 'Nintendo GameCube', 'gamecube'],
			'Game Gear' : ['25', 'Sega Game Gear', 'gamegear'],
			'Genesis' : ['16', 'Sega Genesis', 'genesis'],
			'Gizmondo' : ['55', '', 'gizmondo'],
			'Intellivision' : ['30', 'Intellivision', 'intellivision'],
			'Jaguar' : ['17', 'Atari Jaguar', 'jaguar'],
			'Linux' : ['1', '', ''],
			'Lynx' : ['18', '', 'lynx'],
			'Macintosh' : ['74', 'Mac OS', ''],
			'MAME' : ['0', 'Arcade', ''],
			'Mophun' : ['71', '', ''],
			'MSX' : ['57', '', 'msx'],
			'Neo Geo' : ['36', 'NeoGeo', 'neo'],
			'Neo Geo CD' : ['54', '', 'neogeocd'],
			'Neo Geo Pocket' : ['52', '', ''],
			'Neo Geo Pocket Color' : ['53', '', 'ngpc'],  
			'NES' : ['22', 'Nintendo Entertainment System (NES)', 'nes'],
			'N-Gage' : ['32', '', 'ngage'],
			'Nintendo 64' : ['9', 'Nintendo 64', 'n64'],  
			'Nintendo DS' : ['44', 'Nintendo DS', ''],
			'Nintendo DSi' : ['87', '', ''],
			'Odyssey' : ['75', '', 'odyssey'],
			'Odyssey 2' : ['78', '', 'odyssey2'],
			'PC-88' : ['94', '', 'pc88'],
			'PC-98' : ['95', '', 'pc98'],
			'PC Booter' : ['4', '', ''],
			'PC-FX' : ['59', '', 'pcfx'],
			'PlayStation' : ['6', 'Sony Playstation', 'ps'],  
			'PlayStation 2' : ['7', 'Sony Playstation 2', 'ps2'],
			'PlayStation 3' : ['81', 'Sony Playstation 3', ''],
			'PSP' : ['46', 'Sony PSP', ''],
			'SEGA 32X' : ['21', 'Sega 32X', 'sega32x'],  
			'SEGA CD' : ['20', 'Sega CD', 'segacd'],
			'SEGA Master System' : ['26', 'Sega Master System', 'sms'],  
			'SEGA Saturn' : ['23', 'Sega Saturn', 'saturn'],
			'SNES' : ['15', 'Super Nintendo (SNES)', 'snes'],
			'Spectravideo' : ['85', '', ''],
			'TI-99/4A' : ['47', '', 'ti99'],
			'TRS-80' : ['58', '', ''],
			'TRS-80 CoCo' : ['62', '', ''],  
			'TurboGrafx-16' : ['40', 'TurboGrafx 16', 'tg16'],
			'TurboGrafx CD' : ['45', '', ''],
			'Vectrex' : ['37', '', 'vectrex'],
			'VIC-20' : ['43', '', 'vic20'],
			'Virtual Boy' : ['38', 'Nintendo Virtual Boy', 'virtualboy'],  
			'V.Smile' : ['42', '', ''],
			'Wii' : ['82', 'Nintendo Wii', ''],
			'Windows' : ['3', 'PC', ''], 
			'Windows 3.x' : ['5', '', ''],
			'WonderSwan' : ['48', '', 'wonderswan'],
			'WonderSwan Color' : ['49', '', ''],  
			'Xbox' : ['13', 'Microsoft Xbox', 'xbox'],
			'Xbox 360' : ['69', 'Microsoft Xbox 360', ''],
			'Zeebo' : ['88', '', ''],
			'Zodiac' : ['68', '', 'zod'],
			'ZX Spectr' : ['41', 'Sinclair ZX Spectrum', '']}

missingFilterOptions = {util.localize(32157) : util.localize(32158),
					util.localize(32159) : util.localize(32160),
					util.localize(32161) : util.localize(32162)}



def getPlatformByRomCollection(source, romCollectionName):
	platform = ''
	if(source.find('mobygames.com') != -1):
		try:
			platform = consoleDict[romCollectionName][0]
		except:
			Logutil.log('Could not find platform name for Rom Collection %s' %romCollectionName, util.LOG_LEVEL_WARNING)
	elif(source.find('thegamesdb.net') != -1):
		try:
			platform = consoleDict[romCollectionName][1]
		except:
			Logutil.log('Could not find platform name for Rom Collection %s' %romCollectionName, util.LOG_LEVEL_WARNING)
	elif(source.find('archive.vg') != -1):
		try:
			platform = consoleDict[romCollectionName][2]
		except:
			Logutil.log('Could not find platform name for Rom Collection %s' %romCollectionName, util.LOG_LEVEL_WARNING)
	
	return platform

			
imagePlacingDict = {'gameinfobig' : 'one big',
					'gameinfobigVideo' : 'one big or video',
					'gameinfosmall' : 'four small',
					'gameinfosmallVideo' : 'three small + video',
					'gameinfomamemarquee' : 'MAME: marquee in list',
					'gameinfomamecabinet' : 'MAME: cabinet in list'}			


class FileType(object):
	"""
	This config object is defined in config_template.xml in element FileTypes.

	name: In the case of MAME, this will be either: boxfront, cabinet, marquee, action, title.
	      For all other emulators: boxfront, boxback, cartridge, screenshot, fanart.
	id: Unique identifier for the FileType, defined in config_template.xml, and used in the File table in the database.
	type: The filetype, either image or video.
	parent: The class that this file pertains to. Current supported values: game, romcollection, developer, publisher.
	"""
	def __init__(self):
		self.name = ''
		self.id = -1
		self.type = ''
		self.parent = ''

	def __repr__(self):
		return "<FileType: %s>" % self.__dict__


class ImagePlacing:	
	name = ''	
	fileTypesForGameList = None
	fileTypesForGameListSelected = None			
	fileTypesForMainView1 = None
	fileTypesForMainView2 = None
	fileTypesForMainView3 = None						
	fileTypesForMainViewBackground = None
	fileTypesForMainViewGameInfoBig = None
	fileTypesForMainViewGameInfoUpperLeft = None
	fileTypesForMainViewGameInfoUpperRight = None
	fileTypesForMainViewGameInfoLowerLeft = None
	fileTypesForMainViewGameInfoLowerRight = None	
	fileTypesForMainViewGameInfoUpper = None
	fileTypesForMainViewGameInfoLower = None
	fileTypesForMainViewGameInfoLeft = None
	fileTypesForMainViewGameInfoRight = None
	
	fileTypesForMainViewVideoWindowBig = None
	fileTypesForMainViewVideoWindowSmall = None
	fileTypesForMainViewVideoFullscreen = None


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


class Scraper(object):
	"""
	A scraper represents the details of how to interpret the XML response from a site to extract the game's
	metadata.

	parseInstruction: Name of the XML file which details how to interpret the XML response. The XML files are
	contained in the scraper/ directory.
	source: URL to retrieve the element in question, with placeholders defined.
	sourceAppend:
	encoding: Expected encoding of the site, defaults to 'utf-8' unless overridden.
	returnUrl:
	replaceKeyString:
	replaceValueString:
	"""
	def __init__(self, **kwargs):
		self.parseInstruction = ''
		self.source = ''
		self.sourceAppend = ''
		self.encoding = 'utf-8'
		self.returnUrl = False
		self.replaceKeyString = ''
		self.replaceValueString = ''

		""" Set any variables explicitly passed """
		for name in kwargs:
			setattr(self, name, kwargs[name])

	def __repr__(self):
		return "<Scraper: %s>" % self.__dict__


class Site(object):
	"""
	A site represents a source of metadata for the rom collections, e.g. giantbomb.com, local NFO.

	These are defined in config_template.xml.

	name: The name of the site
	descFilePerGame:
	searchGameByCRC: Use CRC of the rom to match, rather than the rom's title.
	searchGameByCRCIgnoreRomName: This doesn't appear to be used at the moment.
	useFoldernameAsCRC: Generate CRC based on the foldername
	useFilenameAsCRC: Generate CRC based on the filename

	scrapers: A list of Scraper objects which are the default for this site.
	"""
	def __init__(self, **kwargs):
		self.name = ''
		# Used if the source for the game metadata is contained in a single file
		# (e.g. MAME history.dat file) or in multiple files/web URL
		self.descFilePerGame = False
		self.searchGameByCRC = True
		self.searchGameByCRCIgnoreRomName = False
		self.useFoldernameAsCRC = False
		self.useFilenameAsCRC = False

		self.scrapers = []

		""" Set any variables explicitly passed """
		for name in kwargs:
			setattr(self, name, kwargs[name])

	def __repr__(self):
		return "<Site: %s>" % self.__dict__

	def is_multigame_scraper(self):
		return not self.descFilePerGame

	def is_localartwork_scraper(self):
		return self.name == util.localize(32153)
	

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
	    primarily to work around SMB issues
	progressiveZipExtraction: Process zip files more effectively. Instead of transfering the whole zip
	    file, first load just the file list. Then - after selecting the desired files from the list - extract
	    only the compressed files locally and unzip those. Saves on transfering the whole zip file from slow 
	    storage like SD cards or network shares before anything else is handled. Instead it shows the file
	    list almost instantly and transfers only the parts of the zip file that are required to extract the
	    desired compressed files. Hugh advantage on large merged romsets. 
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
		self.progressiveZipExtraction = False
		self.diskPrefix = '_Disk.*'

		# These are used for XBox, which is now legacy and no longer supported by Kodi
		self.xboxCreateShortcut = False
		self.xboxCreateShortcutAddRomfile = False
		self.xboxCreateShortcutUseShortGamename = False

	def __repr__(self):
		return "<RomCollection: %s>" % self.__dict__

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



class Config(object):
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

		Logutil.log('Config() set path to %s' %configFile, util.LOG_LEVEL_INFO)
		self.configFile = configFile

	def __repr__(self):
		return "<Config: %s>" % self.__dict__
	
	def initXml(self):
		Logutil.log('initXml', util.LOG_LEVEL_INFO)
		
		if(not self.configFile):
			self.configFile = util.getConfigXmlPath()
		
		if(not os.path.isfile(self.configFile)):
			Logutil.log('File config.xml does not exist. Place a valid config file here: %s' %self.configFile, util.LOG_LEVEL_ERROR)
			return None, False, util.localize(32003)
		
		# force utf-8
		tree = ElementTree()
		if sys.version_info >= (2,7):
			parser = XMLParser(encoding='utf-8')
		else:
			parser = XMLParser()

		tree.parse(self.configFile, parser)
		if(tree == None):
			Logutil.log('Could not read config.xml', util.LOG_LEVEL_ERROR)
			return None, False, util.localize(32004)
		
		self.tree = tree
		
		return tree, True, ''
	
	def checkRomCollectionsAvailable(self):
		Logutil.log('checkRomCollectionsAvailable', util.LOG_LEVEL_INFO)
	
		tree, success, errorMsg = self.initXml()
		if not success:
			return False, errorMsg
		
		romCollectionRows = tree.findall('RomCollections/RomCollection')
		numRomCollections = len(romCollectionRows)
		Logutil.log("Number of Rom Collections in config.xml: %i" %numRomCollections, util.LOG_LEVEL_INFO)
				
		return numRomCollections > 0, ''
	
	def readXml(self):
		Logutil.log('readXml', util.LOG_LEVEL_INFO)
		
		tree, success, errorMsg = self.initXml()
		if not success:
			return False, errorMsg	
		
		# Rom Collections
		romCollections, errorMsg = self.readRomCollections(tree)
		if romCollections is None:
			return False, errorMsg		
		self.romCollections = romCollections
		
		# Scrapers
		scrapers, errorMsg = self.readScrapers(tree)
		if scrapers is None:
			return False, errorMsg		
		self.scraperSites = scrapers
				
		self.fileTypeIdsForGamelist = self.getFileTypeIdsForGameList(tree, romCollections)
		
		# Missing filter settings
		missingFilter = tree.find('MissingFilter')
		
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
		Logutil.log('Begin readRomCollections', util.LOG_LEVEL_INFO)
		
		romCollections = {}
		
		romCollectionRows = tree.findall('RomCollections/RomCollection')
								
		if len(romCollectionRows) == 0:
			Logutil.log('Configuration error. config.xml does not contain any RomCollections', util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'
			
		for romCollectionRow in romCollectionRows:
			
			romCollection = RomCollection()
			romCollection.name = romCollectionRow.attrib.get('name')
			if romCollection.name is None:
				Logutil.log('Configuration error. RomCollection must have an attribute name', util.LOG_LEVEL_ERROR)
				return None, util.localize(32005)
			
			Logutil.log('current Rom Collection: ' +str(romCollection.name), util.LOG_LEVEL_INFO)

			id = romCollectionRow.attrib.get('id', '')
			if id == '':
				Logutil.log('Configuration error. RomCollection %s must have an id' %romCollection.name, util.LOG_LEVEL_ERROR)
				return None, util.localize(32005)

			if id in romCollections:
				Logutil.log('Error while adding RomCollection. Make sure that the id is unique.', util.LOG_LEVEL_ERROR)
				return None, util.localize(32006)
			
			romCollection.id = id
			
			# romPath
			for romPathRow in romCollectionRow.findall('romPath'):
				Logutil.log('Rom path: ' +romPathRow.text, util.LOG_LEVEL_INFO)
				if romPathRow.text is not None:
					romCollection.romPaths.append(romPathRow.text)
				
			# mediaPath
			for mediaPathRow in romCollectionRow.findall('mediaPath'):
				mediaPath = MediaPath()
				if mediaPathRow.text is not None:
					mediaPath.path = mediaPathRow.text
				Logutil.log('Media path: ' +mediaPath.path, util.LOG_LEVEL_INFO)
				fileType, errorMsg = self.readFileType(mediaPathRow.attrib.get('type'), tree)
				if fileType is None:
					return None, errorMsg
				mediaPath.fileType = fileType
				romCollection.mediaPaths.append(mediaPath)
			
			#Scraper
			for scraperRow in romCollectionRow.findall('scraper'):
				if 'name' not in scraperRow.attrib:
					Logutil.log('Configuration error. RomCollection/scraper must have an attribute name', util.LOG_LEVEL_ERROR)
					return None, util.localize(32005)

				siteName = scraperRow.attrib.get('name')
				
				# Read additional scraper properties
				replaceKeyString = scraperRow.attrib.get('replaceKeyString', '')
				replaceValueString = scraperRow.attrib.get('replaceValueString', '')
								
				# elementtree version 1.2.7 does not support xpath like this: Scrapers/Site[@name="%s"]
				siteRow = None
				for element in tree.findall('Scrapers/Site'):
					if element.attrib.get('name') == siteName:
						siteRow = element
						break
				
				if siteRow is None:
					Logutil.log('Configuration error. Site %s does not exist in config.xml' %siteName, util.LOG_LEVEL_ERROR)
					return None, util.localize(32005)
								
				scraper, errorMsg = self.readScraper(siteRow, romCollection.name, replaceKeyString, replaceValueString, True, tree)
				if scraper is None:
					return None, errorMsg
				romCollection.scraperSites.append(scraper)
				
			# ImagePlacing - Main window
			romCollection.imagePlacingMain = ImagePlacing()
			imagePlacingRow = romCollectionRow.find('imagePlacingMain')
			if imagePlacingRow is not None:
				Logutil.log('Image Placing name: ' +str(imagePlacingRow.text), util.LOG_LEVEL_INFO)
				fileTypeFor, errorMsg = self.readImagePlacing(imagePlacingRow.text, tree)
				if fileTypeFor is None:
					return None, errorMsg
				
				romCollection.imagePlacingMain = fileTypeFor
				
			# ImagePlacing - Info window
			romCollection.imagePlacingInfo = ImagePlacing()
			imagePlacingRow = romCollectionRow.find('imagePlacingInfo')
			if imagePlacingRow is not None:
				Logutil.log('Image Placing name: ' +str(imagePlacingRow.text), util.LOG_LEVEL_INFO)
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
						'doNotExtractZipFiles', 'makeLocalCopy', 'progressiveZipExtraction', 'xboxCreateShortcut',
						'xboxCreateShortcutAddRomfile', 'xboxCreateShortcutUseShortGamename']:
				romCollection.__setattr__(var, romCollectionRow.findtext(var, '').upper() == 'TRUE')

			# Add to dict
			romCollections[id] = romCollection
			
		return romCollections, ''
		
	def readScrapers(self, tree):
		
		sites = {}
				
		siteRows = tree.findall('Scrapers/Site')
		for siteRow in siteRows:
			site, errorMsg = self.readScraper(siteRow, '', '', '', False, tree)
			if site is None:
				return None, errorMsg
			
			name = siteRow.attrib.get('name')
			sites[name] = site

		return sites, ''
			
	def readScraper(self, siteRow, romCollectionName, inReplaceKeyString, inReplaceValueString, replaceValues, tree):
		
		site = Site()
		site.name = siteRow.attrib.get('name')
		Logutil.log('Parsing scraper site: ' +str(site.name), util.LOG_LEVEL_INFO)

		for var in ['descFilePerGame', 'searchGameByCRC', 'searchGameByCRCIgnoreRomName',
					'useFoldernameAsCRC', 'useFilenameAsCRC']:
			site.__setattr__(var, siteRow.get(var, '').upper() == 'TRUE')

		scrapers = []

		for scraperRow in siteRow.findall('Scraper'):
			scraper = Scraper()
			
			parseInstruction = scraperRow.attrib.get('parseInstruction', '')
			if parseInstruction != '':
				if not os.path.isabs(parseInstruction):
					# If it is a relative path, search in RCBs home directory
					parseInstruction = os.path.join(util.RCBHOME, 'resources', 'scraper', parseInstruction)
				
				if not os.path.isfile(parseInstruction):
					Logutil.log('Configuration error. parseInstruction file %s does not exist.' %parseInstruction, util.LOG_LEVEL_ERROR)
					return None, util.localize(32005)
				
				scraper.parseInstruction = parseInstruction
				
			source = scraperRow.attrib.get('source', '')
			if source != '':
				if replaceValues:
					#platform = getPlatformByRomCollection(source, romCollectionName)
					platform = urllib.quote(getPlatformByRomCollection(source, romCollectionName),
											safe='')
					source = source.replace('%PLATFORM%', platform)
				scraper.source = source

			scraper.encoding = scraperRow.get('encoding', 'utf-8')
			scraper.returnUrl = scraperRow.get('returnUrl', '').upper() == 'TRUE'
			scraper.sourceAppend = scraperRow.get('sourceAppend', '')
				
			scraper.replaceKeyString = inReplaceKeyString
			scraper.replaceValueString = inReplaceValueString
			
			scrapers.append(scraper)
			
		site.scrapers = scrapers

		Logutil.log('Parsed scraper site: {0}'.format(site), util.LOG_LEVEL_INFO)

		return site, ''
	
	def readFileType(self, name, tree):
		fileTypeRows = tree.findall('FileTypes/FileType')

		fileTypeRow = next((element for element in fileTypeRows if element.attrib.get('name') == name), None)
		if fileTypeRow is None:
			Logutil.log('Configuration error. FileType %s does not exist in config.xml' %name, util.LOG_LEVEL_ERROR)
			return None, util.localize(32005)
			
		fileType = FileType()
		fileType.name = name

		if 'id' not in fileTypeRow.attrib:
			Logutil.log('Configuration error. FileType %s must have an id' %name, util.LOG_LEVEL_ERROR)
			return None, util.localize(32005)
		fileType.id = fileTypeRow.attrib.get('id')
		
		type = fileTypeRow.find('type')
		if(type != None):
			fileType.type = type.text
			
		parent = fileTypeRow.find('parent')
		if(parent != None):
			fileType.parent = parent.text
			
		return fileType, ''
		
	def readImagePlacing(self, imagePlacingName, tree):
		
		#fileTypeForRow = None
		fileTypeForRows = tree.findall('ImagePlacing/fileTypeFor')

		fileTypeForRow = next((element for element in fileTypeForRows if element.attrib.get('name') == imagePlacingName), None)
		if fileTypeForRow is None:
			Logutil.log('Configuration error. ImagePlacing/fileTypeFor %s does not exist in config.xml' %str(imagePlacingName), util.LOG_LEVEL_ERROR)
			return None, util.localize(32005)
		
		imagePlacing = ImagePlacing()
		
		imagePlacing.name = imagePlacingName
			
		imagePlacing.fileTypesForGameList = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameList', tree)
		imagePlacing.fileTypesForGameListSelected = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameListSelected', tree)
		imagePlacing.fileTypesForMainView1 = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainView1', tree)
		imagePlacing.fileTypesForMainView2 = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainView2', tree)
		imagePlacing.fileTypesForMainView3 = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainView3', tree)
		imagePlacing.fileTypesForMainViewBackground = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewBackground', tree)
		imagePlacing.fileTypesForMainViewGameInfoBig = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoBig', tree)
		imagePlacing.fileTypesForMainViewGameInfoUpperLeft = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoUpperLeft', tree)
		imagePlacing.fileTypesForMainViewGameInfoUpperRight = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoUpperRight', tree)
		imagePlacing.fileTypesForMainViewGameInfoLowerLeft = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoLowerLeft', tree)
		imagePlacing.fileTypesForMainViewGameInfoLowerRight = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoLowerRight', tree)
		
		imagePlacing.fileTypesForMainViewGameInfoLower = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoLower', tree)
		imagePlacing.fileTypesForMainViewGameInfoUpper = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoUpper', tree)
		imagePlacing.fileTypesForMainViewGameInfoRight = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoRight', tree)
		imagePlacing.fileTypesForMainViewGameInfoLeft = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoLeft', tree)
		
		imagePlacing.fileTypesForMainViewVideoWindowBig = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewVideoWindowBig', tree)
		imagePlacing.fileTypesForMainViewVideoWindowSmall = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewVideoWindowSmall', tree)
		imagePlacing.fileTypesForMainViewVideoFullscreen = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewVideoFullscreen', tree)
			
		return imagePlacing, ''
	
	def readFileTypeForElement(self, fileTypeForRow, key, tree):
		fileTypeList = []
		fileTypesForControl = fileTypeForRow.findall(key)		
		for fileTypeForControl in fileTypesForControl:						
				
			fileType, errorMsg = self.readFileType(fileTypeForControl.text, tree)
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
		for romCollection in romCollections.values():
			for fileType in romCollection.imagePlacingMain.fileTypesForGameList:				
				if(fileTypeIds.count(fileType.id) == 0):
					fileTypeIds.append(fileType.id)
			for fileType in romCollection.imagePlacingMain.fileTypesForGameListSelected:
				if(fileTypeIds.count(fileType.id) == 0):
					fileTypeIds.append(fileType.id)
			
			#fullscreen video
			fileType, errorMsg = self.readFileType('gameplay', tree)
			if fileType is not None:
				fileTypeIds.append(fileType.id)

		return fileTypeIds

	def getRomCollectionNames(self):
		"""
		Returns: an alphabetically-sorted list of the Rom Collection names, suitable for a UI list

		"""
		names = []
		for rckey, rcval in self.romCollections.iteritems():
			names.append(rcval.name)

		names.sort()

		return names

	def getRomCollectionById(self, id):
		"""
		Find the matching Rom Collection by ID

		Args:
		    id: the ID of the Rom Collection to be found (as a str)

		Returns:
		    The Rom Collection with the matching ID, or None if not found

		"""
		try:
			return self.romCollections.get(id)
		except KeyError as e:
			log.warn("Unable to find rom collection with ID {0}".format(id))
			return None

	def getRomCollectionByName(self, name):
		"""
		Find the matching Rom Collection by Name

		Args:
		    name: the name of the Rom Collection to be found

		Returns:
		    The Rom Collection with the matching name, or None if not found

		"""
		for rckey, rcval in self.romCollections.iteritems():
			if rcval.name == name:
				return rcval

		return None
