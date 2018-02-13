
import xbmc, xbmcgui, xbmcaddon
import glob, time, array, os, sys, shutil, re
from threading import *

from util import *
import util
import dbupdate, helper, config
from launcher import RCBLauncher
import dialogimportoptions, dialogcontextmenu, dialogprogress, dialogmissinginfo
from config import *
from configxmlupdater import *
import wizardconfigxml
from gamedatabase import *


#Action Codes
# See guilib/Key.h
ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110, 122)
ACTION_PLAYFULLSCREEN = (12, 79, 227)
ACTION_MOVEMENT_LEFT = (1,)
ACTION_MOVEMENT_RIGHT = (2,)
ACTION_MOVEMENT_UP = (3,)
ACTION_MOVEMENT_DOWN = (4,)
ACTION_MOVEMENT = (1, 2, 3, 4, 5, 6, 159, 160)
ACTION_INFO = (11,)
ACTION_CONTEXT = (117,)


#ControlIds
CONTROL_CONSOLES = 500
CONTROL_GENRE = 600
CONTROL_YEAR = 700
CONTROL_PUBLISHER = 800
CONTROL_CHARACTER = 900
FILTER_CONTROLS = (500, 600, 700, 800, 900,)
GAME_LISTS = (50, 51, 52, 53, 54, 55, 56, 57, 58)
CONTROL_SCROLLBARS = (2200, 2201, 60, 61, 62, 63)

CONTROL_GAMES_GROUP_START = 50
CONTROL_GAMES_GROUP_END = 59

CONTROL_BUTTON_CHANGE_VIEW = 2
CONTROL_BUTTON_FAVORITE = 1000
CONTROL_BUTTON_SEARCH = 1100
CONTROL_BUTTON_VIDEOFULLSCREEN = (2900, 2901,)
NON_EXIT_RCB_CONTROLS = (500, 600, 700, 800, 900, 2, 1000, 1100)

CONTROL_LABEL_MSG = 4000
CONTROL_BUTTON_MISSINGINFODIALOG = 4001


class MyPlayer(xbmc.Player):

	gui = None

	def onPlayBackEnded(self):
		print 'RCB: onPlaybackEnded'

		if(self.gui == None):
			print "RCB_WARNING: gui == None in MyPlayer"
			return

		self.gui.setFocus(self.gui.getControl(CONTROL_GAMES_GROUP_START))


class UIGameDB(xbmcgui.WindowXML):

	gdb = None

	selectedControlId = 0
	selectedConsoleId = 0
	selectedGenreId = 0
	selectedYearId = 0
	selectedPublisherId = 0
	selectedCharacter = util.localize(32120)

	selectedConsoleIndex = 0
	selectedGenreIndex = 0
	selectedYearIndex = 0
	selectedPublisherIndex = 0
	selectedCharacterIndex = 0

	rcb_playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlistOffsets = {}

	applyFilterThread = None
	applyFilterThreadStopped = False
	applyFiltersInProgress = False

	filterChanged = False

	__useRefactoredView = False
	__loadImagesFromFile = True

	#last selected game position (prevent invoke showgameinfo twice)
	lastPosition = -1

	#dummy to be compatible with ProgressDialogGUI
	itemCount = 0

	# set flag if we are watching fullscreen video
	fullScreenVideoStarted = False
	# set flag if we opened GID
	gameinfoDialogOpen = False

	#cachingOption will be overwritten by config. Don't change it here.
	cachingOption = 3

	searchTerm = ''

	def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback, isMedia=True):
		Logutil.log("Init Rom Collection Browser: " + util.RCBHOME, util.LOG_LEVEL_INFO)

		addon = xbmcaddon.Addon(id='%s' % util.SCRIPTID)
		Logutil.log("RCB version: " + addon.getAddonInfo('version'), util.LOG_LEVEL_INFO)

		# Check if RCB service is available
		try:
			serviceAddon = xbmcaddon.Addon(id=util.SCRIPTID)
			Logutil.log("RCB service addon: " + str(serviceAddon), util.LOG_LEVEL_INFO)
		except:
			Logutil.log("No RCB service addon available.", util.LOG_LEVEL_INFO)

		self.initialized = False
		self.Settings = util.getSettings()

		# Make sure that we don't start RCB in cycles
		self.Settings.setSetting('rcb_launchOnStartup', 'false')

		# Check if background game import is running
		if self.checkUpdateInProgress():
			self.quit = True
			return

		# timestamp1 = time.clock()

		self.quit = False

		self.config, success = self.initializeConfig()
		if not success:
			self.quit = True
			return

		success = self.initializeDataBase()
		if not success:
			self.quit = True
			return

		cachingOptionStr = self.Settings.getSetting(util.SETTING_RCB_CACHINGOPTION)
		if(cachingOptionStr == 'CACHEALL'):
			self.cachingOption = 0
		#elif(cachingOptionStr == 'CACHESELECTION'):
		#	self.cachingOption = 1
		elif(cachingOptionStr == 'CACHEITEM'):
			self.cachingOption = 2
		elif(cachingOptionStr == 'CACHEITEMANDNEXT'):
			self.cachingOption = 3

		self.cacheItems()
		
		#store content of mediapath folders in a dictionary
		#self.mediaDict is a nested dictionary with Rom Collection Id as first key and media type name as second key
		# '1': {'boxfront': ['list of boxfront files'], 'screenshot' : ['list of screenshot files']}
		self.mediaDict = None

		#load video fileType for later use in showGameInfo
		self.fileTypeGameplay, errorMsg = self.config.readFileType('gameplay', self.config.tree)
		if(self.fileTypeGameplay == None):
			Logutil.log("Error while loading fileType gameplay: " + errorMsg, util.LOG_LEVEL_WARNING)

		#timestamp2 = time.clock()
		#diff = (timestamp2 - timestamp1) * 1000
		#print "RCB startup time: %d ms" % (diff)

		self.player = MyPlayer()
		self.player.gui = self

		self.initialized = True

	# FIXME TODO Move to config.py
	def initializeConfig(self):
		Logutil.log("initializeConfig", util.LOG_LEVEL_INFO)

		config = Config(None)
		createNewConfig = False

		#check if we have config file
		configFile = util.getConfigXmlPath()
		if(not os.path.isfile(configFile)):
			Logutil.log("No config file available. Create new one.", util.LOG_LEVEL_INFO)
			dialog = xbmcgui.Dialog()
			createNewConfig = dialog.yesno(util.SCRIPTNAME, util.localize(32100), util.localize(32101))
			if(not createNewConfig):
				return config, False
		else:
			rcAvailable, message = config.checkRomCollectionsAvailable()
			if(not rcAvailable):
				Logutil.log("No Rom Collections found in config.xml.", util.LOG_LEVEL_INFO)
				dialog = xbmcgui.Dialog()
				createNewConfig = dialog.yesno(util.SCRIPTNAME, util.localize(32100), util.localize(32101))
				if(not createNewConfig):
					return config, False

		if (createNewConfig):
			statusOk, errorMsg = wizardconfigxml.ConfigXmlWizard().createConfigXml(configFile)
			if(statusOk == False):
				xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32001), errorMsg)
				return config, False
		else:
			#check if config.xml is up to date
			returnCode, message = ConfigxmlUpdater().updateConfig(self)
			if(returnCode == False):
				xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32001), message)

		#read config.xml
		statusOk, errorMsg = config.readXml()
		if(statusOk == False):
			xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32002), errorMsg)

		return config, statusOk

	# FIXME TODO Move to gamedatabase.py
	def initializeDataBase(self):
		try:
			self.gdb = GameDataBase(util.getAddonDataPath())
			self.gdb.connect()
		except Exception, (exc):
			xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32000), str(exc))
			Logutil.log('Error accessing database: ' + str(exc), util.LOG_LEVEL_ERROR)
			return False

		#check if database is up to date
		#create new one or alter existing one
		doImport, errorMsg = self.gdb.checkDBStructure()

		if(doImport == -1):
			xbmcgui.Dialog().ok(util.SCRIPTNAME, errorMsg)
			return False

		if(doImport == 2):
			xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32102), util.localize(32103))

		self.checkImport(doImport, None, False)
		return True


	def onInit(self):

		Logutil.log("Begin onInit", util.LOG_LEVEL_INFO)

		if(self.quit):
			Logutil.log("RCB decided not to run. Bye.", util.LOG_LEVEL_INFO)
			self.close()
			return

		self.clearList()
		self.rcb_playList.clear()
		xbmc.sleep(util.WAITTIME_UPDATECONTROLS)

		#reset last view
		self.loadViewState()

		#self.fillListInBackground()

		Logutil.log("End onInit", util.LOG_LEVEL_INFO)


	def onAction(self, action):

		Logutil.log("onAction: " + str(action.getId()), util.LOG_LEVEL_INFO)

		if(action.getId() == 0):
			Logutil.log("actionId == 0. Input ignored", util.LOG_LEVEL_INFO)
			return

		try:
			if(action.getId() in ACTION_CANCEL_DIALOG):
				Logutil.log("onAction: ACTION_CANCEL_DIALOG", util.LOG_LEVEL_INFO)

				#don't exit RCB here. Just close the filters
				if(self.selectedControlId in NON_EXIT_RCB_CONTROLS):
					Logutil.log("selectedControl in NON_EXIT_RCB_CONTROLS: %s" % self.selectedControlId, util.LOG_LEVEL_INFO)
					#HACK: when list is empty, focus sits on other controls than game list
					if(self.getListSize() > 0):
						self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))
						return

					Logutil.log("ListSize == 0 in onAction. Assume that we have to exit.", util.LOG_LEVEL_WARNING)

				if(self.player.isPlayingVideo()):
					self.player.stop()
					xbmc.sleep(util.WAITTIME_PLAYERSTOP)

				self.exit()
			elif(action.getId() in ACTION_MOVEMENT):

				Logutil.log("onAction: ACTION_MOVEMENT", util.LOG_LEVEL_DEBUG)

				control = self.getControlById(self.selectedControlId)
				if(control == None):
					Logutil.log("control == None in onAction", util.LOG_LEVEL_WARNING)
					return

				if(CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END):
					if(not self.fullScreenVideoStarted):
						if(self.cachingOption > 0):
							#HACK: check last position in list (prevent loading game info)
							pos = self.getCurrentListPosition()
							Logutil.log('onAction: current position = ' + str(pos), util.LOG_LEVEL_DEBUG)
							Logutil.log('onAction: last position = ' + str(self.lastPosition), util.LOG_LEVEL_DEBUG)
							if(pos != self.lastPosition):
								self.showGameInfo()

							self.lastPosition = pos

				if(self.selectedControlId in FILTER_CONTROLS):

					if(self.player.isPlayingVideo()):
						self.player.stop()
						xbmc.sleep(util.WAITTIME_PLAYERSTOP)

					pos = control.getSelectedPosition()
					cid = control.getId()
					if cid == CONTROL_CONSOLES and self.hasConsoleFilterChanged(pos):
						self.updateSelectedConsole(control)

					elif cid == CONTROL_GENRE and self.hasGenreFilterChanged(pos):
						self.updateSelectedGenre(control)

					elif cid == CONTROL_YEAR and self.hasYearFilterChanged(pos):
						self.updateSelectedYear(control)

					elif cid == CONTROL_PUBLISHER and self.hasPublisherFilterChanged(pos):
						self.updateSelectedPublisher(control)

					elif cid == CONTROL_CHARACTER and self.hasCharacterFilterChanged(pos):
						self.updateSelectedCharacter(control)

			elif(action.getId() in ACTION_INFO):
				Logutil.log("onAction: ACTION_INFO", util.LOG_LEVEL_DEBUG)

				control = self.getControlById(self.selectedControlId)
				if(control == None):
					Logutil.log("control == None in onAction", util.LOG_LEVEL_WARNING)
					return
				if(CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END):
					self.showGameInfoDialog()
			elif (action.getId() in ACTION_CONTEXT):

				if(self.player.isPlayingVideo()):
					self.player.stop()
					xbmc.sleep(util.WAITTIME_PLAYERSTOP)

				self.showContextMenu()

				self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))

				Logutil.log('onAction: ACTION_CONTEXT', util.LOG_LEVEL_INFO)
			elif (action.getId() in ACTION_PLAYFULLSCREEN):
				Logutil.log('onAction: ACTION_PLAYFULLSCREEN', util.LOG_LEVEL_INFO)
				self.startFullscreenVideo()
		except Exception, (exc):
			Logutil.log("RCB_ERROR: unhandled Error in onAction: " + str(exc), util.LOG_LEVEL_ERROR)

	def onClick(self, controlId):
		log.debug("onClick: {0}".format(controlId))

		if controlId in FILTER_CONTROLS:
			if self.filterChanged:
				log.debug("onClick: apply Filters")
				self.applyFilters()
				self.filterChanged = False
			else:
				log.debug("onClick: Show Game Info")
				self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))
				self.showGameInfo()
		elif controlId in GAME_LISTS:
			log.debug("onClick: Launch Emu")
			self.launchEmu()
		elif controlId in CONTROL_BUTTON_VIDEOFULLSCREEN:
			log.debug("onClick: Video fullscreen")
			self.startFullscreenVideo()
		elif controlId == CONTROL_BUTTON_FAVORITE:
			log.debug("onClick: Button Favorites")
			self.showGames()
		elif controlId == CONTROL_BUTTON_SEARCH:
			log.debug("onClick: Button Search")

			searchButton = self.getControlById(CONTROL_BUTTON_SEARCH)
			if searchButton is None:
				return

			self.searchTerm = xbmcgui.Dialog().input(util.localize(32116), type=xbmcgui.INPUT_ALPHANUM)
			lbl = util.localize(32117) if self.searchTerm == '' else util.localize(32117) + ': ' + self.searchTerm
			searchButton.setLabel(lbl)

			self.showGames()

		elif controlId == CONTROL_BUTTON_MISSINGINFODIALOG:
			missingInfoDialog = dialogmissinginfo.MissingInfoDialog("script-RCB-missinginfo.xml", util.getAddonInstallPath(), util.getConfiguredSkin(), "720p", gui=self)
			if missingInfoDialog.saveConfig:
				self.config.readXml()
				self.showGames()

			del missingInfoDialog

		elif controlId == CONTROL_BUTTON_CHANGE_VIEW:
			# Need to change viewmode manually since Frodo
			xbmc.executebuiltin('Container.NextViewMode')

	def onFocus(self, controlId):
		Logutil.log("onFocus: " + str(controlId), util.LOG_LEVEL_DEBUG)
		self.selectedControlId = controlId

	""" Check if one of the filter lists has changed """
	def hasConsoleFilterChanged(self, pos):
		return self.selectedConsoleIndex != pos

	def hasGenreFilterChanged(self, pos):
		return self.selectedGenreIndex != pos

	def hasYearFilterChanged(self, pos):
		return self.selectedYearIndex != pos

	def hasPublisherFilterChanged(self, pos):
		return self.selectedPublisherIndex != pos

	def hasCharacterFilterChanged(self, pos):
		return self.selectedCharacterIndex != pos

	""" Handle when one of the filter lists has changed """
	def updateSelectedConsole(self, control):
		label = str(control.getSelectedItem().getLabel())
		label2 = str(control.getSelectedItem().getLabel2())

		self.selectedConsoleId = int(label2)
		self.selectedConsoleIndex = control.getSelectedPosition()
		self.filterChanged = True

	def updateSelectedPublisher(self, control):
		label = str(control.getSelectedItem().getLabel())
		label2 = str(control.getSelectedItem().getLabel2())

		self.selectedPublisherId = int(label2)
		self.selectedPublisherIndex = control.getSelectedPosition()
		self.filterChanged = True

	def updateSelectedGenre(self, control):
		label = str(control.getSelectedItem().getLabel())
		label2 = str(control.getSelectedItem().getLabel2())

		self.selectedGenreId = int(label2)
		self.selectedGenreIndex = control.getSelectedPosition()
		self.filterChanged = True

	def updateSelectedYear(self, control):
		label = str(control.getSelectedItem().getLabel())
		label2 = str(control.getSelectedItem().getLabel2())

		self.selectedYearId = int(label2)
		self.selectedYearIndex = control.getSelectedPosition()
		self.filterChanged = True

	def updateSelectedCharacter(self, control):
		# Note - different to the others
		label = str(control.getSelectedItem().getLabel())
		label2 = str(control.getSelectedItem().getLabel2())

		self.selectedCharacter = label
		self.selectedCharacterIndex = control.getSelectedPosition()
		log.debug("char is {0}, index is {1}".format(self.selectedCharacter, self.selectedCharacterIndex))
		self.filterChanged = True

	def updateControls(self, onInit):
		log.debug("Begin updateControls")

		# Prepare Filter Controls. If statement takes care of dependencies between each filter control
		if onInit:
			self.showConsoles()
		if onInit or self.selectedControlId == CONTROL_CONSOLES:
			self.showGenre()
		if onInit or self.selectedControlId in [CONTROL_CONSOLES, CONTROL_GENRE]:
			self.showYear()
		if onInit or self.selectedControlId in [CONTROL_CONSOLES, CONTROL_GENRE, CONTROL_YEAR]:
			self.showPublisher()
		if onInit:
			self.showCharacterFilter()

		log.debug("End updateControls")

	def showConsoles(self):
		log.debug("Begin showConsoles")

		showEntryAllItems = getSettings().getSetting(util.SETTING_RCB_SHOWENTRYALLCONSOLES).upper() == 'TRUE'

		consoles = []
		for romCollection in self.config.romCollections.values():
			consoles.append([romCollection.id, romCollection.name])

		# Sort the consoles by name
		consoles = sorted (consoles, key=lambda console: console[1])

		self.showFilterControl(consoles, CONTROL_CONSOLES, showEntryAllItems)

		# Reset selection after loading the list
		self.selectedConsoleId = 0
		self.selectedConsoleIndex = 0

		log.debug("End showConsoles")

	def showGenre(self):
		log.debug("Begin showGenre with selected console {0}".format(self.selectedConsoleId))

		rows = Genre(self.gdb).getFilteredGenresByConsole(self.selectedConsoleId)
		log.debug("Found {0} genres to add to filter list".format(len(rows)))

		showEntryAllItems = getSettings().getSetting(util.SETTING_RCB_SHOWENTRYALLGENRES).upper() == 'TRUE'
		self.showFilterControl(rows, CONTROL_GENRE, showEntryAllItems)

		# Reset selection after loading the list
		self.selectedGenreId = 0
		self.selectedGenreIndex = 0

		log.debug("End showGenre")

	def showYear(self):
		log.debug("Begin showYear with selected console {0}".format(self.selectedConsoleId))

		rows = Year(self.gdb).getFilteredYears(self.selectedConsoleId, self.selectedGenreId, 0, '0 = 0')
		log.debug("Found {0} years to add to filter list".format(len(rows)))

		showEntryAllItems = getSettings().getSetting(util.SETTING_RCB_SHOWENTRYALLYEARS).upper() == 'TRUE'
		self.showFilterControl(rows, CONTROL_YEAR, showEntryAllItems)

		# Reset selection after loading the list
		self.selectedYearId = 0
		self.selectedYearIndex = 0

		log.debug("End showYear")

	def showPublisher(self):
		log.debug("Begin showPublisher with selected console {0}".format(self.selectedConsoleId))

		rows = Publisher(self.gdb).getFilteredPublishers(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId, '0 = 0')
		log.debug("Found {0} publishers to add to filter list".format(len(rows)))

		showEntryAllItems = getSettings().getSetting(util.SETTING_RCB_SHOWENTRYALLPUBLISHER).upper() == 'TRUE'
		self.showFilterControl(rows, CONTROL_PUBLISHER, showEntryAllItems)

		# Reset selection after loading the list
		self.selectedPublisherId = 0
		self.selectedPublisherIndex = 0

		log.debug("End showPublisher")

	def showFilterControl(self, rows, controlId, showEntryAllItems):
		log.debug("begin showFilterControl: {0}".format(controlId))

		control = self.getControlById(controlId)
		if control is None:
			return

		control.setVisible(True)
		control.reset()  # Clear any existing entries in the ControlList

		items = []
		if showEntryAllItems:
			items.append(xbmcgui.ListItem(util.localize(32120), "0"))  # Add "All" entry

		for row in rows:
			items.append(xbmcgui.ListItem(helper.saveReadString(row[util.ROW_NAME]), str(row[util.ROW_ID])))

		control.addItems(items)

	def showCharacterFilter(self):
		log.debug("Begin showCharacterFilter")

		control = self.getControlById(CONTROL_CHARACTER)
		if control is None:
			return

		control.reset()

		showEntryAllItems = getSettings().getSetting(util.SETTING_RCB_SHOWENTRYALLCHARS).upper() == 'TRUE'

		items = []

		if showEntryAllItems:
			items.append(xbmcgui.ListItem(util.localize(32120), util.localize(32120)))
		items.append(xbmcgui.ListItem("0-9", "0-9"))

		for i in range(0, 26):
			char = chr(ord('A') + i)
			items.append(xbmcgui.ListItem(char, char))

		control.addItems(items)
		log.debug("End showCharacterFilter")


	def applyFilters(self):

		Logutil.log("Begin applyFilters" , util.LOG_LEVEL_INFO)

		self.updateControls(False)
		xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
		self.showGames()

	def _getMaxGamesToDisplay(self):
		# Set a limit of games to show
		maxNumGamesIndex = self.Settings.getSetting(util.SETTING_RCB_MAXNUMGAMESTODISPLAY)
		return util.MAXNUMGAMES_ENUM[int(maxNumGamesIndex)]

	""" Functions for generating query strings for filtering """
	def _buildLikeStatement(self, selectedCharacter, searchTerm):
		log.debug("buildLikeStatement")

		likeStatement = ''

		if selectedCharacter == util.localize(32120):    # All
			likeStatement = "0 = 0"
		elif selectedCharacter == '0-9':
			likeStatement = "(name REGEXP '^[0-9]')"
		else:
			likeStatement = "name LIKE '{0}%'".format(selectedCharacter)

		if searchTerm != '':
			likeStatement += " AND name LIKE '%{0}%'".format(searchTerm)

		return likeStatement

	def _buildMissingFilterStatement(self, config):

		if config.showHideOption.lower() == util.localize(32157):    # ignore
			return ''

		statement = ''

		andStatementInfo = self._buildInfoStatement(config.missingFilterInfo.andGroup, ' AND ')
		if andStatementInfo != '':
			statement = andStatementInfo

		orStatementInfo = self._buildInfoStatement(config.missingFilterInfo.orGroup, ' OR ')
		if orStatementInfo != '':
			if statement != '':
				statement = statement + ' OR '
			statement = statement + orStatementInfo

		andStatementArtwork = self._buildArtworkStatement(config, config.missingFilterArtwork.andGroup, ' AND ')
		if andStatementArtwork != '':
			if statement != '':
				statement = statement + ' OR '
			statement = statement + andStatementArtwork

		orStatementArtwork = self._buildArtworkStatement(config, config.missingFilterArtwork.orGroup, ' OR ')
		if orStatementArtwork != '':
			if statement != '':
				statement = statement + ' OR '
			statement = statement + orStatementArtwork

		if statement != '':
			statement = '(%s)' % (statement)
			if config.showHideOption.lower() == util.localize(32161):
				statement = 'NOT ' + statement

		return statement

	def _buildInfoStatement(self, group, operator):
		statement = ''
		for item in group:
			if statement == '':
				statement = '('
			else:
				statement = statement + operator
			statement = statement + config.gameproperties[item][1]
		if statement != '':
			statement = statement + ')'

		return statement

	def _buildArtworkStatement(self, config, group, operator):
		statement = ''
		for item in group:
			if statement == '':
				statement = '('
			else:
				statement = statement + operator

			typeId = ''

			fileTypeRows = config.tree.findall('FileTypes/FileType')
			for element in fileTypeRows:
				if element.attrib.get('name') == item:
					typeId = element.attrib.get('id')
					break
			statement = statement + 'Id NOT IN (SELECT ParentId from File Where fileTypeId = %s)' % str(typeId)

		if statement != '':
			statement = statement + ')'

		return statement

	def _getGamesListQueryStatement(self):
		# Build statement for character search (where name LIKE 'A%')
		likeStatement = self._buildLikeStatement(self.selectedCharacter, self.searchTerm)

		# Build statement for missing filters
		missingFilterStatement = self._buildMissingFilterStatement(self.config)
		if missingFilterStatement != '':
			likeStatement = likeStatement + ' AND ' + missingFilterStatement

		return likeStatement
	""" End of Functions for generating query strings for filtering """

	def _isGameFavourite(self):
		try:
			if self.getControlById(CONTROL_BUTTON_FAVORITE).isSelected():
				return True
		except AttributeError:
			pass

		return False

	def showGamesNew(self):
		Logutil.log("Begin showGamesNew", util.LOG_LEVEL_INFO)

		self.lastPosition = -1

		preventUnfilteredSearch = self.Settings.getSetting(util.SETTING_RCB_PREVENTUNFILTEREDSEARCH).upper() == 'TRUE'
		if preventUnfilteredSearch:
			if self.selectedCharacter == util.localize(32120) and self.selectedConsoleId == 0 and self.selectedGenreId == 0 and self.selectedYearId == 0 and self.selectedPublisherId == 0:
				Logutil.log("preventing unfiltered search", util.LOG_LEVEL_WARNING)
				return

		isFavorite = self._isGameFavourite()

		showFavoriteStars = self.Settings.getSetting(util.SETTING_RCB_SHOWFAVORITESTARS).upper() == 'TRUE'

		timestamp1 = time.clock()

		likeStatement = self._getGamesListQueryStatement()
		maxNumGames = self._getMaxGamesToDisplay()

		games = Game(self.gdb).getGamesByFilter(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId,
												self.selectedPublisherId, isFavorite, likeStatement, maxNumGames)

		timestamp2 = time.clock()
		diff = (timestamp2 - timestamp1) * 1000
		print "showGames: load %d games from db in %d ms" % (len(games), diff)

		self.writeMsg(util.localize(32121))

		self.clearList()
		self.rcb_playList.clear()

		filecache = self.getFileDictForGamelist()
		for game in games:
			item = xbmcgui.ListItem(game.name, str(game.id))
			item.setProperty('romCollectionId', str(game.romCollectionId))

			for prop in ['gameId', 'plot', 'playcount', 'originalTitle', 'alternateTitle', 'favorite']:
				try:
					item.setProperty(prop, getattr(game, prop))
				except AttributeError:
					Logutil.log("Unable to retrieve attribute " + prop, util.LOG_LEVEL_WARNING)

			if not showFavoriteStars:
				item.setProperty('isfavorite', '')

			# FIXME TODO Videos

			try:
				romCollection = self.config.romCollections[str(game.romCollectionId)]
			except KeyError:
				Logutil.log('Cannot get rom collection with id: ' + str(game.romCollectionId), util.LOG_LEVEL_ERROR)
				# Won't be able to get game images, move to next game
				continue

			# Set the icon and thumb to be displayed in the main gamelist
			images = romCollection.getImagesForGameListView()
			Logutil.log('Rom collection {0} has {1} images for gamelist view: {2}'.format(romCollection.name, len(images), images), util.LOG_LEVEL_DEBUG)

			# f = File(self.gdb)
			for k, v in images.items():
				try:
					# Retrieve from DB
					# imagepath = f.getFilenameByGameIdAndTypeId(game.gameId, v.id)
					# Retrieve from cache
					imagepath = helper.getFilenameForGame(game.gameId, v.id, filecache)
					Logutil.log('Looking for {0}, imagetype {1}, found {2}'.format(k, v.name, imagepath), util.LOG_LEVEL_DEBUG)
					item.setArt({k: imagepath})

				except Exception as err:
					Logutil.log('Unable to set art: ' + repr(err), util.LOG_LEVEL_WARNING)

			# Add the listitem to the list
			self.addItem(item)

		xbmc.executebuiltin("Container.SortDirection")

		self.writeMsg("")

		timestamp3 = time.clock()
		diff = (timestamp3 - timestamp2) * 1000
		Logutil.log("showGames: load %i games to list in %d ms" % (self.getListSize(), diff), util.LOG_LEVEL_INFO)

		Logutil.log("End showGamesNew", util.LOG_LEVEL_INFO)

	
	def showGamesFromFile(self):
		Logutil.log("Begin showGamesFromFile" , util.LOG_LEVEL_INFO)

		self.lastPosition = -1

		preventUnfilteredSearch = self.Settings.getSetting(util.SETTING_RCB_PREVENTUNFILTEREDSEARCH).upper() == 'TRUE'

		if(preventUnfilteredSearch):
			if(self.selectedCharacter == util.localize(32120) and self.selectedConsoleId == 0 and self.selectedGenreId == 0 and self.selectedYearId == 0 and self.selectedPublisherId == 0):
				Logutil.log("preventing unfiltered search", util.LOG_LEVEL_WARNING)
				return

		isFavorite = 0
		isFavoriteButton = self.getControlById(CONTROL_BUTTON_FAVORITE)
		if(isFavoriteButton != None):
			if(bool(isFavoriteButton.isSelected())):
				isFavorite = 1

		timestamp1 = time.clock()

		# build statement for character search (where name LIKE 'A%')
		likeStatement = self._buildLikeStatement(self.selectedCharacter, self.searchTerm)

		#build statement for missing filters
		missingFilterStatement = self._buildMissingFilterStatement(self.config)
		if(missingFilterStatement != ''):
			likeStatement = likeStatement + ' AND ' + missingFilterStatement
		#set a limit of games to show
		maxNumGamesIndex = self.Settings.getSetting(util.SETTING_RCB_MAXNUMGAMESTODISPLAY)
		maxNumGames = util.MAXNUMGAMES_ENUM[int(maxNumGamesIndex)]

		games = Game(self.gdb).getFilteredGames(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId, self.selectedPublisherId, isFavorite, likeStatement, maxNumGames)

		if(games == None):
			Logutil.log("games == None in showGames", util.LOG_LEVEL_WARNING)
			return

		fileDict = self.getFileDictForGamelist()
		self.cacheMediaPathsForSelection(self.selectedConsoleId)

		timestamp2 = time.clock()
		diff = (timestamp2 - timestamp1) * 1000
		print "showGamesFromFile: load %d games from db in %d ms" % (len(games), diff)

		self.writeMsg(util.localize(32121))

		self.clearList()
		self.rcb_playList.clear()
		
		showFavoriteStars = self.Settings.getSetting(util.SETTING_RCB_SHOWFAVORITESTARS).upper() == 'TRUE'

		for gameRow in games:

			romCollection = None
			try:
				romCollection = self.config.romCollections[str(gameRow[util.GAME_romCollectionId])]
			except KeyError:
				Logutil.log('Cannot get rom collection with id: ' + str(gameRow[util.GAME_romCollectionId]), util.LOG_LEVEL_ERROR)

			try:
				#create ListItem
				item = xbmcgui.ListItem(gameRow[util.ROW_NAME], str(gameRow[util.ROW_ID]))
				item.setProperty('gameId', helper.saveReadString(gameRow[util.ROW_ID]))

				#favorite handling
				isFavorite = helper.saveReadString(gameRow[util.GAME_isFavorite])
				if(isFavorite == '1' and showFavoriteStars):
					item.setProperty('isfavorite', '1')
				else:
					item.setProperty('isfavorite', '')
				#0 = cacheAll: load all game data at once
				if(self.cachingOption == 0):
					self.setAllItemDataFromFile(item, gameRow, self.fileDict, romCollection)
								
				self.addItem(item)

			except Exception, (exc):
				Logutil.log('Error loading game: %s' % str(exc), util.LOG_LEVEL_ERROR)

		xbmc.executebuiltin("Container.SortDirection")

		self.writeMsg("")

		timestamp3 = time.clock()
		diff = (timestamp3 - timestamp2) * 1000
		Logutil.log("showGamesFromFile: load %i games to list in %d ms" % (self.getListSize(), diff), util.LOG_LEVEL_INFO)

		Logutil.log("End showGamesFromFile" , util.LOG_LEVEL_INFO)
		
		
	def showGames(self):
		if self.__useRefactoredView:
			self.showGamesNew()
			return
		
		if self.__loadImagesFromFile:
			self.showGamesFromFile()
			return

		Logutil.log("Begin showGamesFromDB" , util.LOG_LEVEL_INFO)

		self.lastPosition = -1

		preventUnfilteredSearch = self.Settings.getSetting(util.SETTING_RCB_PREVENTUNFILTEREDSEARCH).upper() == 'TRUE'

		if(preventUnfilteredSearch):
			if(self.selectedCharacter == util.localize(32120) and self.selectedConsoleId == 0 and self.selectedGenreId == 0 and self.selectedYearId == 0 and self.selectedPublisherId == 0):
				Logutil.log("preventing unfiltered search", util.LOG_LEVEL_WARNING)
				return

		isFavorite = 0
		isFavoriteButton = self.getControlById(CONTROL_BUTTON_FAVORITE)
		if(isFavoriteButton != None):
			if(bool(isFavoriteButton.isSelected())):
				isFavorite = 1

		timestamp1 = time.clock()

		# build statement for character search (where name LIKE 'A%')
		likeStatement = self._buildLikeStatement(self.selectedCharacter, self.searchTerm)

		#build statement for missing filters
		missingFilterStatement = self._buildMissingFilterStatement(self.config)
		if(missingFilterStatement != ''):
			likeStatement = likeStatement + ' AND ' + missingFilterStatement
		#set a limit of games to show
		maxNumGamesIndex = self.Settings.getSetting(util.SETTING_RCB_MAXNUMGAMESTODISPLAY)
		maxNumGames = util.MAXNUMGAMES_ENUM[int(maxNumGamesIndex)]

		games = Game(self.gdb).getFilteredGames(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId, self.selectedPublisherId, isFavorite, likeStatement, maxNumGames)

		if(games == None):
			Logutil.log("games == None in showGames", util.LOG_LEVEL_WARNING)
			return

		fileDict = self.getFileDictForGamelist()

		timestamp2 = time.clock()
		diff = (timestamp2 - timestamp1) * 1000
		print "showGamesFromDB: load %d games from db in %d ms" % (len(games), diff)

		self.writeMsg(util.localize(32121))

		self.clearList()
		self.rcb_playList.clear()

		count = 0
		for gameRow in games:

			romCollection = None
			try:
				romCollection = self.config.romCollections[str(gameRow[util.GAME_romCollectionId])]
			except:
				Logutil.log('Cannot get rom collection with id: ' + str(gameRow[util.GAME_romCollectionId]), util.LOG_LEVEL_ERROR)

			try:
				#images for gamelist
				# icon
				imageGameList = self.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameList, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict)
				# thumb
				imageGameListSelected = self.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameListSelected, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict)

				#create ListItem
				item = xbmcgui.ListItem(gameRow[util.ROW_NAME], str(gameRow[util.ROW_ID]))
				item.setProperty('gameId', helper.saveReadString(gameRow[util.ROW_ID]))

				#favorite handling
				showFavoriteStars = self.Settings.getSetting(util.SETTING_RCB_SHOWFAVORITESTARS).upper() == 'TRUE'
				isFavorite = helper.saveReadString(gameRow[util.GAME_isFavorite])
				if(isFavorite == '1' and showFavoriteStars):
					item.setProperty('isfavorite', '1')
				else:
					item.setProperty('isfavorite', '')
				#0 = cacheAll: load all game data at once
				if(self.cachingOption == 0):
					self.setAllItemData(item, gameRow, self.fileDict, romCollection)

				#self.addItem(item, False)
				self.addItem(item)

				# add video to playlist for fullscreen support
				#self.loadVideoFiles(item, gameRow, imageGameList, imageGameListSelected, count, fileDict, romCollection)

				count = count + 1
			except Exception, (exc):
				Logutil.log('Error loading game: %s' % str(exc), util.LOG_LEVEL_ERROR)

		xbmc.executebuiltin("Container.SortDirection")

		self.writeMsg("")

		timestamp3 = time.clock()
		diff = (timestamp3 - timestamp2) * 1000
		Logutil.log("showGamesFromDB: load %i games to list in %d ms" % (self.getListSize(), diff), util.LOG_LEVEL_INFO)

		Logutil.log("End showGamesFromDB" , util.LOG_LEVEL_INFO)


	def showGameInfo(self):
		
		if self.__useRefactoredView:
			self.showGameInfoNew()
			return
		
		if self.__loadImagesFromFile:
			self.showGameInfoFromFile()
			return

		Logutil.log("Begin showGameInfo" , util.LOG_LEVEL_INFO)

		self.writeMsg("")

		if(self.getListSize() == 0):
			Logutil.log("ListSize == 0 in showGameInfo", util.LOG_LEVEL_WARNING)
			return

		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0

		selectedGame, gameRow = self.getGameByPosition(self.gdb, pos)
		if(selectedGame == None or gameRow == None):
			Logutil.log("game == None in showGameInfo", util.LOG_LEVEL_WARNING)
			return

		romCollection = None
		try:
			romCollection = self.config.romCollections[str(gameRow[util.GAME_romCollectionId])]
		except:
			Logutil.log('Cannot get rom collection with id: ' + str(gameRow[util.GAME_romCollectionId]), util.LOG_LEVEL_ERROR)

		if(self.cachingOption == 0):
			fileDict = self.fileDict
		else:
			fileDict = self.getFileDictByGameRow(gameRow)

		#gameinfos are already loaded with cachingOption 0 (cacheAll)
		if(self.cachingOption > 0):
			self.loadGameInfos(gameRow, selectedGame, pos, romCollection, fileDict)

		video = selectedGame.getProperty('gameplaymain')
		if(video == "" or video == None or not romCollection.autoplayVideoMain):
			if(self.player.isPlayingVideo()):
				self.player.stop()

		Logutil.log("End showGameInfo" , util.LOG_LEVEL_INFO)
		
		
	def showGameInfoFromFile(self):
		Logutil.log("Begin showGameInfoFromFile" , util.LOG_LEVEL_INFO)

		self.writeMsg("")

		if(self.getListSize() == 0):
			Logutil.log("ListSize == 0 in showGameInfoFromFile", util.LOG_LEVEL_WARNING)
			return

		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0

		selectedGame, gameRow = self.getGameByPosition(self.gdb, pos)
		if(selectedGame == None or gameRow == None):
			Logutil.log("game == None in showGameInfoFromFile", util.LOG_LEVEL_WARNING)
			return

		romCollection = None
		try:
			romCollection = self.config.romCollections[str(gameRow[util.GAME_romCollectionId])]
		except:
			Logutil.log('Cannot get rom collection with id: ' + str(gameRow[util.GAME_romCollectionId]), util.LOG_LEVEL_ERROR)

		if(self.cachingOption == 0):
			fileDict = self.fileDict
		else:
			fileDict = self.getFileDictByGameRow(gameRow)

		#gameinfos are already loaded with cachingOption 0 (cacheAll)
		if(self.cachingOption > 0):
			self.loadGameInfosFromFile(gameRow, selectedGame, pos, fileDict)

		video = selectedGame.getProperty('gameplaymain')
		if(video == "" or video == None or not romCollection.autoplayVideoMain):
			if(self.player.isPlayingVideo()):
				self.player.stop()

		Logutil.log("End showGameInfoFromFile" , util.LOG_LEVEL_INFO)

	
	def showGameInfoNew(self):
		''' Called when a game is selected in the list; retrieves the object and sets the artwork data. This is to
		    work around the fact that we may delay loading it in the main list population as a caching mechanism
		'''
		Logutil.log("Begin showGameInfoNew", util.LOG_LEVEL_INFO)

		starttime = time.clock()

		self.writeMsg("")

		selectedGame = self.getSelectedItem()

		if selectedGame is None:
			Logutil.log("selectedGame == None in getGameByPosition", util.LOG_LEVEL_WARNING)
			return

		Logutil.log('Selected game with property gameId {0}, romCollectionId {1}'.format(selectedGame.getProperty('gameId'),
				selectedGame.getProperty('romCollectionId')), util.LOG_LEVEL_DEBUG)

		try:
			romCollection = self.config.romCollections[selectedGame.getProperty('romCollectionId')]
		except Exception as err:
			print err.message
			Logutil.log('Cannot get rom collection with id: ' + str(selectedGame.getProperty('romCollectionId')), util.LOG_LEVEL_ERROR)
			return

		# Set the artwork to be displayed
		images = romCollection.getImagesForGameListViewSelected()
		f = File(self.gdb)
		for k, v in images.items():
			try:
				imagepath = f.getFilenameByGameIdAndTypeId(selectedGame.getProperty('gameId'), v.id)
				Logutil.log('Looking for {0}, imagetype {1}, found {2}'.format(k, v.name, imagepath), util.LOG_LEVEL_DEBUG)
				selectedGame.setArt({k: imagepath})

			except Exception as err:
				Logutil.log('Unable to set art: ' + repr(err), util.LOG_LEVEL_WARNING)

		# FIXME TODO Check if video works
		video = selectedGame.getProperty('gameplaymain')
		if video == "" or video is None or not romCollection.autoplayVideoMain:
			if self.player.isPlayingVideo():
				self.player.stop()

		endtime = time.clock()
		diff = (endtime - starttime) * 1000
		Logutil.log('Time taken to showGameInfo using new format: {0}ms'.format(diff), util.LOG_LEVEL_INFO)

		Logutil.log("End showGameInfoNew" , util.LOG_LEVEL_INFO)

	def getSelectedItem(self):
		if self.getListSize() == 0:
			Logutil.log("ListSize == 0 in getSelectedItem", util.LOG_LEVEL_WARNING)
			return

		pos = self.getCurrentListPosition()
		if pos == -1:
			pos = 0

		return self.getListItem(pos)

	def launchEmu(self):

		Logutil.log("Begin launchEmu" , util.LOG_LEVEL_INFO)

		if(self.getListSize() == 0):
			Logutil.log("ListSize == 0 in launchEmu", util.LOG_LEVEL_WARNING)
			return

		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0
		selectedGame = self.getListItem(pos)

		if(selectedGame == None):
			Logutil.log("selectedGame == None in launchEmu", util.LOG_LEVEL_WARNING)
			return

		gameId = selectedGame.getProperty('gameId')
		Logutil.log("launching game with id: " + str(gameId), util.LOG_LEVEL_INFO)

		#stop video (if playing)
		if(self.player.isPlayingVideo()):
			#self.player.stoppedByRCB = True
			self.player.stop()

		launcher = RCBLauncher()
		launcher.launchEmu(self.gdb, self, gameId, self.config, selectedGame)
		Logutil.log("End launchEmu" , util.LOG_LEVEL_INFO)


	#FIXME TODO: remove fullscreen support (build fullscreen video views instead)
	def startFullscreenVideo(self):
		Logutil.log("startFullscreenVideo" , util.LOG_LEVEL_INFO)

		self.fullScreenVideoStarted = True

		#Hack: On xbox the list is cleared before starting the player
		if (os.environ.get("OS", "xbox") == "xbox"):
			self.saveViewState(True)

		pos = self.getCurrentListPosition()

		#missing videos may lead to a wrong offset. We have to take care with our own hash
		if(len(self.playlistOffsets) != 0):
			try:
				pos = self.playlistOffsets[pos]
			except:
				Logutil.log("Error while reading playlist offset", util.LOG_LEVEL_WARNING)
			self.playlistOffsets = {}

		#stop video (if playing)
		if(self.player.isPlayingVideo()):
			#self.player.stoppedByRCB = True
			self.player.stop()
		
		self.player.play(self.rcb_playList, windowed=False, startpos=pos)		

		self.fullScreenVideoStarted = False


	def updateDB(self):
		Logutil.log("Begin updateDB" , util.LOG_LEVEL_INFO)
		self.importGames(None, False)
		Logutil.log("End updateDB" , util.LOG_LEVEL_INFO)


	def rescrapeGames(self, romCollections):
		Logutil.log("Begin rescrapeGames" , util.LOG_LEVEL_INFO)
		self.importGames(romCollections, True)
		self.config.readXml()
		Logutil.log("End rescrapeGames" , util.LOG_LEVEL_INFO)


	def importGames(self, romCollections, isRescrape):
		self.saveViewState(False)
		self.clearList()
		self.clearCache()
		self.checkImport(3, romCollections, isRescrape)
		self.cacheItems()
		self.updateControls(True)
		self.loadViewState()


	def updateGamelist(self):
		#only update controls if they are available
		if(self.initialized):
			self.showGames()
			focusControl = self.getControlById(CONTROL_GAMES_GROUP_START)
			if(focusControl != None):
				self.setFocus(focusControl)
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			self.showGameInfo()


	def deleteGame(self, gameID):
		Logutil.log("Begin deleteGame" , util.LOG_LEVEL_INFO)

		Logutil.log("Delete Year" , util.LOG_LEVEL_INFO)
		Year(self.gdb).delete(gameID)
		Logutil.log("Delete Publisher" , util.LOG_LEVEL_INFO)
		Publisher(self.gdb).delete(gameID)
		Logutil.log("Delete Developer" , util.LOG_LEVEL_INFO)
		Developer(self.gdb).delete(gameID)
		Logutil.log("Delete Genre" , util.LOG_LEVEL_INFO)
		Genre(self.gdb).delete(gameID)
		Logutil.log("Delete File" , util.LOG_LEVEL_INFO)
		File(self.gdb).delete(gameID)
		Logutil.log("Delete Game" , util.LOG_LEVEL_INFO)
		Game(self.gdb).delete(gameID)

		Logutil.log("End deleteGame" , util.LOG_LEVEL_INFO)


	def deleteRCGames(self, rcID, rcDelete, rDelete):
		Logutil.log("begin Delete Games" , util.LOG_LEVEL_INFO)
		count = 0

		rcList = Game(self.gdb).getFilteredGames(rcID, 0, 0, 0, 0, '0 = 0')
		progressDialog = dialogprogress.ProgressDialogGUI()
		progressDialog.itemCount = len(rcList)

		if(rcList != None):
			progDialogRCDelStat	 = util.localize(32104) + " (%i / %i)" % (count, progressDialog.itemCount)
			progressDialog.writeMsg(util.localize(32105), progDialogRCDelStat, "", count)
			for items in rcList:
				count = count + 1
				progDialogRCDelStat	 = util.localize(32104) + " (%i / %i)" % (count, progressDialog.itemCount)
				progressDialog.writeMsg("", progDialogRCDelStat, "", count)
				self.deleteGame(items[util.ROW_ID])
			if(len(rcList) > 0):
				progressDialog.writeMsg("", util.localize(32106), "", count)
			else:
				progressDialog.writeMsg(util.localize(32106), "", "", count)
			time.sleep(1)
			self.gdb.commit()
			self.config = Config(None)
			self.config.readXml()
			self.clearList()
			self.rcb_playList.clear()
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			self.updateControls(True)
			if(rDelete):
				self.selectedConsoleId = self.setFilterSelection(CONTROL_CONSOLES, self.selectedConsoleIndex)
				self.setFilterSelection(CONTROL_GAMES_GROUP_START, 0)
			self.showGames()

		rcList = None
		Logutil.log("end Delete Games" , util.LOG_LEVEL_INFO)


	def cleanDB(self):
		Logutil.log("Begin cleanDB" , util.LOG_LEVEL_INFO)

		count = 0
		removeCount = 0
		list = File(self.gdb).getFilesList()
		progressDialog2 = dialogprogress.ProgressDialogGUI()
		progressDialog2.itemCount = len(list)
		progDialogCleanStat	 = util.localize(32107) + " (%i / %i)" % (count, progressDialog2.itemCount)
		progressDialog2.writeMsg(util.localize(32108), progDialogCleanStat, "")
		if(list != None):
			for items in list:
				count = count + 1
				progDialogCleanStat	 = util.localize(32107) + " (%i / %i)" % (count, progressDialog2.itemCount)
				progressDialog2.writeMsg("", progDialogCleanStat, "", count)
				if (os.path.exists(items[util.ROW_NAME]) != True):
					if(items[util.FILE_fileTypeId] == 0):
						self.deleteGame(items[util.FILE_parentId])
					else:
						File(self.gdb).deleteByFileId(items[util.ROW_ID])
					removeCount = removeCount + 1
			progressDialog2.writeMsg("", util.localize(32109), "", count)
			self.gdb.compact()
			time.sleep(.5)
			progressDialog2.writeMsg("", util.localize(32110), "", count)
			time.sleep(1)
			self.showGames()
		list = None
		Logutil.log("End cleanDB" , util.LOG_LEVEL_INFO)


	def showGameInfoDialog(self):
		""" Called when a game is opened in the GameInfo dialog """
		Logutil.log("Begin showGameInfoDialog", util.LOG_LEVEL_INFO)

		if(self.getListSize() == 0):
			Logutil.log("ListSize == 0 in saveViewState", util.LOG_LEVEL_WARNING)
			return

		selectedGameIndex = self.getCurrentListPosition()
		if(selectedGameIndex == -1):
			selectedGameIndex = 0
		selectedGame = self.getListItem(selectedGameIndex)
		if(selectedGame == None):
			Logutil.log("selectedGame == None in showGameInfoDialog", util.LOG_LEVEL_WARNING)
			return

		gameId = selectedGame.getProperty('gameId')

		fileDict = self.getFileDictForGamelist()

		self.saveViewMode()

		if(self.player.isPlayingVideo()):
			self.player.stop()

		self.gameinfoDialogOpen = True

		constructorParam = "720p"

		import dialoggameinfo
		try:
			gid = dialoggameinfo.UIGameInfoView("script-RCB-gameinfo.xml", util.getAddonInstallPath(), util.getConfiguredSkin(), constructorParam, gdb=self.gdb, gameId=gameId, listItem=selectedGame,
				consoleId=self.selectedConsoleId, genreId=self.selectedGenreId, yearId=self.selectedYearId, publisherId=self.selectedPublisherId, selectedGameIndex=selectedGameIndex,
				consoleIndex=self.selectedConsoleIndex, genreIndex=self.selectedGenreIndex, yearIndex=self.selectedYearIndex, publisherIndex=self.selectedPublisherIndex,
				selectedCharacter=self.selectedCharacter, selectedCharacterIndex=self.selectedCharacterIndex, controlIdMainView=self.selectedControlId, fileDict=fileDict, config=self.config, settings=self.Settings,
				fileTypeGameplay=self.fileTypeGameplay)
		except:
			gid = dialoggameinfo.UIGameInfoView("script-RCB-gameinfo.xml", util.getAddonInstallPath(), "Default", constructorParam, gdb=self.gdb, gameId=gameId, listItem=selectedGame,
				consoleId=self.selectedConsoleId, genreId=self.selectedGenreId, yearId=self.selectedYearId, publisherId=self.selectedPublisherId, selectedGameIndex=selectedGameIndex,
				consoleIndex=self.selectedConsoleIndex, genreIndex=self.selectedGenreIndex, yearIndex=self.selectedYearIndex, publisherIndex=self.selectedPublisherIndex,
				selectedCharacter=self.selectedCharacter, selectedCharacterIndex=self.selectedCharacterIndex, controlIdMainView=self.selectedControlId, fileDict=fileDict, config=self.config, settings=self.Settings,
				fileTypeGameplay=self.fileTypeGameplay)

		del gid

		self.gameinfoDialogOpen = False

		#force restart of video if available
		#selectedGame.setProperty('gameplaymain', video)
		self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))

		Logutil.log("End showGameInfoDialog", util.LOG_LEVEL_INFO)


	def showContextMenu(self):

		constructorParam = "720p"
		cm = dialogcontextmenu.ContextMenuDialog("script-RCB-contextmenu.xml", util.getAddonInstallPath(), util.getConfiguredSkin(), constructorParam, gui=self)
		del cm



	"""
	******************
	* HELPER METHODS *
	******************
	"""

	def getFileDictForGamelist(self):
		# 0 = cacheAll
		if(self.cachingOption == 0):
			fileDict = self.fileDict
		else:
			fileRows = File(self.gdb).getFilesForGamelist(self.config.fileTypeIdsForGamelist)
			if(fileRows == None):
				Logutil.log("fileRows == None in showGames", util.LOG_LEVEL_WARNING)
				return

			fileDict = helper.cacheFiles(fileRows)

		return fileDict


	def getFileForControl(self, fileTypes, gameId, publisherId, developerId, romCollectionId, fileDict):
		files = helper.getFilesByControl_Cached(self.gdb, fileTypes, gameId, publisherId, developerId, romCollectionId, fileDict)
		if(files != None and len(files) != 0):
			file = files[0]
		else:
			file = ""

		Logutil.log("Found file {0}".format(file), util.LOG_LEVEL_DEBUG)

		return file
	
	
	def getFileForControl_New(self, fileTypes, romCollection, mediaPathsDict, gamenameFromFile, isVideo=False):
		
		Logutil.log("begin getFileForControl_New", util.LOG_LEVEL_DEBUG)
		
		for fileType in fileTypes:
			#log.debug("fileType: " +str(fileType.name))
			
			if(fileType.parent != util.FILETYPEPARENT_GAME):
				continue
						
			#log.debug("before rc.getMediaPathByType")
			mediaPath = romCollection.getMediaPathByType(fileType.name)
			#log.debug("after rc.getMediaPathByType")
			
			#log.debug("mediaPath: %s" %mediaPath)
			if(not mediaPath):
				continue
			
			pathnameFromFile = mediaPath.replace("%GAME%", gamenameFromFile)
			#log.debug("resolved path from rom file name: {0}".format(pathnameFromFile))
						
			mediaPathsList = mediaPathsDict[fileType.name]
			
			extensionlist = ['png', 'jpg', 'gif']
			if isVideo:
				extensionlist = ['wmv', 'mp4', 'flv']
			for extension in extensionlist:
				path = pathnameFromFile.replace('*', extension)
				#log.debug("looking for image: {0}".format(path))
				if os.path.basename(path) in mediaPathsList:
				#if xbmcvfs.exists(path):
					#log.debug("image found")
					#log.info("end getFileForControl_New")
					Logutil.log("end getFileForControl_New", util.LOG_LEVEL_INFO)
					return path
				
		Logutil.log("end getFileForControl_New", util.LOG_LEVEL_DEBUG)
		return ""


	def loadVideoFiles(self, listItem, gameRow, romCollection, mediaPathsDict, gamenameFromFile):

		Logutil.log("begin loadVideoFiles", util.LOG_LEVEL_INFO)

		#check if we should use autoplay video
		if(romCollection.autoplayVideoMain):
			listItem.setProperty('autoplayvideomain', 'true')
		else:
			listItem.setProperty('autoplayvideomain', '')

		#get video window size
		if (romCollection.imagePlacingMain.name.startswith('gameinfosmall')):
			listItem.setProperty('videosizesmall', 'small')
			listItem.setProperty('videosizebig', '')
		else:
			listItem.setProperty('videosizebig', 'big')
			listItem.setProperty('videosizesmall', '')

		if(self.fileTypeGameplay == None):
			Logutil.log("fileType gameplay == None. No video loaded.", util.LOG_LEVEL_INFO)

		#load gameplay videos
		#HACK: other video types are not supported
		video = self.getFileForControl_New((self.fileTypeGameplay,), romCollection, mediaPathsDict, gamenameFromFile, True)
		if video:
			#make video accessible via UI
			listItem.setProperty('gameplaymain', video)
			
		Logutil.log("end loadVideoFiles", util.LOG_LEVEL_INFO)


	def getGameByPosition(self, gdb, pos):
		Logutil.log("size = %i" % self.getListSize(), util.LOG_LEVEL_DEBUG)
		Logutil.log("pos = %s" % pos, util.LOG_LEVEL_DEBUG)

		selectedGame = self.getListItem(pos)
		if(selectedGame == None):
			Logutil.log("selectedGame == None in getGameByPosition", util.LOG_LEVEL_WARNING)
			return None, None

		gameId = selectedGame.getProperty('gameId')
		if(gameId == ''):
			Logutil.log("gameId is empty in getGameByPosition", util.LOG_LEVEL_WARNING)
			return None, None

		gameRow = Game(gdb).getObjectById(gameId)

		if(gameRow == None):
			Logutil.log("gameId = %s" % gameId, util.LOG_LEVEL_WARNING)
			Logutil.log("gameRow == None in getGameByPosition", util.LOG_LEVEL_WARNING)
			return None, None

		return selectedGame, gameRow


	def getGameId(self, gdb, pos):
		Logutil.log("pos = %s" % pos, util.LOG_LEVEL_INFO)

		selectedGame = self.getListItem(pos)

		if(selectedGame == None):
			Logutil.log("selectedGame == No game selected", util.LOG_LEVEL_WARNING)
			return None

		gameId = selectedGame.getProperty('gameId')

		if(gameId == None):
			Logutil.log("No Game Id Found", util.LOG_LEVEL_WARNING)
			return None

		Logutil.log("gameId = " + gameId, util.LOG_LEVEL_INFO)

		return gameId


	def loadGameInfosFromFile(self, gameRow, selectedGame, pos, fileDict):
		Logutil.log("begin loadGameInfosFromFile", util.LOG_LEVEL_DEBUG)
		Logutil.log("gameRow = " + str(gameRow), util.LOG_LEVEL_DEBUG)

		if(self.getListSize() == 0):
			Logutil.log("ListSize == 0 in loadGameInfosFromFile", util.LOG_LEVEL_WARNING)
			return
		
		romCollection = self.config.romCollections[str(gameRow[util.GAME_romCollectionId])]

		# > 1: cacheItem, cacheItemAndNext
		if(self.cachingOption > 1):
			self.setAllItemDataFromFile(selectedGame, gameRow, fileDict, romCollection)

		# > 2: cacheItemAndNext
		if(self.cachingOption > 2):
			#prepare items before and after actual position
			#go 5 items back and forward to make sure that thumb lists do not look bad
			for i in range(0, 5):
				
				posBefore = pos - i
				if(posBefore < 0):
					posBefore = self.getListSize() - i
	
				selectedGame, gameRow = self.getGameByPosition(self.gdb, posBefore)
				if(selectedGame == None or gameRow == None):
					continue
				
				romCollection = self.config.romCollections[str(gameRow[util.GAME_romCollectionId])]
				
				fileDict = self.getFileDictByGameRow(gameRow)
				self.setAllItemDataFromFile(selectedGame, gameRow, fileDict, romCollection)
	
				posAfter = pos + i
				if(posAfter >= self.getListSize()):
					posAfter = 0
	
				selectedGame, gameRow = self.getGameByPosition(self.gdb, posAfter)
				if(selectedGame == None or gameRow == None):
					continue
				
				romCollection = self.config.romCollections[str(gameRow[util.GAME_romCollectionId])]
								
				fileDict = self.getFileDictByGameRow(gameRow)
				self.setAllItemDataFromFile(selectedGame, gameRow, fileDict, romCollection)

		Logutil.log("end loadGameInfosFromFile", util.LOG_LEVEL_DEBUG)
		
		
	def loadGameInfos(self, gameRow, selectedGame, pos, romCollection, fileDict):
		Logutil.log("begin loadGameInfosFromDb", util.LOG_LEVEL_DEBUG)
		Logutil.log("gameRow = " + str(gameRow), util.LOG_LEVEL_DEBUG)

		if(self.getListSize() == 0):
			Logutil.log("ListSize == 0 in loadGameInfosFromDb", util.LOG_LEVEL_WARNING)
			return

		# > 1: cacheItem, cacheItemAndNext
		if(self.cachingOption > 1):
			self.setAllItemData(selectedGame, gameRow, fileDict, romCollection)

		# > 2: cacheItemAndNext
		if(self.cachingOption > 2):
			#prepare items before and after actual position
			#go 5 items back and forward to make sure that thumb lists do not look bad
			for i in range(0, 5):
				
				posBefore = pos - i
				if(posBefore < 0):
					posBefore = self.getListSize() - i
	
				selectedGame, gameRow = self.getGameByPosition(self.gdb, posBefore)
				if(selectedGame == None or gameRow == None):
					continue
								
				fileDict = self.getFileDictByGameRow(gameRow)
				self.setAllItemData(selectedGame, gameRow, fileDict, romCollection)
	
				posAfter = pos + i
				if(posAfter >= self.getListSize()):
					posAfter = 0
	
				selectedGame, gameRow = self.getGameByPosition(self.gdb, posAfter)
				if(selectedGame == None or gameRow == None):
					continue
				
				fileDict = self.getFileDictByGameRow(gameRow)
				self.setAllItemData(selectedGame, gameRow, fileDict, romCollection)

		Logutil.log("end loadGameInfosFromDb", util.LOG_LEVEL_DEBUG)


	def getFileDictByGameRow(self, gameRow):

		files = File(self.gdb).getFilesByParentIds(gameRow[util.ROW_ID], gameRow[util.GAME_romCollectionId], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId])

		fileDict = helper.cacheFiles(files)

		return fileDict


	def setAllItemDataFromFile(self, item, gameRow, fileDict, romCollection):
		
		mediaPathsDict = self.mediaDict[gameRow[util.GAME_romCollectionId]]
		romfile = helper.getFilenameForGame(gameRow[util.ROW_ID], 0, fileDict)
		gamenameFromFile = romCollection.getGamenameFromFilename(romfile)
		
		item.setArt({
			'icon': self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile),
			'thumb': self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForGameListSelected, romCollection, mediaPathsDict, gamenameFromFile),
			
			IMAGE_CONTROL_BACKGROUND: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewBackground, romCollection, mediaPathsDict, gamenameFromFile),
			IMAGE_CONTROL_GAMEINFO_BIG: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile),

			IMAGE_CONTROL_GAMEINFO_UPPERLEFT: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoUpperLeft, romCollection, mediaPathsDict, gamenameFromFile),
			IMAGE_CONTROL_GAMEINFO_UPPERRIGHT: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoUpperRight, romCollection, mediaPathsDict, gamenameFromFile),
			IMAGE_CONTROL_GAMEINFO_LOWERLEFT: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLowerLeft, romCollection, mediaPathsDict, gamenameFromFile),
			IMAGE_CONTROL_GAMEINFO_LOWERRIGHT: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLowerRight, romCollection, mediaPathsDict, gamenameFromFile),

			IMAGE_CONTROL_GAMEINFO_UPPER: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoUpper, romCollection, mediaPathsDict, gamenameFromFile),
			IMAGE_CONTROL_GAMEINFO_LOWER: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLower, romCollection, mediaPathsDict, gamenameFromFile),
			IMAGE_CONTROL_GAMEINFO_LEFT: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLeft, romCollection, mediaPathsDict, gamenameFromFile),
			IMAGE_CONTROL_GAMEINFO_RIGHT: self.getFileForControl_New(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoRight, romCollection, mediaPathsDict, gamenameFromFile),
		})
		
		#FIXME TODO: remove fullscreen support (build fullscreen video views instead)
		self.loadVideoFiles(item, gameRow, romCollection, mediaPathsDict, gamenameFromFile)

		#set additional properties
		description = helper.saveReadString(gameRow[util.GAME_description])
		if(description == None):
			description = ""
		item.setProperty('plot', description)

		try:
			item.setProperty('romcollection', romCollection.name)
			item.setProperty('console', romCollection.name)
		except:
			pass

		item.setProperty('year', helper.saveReadString(helper.getPropertyFromCache(gameRow, self.yearDict, util.GAME_yearId, util.ROW_NAME)))
		item.setProperty('publisher', helper.saveReadString(helper.getPropertyFromCache(gameRow, self.publisherDict, util.GAME_publisherId, util.ROW_NAME)))
		item.setProperty('developer', helper.saveReadString(helper.getPropertyFromCache(gameRow, self.developerDict, util.GAME_developerId, util.ROW_NAME)))
		item.setProperty('reviewer', helper.saveReadString(helper.getPropertyFromCache(gameRow, self.reviewerDict, util.GAME_reviewerId, util.ROW_NAME)))

		genre = ""
		try:
			#0 = cacheAll: load all game data at once
			if(self.cachingOption == 0):
				genre = self.genreDict[gameRow[util.ROW_ID]]
			else:
				genres = Genre(self.gdb).getGenresByGameId(gameRow[util.ROW_ID])
				if (genres != None):
					for i in range(0, len(genres)):
						genreRow = genres[i]
						genre = '%s%s' %(genre, genreRow[util.ROW_NAME])
						if(i < len(genres) - 1):
							genre = "%s, " %genre
		except:
			pass
		item.setProperty('genre', genre)

		item.setProperty('maxplayers', helper.saveReadString(gameRow[util.GAME_maxPlayers]))
		item.setProperty('rating', helper.saveReadString(gameRow[util.GAME_rating]))
		item.setProperty('votes', helper.saveReadString(gameRow[util.GAME_numVotes]))
		item.setProperty('url', helper.saveReadString(gameRow[util.GAME_url]))
		item.setProperty('region', helper.saveReadString(gameRow[util.GAME_region]))
		item.setProperty('media', helper.saveReadString(gameRow[util.GAME_media]))
		item.setProperty('perspective', helper.saveReadString(gameRow[util.GAME_perspective]))
		item.setProperty('controllertype', helper.saveReadString(gameRow[util.GAME_controllerType]))
		item.setProperty('originaltitle', helper.saveReadString(gameRow[util.GAME_originalTitle]))
		item.setProperty('alternatetitle', helper.saveReadString(gameRow[util.GAME_alternateTitle]))
		item.setProperty('translatedby', helper.saveReadString(gameRow[util.GAME_translatedBy]))
		item.setProperty('version', helper.saveReadString(gameRow[util.GAME_version]))

		item.setProperty('playcount', helper.saveReadString(gameRow[util.GAME_launchCount]))

		return item
	
	
	def setAllItemData(self, item, gameRow, fileDict, romCollection):
		item.setArt({
			'icon': self.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameList, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			'thumb': self.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameListSelected, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			
			IMAGE_CONTROL_BACKGROUND: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewBackground, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			IMAGE_CONTROL_GAMEINFO_BIG: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),

			IMAGE_CONTROL_GAMEINFO_UPPERLEFT: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoUpperLeft, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			IMAGE_CONTROL_GAMEINFO_UPPERRIGHT: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoUpperRight, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			IMAGE_CONTROL_GAMEINFO_LOWERLEFT: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLowerLeft, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			IMAGE_CONTROL_GAMEINFO_LOWERRIGHT: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLowerRight, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),

			IMAGE_CONTROL_GAMEINFO_UPPER: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoUpper, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			IMAGE_CONTROL_GAMEINFO_LOWER: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLower, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			IMAGE_CONTROL_GAMEINFO_LEFT: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLeft, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			IMAGE_CONTROL_GAMEINFO_RIGHT: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainViewGameInfoRight, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),

			IMAGE_CONTROL_1: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainView1, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			IMAGE_CONTROL_2: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainView2, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
			IMAGE_CONTROL_3: self.getFileForControl(romCollection.imagePlacingMain.fileTypesForMainView3, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], fileDict),
		})

		#set additional properties
		description = helper.saveReadString(gameRow[util.GAME_description])
		if(description == None):
			description = ""
		item.setProperty('plot', description)

		try:
			item.setProperty('romcollection', romCollection.name)
			item.setProperty('console', romCollection.name)
		except:
			pass

		item.setProperty('year', helper.saveReadString(helper.getPropertyFromCache(gameRow, self.yearDict, util.GAME_yearId, util.ROW_NAME)))
		item.setProperty('publisher', helper.saveReadString(helper.getPropertyFromCache(gameRow, self.publisherDict, util.GAME_publisherId, util.ROW_NAME)))
		item.setProperty('developer', helper.saveReadString(helper.getPropertyFromCache(gameRow, self.developerDict, util.GAME_developerId, util.ROW_NAME)))
		item.setProperty('reviewer', helper.saveReadString(helper.getPropertyFromCache(gameRow, self.reviewerDict, util.GAME_reviewerId, util.ROW_NAME)))

		genre = ""
		try:
			#0 = cacheAll: load all game data at once
			if(self.cachingOption == 0):
				genre = self.genreDict[gameRow[util.ROW_ID]]
			else:
				genres = Genre(self.gdb).getGenresByGameId(gameRow[util.ROW_ID])
				if (genres != None):
					for i in range(0, len(genres)):
						genreRow = genres[i]
						genre += genreRow[util.ROW_NAME]
						if(i < len(genres) - 1):
							genre += ", "
		except:
			pass
		item.setProperty('genre', genre)

		item.setProperty('maxplayers', helper.saveReadString(gameRow[util.GAME_maxPlayers]))
		item.setProperty('rating', helper.saveReadString(gameRow[util.GAME_rating]))
		item.setProperty('votes', helper.saveReadString(gameRow[util.GAME_numVotes]))
		item.setProperty('url', helper.saveReadString(gameRow[util.GAME_url]))
		item.setProperty('region', helper.saveReadString(gameRow[util.GAME_region]))
		item.setProperty('media', helper.saveReadString(gameRow[util.GAME_media]))
		item.setProperty('perspective', helper.saveReadString(gameRow[util.GAME_perspective]))
		item.setProperty('controllertype', helper.saveReadString(gameRow[util.GAME_controllerType]))
		item.setProperty('originaltitle', helper.saveReadString(gameRow[util.GAME_originalTitle]))
		item.setProperty('alternatetitle', helper.saveReadString(gameRow[util.GAME_alternateTitle]))
		item.setProperty('translatedby', helper.saveReadString(gameRow[util.GAME_translatedBy]))
		item.setProperty('version', helper.saveReadString(gameRow[util.GAME_version]))

		item.setProperty('playcount', helper.saveReadString(gameRow[util.GAME_launchCount]))

		return item


	def checkImport(self, doImport, romCollections, isRescrape):

		#doImport: 0=nothing, 1=import Settings and Games, 2=import Settings only, 3=import games only
		if(doImport == 0):
			return

		#Show options dialog if user wants to see it
		#Import is started from dialog
		showImportOptionsDialog = self.Settings.getSetting(util.SETTING_RCB_SHOWIMPORTOPTIONSDIALOG).upper() == 'TRUE'
		if(showImportOptionsDialog):
			constructorParam = "720p"
			iod = dialogimportoptions.ImportOptionsDialog("script-RCB-importoptions.xml", util.getAddonInstallPath(), util.getConfiguredSkin(), constructorParam, gui=self, romCollections=romCollections, isRescrape=isRescrape)
			del iod
		else:
			message = util.localize(32118)

			dialog = xbmcgui.Dialog()
			retGames = dialog.yesno(util.localize(32999), util.localize(32500), message)
			if(retGames == True):
				#Import Games
				if(romCollections == None):
					self.doImport(self.config.romCollections, isRescrape)
				else:
					self.doImport(romCollections, isRescrape)


	def doImport(self, romCollections, isRescrape):
		progressDialog = dialogprogress.ProgressDialogGUI()
		progressDialog.writeMsg(util.localize(32111), "", "")

		updater = dbupdate.DBUpdate()
		updater.updateDB(self.gdb, progressDialog, romCollections, self.Settings, isRescrape)
		del updater
		progressDialog.writeMsg("", "", "", -1)
		del progressDialog


	def checkUpdateInProgress(self):

		Logutil.log("checkUpdateInProgress" , util.LOG_LEVEL_INFO)

		scrapeOnStartupAction = self.Settings.getSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION)
		Logutil.log("scrapeOnStartupAction = " + str(scrapeOnStartupAction) , util.LOG_LEVEL_INFO)

		if (scrapeOnStartupAction == 'update'):
			retCancel = xbmcgui.Dialog().yesno(util.localize(32999), util.localize(32112), util.localize(32113))
			if(retCancel == True):
				self.Settings.setSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION, 'cancel')
			return True

		elif (scrapeOnStartupAction == 'cancel'):
			xbmcgui.Dialog().ok(util.localize(32999), util.localize(32114), util.localize(32115))

			#HACK: Assume that there is a problem with canceling the action
			#self.Settings.setSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION, 'nothing')

			return True

		return False

	def saveViewState(self, isOnExit):

		Logutil.log("Begin saveViewState" , util.LOG_LEVEL_INFO)

		if(self.getListSize() == 0):
			Logutil.log("ListSize == 0 in saveViewState", util.LOG_LEVEL_WARNING)
			return

		selectedGameIndex = self.getCurrentListPosition()
		if(selectedGameIndex == -1):
			selectedGameIndex = 0
		if(selectedGameIndex == None):
			Logutil.log("selectedGameIndex == None in saveViewState", util.LOG_LEVEL_WARNING)
			return

		self.saveViewMode()

		helper.saveViewState(self.gdb, isOnExit, util.VIEW_MAINVIEW, selectedGameIndex, self.selectedConsoleIndex, self.selectedGenreIndex, self.selectedPublisherIndex,
			self.selectedYearIndex, self.selectedCharacterIndex, self.selectedControlId, None, self.Settings)

		Logutil.log("End saveViewState" , util.LOG_LEVEL_INFO)


	def saveViewMode(self):

		Logutil.log("Begin saveViewMode" , util.LOG_LEVEL_INFO)

		view_mode = ""
		for id in range(CONTROL_GAMES_GROUP_START, CONTROL_GAMES_GROUP_END + 1):
			try:
				if xbmc.getCondVisibility("Control.IsVisible(%i)" % id):
					view_mode = repr(id)
					break
			except:
				pass

		self.Settings.setSetting(util.SETTING_RCB_VIEW_MODE, view_mode)

		#favorites
		controlFavorites = self.getControlById(CONTROL_BUTTON_FAVORITE)
		if(controlFavorites != None):
			self.Settings.setSetting(util.SETTING_RCB_FAVORITESSELECTED, str(controlFavorites.isSelected()))

		#searchText
		controlSearchText = self.getControlById(CONTROL_BUTTON_SEARCH)
		if(controlSearchText != None):
			self.Settings.setSetting(util.SETTING_RCB_SEARCHTEXT, self.searchTerm)

		Logutil.log("End saveViewMode" , util.LOG_LEVEL_INFO)


	def loadViewState(self):

		Logutil.log("Begin loadViewState" , util.LOG_LEVEL_INFO)

		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):
			Logutil.log("rcbSetting == None in loadViewState", util.LOG_LEVEL_WARNING)
			return

		#first load console filter
		self.showConsoles()

		#set console filter selection
		if(rcbSetting[util.RCBSETTING_lastSelectedConsoleIndex] != None):
			self.selectedConsoleId = int(self.setFilterSelection(CONTROL_CONSOLES, rcbSetting[util.RCBSETTING_lastSelectedConsoleIndex]))
			self.selectedConsoleIndex = rcbSetting[util.RCBSETTING_lastSelectedConsoleIndex]

		#load other filters
		self.showGenre()
		if(rcbSetting[util.RCBSETTING_lastSelectedGenreIndex] != None):
			self.selectedGenreId = int(self.setFilterSelection(CONTROL_GENRE, rcbSetting[util.RCBSETTING_lastSelectedGenreIndex]))
			self.selectedGenreIndex = rcbSetting[util.RCBSETTING_lastSelectedGenreIndex]

		self.showYear()
		if(rcbSetting[util.RCBSETTING_lastSelectedYearIndex] != None):
			self.selectedYearId = int(self.setFilterSelection(CONTROL_YEAR, rcbSetting[util.RCBSETTING_lastSelectedYearIndex]))
			self.selectedYearIndex = rcbSetting[util.RCBSETTING_lastSelectedYearIndex]

		self.showPublisher()
		if(rcbSetting[util.RCBSETTING_lastSelectedPublisherIndex] != None):
			self.selectedPublisherId = int(self.setFilterSelection(CONTROL_PUBLISHER, rcbSetting[util.RCBSETTING_lastSelectedPublisherIndex]))
			self.selectedPublisherIndex = rcbSetting[util.RCBSETTING_lastSelectedPublisherIndex]

		self.showCharacterFilter()
		if(rcbSetting[util.RCBSETTING_lastSelectedCharacterIndex] != None):
			self.selectedCharacter = self.setFilterSelection(CONTROL_CHARACTER, rcbSetting[util.RCBSETTING_lastSelectedCharacterIndex])
			self.selectedCharacterIndex = rcbSetting[util.RCBSETTING_lastSelectedCharacterIndex]

		#HACK: Dummy item because loading an empty list crashes XBMC
		item = xbmcgui.ListItem(util.localize(32119), '', '', '')
		#self.addItem(item, False)
		self.addItem(item)

		#reset view mode
		viewModeId = self.Settings.getSetting(util.SETTING_RCB_VIEW_MODE)
		if(viewModeId != None and viewModeId != ''):
			xbmc.executebuiltin("Container.SetViewMode(%i)" % int(viewModeId))

		#searchText
		self.searchTerm = self.Settings.getSetting(util.SETTING_RCB_SEARCHTEXT)
		searchButton = self.getControlById(CONTROL_BUTTON_SEARCH)
		if(self.searchTerm != '' and searchButton != None):
			searchButton.setLabel(util.localize(32117) + ': ' + self.searchTerm)

		#favorites
		isFavoriteButton = self.getControlById(CONTROL_BUTTON_FAVORITE)
		if(isFavoriteButton != None):
			favoritesSelected = self.Settings.getSetting(util.SETTING_RCB_FAVORITESSELECTED)
			isFavoriteButton.setSelected(favoritesSelected == '1')

		# Reset game list
		self.showGames()

		self.setFilterSelection(CONTROL_GAMES_GROUP_START, rcbSetting[util.RCBSETTING_lastSelectedGameIndex])

		#always set focus on game list on start
		focusControl = self.getControlById(CONTROL_GAMES_GROUP_START)
		if(focusControl != None):
			self.setFocus(focusControl)

		self.showGameInfo()

		Logutil.log("End loadViewState" , util.LOG_LEVEL_INFO)


	def setFilterSelection(self, controlId, selectedIndex):

		Logutil.log("Begin setFilterSelection" , util.LOG_LEVEL_DEBUG)

		if(selectedIndex != None):
			control = self.getControlById(controlId)
			if(control == None):
				Logutil.log("control == None in setFilterSelection", util.LOG_LEVEL_WARNING)
				return 0

			if(controlId == CONTROL_GAMES_GROUP_START):
				listSize = self.getListSize()
				if(listSize == 0 or selectedIndex > listSize - 1):
					Logutil.log("ListSize == 0 or index out of range in setFilterSelection", util.LOG_LEVEL_WARNING)
					return 0

				self.setCurrentListPosition(selectedIndex)
				#HACK: selectItem takes some time and we can't read selectedItem immediately
				xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
				selectedItem = self.getListItem(selectedIndex)

			else:
				if(selectedIndex > control.size() - 1):
					Logutil.log("Index out of range in setFilterSelection", util.LOG_LEVEL_WARNING)
					return 0

				control.selectItem(selectedIndex)
				#HACK: selectItem takes some time and we can't read selectedItem immediately
				xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
				selectedItem = control.getSelectedItem()

			if(selectedItem == None):
				Logutil.log("End setFilterSelection" , util.LOG_LEVEL_DEBUG)
				return 0
			label2 = selectedItem.getLabel2()
			Logutil.log("End setFilterSelection" , util.LOG_LEVEL_DEBUG)
			return label2
		else:
			Logutil.log("End setFilterSelection" , util.LOG_LEVEL_DEBUG)
			return 0


	def cacheMediaPathsForSelection(self, consoleId):
		log.info('Begin cacheMediaPathsForSelection')
		
		if self.mediaDict is None:
			self.mediaDict = {}
			
		#if this console is already cached there is nothing to do
		if consoleId in self.mediaDict.keys():
			log.info('MediaPaths for RomCollection %s are already in cache' %str(consoleId))
			return
		
		if(consoleId > 0):
			self.cacheMediaPathsForConsole(consoleId)
			return
		else:
			for rcId in self.config.romCollections.keys():
				if rcId in self.mediaDict.keys():
					log.info('MediaPaths for RomCollection %s are already in cache' %str(rcId))
					continue
				self.cacheMediaPathsForConsole(rcId)
				

	def cacheMediaPathsForConsole(self, consoleId):
		log.info('Begin cacheMediaPathsForConsole')
		log.info('Caching mediaPaths for Rom Collection %s' %str(consoleId))
		
		romCollection = self.config.romCollections[str(consoleId)]
				
		mediaPathDict = {}
		
		for mediaPath in romCollection.mediaPaths:
			dirs, files = xbmcvfs.listdir(os.path.dirname(mediaPath.path))			
			mediaPathDict[mediaPath.fileType.name] = files
			#FIXME TODO check sub directories for platforms with foldernames as gamenames

		self.mediaDict[consoleId] = mediaPathDict
		

	def cacheItems(self):
		Logutil.log("Begin cacheItems" , util.LOG_LEVEL_INFO)

		#cacheAll
		if(self.cachingOption == 0):
			fileRows = File(self.gdb).getAll()
			if(fileRows == None):
				Logutil.log("fileRows == None in cacheItems", util.LOG_LEVEL_WARNING)
				return
			self.fileDict = helper.cacheFiles(fileRows)

		self.yearDict = helper.cacheYears(self.gdb)

		self.publisherDict = helper.cachePublishers(self.gdb)

		self.developerDict = helper.cacheDevelopers(self.gdb)

		self.reviewerDict = helper.cacheReviewers(self.gdb)

		#0 = cacheAll: load all game data at once
		if(self.cachingOption == 0):
			self.genreDict = helper.cacheGenres(self.gdb)
		else:
			self.genreDict = None

		Logutil.log("End cacheItems" , util.LOG_LEVEL_INFO)


	def clearCache(self):
		Logutil.log("Begin clearCache" , util.LOG_LEVEL_INFO)

		self.fileDict = None
		self.yearDict = None
		self.publisherDict = None
		self.developerDict = None
		self.reviewerDict = None
		self.genreDict = None

		Logutil.log("End clearCache" , util.LOG_LEVEL_INFO)





	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except Exception, (exc):
			#HACK there seems to be a problem with recognizing the scrollbar controls
			if(controlId not in (CONTROL_SCROLLBARS)):
				Logutil.log("Control with id: %s could not be found. Check WindowXML file. Error: %s" % (str(controlId), str(exc)), util.LOG_LEVEL_ERROR)
				self.writeMsg(util.localize(32025) % str(controlId))
			return None

		return control


	def writeMsg(self, msg, count=0):

		control = self.getControlById(CONTROL_LABEL_MSG)
		if(control == None):
			Logutil.log("RCB_WARNING: control == None in writeMsg", util.LOG_LEVEL_WARNING)
			return
		try:
			control.setLabel(msg)
		except:
			pass


	def exit(self):

		Logutil.log("exit" , util.LOG_LEVEL_INFO)

		self.saveViewState(True)

		"""
		if self.memDB:
			Logutil.log("Saving DB to disk", util.LOG_LEVEL_INFO)
			if self.gdb.toDisk():
				Logutil.log("Database saved ok!", util.LOG_LEVEL_INFO)
			else:
				Logutil.log("Failed to save database!", util.LOG_LEVEL_INFO)
		"""

		self.gdb.close()
		self.close()


def main():

	skin = util.getConfiguredSkin()

	kodiVersion = KodiVersions.getKodiVersion()
	Logutil.log("Kodi Version = " + str(kodiVersion), util.LOG_LEVEL_INFO)

	if KodiVersions.getKodiVersion() > KodiVersions.KRYPTON:
		ui = UIGameDB("script-Rom_Collection_Browser-main.xml", util.getAddonInstallPath(), skin, "720p", True)
	else:
		ui = UIGameDB("script-Rom_Collection_Browser-main.xml", util.getAddonInstallPath(), skin, "720p")

	ui.doModal()
	del ui

main()
