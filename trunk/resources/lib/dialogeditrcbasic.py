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
	romCollections = None
	
	def __init__(self, *args, **kwargs):
		Logutil.log('init Edit RC Basic', util.LOG_LEVEL_INFO)
		
		self.gui = kwargs[ "gui" ]
		self.romCollections = self.gui.config.romCollections
		
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
						
			configWriter = ConfigXmlWriter(False)
			success, message = configWriter.writeRomCollections(self.romCollections, True)
			
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
			
		elif (controlID == CONTROL_BUTTON_EMUCMD):
			
			dialog = xbmcgui.Dialog()
			
			emulatorPath = dialog.browse(1, '%s Emulator' %self.selectedRomCollection.name, 'files')
			if(emulatorPath == ''):
				return
						
			self.selectedRomCollection.emulatorCmd = emulatorPath
			control = self.getControlById(CONTROL_BUTTON_EMUCMD)
			control.setLabel(emulatorPath)
			
		elif (controlID == CONTROL_BUTTON_PARAMS):
			
			control = self.getControlById(CONTROL_BUTTON_PARAMS)
			emulatorParams = control.getLabel()
			
			keyboard = xbmc.Keyboard()
			keyboard.setHeading('Enter Emulator Params')			
			keyboard.setDefault(emulatorParams)
			keyboard.doModal()
			if (keyboard.isConfirmed()):
				emulatorParams = keyboard.getText()
						
			self.selectedRomCollection.emulatorParams = emulatorParams
			control.setLabel(emulatorParams)
			
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
			
			dialog = xbmcgui.Dialog()
			
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
			
			#get new value
			mediaPathInput = dialog.browse(0, '%s Path' %currentMediaPath.fileType.name, 'files')
			if(mediaPathInput == ''):
				return
			
			control = self.getControlById(CONTROL_BUTTON_MEDIAPATH)
			control.setLabel(mediaPathInput)
			
			#write new path to selected Rom Collection
			#HACK: only 1 media per type is supported with this implementation
			control = self.getControlById(CONTROL_BUTTON_MEDIAFILEMASK)
			mediaFileMask = control.getLabel()
			mediaPathComplete = os.path.join(mediaPathInput, mediaFileMask.strip())
			currentMediaPath.path = mediaPathComplete
			self.selectedRomCollection.mediaPaths[currentMediaPathIndex] = currentMediaPath
		
		elif (controlID == CONTROL_BUTTON_MEDIAFILEMASK):
			
			dialog = xbmcgui.Dialog()
			
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
			
			control = self.getControlById(CONTROL_BUTTON_MEDIAFILEMASK)
			mediaFileMask = control.getLabel()
			
			keyboard = xbmc.Keyboard()
			keyboard.setHeading('Enter Media File Mask')
			keyboard.setDefault(mediaFileMask)			
			keyboard.doModal()
			if (keyboard.isConfirmed()):
				mediaFileMask = keyboard.getText()
							
			control.setLabel(mediaFileMask)
			
			#write new path to selected Rom Collection
			#HACK: only 1 media per type is supported with this implementation
			control = self.getControlById(CONTROL_BUTTON_MEDIAPATH)
			mediaPath = control.getLabel()
			mediaPathComplete = os.path.join(mediaPath, mediaFileMask.strip())
			currentMediaPath.path = mediaPathComplete
			self.selectedRomCollection.mediaPaths[currentMediaPathIndex] = currentMediaPath
						
	
	def onFocus(self, controlId):
		self.selectedControlId = controlId
	
	
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
		self.selectItemInList(self.imagePlacingList, self.selectedRomCollection.imagePlacing.name, CONTROL_LIST_IMAGEPLACING)
		
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
		sites = self.gui.config.scraperSites
		for site in sites:
			name = site.name
			if(name == selectedScraperName):
				selectedSite = site
				break
						
		if(selectedSite == None):
			#should not happen
			return
		
		control = self.getControlById(CONTROL_BUTTON_SCRAPERNAME)
		control.setLabel(selectedSite.name)
		
		#HACK: only use source and parser from 1st scraper
		firstScraper = None
		if(len(selectedSite.scrapers) >= 1):			
			firstScraper = selectedSite.scrapers[0]
		if(firstScraper == None):
			#should not happen
			return
		
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
		sites = self.addScraperToSiteList(CONTROL_LIST_SCRAPER1, platformId, sites)
		sites = self.addScraperToSiteList(CONTROL_LIST_SCRAPER2, platformId, sites)
		sites = self.addScraperToSiteList(CONTROL_LIST_SCRAPER3, platformId, sites)
			
		self.selectedRomCollection.scraperSites = sites
		
		
		#Image Placing
		control = self.getControlById(CONTROL_LIST_IMAGEPLACING)
		imgPlacingItem = control.getSelectedItem()
		imgPlacingName = imgPlacingItem.getLabel()
		
		imgPlacing, errorMsg = self.gui.config.readImagePlacing(imgPlacingName, self.gui.config.tree)
		self.selectedRomCollection.imagePlacing = imgPlacing

	
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
		sites = self.gui.config.tree.findall('Scrapers/Site')
		for site in sites:
			name = site.attrib.get('name')
			
			#only add scrapers without http
			if(localOnly):
				#don't use local nfo scraper
				if(name == 'local nfo'):
					 continue
				skipScraper = False
				scrapers = site.findall('Scraper')
				for scraper in scrapers:
					source = scraper.attrib.get('source')
					if(source.startswith('http')):
						skipScraper = True
						break
				if(skipScraper):
					continue
			
			if(name != None):
				Logutil.log('add scraper name: ' +str(name), util.LOG_LEVEL_INFO)
				sitesInList.append(name)
				
		return sitesInList
	
	
	def selectScrapersInList(self, sitesInRomCollection, sitesInList):
		
		Logutil.log('selectScrapersInList', util.LOG_LEVEL_INFO)
		
		if(len(sitesInRomCollection) >= 1):
			self.selectItemInList(sitesInList, sitesInRomCollection[0].name, CONTROL_LIST_SCRAPER1)			
		else:
			self.selectItemInList(sitesInList, 'None', CONTROL_LIST_SCRAPER1)
		if(len(sitesInRomCollection) >= 2):
			self.selectItemInList(sitesInList, sitesInRomCollection[1].name, CONTROL_LIST_SCRAPER2)
		else:
			self.selectItemInList(sitesInList, 'None', CONTROL_LIST_SCRAPER2)
		if(len(sitesInRomCollection) >= 3):
			self.selectItemInList(sitesInList, sitesInRomCollection[2].name, CONTROL_LIST_SCRAPER3)
		else:
			self.selectItemInList(sitesInList, 'None', CONTROL_LIST_SCRAPER3)
				
	
	def selectItemInList(self, options, itemName, controlId):				
		
		Logutil.log('selectItemInList', util.LOG_LEVEL_INFO)		
		
		for i in range(0, len(options)):			
			option = options[i]
			if(itemName == option):
				control = self.getControlById(controlId)
				control.selectItem(i)
				break
			
			
	def addScraperToSiteList(self, controlId, platformId, sites):				

		Logutil.log('addScraperToSiteList', util.LOG_LEVEL_INFO)
		
		control = self.getControlById(controlId)
		scraperItem = control.getSelectedItem()
		scraper = scraperItem.getLabel()
		
		if(scraper != 'mobygames.com'):
			platformId = '0'
		
		site, errorMsg = self.gui.config.readScraper(scraper, platformId, '', '', self.gui.config.tree)
		if(site != None):
			sites.append(site)
			
		return sites