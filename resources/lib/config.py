import os

import util
from util import *
from elementtree.ElementTree import *


consoleList = ['3DO',
			'Amiga',
			'Amiga CD32',
			'Amstrad CPC',
			'Apple II',
			'Atari 2600',
			'Atari 5200',
			'Atari 7800',
			'Atari 8-bit',
			'Atari ST',
			'SNES',
			'Sega 32']


#key, mobygames-id
consoleDict = {'3DO' : '1',
			'Amiga' : '2',
			'Amiga CD32' : '3',
			'Amstrad CPC' : '4',
			'Apple II' : '5',
			'Atari 2600' : '6',
			'Atari 5200' : '7',
			'Atari 7800' : '8',
			'Atari 8-bit' : '9',
			'Atari ST' : '10',
			'SNES' : '15',
			'Sega 32' : '21'}


class FileType:
	name = ''
	id = -1
	type = ''
	parent = ''
	
class ImagePlacing:
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
	fileTypesForMainViewVideoWindowBig = None
	fileTypesForMainViewVideoWindowSmall = None
	fileTypesForMainViewVideoFullscreen = None
	
	fileTypesForGameInfoViewBackground = None
	fileTypesForGameInfoViewGamelist = None
	fileTypesForGameInfoView1 = None
	fileTypesForGameInfoView2 = None
	fileTypesForGameInfoView3 = None
	fileTypesForGameInfoView4 = None
	fileTypesForGameInfoViewVideoWindow = None
	
class MediaPath:
	path = ''
	fileType = None
	
class Scraper:
	parseInstruction = ''
	source = ''
	returnUrl = False
	replaceKeyString = ''
	replaceValueString = ''
	
class Site:
	name = ''
	scrapers = None

class RomCollection:
	id = -1
	name = ''
	
	emulatorCmd = ''
	emulatorParams = ''
	romPaths = None
	mediaPaths = None
	scraperSites = None
	imagePlacing = None	
	ignoreOnScan = False
	allowUpdate = True
	fullReimport = False
	createNfoWhileScraping = True
	searchGameByCRC = True
	searchGameByCRCIgnoreRomName = False
	useFoldernameAsCRC = False
	useFilenameAsCRC = False
	useFoldernameAsGamename = False
	maxFolderDepth = 99
	ignoreGameWithoutDesc = False	
	descFilePerGame = False
	diskPrefix = '_Disk'
	xboxCreateShortcut = False
	xboxCreateShortcutAddRomfile = False
	xboxCreateShortcutUseShortGamename = False


class Config:
		
	romCollections = None
	fileTypeIdsForGamelist = None
		
	
	def readXml(self):
		configFile = util.getConfigXmlPath()		
		
		if(not os.path.isfile(configFile)):
			Logutil.log('File config.xml does not exist. Place a valid config file here: ' +str(configFile), util.LOG_LEVEL_ERROR)
			return False, 'Error: File config.xml does not exist'
		
		tree = ElementTree().parse(configFile)			
		if(tree == None):
			Logutil.log('Could not read config.xml', util.LOG_LEVEL_ERROR)
			return False, 'Could not read config.xml.'
		
		romCollections, errorMsg = self.readRomCollections(tree)
		if(romCollections == None):
			return False, errorMsg
		
		self.romCollections = romCollections
				
		self.fileTypeIdsForGamelist = self.getFileTypeIdsForGameList(romCollections)
		
		return True, ''
	
	
	def writeXml(self):
		
		configFile = util.getConfigXmlPath()
		
		root = Element('config')
		romCollectionsXml = SubElement(root, 'RomCollections')
		fileTypesXml = SubElement(root, 'FileTypes')
		imagePlacingXml = SubElement(root, 'ImagePlacing')
		scrapersXml = SubElement(root, 'Scrapers')
		
		for romCollection in self.romCollections.values():
			romCollectionXml = SubElement(romCollectionsXml, 'RomCollection', {'id' : str(romCollection.id), 'name' : romCollection.name})
			SubElement(romCollectionXml, 'emulatorCmd').text = romCollection.emulatorCmd
			SubElement(romCollectionXml, 'emulatorParams').text = romCollection.emulatorParams
			
			for romPath in romCollection.romPaths:
				SubElement(romCollectionXml, 'romPath').text = str(romPath)
				
			for mediaPath in romCollection.mediaPaths:								
				SubElement(romCollectionXml, 'mediaPath', {'type' : mediaPath.type.name}).text = mediaPath.path
				
			#some default values
			SubElement(romCollectionXml, 'ignoreOnScan').text = 'False'
			SubElement(romCollectionXml, 'searchGameByCRC').text = 'True'
			SubElement(romCollectionXml, 'descFilePerGame').text = 'True'
				
			SubElement(romCollectionXml, 'imagePlacing').text = 'gameinfobig'
			
			mobyConsoleId = '0'
			try:
				mobyConsoleId = consoleDict[romCollection.name]
			except:
				pass
						
			SubElement(romCollectionXml, 'scraper', {'name' : 'thevideogamedb.com'})
			SubElement(romCollectionXml, 'scraper', {'name' : 'thegamesdb.net', 'replaceKeyString' : ' III, II', 'replaceValueString' : ' 3, 2'})
			SubElement(romCollectionXml, 'scraper', {'name' : 'giantbomb.com', 'replaceKeyString' : ' III, II', 'replaceValueString' : ' 3, 2'})
			SubElement(romCollectionXml, 'scraper', {'name' : 'mobygames.com', 'replaceKeyString' : ' III, II', 'replaceValueString' : ' 3, 2', 'platform' : mobyConsoleId})
			
		self.writeFileType(fileTypesXml, '1', 'boxfront')
		self.writeFileType(fileTypesXml, '2', 'boxback')
		self.writeFileType(fileTypesXml, '3', 'cartridge')
		self.writeFileType(fileTypesXml, '4', 'screenshot')
		self.writeFileType(fileTypesXml, '5', 'fanart')
			
		fileTypeFor = SubElement(imagePlacingXml, 'fileTypeFor', {'name' : 'gameinfobig'})
		SubElement(fileTypeFor, 'fileTypeForGameList').text = 'boxfront'
		SubElement(fileTypeFor, 'fileTypeForGameList').text = 'screenshot'
		SubElement(fileTypeFor, 'fileTypeForGameListSelected').text = 'boxfront'
		SubElement(fileTypeFor, 'fileTypeForGameListSelected').text = 'screenshot'
		SubElement(fileTypeFor, 'fileTypeForMainViewBackground').text = 'fanart'
		SubElement(fileTypeFor, 'fileTypeForMainViewBackground').text = 'boxfront'
		SubElement(fileTypeFor, 'fileTypeForMainViewBackground').text = 'screenshot'
		SubElement(fileTypeFor, 'fileTypeForMainViewGameInfoBig').text = 'screenshot'
		SubElement(fileTypeFor, 'fileTypeForMainViewGameInfoBig').text = 'boxfront'
		SubElement(fileTypeFor, 'fileTypeForGameInfoViewBackground').text = 'fanart'
		SubElement(fileTypeFor, 'fileTypeForGameInfoViewBackground').text = 'boxfront'
		SubElement(fileTypeFor, 'fileTypeForGameInfoViewBackground').text = 'screenshot'
		SubElement(fileTypeFor, 'fileTypeForGameInfoViewGamelist').text = 'boxfront'
		SubElement(fileTypeFor, 'fileTypeForGameInfoViewGamelist').text = 'screenshot'
		SubElement(fileTypeFor, 'fileTypeForGameInfoView1').text = 'boxfront'
		SubElement(fileTypeFor, 'fileTypeForGameInfoView2').text = 'boxback'
		SubElement(fileTypeFor, 'fileTypeForGameInfoView3').text = 'cartridge'
		SubElement(fileTypeFor, 'fileTypeForGameInfoView4').text = 'screenshot'
		
		#Scrapers
		#local nfo
		site = SubElement(scrapersXml, 'Site', {'name' : 'local nfo'})
		SubElement(site, 'Scraper', {'parseInstruction' : '00 - local nfo.xml', 'source' : 'nfo'})
		
		#thevideogamedb.com
		site = SubElement(scrapersXml, 'Site', {'name' : 'thevideogamedb.com'})
		SubElement(site, 'Scraper', {'parseInstruction' : '01 - thevideogamedb.xml', 'source' : 'http://thevideogamedb.com/API/GameDetail.aspx?apikey=%VGDBAPIKey%&crc=%CRC%'})		
		
		site = SubElement(scrapersXml, 'Site', {'name' : 'thegamesdb.net'})
		SubElement(site, 'Scraper', {'parseInstruction' : '02 - thegamesdb.xml', 'source' : 'http://thegamesdb.net/api/GetGame.php?name=%GAME%'})
		
		#giantbomb.com
		site = SubElement(scrapersXml, 'Site', {'name' : 'giantbomb.com'})
		SubElement(site, 'Scraper', {'parseInstruction' : '03.01 - giantbomb - search.xml', 'source' : 'http://api.giantbomb.com/search/?api_key=%GIANTBOMBAPIKey%&amp;query=%GAME%&resources=game&field_list=api_detail_url,name&format=xml',
									'returnUrl' : 'true', 'replaceKeyString' : '%REPLACEKEYS%', 'replaceValueString' : '%REPLACEVALUES%'})
		SubElement(site, 'Scraper', {'parseInstruction' : '03.02 - giantbomb - detail.xml', 'source' : '1'})		
		
		#mobygames.com
		site = SubElement(scrapersXml, 'Site', {'name' : 'mobygames.com'})
		SubElement(site, 'Scraper', {'parseInstruction' : '04.01 - mobygames - gamesearch.xml', 'source' : 'http://www.mobygames.com/search/quick?game=%GAME%&p=%PLATFORM%',
									'returnUrl' : 'true', 'replaceKeyString' : '%REPLACEKEYS%', 'replaceValueString' : '%REPLACEVALUES%'})
		SubElement(site, 'Scraper', {'parseInstruction' : '04.02 - mobygames - details.xml', 'source' : '1'})				
		SubElement(site, 'Scraper', {'parseInstruction' : '04.03 - mobygames - coverlink.xml', 'source' : '1', 'returnUrl' : 'true'})
		SubElement(site, 'Scraper', {'parseInstruction' : '04.04 - mobygames - coverart.xml', 'source' : '2'})
		SubElement(site, 'Scraper', {'parseInstruction' : '04.05 - mobygames - screenshotlink.xml', 'source' : '1', 'returnUrl' : 'true'})
		SubElement(site, 'Scraper', {'parseInstruction' : '04.06 - mobygames - screenshotoriginallink.xml', 'source' : '3', 'returnUrl' : 'true'})
		SubElement(site, 'Scraper', {'parseInstruction' : '04.07 - mobygames - screenshots.xml', 'source' : '4'})
			
		#write file		
		try:
			util.indentXml(root)
			tree = ElementTree(root)			
			tree.write(configFile)
			
			return 2, ""
			
		except Exception, (exc):
			print("Error: Cannot write config.xml: " +str(exc))
			return -1, "Error: Cannot write config.xml: " +str(exc)
		
	
	def writeFileType(self, fileTypesXml, id, name):
		fileType = SubElement(fileTypesXml, 'FileType' , {'id' : id, 'name' : name})
		SubElement(fileType, 'type').text = 'image'
		SubElement(fileType, 'parent').text = 'game'
		
		
	def readRomCollections(self, tree):
		
		romCollections = {}
		
		romCollectionRows = tree.findall('RomCollections/RomCollection')
				
		"""	
		#TODO Find out how to check result of findall. None, len() and list() don't work
		if (len(list(romCollections)) == 0):
			Logutil.log('Configuration error. config.xml does not contain any RomCollections', util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'
		"""
			
		for romCollectionRow in romCollectionRows:
			
			romCollection = RomCollection()
			romCollection.name = romCollectionRow.attrib.get('name')
			if(romCollection.name == None):
				Logutil.log('Configuration error. RomCollection must have an attribute name', util.LOG_LEVEL_ERROR)
				return None, 'Configuration error. See xbmc.log for details'
			
			id = romCollectionRow.attrib.get('id')
			if(id == ''):
				Logutil.log('Configuration error. RomCollection %s must have an id' %romCollection.name, util.LOG_LEVEL_ERROR)
				return None, 'Configuration error. See xbmc.log for details'
			romCollection.id = id
			
			#romPath
			romCollection.romPaths = []
			romPathRows = romCollectionRow.findall('romPath')
			for romPathRow in romPathRows:
				romCollection.romPaths.append(romPathRow.text)
				
			#mediaPath
			romCollection.mediaPaths = []
			mediaPathRows = romCollectionRow.findall('mediaPath')
			for mediaPathRow in mediaPathRows:
				mediaPath = MediaPath()
				mediaPath.path = mediaPathRow.text
				fileType, errorMsg = self.readFileType(mediaPathRow.attrib.get('type'), tree)
				if(fileType == None):
					return None, errorMsg
				mediaPath.fileType = fileType
				
				romCollection.mediaPaths.append(mediaPath)
			
			#Scraper
			romCollection.scraperSites = []						
			scraperRows = romCollectionRow.findall('scraper')
			for scraperRow in scraperRows:
				siteName = scraperRow.attrib.get('name')
				if(siteName == None or siteName == ''):
					Logutil.log('Configuration error. RomCollection/scraper must have an attribute name', util.LOG_LEVEL_ERROR)
					return None, 'Configuration error. See xbmc.log for details'
				
				#read additional scraper properties
				platform = scraperRow.attrib.get('platform')
				if(platform == None):
					platform = ''
				replaceKeyString = scraperRow.attrib.get('replaceKeyString')
				if(replaceKeyString == None):
					replaceKeyString = ''
				replaceValueString = scraperRow.attrib.get('replaceValueString')
				if(replaceValueString == None):
					replaceValueString = ''
				
				scraper, errorMsg = self.readScraper(siteName, platform, replaceKeyString, replaceValueString, tree)
				if(scraper == None):
					return None, errorMsg
				romCollection.scraperSites.append(scraper)
				
			#imagePlacing
			romCollection.imagePlacing = []
			imagePlacingRow = romCollectionRow.find('imagePlacing')
			if(imagePlacingRow != None):
				fileTypeFor, errorMsg = self.readImagePlacing(imagePlacingRow.text, tree)
				if(fileTypeFor == None):
					return None, errorMsg
				
				romCollection.imagePlacing = fileTypeFor
			
			#all simple RomCollection properties
			emulatorCmd = romCollectionRow.find('emulatorCmd')
			if(emulatorCmd != None):
				romCollection.emulatorCmd = emulatorCmd.text
			
			emulatorParams = romCollectionRow.find('emulatorParams')
			if(emulatorParams != None):
				romCollection.emulatorParams = emulatorParams.text
			
			ignoreOnScan = romCollectionRow.find('ignoreOnScan')
			if(ignoreOnScan != None):
				romCollection.ignoreOnScan = ignoreOnScan.text.upper() == 'TRUE'
				
			allowUpdate = romCollectionRow.find('allowUpdate')
			if(allowUpdate != None):
				romCollection.allowUpdate = allowUpdate.text.upper() == 'TRUE'
			
			fullReimport = romCollectionRow.find('fullReimport')
			if(fullReimport != None):
				romCollection.fullReimport = fullReimport.text.upper() == 'TRUE'			
				
			createNfoWhileScraping = romCollectionRow.find('createNfoWhileScraping')
			if(createNfoWhileScraping != None):
				romCollection.createNfoWhileScraping = createNfoWhileScraping.text.upper() == 'TRUE'
				
			searchGameByCRC = romCollectionRow.find('searchGameByCRC')
			if(searchGameByCRC != None):
				romCollection.searchGameByCRC = searchGameByCRC.text.upper() == 'TRUE'
				
			searchGameByCRCIgnoreRomName = romCollectionRow.find('searchGameByCRCIgnoreRomName')
			if(searchGameByCRCIgnoreRomName != None):
				romCollection.searchGameByCRCIgnoreRomName = searchGameByCRCIgnoreRomName.text.upper() == 'TRUE'
				
			useFoldernameAsCRC = romCollectionRow.find('useFoldernameAsCRC')
			if(useFoldernameAsCRC != None):
				romCollection.useFoldernameAsCRC = useFoldernameAsCRC.text.upper() == 'TRUE'
				
			useFilenameAsCRC = romCollectionRow.find('useFilenameAsCRC')
			if(useFilenameAsCRC != None):
				romCollection.useFilenameAsCRC = useFilenameAsCRC.text.upper() == 'TRUE'
			
			useFoldernameAsGamename = romCollectionRow.find('useFoldernameAsGamename')
			if(useFoldernameAsGamename != None):
				romCollection.useFoldernameAsGamename = useFoldernameAsGamename.text.upper() == 'TRUE'	
			
			maxFolderDepth = romCollectionRow.find('maxFolderDepth')
			if(maxFolderDepth != None):
				romCollection.maxFolderDepth = int(maxFolderDepth.text)
				
			ignoreGameWithoutDesc = romCollectionRow.find('ignoreGameWithoutDesc')
			if(ignoreGameWithoutDesc != None):
				romCollection.ignoreGameWithoutDesc = ignoreGameWithoutDesc.text.upper() == 'TRUE'
				
			descFilePerGame = romCollectionRow.find('descFilePerGame')
			if(descFilePerGame != None):
				romCollection.descFilePerGame = descFilePerGame.text.upper() == 'TRUE'
				
			diskPrefix = romCollectionRow.find('diskPrefix')
			if(diskPrefix != None):
				romCollection.diskPrefix = diskPrefix.text							
				
			xboxCreateShortcut = romCollectionRow.find('xboxCreateShortcut')
			if(xboxCreateShortcut != None):
				romCollection.xboxCreateShortcut = xboxCreateShortcut.text.upper() == 'TRUE'
				
			xboxCreateShortcutAddRomfile = romCollectionRow.find('xboxCreateShortcutAddRomfile')
			if(xboxCreateShortcutAddRomfile != None):
				romCollection.xboxCreateShortcutAddRomfile = xboxCreateShortcutAddRomfile.text.upper() == 'TRUE'
				
			xboxCreateShortcutUseShortGamename = romCollectionRow.find('xboxCreateShortcutUseShortGamename')
			if(xboxCreateShortcutUseShortGamename != None):
				romCollection.xboxCreateShortcutUseShortGamename = xboxCreateShortcutUseShortGamename.text.upper() == 'TRUE'
									
			try:
				romCollections[id] = romCollection 
			except:
				return None, 'Error while adding RomCollection. Make sure that the id is unique'
		
		return romCollections, ''
		
			
	def readScraper(self, siteName, platform, inReplaceKeyString, inReplaceValueString, tree):
		
		#elementtree version 1.2.7 does not support xpath like this: Scrapers/Site[@name="%s"] 
		siteRow = None
		siteRows = tree.findall('Scrapers/Site')
		for element in siteRows:
			if(element.attrib.get('name') == siteName):
				siteRow = element
				break
		
		if(siteRow == None):
			Logutil.log('Configuration error. Site %s does not exist in config.xml' %siteName, util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'
		
		site = Site()
		site.name = siteName
		
		scrapers = []
		
		scraperRows = siteRow.findall('Scraper')
		for scraperRow in scraperRows:
			scraper = Scraper()
			
			parseInstruction = scraperRow.attrib.get('parseInstruction')
			if(parseInstruction != None and parseInstruction != ''):
				if(not os.path.isabs(parseInstruction)):
					#if it is a relative path, search in RCBs home directory
					parseInstruction = os.path.join(util.RCBHOME, 'resources', 'scraper', parseInstruction)
				
				if(not os.path.isfile(parseInstruction)):
					Logutil.log('Configuration error. parseInstruction file %s does not exist.' %parseInstruction, util.LOG_LEVEL_ERROR)
					return None, 'Configuration error. See xbmc.log for details'
				
				scraper.parseInstruction = parseInstruction
				
			source = scraperRow.attrib.get('source')
			if(source != None and source != ''):				
				scraper.source = source.replace('%PLATFORM%', platform)
				
			returnUrl = scraperRow.attrib.get('returnUrl')
			if(returnUrl != None and returnUrl != ''):
				scraper.returnUrl = returnUrl.upper() == 'TRUE'
				
			replaceKeyString = scraperRow.attrib.get('replaceKeyString')
			if(replaceKeyString != None and replaceKeyString != ''):
				scraper.replaceKeyString = replaceKeyString.replace('%REPLACEKEYS%', inReplaceKeyString)
				
			replaceValueString = scraperRow.attrib.get('replaceValueString')
			if(replaceValueString != None and replaceValueString != ''):
				scraper.replaceValueString = replaceValueString.replace('%REPLACEVALUES%', inReplaceValueString)
			
			scrapers.append(scraper)
			
		site.scrapers = scrapers
			
		return site, ''
	
	
	def readFileType(self, name, tree):
		fileTypeRow = None 
		fileTypeRows = tree.findall('FileTypes/FileType')
		for element in fileTypeRows:
			if(element.attrib.get('name') == name):
				fileTypeRow = element
				break
			
		if(fileTypeRow == None):
			Logutil.log('Configuration error. FileType %s does not exist in config.xml' %name, util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'
			
		fileType = FileType()
		fileType.name = name
		
		id = fileTypeRow.attrib.get('id')
		if(id == ''):
			Logutil.log('Configuration error. FileType %s must have an id' %name, util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'
			
		fileType.id = id
		
		type = fileTypeRow.find('type')
		if(type != None):
			fileType.type = type.text
			
		parent = fileTypeRow.find('parent')
		if(parent != None):
			fileType.parent = parent.text
			
		return fileType, ''
		
		
	def readImagePlacing(self, imagePlacing, tree):
		
		fileTypeForRow = None 
		fileTypeForRows = tree.findall('ImagePlacing/fileTypeFor')
		for element in fileTypeForRows:
			if(element.attrib.get('name') == imagePlacing):
				fileTypeForRow = element
				break
		
		if(fileTypeForRow == None):
			Logutil.log('Configuration error. ImagePlacing/fileTypeFor %s does not exist in config.xml' %imagePlacing, util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'
		
		imagePlacing = ImagePlacing()
			
		imagePlacing.fileTypesForGameList, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameList', tree)		
		imagePlacing.fileTypesForGameListSelected, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameListSelected', tree)
		imagePlacing.fileTypesForMainView1, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainView1', tree)
		imagePlacing.fileTypesForMainView2, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainView2', tree)
		imagePlacing.fileTypesForMainView3, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainView3', tree)
		imagePlacing.fileTypesForMainViewBackground, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewBackground', tree)
		imagePlacing.fileTypesForMainViewGameInfoBig, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoBig', tree)
		imagePlacing.fileTypesForMainViewGameInfoUpperLeft, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoUpperLeft', tree)
		imagePlacing.fileTypesForMainViewGameInfoUpperRight, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoUpperRight', tree)
		imagePlacing.fileTypesForMainViewGameInfoLowerLeft, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoLowerLeft', tree)
		imagePlacing.fileTypesForMainViewGameInfoLowerRight, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewGameInfoLowerRight', tree)
		imagePlacing.fileTypesForMainViewVideoWindowBig, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewVideoWindowBig', tree)
		imagePlacing.fileTypesForMainViewVideoWindowSmall, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewVideoWindowSmall', tree)
		imagePlacing.fileTypesForMainViewVideoFullscreen, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForMainViewVideoFullscreen', tree)
		
		imagePlacing.fileTypesForGameInfoViewBackground, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameInfoViewBackground', tree)
		imagePlacing.fileTypesForGameInfoViewGamelist, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameInfoViewGamelist', tree)
		imagePlacing.fileTypesForGameInfoView1, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameInfoView1', tree)
		imagePlacing.fileTypesForGameInfoView2, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameInfoView2', tree)
		imagePlacing.fileTypesForGameInfoView3, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameInfoView3', tree)
		imagePlacing.fileTypesForGameInfoView4, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameInfoView4', tree)
		imagePlacing.fileTypesForGameInfoViewVideoWindow, errorMsg = self.readFileTypeForElement(fileTypeForRow, 'fileTypeForGameInfoViewVideoWindow', tree)		
			
		return imagePlacing, ''
	
	
	def readFileTypeForElement(self, fileTypeForRow, key, tree):
		fileTypeList = []
		fileTypesForControl = fileTypeForRow.findall(key)		
		for fileTypeForControl in fileTypesForControl:						
				
			fileType, errorMsg = self.readFileType(fileTypeForControl.text, tree)
			if(fileType == None):
				return None, errorMsg
						
			fileTypeList.append(fileType)
				
		return fileTypeList, ''
		
	
	def getFileTypeIdsForGameList(self, romCollections):
		
		fileTypeIds = []
		for romCollection in romCollections.values():
			for fileType in romCollection.imagePlacing.fileTypesForGameList:				
				if(fileTypeIds.count(fileType.id) == 0):
					fileTypeIds.append(fileType.id)
			for fileType in romCollection.imagePlacing.fileTypesForGameListSelected:
				if(fileTypeIds.count(fileType.id) == 0):
					fileTypeIds.append(fileType.id)
			for fileType in romCollection.imagePlacing.fileTypesForMainViewVideoFullscreen:
				if(fileTypeIds.count(fileType.id) == 0):
					fileTypeIds.append(fileType.id)

		return fileTypeIds
	
	
	