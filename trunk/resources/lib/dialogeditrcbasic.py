import xbmc, xbmcgui

import os

import util, config
from util import *
from configxmlwriter import *

ACTION_EXIT_SCRIPT = (10,)
ACTION_CANCEL_DIALOG = ACTION_EXIT_SCRIPT + (9,)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_SAVE = 6000
CONTROL_BUTTON_CANCEL = 6010

CONTROL_LIST_ROMCOLLECTIONS = 5210
CONTROL_BUTTON_RC_DOWN = 5211
CONTROL_BUTTON_RC_UP = 5212

#Import Games
CONTROL_BUTTON_ROMPATH = 5240
CONTROL_BUTTON_FILEMASK = 5250
CONTROL_BUTTON_IGNOREONSCAN = 5330
CONTROL_BUTTON_ALLOWUPDATE = 5400
CONTROL_BUTTON_MAXFOLDERDEPTH = 5410
CONTROL_BUTTON_DISKINDICATOR = 5420
CONTROL_BUTTON_USEFOLDERASGAMENAME = 5430

#Import Game data
CONTROL_LIST_SCRAPER1 = 5290
CONTROL_LIST_SCRAPER2 = 5300
CONTROL_LIST_SCRAPER3 = 5310
CONTROL_LIST_MEDIATYPES = 5260
CONTROL_BUTTON_MEDIA_DOWN = 5261
CONTROL_BUTTON_MEDIA_UP = 5262
CONTROL_BUTTON_MEDIAPATH = 5270
CONTROL_BUTTON_MEDIAFILEMASK = 5280
CONTROL_BUTTON_REMOVEMEDIAPATH = 5490
CONTROL_BUTTON_ADDMEDIAPATH = 5500


#Browse Games
CONTROL_LIST_IMAGEPLACING = 5320

#Launch Games
CONTROL_BUTTON_EMUCMD = 5220
CONTROL_BUTTON_PARAMS = 5230
CONTROL_BUTTON_USEEMUSOLO = 5440
CONTROL_BUTTON_DONTEXTRACTZIP = 5450
CONTROL_BUTTON_SAVESTATEPATH = 5460
CONTROL_BUTTON_SAVESTATEMASK = 5470
CONTROL_BUTTON_SAVESTATEPARAMS = 5480

#Scrapers
CONTROL_LIST_SCRAPERS = 5600
CONTROL_BUTTON_SCRAPERS_DOWN = 5601
CONTROL_BUTTON_SCRAPERS_UP = 5602
CONTROL_BUTTON_SCRAPERNAME = 5510
CONTROL_BUTTON_GAMEDESCPATH = 5520
CONTROL_BUTTON_GAMEDESCMASK = 5530
CONTROL_BUTTON_PARSEINSTRUCTION = 5540
CONTROL_BUTTON_DESCPERGAME = 5550
CONTROL_BUTTON_SEARCHBYCRC = 5560
CONTROL_BUTTON_USEFOLDERASCRC = 5580
CONTROL_BUTTON_USEFILEASCRC = 5590
CONTROL_BUTTON_REMOVESCRAPER = 5610
CONTROL_BUTTON_ADDSCRAPER = 5620



class EditRCBasicDialog(xbmcgui.WindowXMLDialog):
		
	selectedControlId = 0
	selectedRomCollection = None
	selectedOfflineScraper = None
	romCollections = None
	scraperSites = None
	
	def __init__(self, *args, **kwargs):
		Logutil.log('init Edit RC Basic', util.LOG_LEVEL_INFO)
		
		self.gui = kwargs[ "gui" ]
		self.romCollections = self.gui.config.romCollections
		self.scraperSites = self.gui.config.scraperSites
		
		self.doModal()
	
	
	def onInit(self):
		Logutil.log('onInit Edit RC Basic', util.LOG_LEVEL_INFO)
		
		#Rom Collections
		Logutil.log('build rom collection list', util.LOG_LEVEL_INFO)
		romCollectionList = []
		for rcId in self.romCollections.keys():
			romCollection = self.romCollections[rcId]
			romCollectionList.append(romCollection.name)
		self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, romCollectionList)
		
		Logutil.log('build scraper lists', util.LOG_LEVEL_INFO)
		self.availableScrapers = self.getAvailableScrapers(False)
		self.addItemsToList(CONTROL_LIST_SCRAPER1, self.availableScrapers)
		self.addItemsToList(CONTROL_LIST_SCRAPER2, self.availableScrapers)
		self.addItemsToList(CONTROL_LIST_SCRAPER3, self.availableScrapers)
				
		Logutil.log('build scrapers list', util.LOG_LEVEL_INFO)
		scrapers = self.getAvailableScrapers(True)
		self.addItemsToList(CONTROL_LIST_SCRAPERS, scrapers)

		Logutil.log('build imagePlacing list', util.LOG_LEVEL_INFO)		
		self.imagePlacingList = []
		imagePlacingRows = self.gui.config.tree.findall('ImagePlacing/fileTypeFor')
		for imagePlacing in imagePlacingRows:
			Logutil.log('add image placing: ' +str(imagePlacing.attrib.get('name')), util.LOG_LEVEL_INFO)
			self.imagePlacingList.append(imagePlacing.attrib.get('name'))
		self.addItemsToList(CONTROL_LIST_IMAGEPLACING, self.imagePlacingList)
		
		self.updateRomCollectionControls()
		
		self.updateOfflineScraperControls()
		
		
	def onAction(self, action):		
		if (action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
		
	
	def onClick(self, controlID):
		
		Logutil.log('onClick', util.LOG_LEVEL_INFO)
		
		if (controlID == CONTROL_BUTTON_EXIT): # Close window button
			Logutil.log('close', util.LOG_LEVEL_INFO)
			self.close()
		#OK
		elif (controlID == CONTROL_BUTTON_SAVE):
			Logutil.log('save', util.LOG_LEVEL_INFO)
			#store selectedRomCollection
			if(self.selectedRomCollection != None):
				self.updateSelectedRomCollection()
				self.romCollections[self.selectedRomCollection.id] = self.selectedRomCollection
				
			#store selectedOfflineScraper
			if(self.selectedOfflineScraper != None):
				self.updateSelectedOfflineScraper()				
				self.scraperSites[self.selectedOfflineScraper.name] = self.selectedOfflineScraper
						
			configWriter = ConfigXmlWriter(False)
			success, message = configWriter.writeRomCollections(self.romCollections, True)
			
			success, message = configWriter.writeScrapers(self.scraperSites)
			
			self.close()
		#Cancel
		elif (controlID == CONTROL_BUTTON_CANCEL):
			self.close()
		#Rom Collection list
		elif(self.selectedControlId in (CONTROL_BUTTON_RC_DOWN, CONTROL_BUTTON_RC_UP)):						
						
			if(self.selectedRomCollection != None):
				#save current values to selected Rom Collection
				self.updateSelectedRomCollection()
				
				#store previous selectedRomCollections state
				self.romCollections[self.selectedRomCollection.id] = self.selectedRomCollection
			
			#HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			self.updateRomCollectionControls()
		
		#Media Path
		elif(self.selectedControlId in (CONTROL_BUTTON_MEDIA_DOWN, CONTROL_BUTTON_MEDIA_UP)):						
						
			#HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			self.updateMediaPathControls()
		
		#Offline Scraper
		elif(self.selectedControlId in (CONTROL_BUTTON_SCRAPERS_UP, CONTROL_BUTTON_SCRAPERS_DOWN)):
			
			if(self.selectedOfflineScraper != None):
				#save current values to selected ScraperSite
				self.updateSelectedOfflineScraper()
				
				#store previous selectedRomCollections state
				self.scraperSites[self.selectedOfflineScraper.name] = self.selectedOfflineScraper
			
			#HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			self.updateOfflineScraperControls()
			
		elif (controlID == CONTROL_BUTTON_EMUCMD):
			
			dialog = xbmcgui.Dialog()
			
			emulatorPath = dialog.browse(1, '%s Emulator' %self.selectedRomCollection.name, 'files')
			if(emulatorPath == ''):
				return
						
			self.selectedRomCollection.emulatorCmd = emulatorPath
			control = self.getControlById(CONTROL_BUTTON_EMUCMD)
			control.setLabel(emulatorPath)
			
		elif (controlID == CONTROL_BUTTON_PARAMS):
												
			emulatorParams = self.editTextProperty(CONTROL_BUTTON_PARAMS, 'emulator params')
			self.selectedRomCollection.emulatorParams = emulatorParams 			
			
		elif (controlID == CONTROL_BUTTON_ROMPATH):
			
			dialog = xbmcgui.Dialog()
			
			romPath = dialog.browse(0, '%s Roms' %self.selectedRomCollection.name, 'files')
			if(romPath == ''):
				return
						
			control = self.getControlById(CONTROL_BUTTON_FILEMASK)
			fileMaskInput = control.getLabel()
			fileMasks = fileMaskInput.split(',')
			romPaths = []
			for fileMask in fileMasks:
				romPathComplete = os.path.join(romPath, fileMask.strip())					
				romPaths.append(romPathComplete)
						
			self.selectedRomCollection.romPaths = romPaths
			control = self.getControlById(CONTROL_BUTTON_ROMPATH)
			control.setLabel(romPath)
			
		elif (controlID == CONTROL_BUTTON_FILEMASK):
			
			control = self.getControlById(CONTROL_BUTTON_FILEMASK)
			romFileMask = control.getLabel()
			
			keyboard = xbmc.Keyboard()
			keyboard.setHeading('Enter Rom File Mask')
			keyboard.setDefault(romFileMask)			
			keyboard.doModal()
			if (keyboard.isConfirmed()):
				romFileMask = keyboard.getText()
									
			#HACK: this only handles 1 base rom path
			romPath = self.selectedRomCollection.romPaths[0]
			pathParts = os.path.split(romPath)
			romPath = pathParts[0]
			fileMasks = romFileMask.split(',')
			romPaths = []
			for fileMask in fileMasks:				
				romPathComplete = os.path.join(romPath, fileMask.strip())					
				romPaths.append(romPathComplete)
			
			self.selectedRomCollection.romPaths = romPaths
			control.setLabel(romFileMask)
			
		elif (controlID == CONTROL_BUTTON_MEDIAPATH):
			
			#get selected medias type			
			control = self.getControlById(CONTROL_LIST_MEDIATYPES)
			selectedMediaType = str(control.getSelectedItem().getLabel())
			
			#get current media path
			currentMediaPath = None
			currentMediaPathIndex = -1;
			for i in range(0, len(self.selectedRomCollection.mediaPaths)):
				mediaPath = self.selectedRomCollection.mediaPaths[i]
				if(mediaPath.fileType.name == selectedMediaType):
					currentMediaPath = mediaPath
					currentMediaPathIndex = i
					break
			
			mediaPathComplete = self.editPathWithFileMask(CONTROL_BUTTON_MEDIAPATH, '%s Path' %currentMediaPath.fileType.name, CONTROL_BUTTON_MEDIAFILEMASK)
			
			if(mediaPathComplete != ''):
				currentMediaPath.path = mediaPathComplete
				self.selectedRomCollection.mediaPaths[currentMediaPathIndex] = currentMediaPath
		
		elif (controlID == CONTROL_BUTTON_MEDIAFILEMASK):
			
			#get selected medias type			
			control = self.getControlById(CONTROL_LIST_MEDIATYPES)
			selectedMediaType = str(control.getSelectedItem().getLabel())
			
			#get current media path
			currentMediaPath = None
			currentMediaPathIndex = -1;
			for i in range(0, len(self.selectedRomCollection.mediaPaths)):
				mediaPath = self.selectedRomCollection.mediaPaths[i]
				if(mediaPath.fileType.name == selectedMediaType):
					currentMediaPath = mediaPath
					currentMediaPathIndex = i
					break							
				
			mediaPathComplete = self.editFilemask(CONTROL_BUTTON_MEDIAFILEMASK, 'media filemask', currentMediaPath.path)
						
			currentMediaPath.path = mediaPathComplete
			self.selectedRomCollection.mediaPaths[currentMediaPathIndex] = currentMediaPath
		
		elif (controlID == CONTROL_BUTTON_ADDMEDIAPATH):
			
			mediaTypes = self.gui.config.tree.findall('FileTypes/FileType')
			
			mediaTypeList = []
			
			for mediaType in mediaTypes:
				name = mediaType.attrib.get('name')
				if(name != None):
					type = mediaType.find('type')
					if(type != None and type.text == 'video'):
						name = name +' (video)'
					
					#check if media type is already in use for selected RC
					isMediaTypeInUse = False
					for mediaPath in self.selectedRomCollection.mediaPaths:
						if(mediaPath.fileType.name == name):
							isMediaTypeInUse = True
					
					if(not isMediaTypeInUse):
						mediaTypeList.append(name)
			
			mediaTypeIndex = xbmcgui.Dialog().select('Choose a media path to add', mediaTypeList)
			if(mediaTypeIndex == -1):
				return
			
			mediaType = mediaTypeList[mediaTypeIndex]
			mediaType = mediaType.replace(' (video)', '')
						
			mediaPath = MediaPath()
			fileType = FileType()
			fileType.name = mediaType
			mediaPath.fileType = fileType
			
			#TODO: Enter path and mask per wizard? Auto fill mask?
			
			self.selectedRomCollection.mediaPaths.append(mediaPath)			
			
			control = self.getControlById(CONTROL_LIST_MEDIATYPES)
			item = xbmcgui.ListItem(mediaType, '', '', '')
			control.addItem(item)
			
			self.selectItemInList(mediaType, CONTROL_LIST_MEDIATYPES)
			
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			self.updateMediaPathControls()
			
		elif (controlID == CONTROL_BUTTON_REMOVEMEDIAPATH):
									
			mediaTypeList = []
			for mediaPath in self.selectedRomCollection.mediaPaths:
				mediaTypeList.append(mediaPath.fileType.name)
			
			mediaTypeIndex = xbmcgui.Dialog().select('Choose a media path to remove', mediaTypeList)
			if(mediaTypeIndex == -1):
				return
						
			mediaType = mediaTypeList[mediaTypeIndex]
			for mediaPath in self.selectedRomCollection.mediaPaths:
				if(mediaPath.fileType.name == mediaType):
					self.selectedRomCollection.mediaPaths.remove(mediaPath)
					break
				
			self.updateRomCollectionControls()
			
		elif (controlID == CONTROL_BUTTON_MAXFOLDERDEPTH):
			
			maxFolderDepth = self.editTextProperty(CONTROL_BUTTON_MAXFOLDERDEPTH, 'max folder depth')
			self.selectedRomCollection.maxFolderDepth = maxFolderDepth
			
		elif (controlID == CONTROL_BUTTON_DISKINDICATOR):
			
			diskIndicator = self.editTextProperty(CONTROL_BUTTON_DISKINDICATOR, 'disk indicator')
			self.selectedRomCollection.diskPrefix = diskIndicator
						
		elif (controlID == CONTROL_BUTTON_SAVESTATEPATH):
			
			saveStatePathComplete = self.editPathWithFileMask(CONTROL_BUTTON_SAVESTATEPATH, '%s savestate path' %self.selectedRomCollection.name, CONTROL_BUTTON_SAVESTATEMASK)
			if(saveStatePathComplete != ''):
				self.selectedRomCollection.saveStatePath = saveStatePathComplete
				
		elif (controlID == CONTROL_BUTTON_SAVESTATEMASK):
			
			self.selectedRomCollection.saveStatePath = self.editFilemask(CONTROL_BUTTON_SAVESTATEMASK, 'savestate filemask', self.selectedRomCollection.saveStatePath)
			
			
		elif (controlID == CONTROL_BUTTON_SAVESTATEPARAMS):
			
			saveStateParams = self.editTextProperty(CONTROL_BUTTON_SAVESTATEPARAMS, 'savestate params')
			self.selectedRomCollection.saveStateParams = saveStateParams
				
		elif (controlID == CONTROL_BUTTON_SCRAPERNAME):
			
			scraperName = self.editTextProperty(CONTROL_BUTTON_SCRAPERNAME, 'scraper name')			
			self.selectedOfflineScraper.name = scraperName
			
		elif (controlID == CONTROL_BUTTON_GAMEDESCPATH):
			
			gamedescPathComplete = self.editPathWithFileMask(CONTROL_BUTTON_GAMEDESCPATH, '%s game desc path' %self.selectedRomCollection.name, CONTROL_BUTTON_GAMEDESCMASK)
			if(gamedescPathComplete != ''):
				
				#HACK: only use source and parser from 1st scraper
				if(len(self.selectedOfflineScraper.scrapers) >= 1):			
					self.selectedOfflineScraper.scrapers[0].source = gamedescPathComplete
		
		elif (controlID == CONTROL_BUTTON_GAMEDESCMASK):
			
			if(len(self.selectedOfflineScraper.scrapers) >= 1):
				self.selectedOfflineScraper.scrapers[0].source = self.editFilemask(CONTROL_BUTTON_GAMEDESCMASK, 'game desc filemask', self.selectedOfflineScraper.scrapers[0].source)
			
		elif (controlID == CONTROL_BUTTON_PARSEINSTRUCTION):
			
			dialog = xbmcgui.Dialog()
			
			parseInstruction = dialog.browse(1, '%s parse instruction' %self.selectedRomCollection.name, 'files')
			if(parseInstruction == ''):
				return
			
			control = self.getControlById(CONTROL_BUTTON_PARSEINSTRUCTION)
			control.setLabel(parseInstruction)		
			
			if(len(self.selectedOfflineScraper.scrapers) >= 1):
				self.selectedOfflineScraper.scrapers[0].parseInstruction = parseInstruction
				
		elif (controlID == CONTROL_BUTTON_ADDSCRAPER):
			
			name = ''
			
			keyboard = xbmc.Keyboard()
			keyboard.setHeading('Enter scraper name')
			keyboard.doModal()
			if (keyboard.isConfirmed()):
				name = keyboard.getText()
			
			if(name == ''):
				return
			
			site = Site()
			site.name = name
			site.scrapers = []
			self.scraperSites[name] = site
			
			control = self.getControlById(CONTROL_LIST_SCRAPERS)
			item = xbmcgui.ListItem(name, '', '', '')
			control.addItem(item)
			
			self.selectItemInList(name, CONTROL_LIST_SCRAPERS)
			
			if(self.selectedOfflineScraper != None):
				#save current values to selected ScraperSite
				self.updateSelectedOfflineScraper()
				
				#store previous selectedRomCollections state
				self.scraperSites[self.selectedOfflineScraper.name] = self.selectedOfflineScraper
			
			#HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			self.updateOfflineScraperControls()
			
		elif (controlID == CONTROL_BUTTON_REMOVESCRAPER):
			
			scraperSites = self.getAvailableScrapers(True)
			
			scraperIndex = xbmcgui.Dialog().select('Choose a scraper to remove', scraperSites)
			if(scraperIndex == -1):
				return
			
			scraperSite = scraperSites[scraperIndex]
			
			#check if scraper is in use
			for rcName in self.romCollections:
				romCollection = self.romCollections[rcName]
				for scraper in romCollection.scraperSites:
					if(scraper.name == scraperSite):
						xbmcgui.Dialog().ok('Scraper %s is already in use' %scraper.name, 'Please choose another one.')
						return
																	
			scraperSites.remove(scraperSite)
			del self.scraperSites[scraperSite]
			
			if(len(scraperSites) == 0):
				scraperSites.append('None')
				site = Site()
				site.name = 'None'
				site.scrapers = []
				self.scraperSites['None'] = site
				
			control = self.getControlById(CONTROL_LIST_SCRAPERS)
			control.reset()
			self.addItemsToList(CONTROL_LIST_SCRAPERS, scraperSites)
				
			self.updateOfflineScraperControls()
			
	
	def onFocus(self, controlId):
		self.selectedControlId = controlId
	
	
	def editTextProperty(self, controlId, name):
		control = self.getControlById(controlId)
		textValue = control.getLabel()
		
		keyboard = xbmc.Keyboard()
		keyboard.setHeading('Enter ' +name)			
		keyboard.setDefault(textValue)
		keyboard.doModal()
		if (keyboard.isConfirmed()):
			textValue = keyboard.getText()
							
		control.setLabel(textValue)
		
		return textValue
	
	
	def editPathWithFileMask(self, controlId, enterString, controlIdFilemask):
		
			dialog = xbmcgui.Dialog()
			
			#get new value
			pathValue = dialog.browse(0, enterString, 'files')
			if(pathValue == ''):
				return ''
			
			control = self.getControlById(controlId)
			control.setLabel(pathValue)
			
			
			control = self.getControlById(controlIdFilemask)
			filemask = control.getLabel()
			pathComplete = os.path.join(pathValue, filemask.strip())
			
			return pathComplete
		
		
	def editFilemask(self, controlId, enterString, pathComplete):
		control = self.getControlById(controlId)
		filemask = control.getLabel()
		
		keyboard = xbmc.Keyboard()
		keyboard.setHeading('Enter ' +enterString)
		keyboard.setDefault(filemask)
		keyboard.doModal()
		if (keyboard.isConfirmed()):
			filemask = keyboard.getText()
		
		control.setLabel(filemask)
												
		pathParts = os.path.split(pathComplete)
		path = pathParts[0]
		pathComplete = os.path.join(path, filemask.strip())
		
		return pathComplete
	
	
	def updateRomCollectionControls(self):
		
		Logutil.log('updateRomCollectionControls', util.LOG_LEVEL_INFO)
		
		control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
		selectedRomCollectionName = str(control.getSelectedItem().getLabel())
				
		Logutil.log('selected rom collection: ' +str(selectedRomCollectionName), util.LOG_LEVEL_INFO)
				
		self.selectedRomCollection = None
		
		for rcId in self.romCollections.keys():
			romCollection = self.romCollections[rcId]
			if romCollection.name == selectedRomCollectionName:
				self.selectedRomCollection = romCollection
				break
			
		if(self.selectedRomCollection == None):
			return
		
		
		#Import Games
		#HACK: split romPath and fileMask
		firstRomPath = ''
		fileMask = ''
		for romPath in self.selectedRomCollection.romPaths:
			
			pathParts = os.path.split(romPath)			 
			if(firstRomPath == ''):				
				firstRomPath = pathParts[0]
				fileMask = pathParts[1]
			elif(firstRomPath == pathParts[0]):
				fileMask = fileMask +',' +pathParts[1]
								
		control = self.getControlById(CONTROL_BUTTON_ROMPATH)
		control.setLabel(firstRomPath)
		
		control = self.getControlById(CONTROL_BUTTON_FILEMASK)
		control.setLabel(fileMask)
		
		control = self.getControlById(CONTROL_BUTTON_IGNOREONSCAN)		
		control.setSelected(self.selectedRomCollection.ignoreOnScan)
		
		control = self.getControlById(CONTROL_BUTTON_ALLOWUPDATE)
		control.setSelected(self.selectedRomCollection.allowUpdate)
		
		control = self.getControlById(CONTROL_BUTTON_DISKINDICATOR)
		control.setLabel(self.selectedRomCollection.diskPrefix)
		
		control = self.getControlById(CONTROL_BUTTON_MAXFOLDERDEPTH)
		control.setLabel(str(self.selectedRomCollection.maxFolderDepth))
		
		control = self.getControlById(CONTROL_BUTTON_USEFOLDERASGAMENAME)
		control.setSelected(self.selectedRomCollection.useFoldernameAsGamename)
		
		#Import Game Data
		#Media Types
		mediaTypeList = []
		firstMediaPath = ''
		firstMediaFileMask = ''
		for mediaPath in self.selectedRomCollection.mediaPaths:
			mediaTypeList.append(mediaPath.fileType.name)
			if(firstMediaPath == ''):
				pathParts = os.path.split(mediaPath.path)
				firstMediaPath = pathParts[0]
				firstMediaFileMask = pathParts[1]
				
		self.addItemsToList(CONTROL_LIST_MEDIATYPES, mediaTypeList)
		
		control = self.getControlById(CONTROL_BUTTON_MEDIAPATH)
		control.setLabel(firstMediaPath)
		
		control = self.getControlById(CONTROL_BUTTON_MEDIAFILEMASK)
		control.setLabel(firstMediaFileMask)
						
		self.selectScrapersInList(self.selectedRomCollection.scraperSites, self.availableScrapers)
		
		#Browse Games
		self.selectItemInList(self.selectedRomCollection.imagePlacing.name, CONTROL_LIST_IMAGEPLACING)
		
		#Launch Games
		control = self.getControlById(CONTROL_BUTTON_EMUCMD)		
		control.setLabel(self.selectedRomCollection.emulatorCmd)
		
		control = self.getControlById(CONTROL_BUTTON_PARAMS)
		control.setLabel(self.selectedRomCollection.emulatorParams)
		
		control = self.getControlById(CONTROL_BUTTON_USEEMUSOLO)
		control.setSelected(self.selectedRomCollection.useEmuSolo)
		
		pathParts = os.path.split(self.selectedRomCollection.saveStatePath)
		saveStatePath = pathParts[0]
		saveStateFileMask = pathParts[1]
		
		control = self.getControlById(CONTROL_BUTTON_SAVESTATEPATH)
		control.setLabel(saveStatePath)
		
		control = self.getControlById(CONTROL_BUTTON_SAVESTATEMASK)
		control.setLabel(saveStateFileMask)
		
		control = self.getControlById(CONTROL_BUTTON_SAVESTATEPARAMS)
		control.setLabel(self.selectedRomCollection.saveStateParams)
		
		control = self.getControlById(CONTROL_BUTTON_DONTEXTRACTZIP)
		control.setSelected(self.selectedRomCollection.doNotExtractZipFiles)
	
	
	def updateOfflineScraperControls(self):
		
		Logutil.log('updateOfflineScraperControls', util.LOG_LEVEL_INFO)
		
		control = self.getControlById(CONTROL_LIST_SCRAPERS)
		selectedScraperName = str(control.getSelectedItem().getLabel())
		
		selectedSite = None
		try:
			selectedSite = self.scraperSites[selectedScraperName]
		except:
			#should not happen
			return
		
		self.selectedOfflineScraper = selectedSite
		
		control = self.getControlById(CONTROL_BUTTON_SCRAPERNAME)
		control.setLabel(selectedSite.name)
		
		#HACK: only use source and parser from 1st scraper
		firstScraper = None
		if(len(selectedSite.scrapers) >= 1):			
			firstScraper = selectedSite.scrapers[0]
		if(firstScraper == None):
			firstScraper = Scraper()
		
		pathParts = os.path.split(firstScraper.source)
		scraperSource = pathParts[0]
		scraperFileMask = pathParts[1]
		
		control = self.getControlById(CONTROL_BUTTON_GAMEDESCPATH)
		control.setLabel(scraperSource)
		
		control = self.getControlById(CONTROL_BUTTON_GAMEDESCMASK)
		control.setLabel(scraperFileMask)
		
		control = self.getControlById(CONTROL_BUTTON_PARSEINSTRUCTION)
		control.setLabel(firstScraper.parseInstruction)
		
		control = self.getControlById(CONTROL_BUTTON_DESCPERGAME)
		control.setSelected(selectedSite.descFilePerGame)
		
		control = self.getControlById(CONTROL_BUTTON_SEARCHBYCRC)
		control.setSelected(selectedSite.searchGameByCRC)
		
		control = self.getControlById(CONTROL_BUTTON_USEFILEASCRC)
		control.setSelected(selectedSite.useFilenameAsCRC)
		
		control = self.getControlById(CONTROL_BUTTON_USEFOLDERASCRC)
		control.setSelected(selectedSite.useFoldernameAsCRC)
	
	
	def updateMediaPathControls(self):
		
		control = self.getControlById(CONTROL_LIST_MEDIATYPES)
		selectedMediaType = str(control.getSelectedItem().getLabel())
		
		for mediaPath in self.selectedRomCollection.mediaPaths:
			if mediaPath.fileType.name == selectedMediaType:
				
				pathParts = os.path.split(mediaPath.path)
				control = self.getControlById(CONTROL_BUTTON_MEDIAPATH)
				control.setLabel(pathParts[0])				
				control = self.getControlById(CONTROL_BUTTON_MEDIAFILEMASK)
				control.setLabel(pathParts[1])
				
				break
	
	
	def updateSelectedRomCollection(self):
		
		Logutil.log('updateSelectedRomCollection', util.LOG_LEVEL_INFO)
		
		#ignore on scan
		control = self.getControlById(CONTROL_BUTTON_IGNOREONSCAN)
		self.selectedRomCollection.ignoreOnScan = bool(control.isSelected())
		
		#Scraper
		try:
			platformId = config.consoleDict[self.selectedRomCollection.name]
		except:
			platformId = '0'
		
		sites = []
		sites = self.addScraperToSiteList(CONTROL_LIST_SCRAPER1, platformId, sites, self.selectedRomCollection)
		sites = self.addScraperToSiteList(CONTROL_LIST_SCRAPER2, platformId, sites, self.selectedRomCollection)
		sites = self.addScraperToSiteList(CONTROL_LIST_SCRAPER3, platformId, sites, self.selectedRomCollection)
			
		self.selectedRomCollection.scraperSites = sites
		
		
		#Image Placing
		control = self.getControlById(CONTROL_LIST_IMAGEPLACING)
		imgPlacingItem = control.getSelectedItem()
		imgPlacingName = imgPlacingItem.getLabel()
		
		imgPlacing, errorMsg = self.gui.config.readImagePlacing(imgPlacingName, self.gui.config.tree)
		self.selectedRomCollection.imagePlacing = imgPlacing
		
		
	def updateSelectedOfflineScraper(self):
		Logutil.log('updateSelectedOfflineScraper', util.LOG_LEVEL_INFO)
		
		#desc file per game
		control = self.getControlById(CONTROL_BUTTON_DESCPERGAME)
		self.selectedOfflineScraper.descFilePerGame = bool(control.isSelected())
		
		#search game by crc
		control = self.getControlById(CONTROL_BUTTON_SEARCHBYCRC)
		self.selectedOfflineScraper.searchGameByCRC = bool(control.isSelected())
		
		#use foldername as crc
		control = self.getControlById(CONTROL_BUTTON_USEFOLDERASCRC)
		self.selectedOfflineScraper.useFoldernameAsCRC = bool(control.isSelected())
		
		#use filename as crc
		control = self.getControlById(CONTROL_BUTTON_USEFILEASCRC)
		self.selectedOfflineScraper.useFilenameAsCRC = bool(control.isSelected())
		

	
	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except:
			return None
		
		return control
	
	
	def addItemsToList(self, controlId, options):
		Logutil.log('addItemsToList', util.LOG_LEVEL_INFO)
		
		control = self.getControlById(controlId)
		control.setVisible(1)
		control.reset()
				
		items = []
		for option in options:
			items.append(xbmcgui.ListItem(option, '', '', ''))
							
		control.addItems(items)
		
		
	def getAvailableScrapers(self, localOnly):
		Logutil.log('get available scrapers', util.LOG_LEVEL_INFO)
		
		#Scrapers
		sitesInList = []		
		if(not localOnly):
			sitesInList.append('None')
		#get all scrapers
		
		for siteName in self.scraperSites:
			
			site = self.scraperSites[siteName]
			
			#only add scrapers without http
			if(localOnly):
				#don't use local nfo scraper
				if(site.name == 'local nfo'):
					 continue
				skipScraper = False
				
				for scraper in site.scrapers:
					source = scraper.source
					if(source.startswith('http')):
						skipScraper = True
						break
				if(skipScraper):
					continue
			
			
			Logutil.log('add scraper name: ' +str(site.name), util.LOG_LEVEL_INFO)
			sitesInList.append(site.name)
				
		if(len(sitesInList) == 0):
			 sitesInList.append('None')
				
		return sitesInList
	
	
	def selectScrapersInList(self, sitesInRomCollection, sitesInList):
		
		Logutil.log('selectScrapersInList', util.LOG_LEVEL_INFO)
		
		if(len(sitesInRomCollection) >= 1):
			self.selectItemInList(sitesInRomCollection[0].name, CONTROL_LIST_SCRAPER1)			
		else:
			self.selectItemInList('None', CONTROL_LIST_SCRAPER1)
		if(len(sitesInRomCollection) >= 2):
			self.selectItemInList(sitesInRomCollection[1].name, CONTROL_LIST_SCRAPER2)
		else:
			self.selectItemInList('None', CONTROL_LIST_SCRAPER2)
		if(len(sitesInRomCollection) >= 3):
			self.selectItemInList(sitesInRomCollection[2].name, CONTROL_LIST_SCRAPER3)
		else:
			self.selectItemInList('None', CONTROL_LIST_SCRAPER3)
			
			
	def selectItemInList(self, itemName, controlId):				
		
		Logutil.log('selectItemInList', util.LOG_LEVEL_INFO)		
		
		control = self.getControlById(controlId)
		
		for i in range(0, control.size()):
			item = control.getListItem(i)
			if(item.getLabel() == itemName):
				control.selectItem(i)
				break
			
			
	def addScraperToSiteList(self, controlId, platformId, sites, romCollection):				

		Logutil.log('addScraperToSiteList', util.LOG_LEVEL_INFO)
		
		control = self.getControlById(controlId)
		scraperItem = control.getSelectedItem()
		scraper = scraperItem.getLabel()
		
		if(scraper == 'None'):
			return sites
		
		#check if this site is already available for current RC
		for site in romCollection.scraperSites:
			if(site.name == scraper):
				sites.append(site)
				return sites
				
		
		if(scraper != 'mobygames.com'):
			platformId = '0'
		
		siteRow = None
		siteRows = self.gui.config.tree.findall('Scrapers/Site')
		for element in siteRows:
			if(element.attrib.get('name') == scraper):
				siteRow = element
				break
		
		if(siteRow == None):
			xbmcgui.Dialog().ok('Configuration Error', 'Site %s does not exist in config.xml' %scraper)
			return None
		
		site, errorMsg = self.gui.config.readScraper(siteRow, platformId, '', '', True, self.gui.config.tree)
		if(site != None):
			sites.append(site)
			
		return sites