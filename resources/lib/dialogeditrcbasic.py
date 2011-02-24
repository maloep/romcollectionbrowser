import xbmc, xbmcgui

import util, config
from util import *

ACTION_EXIT_SCRIPT = (10,)
ACTION_CANCEL_DIALOG = ACTION_EXIT_SCRIPT + (9,)

CONTROL_BUTTON_EXIT = 5101

CONTROL_BUTTON_EMUCMD = 5220
CONTROL_BUTTON_PARAMS = 5230

CONTROL_LIST_ROMCOLLECTIONS = 5210
CONTROL_LIST_MEDIATYPES = 5260
CONTROL_LIST_SCRAPER1 = 5290
CONTROL_LIST_SCRAPER2 = 5300
CONTROL_LIST_SCRAPER3 = 5310
CONTROL_LIST_IMAGEPLACING = 5320

class EditRCBasicDialog(xbmcgui.WindowXMLDialog):
	
	def __init__(self, *args, **kwargs):
		Logutil.log('init Edit RC Basic', util.LOG_LEVEL_INFO)
		
		self.gui = kwargs[ "gui" ]
		
		self.doModal()
	
	
	def onInit(self):
		Logutil.log('onInit Edit RC Basic', util.LOG_LEVEL_INFO)
		
		#Rom Collections
		romCollectionList = []
		for rcId in self.gui.config.romCollections.keys():
			romCollection = self.gui.config.romCollections[rcId]
			romCollectionList.append(romCollection.name)
		self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, romCollectionList)
		
		
		sitesInList = self.getAvailableScrapers()		
		self.addItemsToList(CONTROL_LIST_SCRAPER1, sitesInList)
		self.addItemsToList(CONTROL_LIST_SCRAPER2, sitesInList)
		self.addItemsToList(CONTROL_LIST_SCRAPER3, sitesInList)
		
		imagePlacingList = ['gameinfobig', 'gameinfosmall']
		self.addItemsToList(CONTROL_LIST_IMAGEPLACING, imagePlacingList)
		
		self.updateControls()
		
		
	def onAction(self, action):
		if (action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
		
	def onClick(self, controlID):
		if (controlID == CONTROL_BUTTON_EXIT): # Close window button
			self.close()
	
	def onFocus(self, controlId):
		pass
	
	
	def updateControls(self):
		
		control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
		selectedRomCollectionName = str(control.getSelectedItem().getLabel())
				
		selectedRomCollection = None
		
		for rcId in self.gui.config.romCollections.keys():
			romCollection = self.gui.config.romCollections[rcId]
			if romCollection.name == selectedRomCollectionName:
				selectedRomCollection = romCollection
				break
			
		if(selectedRomCollection == None):
			return
		
		control = self.getControlById(CONTROL_BUTTON_EMUCMD)
		control.setLabel(selectedRomCollection.emulatorCmd)
		
		control = self.getControlById(CONTROL_BUTTON_PARAMS)
		control.setLabel(selectedRomCollection.emulatorParams)
				
				
				
		
		
		#Media Types
		mediaTypeList = ['boxfront', 'boxback']		
		"""
		for rcId in self.gui.config.romCollections.keys():
			romCollection = self.gui.config.romCollections[rcId]
			romCollectionList.append(romCollection.name)
		"""		
		self.addItemsToList(CONTROL_LIST_MEDIATYPES, mediaTypeList)
	
	
	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except:
			return None
		
		return control
	
	
	def addItemsToList(self, controlId, options):
		control = self.getControlById(controlId)
		control.setVisible(1)
		control.reset()
				
		items = []
		for option in options:
			items.append(xbmcgui.ListItem(option, '', '', ''))
							
		control.addItems(items)
		
		
	def getAvailableScrapers(self):
		#Scrapers
		sitesInList = ['None']		
		#get all scrapers
		scrapers = self.gui.config.tree.findall('Scrapers/Site')
		for scraper in scrapers:
			name = scraper.attrib.get('name')
			if(name != None):
				sitesInList.append(name)
				
		return sitesInList