
from config import *
from util import *
import util
import xbmc, xbmcgui
from dialogbase import DialogBase
from pyscraper.scraper import AbstractScraper


ACTION_MOVEMENT_UP = (3,)
ACTION_MOVEMENT_DOWN = (4,)
ACTION_MOVEMENT = (3, 4, 5, 6, 159, 160)

ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_OK = 5300
CONTROL_BUTTON_CANCEL = 5310

CONTROL_LIST_ROMCOLLECTIONS = 5210
CONTROL_LIST_SCRAPER1 = 5270

CONTROL_BUTTON_RC_DOWN = 5211
CONTROL_BUTTON_RC_UP = 5212

CONTROL_BUTTON_SCRAPER_DOWN = 5271

CONTROL_BUTTON_SCRAPEINBACKGROUND = 5340


class ImportOptionsDialog(DialogBase):
	def __init__(self, *args, **kwargs):
		# Don't put GUI sensitive stuff here (as the xml hasn't been read yet)
		Logutil.log('init ImportOptions', util.LOG_LEVEL_INFO)

		self.gui = kwargs["gui"]
		self.romCollections = kwargs["romCollections"]
		self.isRescrape = kwargs["isRescrape"]

		self.doModal()

	def onInit(self):
		log.info('onInit ImportOptions')
		# 32120 = All
		romCollectionList = [util.localize(32120)] + self.gui.config.getRomCollectionNames()
		log.debug("Adding list of RC names: {0}".format(romCollectionList))
		self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, romCollectionList)

		# Deactivate Rom Collection list
		if self.romCollections is not None:
			# Set overwrite flag to false
			xbmc.executebuiltin('Skin.SetBool(%s)' % util.SETTING_RCB_IMPORTOPTIONS_DISABLEROMCOLLECTIONS)
			if not self.isRescrape:
				self.setFocus(self.getControl(CONTROL_BUTTON_SCRAPEINBACKGROUND))
		else:
			xbmc.executebuiltin('Skin.Reset(%s)' % util.SETTING_RCB_IMPORTOPTIONS_DISABLEROMCOLLECTIONS)

		#disable background scraping control when in rescrape-mode
		if self.isRescrape:
			xbmc.executebuiltin('Skin.SetBool(%s)' % util.SETTING_RCB_IMPORTOPTIONS_ISRESCRAPE)
			self.setFocus(self.getControl(CONTROL_BUTTON_SCRAPER_DOWN))
		else:
			xbmc.executebuiltin('Skin.Reset(%s)' % util.SETTING_RCB_IMPORTOPTIONS_ISRESCRAPE)

		#only provide online scrapers for option All Rom Collections
		sitesInList = AbstractScraper().get_available_online_scrapers()
		# add option for all rom collections
		# 32804 = Use configured default scrapers
		sitesInList.append(util.localize(32804))
		self.addItemsToList(CONTROL_LIST_SCRAPER1, sitesInList)
		self.selectItemInList(util.localize(32804), CONTROL_LIST_SCRAPER1)


	def onAction(self, action):
		if action.getId() in ACTION_CANCEL_DIALOG:
			self.close()

	def onClick(self, controlID):
		if controlID == CONTROL_BUTTON_EXIT:    # Close window button
			self.close()
		elif controlID == CONTROL_BUTTON_OK:
			self.close()
			self.doImport()
		elif controlID == CONTROL_BUTTON_CANCEL:
			self.close()
		elif controlID in (CONTROL_BUTTON_RC_DOWN, CONTROL_BUTTON_RC_UP):    # Rom Collection list

			# HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)

			control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
			selectedRomCollectionName = str(control.getSelectedItem().getLabel())

			#32120 = All
			if selectedRomCollectionName == util.localize(32120):
				sitesInList = AbstractScraper().get_available_online_scrapers()
				# 32804 = Use configured default scrapers
				sitesInList.append(util.localize(32804))
				self.addItemsToList(CONTROL_LIST_SCRAPER1, sitesInList)
				self.selectItemInList(util.localize(32804), CONTROL_LIST_SCRAPER1)
			else:
				sitesInList = AbstractScraper().get_available_scrapers(selectedRomCollectionName)
				self.addItemsToList(CONTROL_LIST_SCRAPER1, sitesInList)
				# get selected rom collection object
				romCollection = self.gui.config.getRomCollectionByName(selectedRomCollectionName)
				self.selectScrapersInList(romCollection.scraperSites, CONTROL_LIST_SCRAPER1)


	def doImport(self):
		log.info('doImport')

		control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
		romCollItem = control.getSelectedItem()
		selectedRomCollection = romCollItem.getLabel()

		control = self.getControlById(CONTROL_LIST_SCRAPER1)
		selectedScraper = control.getSelectedItem().getLabel()

		romCollections = self.setScrapersInConfig()

		control = self.getControlById(CONTROL_BUTTON_SCRAPEINBACKGROUND)
		self.gui.doImport(romCollections, self.isRescrape, control.isSelected(), selectedRomCollection, selectedScraper)


	def setScrapersInConfig(self):
		log.info('setScrapersInConfig')
		# Read selected Rom Collection
		control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
		romCollItem = control.getSelectedItem()
		selectedRC = romCollItem.getLabel()

		if self.romCollections is not None:
			romCollections = self.romCollections
		else:
			#32120 = All
			if selectedRC == util.localize(32120):
				romCollections = self.gui.config.romCollections
			else:
				romCollections = {}
				romCollection = self.gui.config.getRomCollectionByName(selectedRC)
				romCollections[romCollection.id] = romCollection

		control = self.getControlById(CONTROL_LIST_SCRAPER1)
		scraperItem = control.getSelectedItem()

		siteName = scraperItem.getLabel()

		for rcId in romCollections.keys():
			romCollection = self.gui.config.romCollections[rcId]

			sites = []

			for site in romCollection.scraperSites:
				# check if it is the selected scraper or
                # 32804 = Use configured default scrapers
                # search for default scraper or check if we only have one scraper and use this one
				if site.name == siteName or \
					(siteName == util.localize(32804) and \
					(site.default or len(romCollection.scraperSites) == 1)):
						sites.append(site)
						break

			# if we did not find a scraper lets assume the selected scraper is not available in current rom collection
            # create it and set it to default
			if len(sites) == 0:
				site = Site()
				site.name = siteName
				site.default = True
				sites.append(site)

			romCollection.scraperSites = sites

		return romCollections
