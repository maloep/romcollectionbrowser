import os

import util
import urllib
import helper
from pprint import pprint
from util import *
from xml.etree.ElementTree import *

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
	def __init__(self):
		self.name = ''
		''' This is the full path to the file'''
		self.id = -1
		''' Internal DB ID (?)'''
		self.type = ''
		''' 0 = file, 1 = boxfront, 2 = boxback, 4 = screenshot, 5 = fanart (defined in config_template.xml)'''
		self.parent = ''
		''' The ID of the Game/Publisher/Developer/Collection for this file '''

	def __repr__(self):
		return "FileType: type = {0}, name = {1}, parent = {2}".format (self.type, self.name, self.parent)
	
class ImagePlacing:
	def __init__(self):
		self.name = ''

		# The following are all lists of FileTypes
		self.fileTypesForGameList = []
		self.fileTypesForGameListSelected = []
		self.fileTypesForMainView1 = []
		self.fileTypesForMainView2 = []
		self.fileTypesForMainView3 = []
		self.fileTypesForMainViewBackground = []
		self.fileTypesForMainViewGameInfoBig = []
		self.fileTypesForMainViewGameInfoUpperLeft = []
		self.fileTypesForMainViewGameInfoUpperRight = []
		self.fileTypesForMainViewGameInfoLowerLeft = []
		self.fileTypesForMainViewGameInfoLowerRight = []
		self.fileTypesForMainViewGameInfoUpper = []
		self.fileTypesForMainViewGameInfoLower = []
		self.fileTypesForMainViewGameInfoLeft = []
		self.fileTypesForMainViewGameInfoRight = []

		self.fileTypesForMainViewVideoWindowBig = []
		self.fileTypesForMainViewVideoWindowSmall = []
		self.fileTypesForMainViewVideoFullscreen = []

	def __repr__(self):
		str = "ImagePlacing:\n"
		for key, value in vars(self).iteritems():
			str += "\t{0} = {1}\n".format (key, value)
		return str
	
class MediaPath:
	def __init__(self):
		self.path = ''
		self.fileType = None

	def __repr__(self):
		return "MediaPath: type={0}, path={1}".format (self.fileType, self.path)
	
class Scraper:
	def __init__(self):
		self.parseInstruction = ''
		''' XML definition file '''
		self.source = ''
		''' URL to parse using the parseInstruction '''
		self.sourceAppend = ''
		self.encoding = 'utf-8'
		self.returnUrl = False
		self.replaceKeyString = ''
		self.replaceValueString = ''

	def __repr__(self):
		str = "Scraper\n"
		for key, value in vars(self).iteritems():
			str += "\t{0} = {1}\n".format (key, value)
		return str
	
class Site:
	def __init__(self):
		self.name = ''
		self.descFilePerGame = False
		self.searchGameByCRC = True
		self.searchGameByCRCIgnoreRomName = False
		self.useFoldernameAsCRC = False
		self.useFilenameAsCRC = False
	
		self.scrapers = []	# List of Scraper objects

	def __repr__(self):
		str = "Site\n"
		for key, value in vars(self).iteritems():
			str += "\t{0} = {1}\n".format (key, value)
		return str



class MissingFilter:
	andGroup = []
	orGroup = []

class RomCollection:
	def __init__(self):
		self.id = -1
		self.name = ''

		self.useBuiltinEmulator = False
		self.gameclient = ''
		self.emulatorCmd = ''
		''' Full string to execute when launching '''
		self.preCmd = ''
		self.postCmd = ''
		self.emulatorParams = ''
		self.romPaths = []
		''' Rompaths to pass to the emulator command '''
		self.saveStatePath = ''
		self.saveStateParams = ''
		self.mediaPaths = []
		self.scraperSites = []
		''' List of Scrapers to use to retrieve game info '''
		self.imagePlacingMain = []
		self.imagePlacingInfo = []
		self.autoplayVideoMain = True
		self.autoplayVideoInfo = True
		self.ignoreOnScan = False
		self.allowUpdate = True
		self.useEmuSolo = False
		self.usePopen = False
		self.maxFolderDepth = 99
		''' How far down the rompath to look '''
		self.useFoldernameAsGamename = False
		self.doNotExtractZipFiles = False
		''' If true, launch the emulator passing the zip as the rom '''
		self.makeLocalCopy = False
		''' If true, copies the rom to Kodi temp dir before running '''
		self.diskPrefix = '_Disk.*'
		self.xboxCreateShortcut = False
		self.xboxCreateShortcutAddRomfile = False
		self.xboxCreateShortcutUseShortGamename = False

	def __repr__(self):
		rc = "Rom Collection\n"
		for key, value in vars(self).iteritems():
			rc += "\t{0} = {1}\n".format (key, value)
		return rc

class Config:
		
	romCollections = None
	''' Dictionary of RomCollections '''
	scraperSites = None
	''' Dictionary of Sites '''
	fileTypeIdsForGamelist = None
	''' Dictionary of FileTypes '''
	
	showHideOption = 'ignore'
	missingFilterInfo = None
	missingFilterArtwork = None
	
	tree = None
	configPath = None
	
	def __init__(self, configFile):
		Logutil.log('Config() set path to %s' %configFile, util.LOG_LEVEL_INFO)
		self.configFile = configFile
				
	
	def initXml(self):
		Logutil.log('initXml', util.LOG_LEVEL_INFO)
		
		if(not self.configFile):
			self.configFile = util.getConfigXmlPath()
		
		if(not os.path.isfile(self.configFile)):
			Logutil.log('File config.xml does not exist. Place a valid config file here: %s' %self.configFile, util.LOG_LEVEL_ERROR)
			return None, False, util.localize(32003)
		try:
			# force utf-8
			tree = ElementTree().parse(self.configFile, XMLParser(encoding='utf-8'))
		except ParseError as pe:
			Logutil.log('Could not read config.xml', util.LOG_LEVEL_ERROR)
			return None, False, util.localize(32004)

		self.tree = tree
		
		return tree, True, ''
	
	
	def checkRomCollectionsAvailable(self):
		Logutil.log('checkRomCollectionsAvailable', util.LOG_LEVEL_INFO)
	
		tree, success, errorMsg = self.initXml()
		if(not success):
			return False, errorMsg
		
		romCollectionRows = tree.findall('RomCollections/RomCollection')
		numRomCollections = len(romCollectionRows) 
		Logutil.log("Number of Rom Collections in config.xml: %i" %numRomCollections, util.LOG_LEVEL_INFO)
				
		return numRomCollections > 0, ''
				
	
	def readXml(self):
		Logutil.log('readXml', util.LOG_LEVEL_INFO)
		
		tree, success, errorMsg = self.initXml()
		if(not success):
			return False, errorMsg	
		
		#Rom Collections
		romCollections, errorMsg = self.readRomCollections(tree)
		if(romCollections == None):
			return False, errorMsg		
		self.romCollections = romCollections
		
		#Scrapers
		scrapers, errorMsg = self.readScrapers(tree)
		if(scrapers == None):
			return False, errorMsg
		self.scraperSites = scrapers
				
		self.fileTypeIdsForGamelist = self.getFileTypeIdsForGameList(tree, romCollections)
		
		#Missing filter settings
		missingFilter = tree.find('MissingFilter')
		
		if(missingFilter != None):
			showHideOption = self.readTextElement(missingFilter, 'showHideOption')
			if(showHideOption != ''):
				self.showHideOption = showHideOption
			
		self.missingFilterInfo = self.readMissingFilter('missingInfoFilter', missingFilter)
		self.missingFilterArtwork = self.readMissingFilter('missingArtworkFilter', missingFilter)
		
		return True, ''	

	
		
	def readRomCollections(self, tree):
		
		Logutil.log('Begin readRomCollections', util.LOG_LEVEL_INFO)
		
		romCollections = {}

		romCollectionRows = tree.findall('RomCollections/RomCollection')
								
		if (len(romCollectionRows) == 0):
			Logutil.log('Configuration error. config.xml does not contain any RomCollections', util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'
			
		for romCollectionRow in romCollectionRows:
			
			romCollection = RomCollection()
			# Parse the XML child elements
			for child in romCollectionRow:
				#print "Collection: tag = {0}, value = {1}".format (child.tag, child.text)

				try:
					if isinstance (getattr(romCollection, child.tag), (bool)):
						setattr(romCollection, child.tag, child.text.upper() == "TRUE")
					elif isinstance(getattr(romCollection, child.tag), (str)):
						setattr(romCollection, child.tag, child.text)
						#print "  item is a string"
					elif isinstance(getattr(romCollection, child.tag), (list)):
						pass
						#print "  item is a list"
				except:
					pass
					#print "  can't work out: {0}".format (child.tag)


				# Tags that are entered multiple times so we record them as lists
				if child.tag == 'romPath':
					romCollection.romPaths.append(child.text)
				elif child.tag == 'mediaPath':
					mediaPath = MediaPath()
					mediaPath.path = child.text
					Logutil.log('Adding media path: {0}'.format (mediaPath.path), util.LOG_LEVEL_INFO)
					fileType, errorMsg = self.readFileType(child.attrib.get('type'), tree)
					if(fileType == None):
						Logutil.log('Unable to find filetype for {0}'.format (child.attrib.get('type')), util.LOG_LEVEL_WARNING)
						# Skip to the next XML element
						continue

					mediaPath.fileType = fileType
					romCollection.mediaPaths.append(mediaPath)



			# Attributes
			if 'name' not in romCollectionRow.attrib:
				Logutil.log('Error while adding RomCollection: Missing name attribute', util.LOG_LEVEL_ERROR)
				# Skip this collection, move to the next
				continue

			romCollection.name = romCollectionRow.attrib.get('name')
			Logutil.log('current Rom Collection: {0}'.format (romCollection.name), util.LOG_LEVEL_INFO)

			if 'id' not in romCollectionRow.attrib:
				Logutil.log('Error while adding RomCollection {0}: Missing id attribute'.format (romCollection.name),
							util.LOG_LEVEL_ERROR)
				# Skip this collection, move to the next
				continue

			# Check if the key for this romCollection already exists
			id = romCollectionRow.attrib.get('id')
			if id in romCollections:
				Logutil.log('Error while adding RomCollection {0}: Duplicate id attribute.'.format (romCollection.name),
							util.LOG_LEVEL_ERROR)
				# Skip this collection, move to the next
				continue

			romCollection.id = id
			
			#Scraper
			romCollection.scraperSites = []
			for scraperRow in romCollectionRow.findall('scraper'):
				siteName = scraperRow.attrib.get('name')
				Logutil.log('Scraper site: ' +str(siteName), util.LOG_LEVEL_INFO)
				if(siteName == None or siteName == ''):
					Logutil.log('Configuration error. RomCollection/scraper must have an attribute name', util.LOG_LEVEL_ERROR)
					return None, util.localize(32005)

				#read additional scraper properties
				replaceKeyString = scraperRow.attrib.get('replaceKeyString')
				if(replaceKeyString == None):
					replaceKeyString = ''
				replaceValueString = scraperRow.attrib.get('replaceValueString')
				if(replaceValueString == None):
					replaceValueString = ''
								
				#elementtree version 1.2.7 does not support xpath like this: Scrapers/Site[@name="%s"]
				siteRow = None
				for element in tree.findall('Scrapers/Site'):
					if(element.attrib.get('name') == siteName):
						siteRow = element
						break

				if(siteRow == None):
					Logutil.log('Configuration error. Site %s does not exist in config.xml' %siteName, util.LOG_LEVEL_ERROR)
					# FIXME TODO continue, skipping this site
					return None, util.localize(32005)
								
				scraper, errorMsg = self.readScraper(siteRow, romCollection.name, replaceKeyString, replaceValueString, True, tree)
				if(scraper == None):
					return None, errorMsg
				romCollection.scraperSites.append(scraper)
				
			#imagePlacing - Main window
			romCollection.imagePlacingMain = ImagePlacing()
			imagePlacingRow = romCollectionRow.find('imagePlacingMain')			
			if(imagePlacingRow != None):
				Logutil.log('Image Placing name: ' +str(imagePlacingRow.text), util.LOG_LEVEL_INFO)
				fileTypeFor, errorMsg = self.readImagePlacing(imagePlacingRow.text, tree)
				if(fileTypeFor == None):
					return None, errorMsg
				
				romCollection.imagePlacingMain = fileTypeFor
				
			#imagePlacing - Info window
			romCollection.imagePlacingInfo = ImagePlacing()
			imagePlacingRow = romCollectionRow.find('imagePlacingInfo')			
			if(imagePlacingRow != None):
				Logutil.log('Image Placing name: ' +str(imagePlacingRow.text), util.LOG_LEVEL_INFO)
				fileTypeFor, errorMsg = self.readImagePlacing(imagePlacingRow.text, tree)
				if(fileTypeFor == None):
					return None, errorMsg
				
				romCollection.imagePlacingInfo = fileTypeFor

			romCollections[id] = romCollection
			
		return romCollections, ''
		
		
	def readScrapers(self, tree):
		
		sites = {}
				
		siteRows = tree.findall('Scrapers/Site')
		for siteRow in siteRows:
			site, errorMsg = self.readScraper(siteRow, '', '', '', False, tree)
			if(site == None):
				return None, errorMsg
			
			name = siteRow.attrib.get('name')
			sites[name] = site

		return sites, ''
		
	# FIXME TODO Handle input parameters
	def readScraper(self, siteRow, romCollectionName, inReplaceKeyString, inReplaceValueString, replaceValues, tree):
		
		site = Site()
		for key, value in siteRow.attrib.iteritems():
			#print "Site: Key = {0}, Value = {1}".format (key, value)
			if key == 'name':
				setattr(site, key, value)
			else:
				setattr(site, key, value.upper() == "TRUE")

		scrapers = []
		for scraperRow in siteRow.findall('Scraper'):
			scraper = Scraper()

			for key, value in scraperRow.attrib.iteritems():
				#print "Scraper: Key = {0}, Value = {1}".format (key, value)
				if key == 'parseInstruction':
					parseInstruction = scraperRow.attrib.get('parseInstruction')
					if(parseInstruction != None and parseInstruction != ''):
						if(not os.path.isabs(parseInstruction)):
							#if it is a relative path, search in RCBs home directory
							parseInstruction = os.path.join(util.RCBHOME, 'resources', 'scraper', parseInstruction)

						if(not os.path.isfile(parseInstruction)):
							Logutil.log('Configuration error. parseInstruction file %s does not exist.' %parseInstruction, util.LOG_LEVEL_ERROR)
							# FIXME TODO continue, skipping this scraper
							return None, util.localize(32005)

						scraper.parseInstruction = parseInstruction
				elif key == 'returnUrl':
					setattr(scraper, key, value.upper() == "TRUE")
				else:
					setattr(scraper, key, value)
			
			scrapers.append(scraper)
			
		site.scrapers = scrapers
			
		return site, ''
	
	# Return a populated FileType object for a given name
	def readFileType(self, name, tree):

		fileTypeRow = None

		for element in tree.findall('FileTypes/FileType'):
			if(element.attrib.get('name') == name):
				fileTypeRow = element
				break
			
		if(fileTypeRow == None):
			Logutil.log('Configuration error. FileType %s does not exist in config.xml' %name, util.LOG_LEVEL_ERROR)
			return None, util.localize(32005)
			
		fileType = FileType()
		for key, value in fileTypeRow.attrib.iteritems():
			#print "FileType: Key = {0}, Value = {1}".format (key, value)
			setattr(fileType, key, value)

		for child in fileTypeRow:
			#print "FileType: tag = {0}, value = {1}".format (child.tag, child.text)
			setattr(fileType, child.tag, child.text)

		return fileType, ''
		
	# Given imagePlacingInfo or imagePlacingMain, retrieve all the associated ImagePlacing/fileTypeFor elements
	def readImagePlacing(self, imagePlacingName, tree):
		fileTypeForRow = None
		for element in tree.findall('ImagePlacing/fileTypeFor'):
			if(element.attrib.get('name') == imagePlacingName):
				fileTypeForRow = element
				break
		
		if(fileTypeForRow == None):
			Logutil.log('Configuration error. ImagePlacing/fileTypeFor %s does not exist in config.xml' %str(imagePlacingName), util.LOG_LEVEL_ERROR)
			return None, util.localize(32005)
		
		imagePlacing = ImagePlacing()
		imagePlacing.name = imagePlacingName

		for child in fileTypeForRow:
			ftype, msg = self.readFileType(child.text, tree)
			# Since the class variable names are a list, they are called fileTypesForXXX
			# Meanwhile, the XML config file we are reading has each tag as fileTypeForXXX
			varname = child.tag.replace('fileTypeFor', 'fileTypesFor')
			try:
				# Read the existing list, append and write back
				ftypes = getattr(imagePlacing, varname)
				ftypes.append (ftype)
				setattr(imagePlacing, varname, ftypes)
			except AttributeError as e:
				Logutil.log("Error for attribute {0}: {1}".format (varname, str(e)), util.LOG_LEVEL_WARNING)

		return imagePlacing, ''
	
	def readMissingFilter(self, filterName, tree):
		missingFilter = MissingFilter()
		missingFilter.andGroup = []
		missingFilter.orGroup = []
		if(tree != None):
			missingFilterRow = tree.find(filterName)
			if(missingFilterRow != None):
				missingFilter.andGroup = self.getMissingFilterItems(missingFilterRow, 'andGroup')
				missingFilter.orGroup = self.getMissingFilterItems(missingFilterRow, 'orGroup')
		
		return missingFilter		
	
	def getMissingFilterItems(self, missingFilterRow, groupName):
		items = []
		groupRow = missingFilterRow.find(groupName)
		if(groupRow != None):
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
			if(fileType != None):
				fileTypeIds.append(fileType.id)

		return fileTypeIds
	
	
	def readTextElement(self, parent, elementName):
		element = parent.find(elementName)
		if(element != None and element.text != None):
			Logutil.log('%s: %s' %(elementName, element.text), util.LOG_LEVEL_INFO)
			return element.text
		else:
			return ''