
from config import *
from util import *
import util
import xbmc, xbmcgui


ACTION_MOVEMENT_UP = (3,)
ACTION_MOVEMENT_DOWN = (4,)
ACTION_MOVEMENT = (3, 4, 5, 6, 159, 160)

ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_OK = 5300
CONTROL_BUTTON_CANCEL = 5310

CONTROL_LIST_ROMCOLLECTIONS = 5210
CONTROL_LIST_FUZZYFACTOR = 5260
CONTROL_LIST_SCRAPER1 = 5270
CONTROL_LIST_SCRAPER2 = 5280
CONTROL_LIST_SCRAPER3 = 5290

CONTROL_BUTTON_RC_DOWN = 5211
CONTROL_BUTTON_RC_UP = 5212

CONTROL_BUTTON_OVERWRITESETTINGS = 5330


class ImportOptionsDialog(xbmcgui.WindowXMLDialog):
	def __init__(self, *args, **kwargs):
		# Don't put GUI sensitive stuff here (as the xml hasn't been read yet)
		Logutil.log('init ImportOptions', util.LOG_LEVEL_INFO)

		self.gui = kwargs["gui"]
		self.romCollections = kwargs["romCollections"]
		self.isRescrape = kwargs["isRescrape"]

		self.doModal()

	def onInit(self):
		log.info('onInit ImportOptions')
		romCollectionList = [util.localize(32120)] + self.gui.config.getRomCollectionNames()
		log.debug("Adding list of RC names: {0}".format(romCollectionList))
		self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, romCollectionList)

		# Deactivate Rom Collection list
		if self.romCollections is not None:
			# Set overwrite flag to false
			xbmc.executebuiltin('Skin.SetBool(%s)' % util.SETTING_RCB_IMPORTOPTIONS_DISABLEROMCOLLECTIONS)
			self.setFocus(self.getControl(CONTROL_BUTTON_OVERWRITESETTINGS))
		else:
			xbmc.executebuiltin('Skin.Reset(%s)' % util.SETTING_RCB_IMPORTOPTIONS_DISABLEROMCOLLECTIONS)

		sitesInList = self.getAvailableScrapers()

		for scraper in [CONTROL_LIST_SCRAPER1, CONTROL_LIST_SCRAPER2, CONTROL_LIST_SCRAPER3]:
			self.addItemsToList(scraper, sitesInList)

		# Set initial scraper values
		sitesInRomCollection = []
		# Use scraper config of first non-MAME rom collection
		for rcid, rc in self.gui.config.romCollections.iteritems():
			if rc.name != 'MAME' or len(self.gui.config.romCollections) == 1:
				sitesInRomCollection = rc.scraperSites
				break

		self.selectScrapersInList(sitesInRomCollection, sitesInList)

		# Set overwrite flag to false
		xbmc.executebuiltin('Skin.Reset(%s)' % util.SETTING_RCB_OVERWRITEIMPORTOPTIONS)

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
			selectedRomCollection = str(control.getSelectedItem().getLabel())

			# Set initial scraper values
			sitesInRomCollection = []
			# Get selected Rom Collection
			for rcId in self.gui.config.romCollections.keys():
				romCollection = self.gui.config.romCollections[rcId]
				if (selectedRomCollection == util.localize(32120) and romCollection.name != 'MAME') \
					or len(self.gui.config.romCollections) == 1 \
					or romCollection.name == selectedRomCollection:
					sitesInRomCollection = romCollection.scraperSites
					break

			sitesInList = self.getAvailableScrapers()
			self.selectScrapersInList(sitesInRomCollection, sitesInList)

	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except RuntimeError as e:
			return None

		return control

	def addItemsToList(self, controlId, options):
		control = self.getControlById(controlId)
		control.setVisible(True)
		control.reset()    # Clear entries

		items = []
		for option in options:
			items.append(xbmcgui.ListItem(option, '', '', ''))

		control.addItems(items)

	def setRadioButtonValue(self, controlId, setting):
		control = self.getControlById(controlId)
		value = self.gui.Settings.getSetting(setting).upper() == 'TRUE'
		control.setSelected(value)

	def getAvailableScrapers(self):
		# Scrapers
		sitesInList = [util.localize(32854), util.localize(32153)]
		# Get all scrapers
		scrapers = self.gui.config.tree.findall('Scrapers/Site')
		for scraper in scrapers:
			name = scraper.attrib.get('name')
			if name is not None:
				sitesInList.append(name)

		return sitesInList

	def selectScrapersInList(self, sitesInRomCollection, sitesInList):

		if len(sitesInRomCollection) >= 1:
			self.selectScraperInList(sitesInList, sitesInRomCollection[0].name, CONTROL_LIST_SCRAPER1)
		else:
			self.selectScraperInList(sitesInList, util.localize(32854), CONTROL_LIST_SCRAPER1)
		if len(sitesInRomCollection) >= 2:
			self.selectScraperInList(sitesInList, sitesInRomCollection[1].name, CONTROL_LIST_SCRAPER2)
		else:
			self.selectScraperInList(sitesInList, util.localize(32854), CONTROL_LIST_SCRAPER2)
		if len(sitesInRomCollection) >= 3:
			self.selectScraperInList(sitesInList, sitesInRomCollection[2].name, CONTROL_LIST_SCRAPER3)
		else:
			self.selectScraperInList(sitesInList, util.localize(32854), CONTROL_LIST_SCRAPER3)

	def selectScraperInList(self, options, siteName, controlId):
		for i in range(0, len(options)):
			option = options[i]
			if siteName == option:
				control = self.getControlById(controlId)
				control.selectItem(i)
				break

	def doImport(self):
		romCollections, statusOk = self.setScrapersInConfig()

		if statusOk:
			self.gui.doImport(romCollections, self.isRescrape)

	def setScrapersInConfig(self):
		# Read selected Rom Collection
		control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
		romCollItem = control.getSelectedItem()
		selectedRC = romCollItem.getLabel()

		if self.romCollections is not None:
			romCollections = self.romCollections
		else:
			# TODO add id to list and select rc by id
			if selectedRC == util.localize(32120):
				romCollections = self.gui.config.romCollections
			else:
				romCollections = {}
				for romCollection in self.gui.config.romCollections.values():
					if romCollection.name == selectedRC:
						romCollections[romCollection.id] = romCollection
						break

		# Check if we should use configured scrapers
		control = self.getControlById(CONTROL_BUTTON_OVERWRITESETTINGS)
		if not control.isSelected():
			return romCollections, True

		# TODO ignore offline scrapers
		for rcId in romCollections.keys():

			romCollection = self.gui.config.romCollections[rcId]

			sites = []
			sites, statusOk = self.addScraperToRomCollection(CONTROL_LIST_SCRAPER1, sites, romCollection)
			if not statusOk:
				return None, False
			sites, statusOk = self.addScraperToRomCollection(CONTROL_LIST_SCRAPER2, sites, romCollection)
			if not statusOk:
				return None, False
			sites, statusOk = self.addScraperToRomCollection(CONTROL_LIST_SCRAPER3, sites, romCollection)
			if not statusOk:
				return None, False

			romCollection.scraperSites = sites
			romCollections[rcId] = romCollection

		return romCollections, True

	def addScraperToRomCollection(self, controlId, sites, romCollection):

		control = self.getControlById(controlId)
		scraperItem = control.getSelectedItem()
		scraper = scraperItem.getLabel()

		if scraper == util.localize(32854):
			return sites, True

		siteRow = None
		siteRows = self.gui.config.tree.findall('Scrapers/Site')
		for element in siteRows:
			if element.attrib.get('name') == scraper:
				siteRow = element
				break

		if scraper != util.localize(32153):
			if siteRow is None:
				xbmcgui.Dialog().ok(util.localize(32021), util.localize(32022) % scraper)
				return None, False
			site, errorMsg = self.gui.config.readScraper(siteRow, romCollection.name, '', '', True, self.gui.config.tree)
		else:
			site = Site()
			site.name = scraper
			site.descFilePerGame = True

		if site is not None:
			# Check if first scraper is an online or offline scraper
			if site.scrapers is not None and len(site.scrapers) > 0:
				firstScraper = site.scrapers[0]
				if firstScraper.source != 'nfo' and not firstScraper.source.startswith('http') and site.name != romCollection.name:
					xbmcgui.Dialog().ok(util.localize(32021), util.localize(32027) % (site.name, romCollection.name))
					return None, False

			sites.append(site)

		return sites, True
