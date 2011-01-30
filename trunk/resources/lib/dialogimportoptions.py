
import xbmc, xbmcgui

import util, config
from util import *


ACTION_EXIT_SCRIPT = (10,)
ACTION_CANCEL_DIALOG = ACTION_EXIT_SCRIPT + (9,)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_OK = 5300
CONTROL_BUTTON_CANCEL = 5310

CONTROL_RBUTTON_RESCRAPE = 5210
CONTROL_RBUTTON_NFO = 5225
CONTROL_RBUTTON_IGNOREINFO = 5230
CONTROL_RBUTTON_IGNOREARTWORK = 5240

CONTROL_LIST_SCRAPEMODE = 5220
CONTROL_LIST_FUZZYFACTOR = 5260
CONTROL_LIST_SCRAPER1 = 5270
CONTROL_LIST_SCRAPER2 = 5280
CONTROL_LIST_SCRAPER3 = 5290


class ImportOptionsDialog(xbmcgui.WindowXMLDialog):
	def __init__(self, *args, **kwargs):
		# Don't put GUI sensitive stuff here (as the xml hasn't been read yet)
		Logutil.log('init ImportOptions', util.LOG_LEVEL_INFO)
		
		self.gui = kwargs[ "gui" ]
		
		self.doModal()
		
	
	def onInit(self):
		Logutil.log('onInit ImportOptions', util.LOG_LEVEL_INFO)
		
		options = ['Automatic: Accurate',
					'Automatic: Guess Matches',
					'Interactive: Select Matches']
		self.addItemsToList(CONTROL_LIST_SCRAPEMODE, options)
													
		options = ['1.0', '0.9', '0.8', '0.7', '0.6', '0.5' ]
		self.addItemsToList(CONTROL_LIST_FUZZYFACTOR, options)

		sitesInList = ['None']
		
		#get all scrapers
		scrapers = self.gui.config.tree.findall('Scrapers/Site')
		for scraper in scrapers:
			name = scraper.attrib.get('name')
			if(name != None):
				sitesInList.append(name)
		
		self.addItemsToList(CONTROL_LIST_SCRAPER1, sitesInList)
		self.addItemsToList(CONTROL_LIST_SCRAPER2, sitesInList)
		self.addItemsToList(CONTROL_LIST_SCRAPER3, sitesInList)
		
		#set initial control values
		self.setRadioButtonValue(CONTROL_RBUTTON_RESCRAPE, util.SETTING_RCB_ENABLEFULLREIMPORT)
		self.setRadioButtonValue(CONTROL_RBUTTON_NFO, util.SETTING_RCB_CREATENFOFILE)
		self.setRadioButtonValue(CONTROL_RBUTTON_IGNOREINFO, util.SETTING_RCB_IGNOREGAMEWITHOUTDESC)
		self.setRadioButtonValue(CONTROL_RBUTTON_IGNOREARTWORK, util.SETTING_RCB_IGNOREGAMEWITHOUTARTWORK)
		
		fuzzyFactorIndex = self.gui.Settings.getSetting(util.SETTING_RCB_FUZZYFACTOR)
		if (fuzzyFactorIndex == ''):
			fuzzyFactorIndex = 2
		control = self.getControlById(CONTROL_LIST_FUZZYFACTOR)
		control.selectItem(int(fuzzyFactorIndex))
		
		#set initial scraper values
		#TODO handle import of certain rc
		sitesInRomCollection = []
		#use scraper config of first non-MAME rom collection
		for rcId in self.gui.config.romCollections.keys():
			romCollection = self.gui.config.romCollections[rcId]
			if romCollection.name != 'MAME':
				sitesInRomCollection = romCollection.scraperSites
				break
				
		if(len(sitesInRomCollection) >= 1):
			self.selectScraperInList(sitesInList, sitesInRomCollection[0], CONTROL_LIST_SCRAPER1)
		if(len(sitesInRomCollection) >= 2):
			self.selectScraperInList(sitesInList, sitesInRomCollection[1], CONTROL_LIST_SCRAPER2)
		if(len(sitesInRomCollection) >= 2):
			self.selectScraperInList(sitesInList, sitesInRomCollection[2], CONTROL_LIST_SCRAPER3)
			
	
	def onAction(self, action):
		if (action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
	
	def onClick(self, controlID):
		if (controlID == CONTROL_BUTTON_EXIT): # Close window button
			self.close()
		
		#OK
		elif (controlID == CONTROL_BUTTON_OK):
			self.close()
			self.doImport()
			#self.gui.updateDB()
		#Cancel
		elif (controlID == CONTROL_BUTTON_CANCEL):
			self.close()
			
	def onFocus(self, controlID):
		pass
	
	
	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except Exception, (exc):
			#HACK there seems to be a problem with recognizing the scrollbar controls
			if(controlId not in (5221,)):
				Logutil.log("Control with id: %s could not be found. Check WindowXML file. Error: %s" % (str(controlId), str(exc)), util.LOG_LEVEL_ERROR)
				self.writeMsg("Control with id: %s could not be found. Check WindowXML file." % str(controlId))
			return None
		
		return control
	
	
	def addItemsToList(self, controlId, options):
		control = self.getControlById(controlId)
		control.setVisible(1)
		control.reset()
				
		items = []
		for option in options:
			items.append(xbmcgui.ListItem(option, '', "", ""))
							
		control.addItems(items)
		
		
	def setRadioButtonValue(self, controlId, setting):
		control = self.getControlById(controlId)		
		value = self.gui.Settings.getSetting(setting).upper() == 'TRUE'
		control.setSelected(value)
	
	
	def selectScraperInList(self, options, site, controlId):
		for i in range(0, len(options)):
			option = options[i]
			if(site.name == option):
				control = self.getControlById(controlId)
				control.selectItem(i)
				break
		
			
	def doImport(self):
		
		#get selected Scraping mode
		control = self.getControlById(CONTROL_LIST_SCRAPEMODE)
		scrapingMode = control.getSelectedPosition()
		
		Logutil.log('Selected scraping mode: ' +str(scrapingMode), util.LOG_LEVEL_INFO)
		
		
		romCollections = self.setScrapersInConfig()
								
		self.gui.doImport(scrapingMode, romCollections)
		
		
	def setScrapersInConfig(self, ):
		
		romCollections = self.gui.config.romCollections
		
		#TODO ignore MAME
		for rcId in romCollections.keys():
			
			romCollection = self.gui.config.romCollections[rcId]
			
			try:
				platformId = config.consoleDict[romCollection.name]
			except:
				platformId = '0'
			
			print 'platformId = ' +str(platformId)
			
			sites = []
			site = self.getScraperFromConfig(CONTROL_LIST_SCRAPER1, platformId)
			if(site != None):
				sites.append(site)
			site = self.getScraperFromConfig(CONTROL_LIST_SCRAPER2, platformId)
			if(site != None):
				sites.append(site)
			site = self.getScraperFromConfig(CONTROL_LIST_SCRAPER2, platformId)
			if(site != None):
				sites.append(site)
				
			romCollection.scraperSites = sites
			romCollections[rcId] = romCollection
		
		return romCollections 
		
	
	def getScraperFromConfig(self, controlId, platformId):
		
		control = self.getControlById(controlId)
		scraperItem = control.getSelectedItem()
		scraper = scraperItem.getLabel()
		print "scraper to use: " +str(scraper)
		
		site, errorMsg = self.gui.config.readScraper(scraper, platformId, '', '', self.gui.config.tree)
		return site
				