import os

import util
from util import *
from elementtree.ElementTree import *



class Console:
	name = ''
	id = -1
	emulatorCmd = ''
	xboxCreateShortcut = ''
	xboxCreateShortcutAddRomfile = ''
	xboxCreateShortcutUseShortGamename = ''
	
class FileType:
	name = ''
	id = -1
	type = ''
	parent = ''
	
class FileTypeFor:
	name = ''	
	fileType = None
	
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
	name = ''	
	console = None	
	romPaths = None
	mediaPaths = None
	scraperSites = None
	imagePlacing = None	
	ignoreOnScan = False
	allowUpdate = True	
	searchGameByCRC = True
	searchGameByCRCIgnoreRomName = False
	useFoldernameAsCRC = False
	useFilenameAsCRC = False
	maxFolderDepth = 99
	ignoreGameWithoutDesc = False	
	descFilePerGame = False
	diskPrefix = '_Disk'


class Config:
		
	romCollections = None
		
	
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
		return True, ''
		
		
	def readRomCollections(self, tree):
		
		romCollections = []
		
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
			
			#Console
			consoleRow = romCollectionRow.find('console')
			if(consoleRow == None):
				Logutil.log('Configuration error. RomCollection %s does not contain a console' %romCollection.name, util.LOG_LEVEL_ERROR)
				return None, 'Configuration error. See xbmc.log for details'
			
			console, errorMsg = self.readConsole(consoleRow.text, tree)
			if(console == None):
				return None, errorMsg
			
			romCollection.console = console
			
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
				if(siteName == ''):
					Logutil.log('Configuration error. RomCollection/scraper must have an attribute name', util.LOG_LEVEL_ERROR)
					return None, 'Configuration error. See xbmc.log for details'
				scraper, errorMsg = self.readScraper(siteName, tree)
				if(scraper == None):
					return None, errorMsg
				romCollection.scraperSites.append(scraper)
				
			#imagePlacing
			romCollection.imagePlacing = []
			imagePlacingRow = romCollectionRow.find('imagePlacing')
			if(imagePlacingRow != None):
				fileTypeFor, errorMsg = self.readFileTypeFor(imagePlacingRow.text, tree)
				if(fileTypeFor == None):
					return None, errorMsg
				
				romCollection.imagePlacing = fileTypeFor
			
			#all simple RomCollection properties
			ignoreOnScan = romCollectionRow.find('ignoreOnScan')
			if(ignoreOnScan != None):
				romCollection.ignoreOnScan = ignoreOnScan.text.upper() == 'TRUE'
				
			allowUpdate = romCollectionRow.find('allowUpdate')
			if(allowUpdate != None):
				romCollection.allowUpdate = allowUpdate.text.upper() == 'TRUE'
				
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
									
			romCollections.append(romCollection)
		
		return romCollections, ''
		
		
	def readConsole(self, consoleName, tree):
		
		consoleRow = tree.find('Consoles/Console[@name="%s"]'%consoleName)
		if(consoleRow == None):
			Logutil.log('Configuration error. Console %s does not exist in config.xml' %consoleName, util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'
		
		console = Console()
		console.name = consoleName
		
		id = consoleRow.attrib.get('id')
		if(id == ''):
			Logutil.log('Configuration error. Console %s must have an id' %consoleName, util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'

		console.id = id
		
		emulatorCmd = consoleRow.find('emulatorCmd')
		if(emulatorCmd != None):
			console.emulatorCmd = emulatorCmd.text
			
		xboxCreateShortcut = consoleRow.find('xboxCreateShortcut')
		if(xboxCreateShortcut != None):
			console.xboxCreateShortcut = xboxCreateShortcut.text.upper() == 'TRUE'
			
		xboxCreateShortcutAddRomfile = consoleRow.find('xboxCreateShortcutAddRomfile')
		if(xboxCreateShortcutAddRomfile != None):
			console.xboxCreateShortcutAddRomfile = xboxCreateShortcutAddRomfile.text.upper() == 'TRUE'
			
		xboxCreateShortcutUseShortGamename = consoleRow.find('xboxCreateShortcutUseShortGamename')
		if(xboxCreateShortcutUseShortGamename != None):
			console.xboxCreateShortcutUseShortGamename = xboxCreateShortcutUseShortGamename.text.upper() == 'TRUE'
		
		#TODO write console to database
		return console, ''
		
			
	def readScraper(self, siteName, tree):
		siteRow = tree.find('Scrapers/Site[@name="%s"]' %siteName)
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
					parseInstruction = os.path.join(os.getcwd(), '..', 'scraper', parseInstruction)
				
				if(not os.path.isfile(parseInstruction)):
					Logutil.log('Configuration error. parseInstruction file %s does not exist.' %parseInstruction, util.LOG_LEVEL_ERROR)
					return None, 'Configuration error. See xbmc.log for details'
				
				scraper.parseInstruction = parseInstruction
				
			source = scraperRow.attrib.get('source')
			if(source != None and source != ''):
				scraper.source = source
				
			returnUrl = scraperRow.attrib.get('returnUrl')
			if(returnUrl != None and returnUrl != ''):
				scraper.returnUrl = returnUrl.upper() == 'TRUE'
				
			replaceKeyString = scraperRow.attrib.get('replaceKeyString')
			if(replaceKeyString != None and replaceKeyString != ''):
				scraper.replaceKeyString = replaceKeyString
				
			replaceValueString = scraperRow.attrib.get('replaceValueString')
			if(replaceValueString != None and replaceValueString != ''):
				scraper.replaceValueString = replaceValueString
			
			scrapers.append(scraper)
			
		site.scrapers = scrapers
			
		return site, ''
	
	
	def readFileType(self, name, tree):
		fileTypeRow = tree.find('FileTypes/FileType[@name="%s"]' %name)
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
		
		
	def readFileTypeFor(self, imagePlacing, tree):
		fileTypeForRow = tree.find('ImagePlacing/fileTypeFor[@name="%s"]' %imagePlacing)
		
		if(fileTypeForRow == None):
			Logutil.log('Configuration error. ImagePlacing/fileTypeFor %s does not exist in config.xml' %imagePlacing, util.LOG_LEVEL_ERROR)
			return None, 'Configuration error. See xbmc.log for details'
		
		fileTypeForList = []
		for element in fileTypeForRow:
			fileTypeFor = FileTypeFor()
			fileTypeFor.name = element.tag
			fileType, errorMsg = self.readFileType(element.text, tree)
			if(fileType == None):
				return None, errorMsg
			fileTypeFor.fileType = fileType
			fileTypeForList.append(fileTypeFor)
			
		return fileTypeForList, ''
		