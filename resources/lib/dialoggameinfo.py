
import xbmc, xbmcgui
import sys
import helper, util
from launcher import RCBLauncher
from util import *
from gamedatabase import *



ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)
ACTION_MOVEMENT_LEFT = (1,)
ACTION_MOVEMENT_RIGHT = (2,)
ACTION_MOVEMENT_UP = (3,)
ACTION_MOVEMENT_DOWN = (4,)
ACTION_MOVEMENT = (1, 2, 3, 4,)

CONTROL_BUTTON_PLAYGAME = 3000

CONTROL_GAME_LIST_GROUP = 1000
CONTROL_GAME_LIST = 59

CONTROL_LABEL_MSG = 4000

RCBHOME = util.getAddonInstallPath()


class MyPlayer(xbmc.Player):

	gui = None
	
	def onPlayBackEnded(self):
		print 'RCB: onPlaybackEnded'

		if(self.gui == None):
			print "RCB_WARNING: gui == None in MyPlayer"
			return

		self.gui.setFocus(self.gui.getControl(CONTROL_BUTTON_PLAYGAME))


class UIGameInfoView(xbmcgui.WindowXMLDialog):

	__useRefactoredView = False

	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)

		Logutil.log("Init GameInfoView", util.LOG_LEVEL_INFO)

		self.gdb = kwargs[ "gdb" ]
		self.selectedGameId = kwargs[ "gameId" ]
		self.selectedGame = kwargs[ "listItem" ]
		self.config = kwargs["config"]
		self.settings = kwargs["settings"]
		self.selectedConsoleId = kwargs[ "consoleId" ]
		self.selectedGenreId = kwargs[ "genreId" ]
		self.selectedYearId = kwargs[ "yearId" ]
		self.selectedPublisherId = kwargs[ "publisherId" ]
		self.selectedConsoleIndex = kwargs[ "consoleIndex" ]
		self.selectedGenreIndex = kwargs[ "genreIndex" ]
		self.selectedYearIndex = kwargs[ "yearIndex" ]
		self.selectedPublisherIndex = kwargs[ "publisherIndex" ]
		self.selectedCharacter = kwargs[ "selectedCharacter" ]
		self.selectedCharacterIndex = kwargs[ "selectedCharacterIndex" ]
		self.selectedGameIndex = kwargs[ "selectedGameIndex" ]
		self.selectedControlIdMainView = kwargs["controlIdMainView"]
		self.fileTypeGameplay = kwargs["fileTypeGameplay"]
		self.mediaDict = kwargs["mediaDict"]

		self.player = MyPlayer()
		self.player.gui = self
		
		self.doModal()


	def onInit(self):

		Logutil.log("Begin OnInit UIGameInfoView", util.LOG_LEVEL_INFO)

		self.showGame()
		
		control = self.getControlById(CONTROL_BUTTON_PLAYGAME)
		if(control != None):
			self.setFocus(control)
		
		xbmc.sleep(util.WAITTIME_UPDATECONTROLS)

		Logutil.log("End OnInit UIGameInfoView", util.LOG_LEVEL_INFO)


	def onClick(self, controlId):
		Logutil.log("Begin onClick UIGameInfoView", util.LOG_LEVEL_DEBUG)

		if (controlId == CONTROL_BUTTON_PLAYGAME):
			self.launchEmu()

		Logutil.log("End onClick UIGameInfoView", util.LOG_LEVEL_DEBUG)


	def onFocus(self, controlId):
		Logutil.log("onFocus UIGameInfoView", util.LOG_LEVEL_DEBUG)
		self.selectedControlId = controlId

	def onAction(self, action):

		if(action.getId() in ACTION_CANCEL_DIALOG):
			Logutil.log("onAction exit UIGameInfoView", util.LOG_LEVEL_DEBUG)

			#stop Player (if playing)
			if(xbmc.Player().isPlayingVideo()):
				xbmc.Player().stop()

			self.close()


	def showGame(self):

		Logutil.log("Begin showGameList UIGameInfoView", util.LOG_LEVEL_INFO)

		self.writeMsg(util.localize(32121))

		self.clearList()

		game = Game(self.gdb).getGameById(self.selectedGameId)

		item = xbmcgui.ListItem(game.name, str(game.id))
		item.setProperty('romCollectionId', str(game.romCollectionId))
		
		# Properties from the game object
		for var in ['maxplayers', 'rating', 'votes', 'url', 'region', 'media', 'perspective', 'controllertype',
					'originaltitle', 'alternatetitle', 'translatedby', 'version', 'playcount', 'plot', 'year', 
					'publisher', 'developer', 'genre', 'firstRom']:
			try:
				item.setProperty(var, getattr(game, var))
			except AttributeError as e:
				Logutil.log('Error retrieving property ' + var + ': ' + str(e), util.LOG_LEVEL_WARNING)
				item.setProperty(var, '')

		romCollection = None
		try:
			romCollection = self.config.romCollections[str(game.romCollectionId)]
		except:
			Logutil.log(util.localize(32023) % str(game.romCollectionId), util.LOG_LEVEL_ERROR)
			
		# Rom Collection properties
		item.setProperty('romcollection', romCollection.name)
		item.setProperty('console', romCollection.name)

		mediaPathsDict = self.mediaDict[str(game.romCollectionId)]
		romfile = game.firstRom
		gamenameFromFile = romCollection.getGamenameFromFilename(romfile)
		
		item.setArt({
				'icon': helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameList, romCollection, mediaPathsDict, gamenameFromFile, False),
				'thumb': helper.getFileForControl(romCollection.imagePlacingMain.fileTypesForGameListSelected, romCollection, mediaPathsDict, gamenameFromFile, False),
				
				IMAGE_CONTROL_BACKGROUND: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewBackground, romCollection, mediaPathsDict, gamenameFromFile),
				IMAGE_CONTROL_GAMEINFO_BIG: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoBig, romCollection, mediaPathsDict, gamenameFromFile),
	
				IMAGE_CONTROL_GAMEINFO_UPPERLEFT: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoUpperLeft, romCollection, mediaPathsDict, gamenameFromFile),
				IMAGE_CONTROL_GAMEINFO_UPPERRIGHT: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoUpperRight, romCollection, mediaPathsDict, gamenameFromFile),
				IMAGE_CONTROL_GAMEINFO_LOWERLEFT: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLowerLeft, romCollection, mediaPathsDict, gamenameFromFile),
				IMAGE_CONTROL_GAMEINFO_LOWERRIGHT: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLowerRight, romCollection, mediaPathsDict, gamenameFromFile),
	
				IMAGE_CONTROL_GAMEINFO_UPPER: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoUpper, romCollection, mediaPathsDict, gamenameFromFile),
				IMAGE_CONTROL_GAMEINFO_LOWER: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLower, romCollection, mediaPathsDict, gamenameFromFile),
				IMAGE_CONTROL_GAMEINFO_LEFT: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLeft, romCollection, mediaPathsDict, gamenameFromFile),
				IMAGE_CONTROL_GAMEINFO_RIGHT: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoRight, romCollection, mediaPathsDict, gamenameFromFile),
	
				IMAGE_CONTROL_1: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainView1, romCollection, mediaPathsDict, gamenameFromFile),
				IMAGE_CONTROL_2: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainView2, romCollection, mediaPathsDict, gamenameFromFile),
				IMAGE_CONTROL_3: helper.getFileForControl(romCollection.imagePlacingInfo.fileTypesForMainView3, romCollection, mediaPathsDict, gamenameFromFile),
		})

		self.addItem(item)

		self.writeMsg("")

		Logutil.log("End showGameList UIGameInfoView", util.LOG_LEVEL_INFO)
	

	def launchEmu(self):

		Logutil.log("Begin launchEmu UIGameInfoView", util.LOG_LEVEL_INFO)

		launcher = RCBLauncher()
		launcher.launchEmu(self.gdb, self, self.selectedGameId, self.config, self.selectedGame)
		
		self.saveViewState(False)
		self.close()
		
		Logutil.log("End launchEmu UIGameInfoView", util.LOG_LEVEL_INFO)


	def saveViewState(self, isOnExit):

		Logutil.log("Begin saveViewState UIGameInfoView", util.LOG_LEVEL_INFO)

		#TODO: save selectedGameIndex from main view
		selectedGameIndex = 0

		helper.saveViewState(self.gdb, isOnExit, 'gameInfoView', selectedGameIndex, self.selectedConsoleIndex, self.selectedGenreIndex, self.selectedPublisherIndex,
			self.selectedYearIndex, self.selectedCharacterIndex, self.selectedControlIdMainView, self.selectedControlId, self.settings)

		Logutil.log("End saveViewState UIGameInfoView", util.LOG_LEVEL_INFO)


	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except:
			Logutil.log("Control with id: %s could not be found. Check WindowXML file." % str(controlId), util.LOG_LEVEL_ERROR)
			self.writeMsg(util.localize(32025) % str(controlId))
			return None

		return control


	def writeMsg(self, msg):
		control = self.getControlById(CONTROL_LABEL_MSG)
		if(control == None):
			return

		control.setLabel(msg)
