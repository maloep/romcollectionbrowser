
import os
import xbmc, xbmcgui, xbmcvfs

from xml.etree.ElementTree import *
import config, helper
from configxmlwriter import *
from emulatorautoconfig.autoconfig import EmulatorAutoconfig
from util import Logutil as log

RETRIEVE_INFO_ARTWORK_ONLINE = 0     # Game description and artwork need to be downloaded
RETRIEVE_INFO_ARTWORK_LOCALLY = 1    # Game description and artwork already exist locally

GAME_DESCRIPTION_PER_FILE = 0
GAME_DESCRIPTION_SINGLE_FILE = 1     # All game descriptions in a single file, e.g. MAME history.dat
GAME_DESCRIPTION_ONLINE = 2          # Game descriptions to be retrieved from online source


class ConfigXmlWizard(object):
	# FIXME TODO Duplicated in dialogeditromcollection.py. Need a class to handle these, possibly config.py?
	@property
	def current_os(self):
		os = ''
		# FIXME TODO Add other platforms
		# Map between Kodi's platform name (defined in http://kodi.wiki/view/List_of_boolean_conditions)
		# and the os name in emu_autoconfig.xml
		platforms = ('System.Platform.Android',
					 'System.Platform.OSX',
					 'System.Platform.Windows',
					 'System.Platform.Linux')
		try:
			for platform in platforms:
				if xbmc.getCondVisibility(platform):
					os = platform.split('.')[-1]
					break
		except Exception as err:
			pass
		return os

	def createConfigXml(self, configFile):
				
		id = 1		
		consoleList = sorted(config.consoleDict.keys())
				
		success, romCollections = self.addRomCollections(id, None, consoleList, False)
		if(not success):
			log.info("Action canceled. Config.xml will not be written")
			return False, util.localize(32172)
				
		configWriter = ConfigXmlWriter(True)
		success, message = configWriter.writeRomCollections(romCollections, False)
			
		return success, message
	
	
	def addRomCollection(self, configObj):
		Logutil.log("Begin addRomCollection" , util.LOG_LEVEL_INFO)
		
		consoleList = sorted(config.consoleDict.keys())
		id = 1
		
		rcIds = configObj.romCollections.keys()
		rcIds.sort()
		#read existing rom collection ids and names
		for rcId in rcIds:				
			
			#remove already configured consoles from the list			
			if(configObj.romCollections[rcId].name in consoleList):
				consoleList.remove(configObj.romCollections[rcId].name)
			#find highest id
			if(int(rcId) > int(id)):
				id = rcId
								
		id = int(id) +1
		
		success, romCollections = self.addRomCollections(id, configObj, consoleList, True)
		if(not success):
			log.info("Action canceled. Config.xml will not be written")
			return False, util.localize(32172)
				
		configWriter = ConfigXmlWriter(False)
		success, message = configWriter.writeRomCollections(romCollections, False)

		log.info("End addRomCollection")
		return success, message

	def promptEmulatorParams(self, defaultValue):
		""" Ask the user to enter emulator parameters """
		keyboard = xbmc.Keyboard()
		keyboard.setDefault(defaultValue)
		keyboard.setHeading(util.localize(32179))
		keyboard.doModal()
		if keyboard.isConfirmed():
			emuParams = keyboard.getText()
			log.info("emuParams: " + str(emuParams))
			return emuParams
		else:
			log.info("No emuParams selected. Action canceled.")
			return ''

	def promptOtherConsoleName(self):
		"""  Ask the user to enter a (other) console name """
		keyboard = xbmc.Keyboard()
		keyboard.setHeading(util.localize(32177))
		keyboard.doModal()
		if keyboard.isConfirmed():
			console = keyboard.getText()
			log.info("Platform entered manually: " + console)
			return console
		else:
			log.info("No Platform entered. Action canceled.")
			return ''

	def promptEmulatorFileMasks(self):
		keyboard = xbmc.Keyboard()
		keyboard.setHeading(util.localize(32181))
		keyboard.doModal()
		if keyboard.isConfirmed():
			fileMaskInput = keyboard.getText()
			log.info("fileMask: " + str(fileMaskInput))
			fileMasks = fileMaskInput.split(',')
			return fileMasks
		else:
			log.info("No fileMask selected. Action canceled.")
			return []

	def promptRomPath(self, consolename):
		""" Prompt the user to browse to the rompath """
		dialog = xbmcgui.Dialog()
		# http://kodi.wiki/view/Add-on_unicode_paths
		romPath = dialog.browse(0, util.localize(32180) % consolename, 'files').decode('utf-8')
		log.debug(u"rompath selected: {0}".format(romPath))

		return romPath

	def promptArtworkPath(self, console, startingDirectory):
		""" Prompt the user to browse to the artwork path """
		dialog = xbmcgui.Dialog()
		# http://kodi.wiki/view/Add-on_unicode_paths
		artworkPath = dialog.browse(0, util.localize(32193) % console, 'files', '', False, False, startingDirectory).decode('utf-8')
		log.debug(u"artworkPath selected: {0}".format(artworkPath))

		return artworkPath

	def doesSupportRetroplayer(self, romCollectionName):
		supportsRetroPlayer = True
		# If we have full python integration we can also check if specific platform supports RetroPlayer
		if helper.retroPlayerSupportsPythonIntegration():
			supportsRetroPlayer = False
			success, installedAddons = helper.readLibretroCores("all", True, romCollectionName)
			if success and len(installedAddons) > 0:
				supportsRetroPlayer = True
			else:
				success, installedAddons = helper.readLibretroCores("uninstalled", False, romCollectionName)
				if success and len(installedAddons) > 0:
					supportsRetroPlayer = True

		return supportsRetroPlayer

	def addRomCollections(self, id, configObj, consoleList, isUpdate):
		
		romCollections = {}
		dialog = xbmcgui.Dialog()
		
		# Scraping scenario - game descriptions and artwork retrieved from online or available locally
		scenarioIndex = dialog.select(util.localize(32173), [util.localize(32174), util.localize(32175)])
		log.info("scenarioIndex: " + str(scenarioIndex))
		if scenarioIndex == -1:
			del dialog
			log.info("No scenario selected. Action canceled.")
			return False, romCollections
		
		autoconfig = EmulatorAutoconfig(util.getEmuAutoConfigPath())
		
		while True:
					
			fileTypeList, errorMsg = self.buildMediaTypeList(configObj, isUpdate)
			romCollection = RomCollection()
			
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
			romCollection.id = id
			id = id +1
			

			#check if we have general RetroPlayer support
			if helper.isRetroPlayerSupported():
				if self.doesSupportRetroplayer(romCollection.name):
					romCollection.useBuiltinEmulator = dialog.yesno(util.localize(32999), util.localize(32198))
			
			#only ask for emulator and params if we don't use builtin emulator
			if(not romCollection.useBuiltinEmulator):
				
				#maybe there is autoconfig support
				preconfiguredEmulator = None
				
				#emulator
				if romCollection.name in ['Linux', 'Macintosh', 'Windows']:
					# Check for standalone games
					romCollection.emulatorCmd = '"%ROM%"'
					log.info("emuCmd set to '%ROM%' for standalone games.")

				else:
					emulist = []

					log.info(u'Running on {0}. Trying to find emulator per autoconfig.'.format(self.current_os))
					emulators = autoconfig.findEmulators(self.current_os, romCollection.name, True)
					for emulator in emulators:
						if emulator.isInstalled:
							emulist.append(util.localize(32202) % emulator.name)
						else:
							emulist.append(emulator.name)

					# Ask the user which one they want
					if len(emulist) > 0:
						try:
							emuIndex = dialog.select(util.localize(32203), emulist)
							preconfiguredEmulator = emulators[emuIndex]
						except:
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

			if scenarioIndex == RETRIEVE_INFO_ARTWORK_ONLINE:
				# Prompt for artwork path
				artworkPath = self.promptArtworkPath(console, romPath)
				if artworkPath == '':
					log.info("No artworkPath selected. Action canceled.")
					break
				
				romCollection.descFilePerGame = True
				
				# Media Paths
				romCollection.mediaPaths = []

				if romCollection.name == 'MAME':
					mediaTypes = ['boxfront', 'action', 'title', 'cabinet', 'marquee']
				else:
					mediaTypes = ['boxfront', 'boxback', 'cartridge', 'screenshot', 'fanart']
				for t in mediaTypes:
					romCollection.mediaPaths.append(self.createMediaPath(t, artworkPath, scenarioIndex))
				
				# Other MAME specific properties
				if(romCollection.name == 'MAME'):
					# FIXME TODO MAWS not available anymore, shouldn't allow online scraper for MAME
					# Create MAWS scraper
					site = Site(name='maws.mameworld.info')
					site.scrapers = [Scraper(parseInstruction='06 - maws.xml', source='http://maws.mameworld.info/maws/romset/%GAME%')]
					romCollection.scraperSites = [site]
			else:
				romCollection.mediaPaths = []

				# Default to looking in the romPath for the first artwork path
				lastArtworkPath = romPath
				while True:
					
					fileTypeIndex = dialog.select(util.localize(32183), fileTypeList)
					Logutil.log('fileTypeIndex: ' +str(fileTypeIndex), util.LOG_LEVEL_INFO)					
					if(fileTypeIndex == -1):
						log.info("No fileTypeIndex selected.")
						break
					
					fileType = fileTypeList[fileTypeIndex]
					fileTypeList.remove(fileType)
					artworkPath = dialog.browse(0, util.localize(32182) %(console, fileType), 'files', '', False, False, lastArtworkPath)
					
					try:
						unicode(artworkPath)
					except:
						log.info("RCB can't access your artwork path. Make sure it does not contain any non-ascii characters.")
						xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32042), errorMsg)
						break
					
					lastArtworkPath = artworkPath
					Logutil.log('artworkPath: ' +str(artworkPath), util.LOG_LEVEL_INFO)
					if(artworkPath == ''):
						log.info("No artworkPath selected.")
						break
					
					romCollection.mediaPaths.append(self.createMediaPath(fileType, artworkPath, scenarioIndex))

					# Ask to add another artwork path
					if not dialog.yesno(util.localize(32999), util.localize(32184)):
						break

				# Ask user for source of game descriptions (description file per game or for all games, or online/local NFO)
				descIndex = dialog.select(util.localize(32185), [util.localize(32186), util.localize(32187), util.localize(32188)])
				Logutil.log('descIndex: ' +str(descIndex), util.LOG_LEVEL_INFO)
				if(descIndex == -1):
					log.info("No descIndex selected. Action canceled.")
					break
				
				romCollection.descFilePerGame = (descIndex != GAME_DESCRIPTION_SINGLE_FILE)
				
				if descIndex == GAME_DESCRIPTION_ONLINE:
					# Leave scraperSites empty - they will be filled in configwriter
					pass
				
				else:
					descPath = ''
					
					if(romCollection.descFilePerGame):
						#get path
						pathValue = dialog.browse(0, util.localize(32189) %console, 'files')
						if(pathValue == ''):
							break
						
						#get file mask
						keyboard = xbmc.Keyboard()
						keyboard.setHeading(util.localize(32190))
						keyboard.setDefault('%GAME%.txt')
						keyboard.doModal()
						if (keyboard.isConfirmed()):
							filemask = keyboard.getText()
							
						descPath = util.joinPath(pathValue, filemask.strip())
					else:
						descPath = dialog.browse(1, util.localize(32189) %console, 'files', '', False, False, lastArtworkPath)

					log.info("descPath: " + str(descPath))
					if(descPath == ''):
						log.info("No descPath selected. Action canceled.")
						break
					
					parserPath = dialog.browse(1, util.localize(32191) %console, 'files', '', False, False, descPath)
					log.info("parserPath: " + str(parserPath))
					if(parserPath == ''):
						log.info("No parserPath selected. Action canceled.")
						break
					
					# Create scraper
					site = Site(name=console, descFilePerGame=(descIndex == GAME_DESCRIPTION_PER_FILE), searchGameByCRC=True)
					site.scrapers = [Scraper(parseInstruction=parserPath, source=descPath, encoding='iso-8859-1')]
					romCollection.scraperSites = [site]

			log.debug("Created new rom collection: {0}".format(romCollection))

			romCollections[romCollection.id] = romCollection

			# Ask the user if they want to add another rom collection
			if not dialog.yesno(util.localize(32999), util.localize(32192)):
				break
		
		del dialog
		
		return True, romCollections
	
	
	
	def buildMediaTypeList(self, configObj, isUpdate):
		#build fileTypeList
		fileTypeList = []
		
		if(isUpdate):
			fileTypes = configObj.tree.findall('FileTypes/FileType')
		else:
			#build fileTypeList
			configFile = util.joinPath(util.getAddonInstallPath(), 'resources', 'database', 'config_template.xml')
	
			if(not xbmcvfs.exists(configFile)):
				log.error("File config_template.xml does not exist. Place a valid config file here: " + str(configFile))
				return None, util.localize(32040)
			
			tree = ElementTree().parse(configFile)			
			fileTypes = tree.findall('FileTypes/FileType')			
			
		for fileType in fileTypes:
			name = fileType.attrib.get('name')
			if(name != None):
				type = fileType.find('type')				
				if(type != None and type.text == 'video'):
					name = name +' (video)'
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
		if scenarioIndex == RETRIEVE_INFO_ARTWORK_ONLINE:
			mediaPath.path = util.joinPath(path, mediatype, fileMask)
		else:
			mediaPath.path = util.joinPath(path, fileMask)
				
		return mediaPath
