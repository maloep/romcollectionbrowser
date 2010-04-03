
import os, sys
import xbmc, xbmcgui
import dbupdate, importsettings
from gamedatabase import *
import helper


ACTION_EXIT_SCRIPT = ( 10, )
ACTION_CANCEL_DIALOG = ACTION_EXIT_SCRIPT + ( 9, )
ACTION_MOVEMENT_LEFT = ( 1, )
ACTION_MOVEMENT_RIGHT = ( 2, )
ACTION_MOVEMENT_UP = ( 3, )
ACTION_MOVEMENT_DOWN = ( 4, )
ACTION_MOVEMENT = ( 1, 2, 3, 4, )

CONTROL_BUTTON_PLAYGAME = 3000

CONTROL_GAME_LIST_GROUP = 1000
CONTROL_GAME_LIST = 50
CONTROL_IMG_BACK = 2000

CONTROL_LABEL_MSG = 4000

CONTROL_LABEL_GENRE = 6100
CONTROL_LABEL_YEAR = 6200
CONTROL_LABEL_PUBLISHER = 6300
CONTROL_LABEL_DEVELOPER = 6400
CONTROL_LABEL_REGION = 6500
CONTROL_LABEL_MEDIA = 6600
CONTROL_LABEL_CONTROLLER = 6700
CONTROL_LABEL_RATING = 6800
CONTROL_LABEL_VOTES = 6900
CONTROL_LABEL_PLAYERS = 7000
CONTROL_LABEL_PERSPECTIVE = 7100
CONTROL_LABEL_REVIEWER = 7200
CONTROL_LABEL_URL = 7300
CONTROL_LABEL_LAUNCHCOUNT = 7400

CONTROL_LABEL_DESC = 8000

CONTROL_IMG_GAMEINFO1 = 9000
CONTROL_IMG_GAMEINFO2 = 9100
CONTROL_IMG_GAMEINFO3 = 9200
CONTROL_IMG_GAMEINFO4 = 9300

CONTROL_IMG_INGAMEVIDEO = 10000



RCBHOME = os.getcwd()


class UIGameInfoView(xbmcgui.WindowXMLDialog):
	def __init__(self, *args, **kwargs):		
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )		
		
		self.gdb = kwargs[ "gdb" ]
		self.selectedGameId = kwargs[ "gameId" ]		
		self.selectedConsoleId = kwargs[ "consoleId" ]		
		self.selectedGenreId = kwargs[ "genreId" ]				
		self.selectedYearId = kwargs[ "yearId" ]		
		self.selectedPublisherId = kwargs[ "publisherId" ]
		self.selectedConsoleIndex = kwargs[ "consoleIndex" ]
		self.selectedGenreIndex = kwargs[ "genreIndex" ]		
		self.selectedYearIndex = kwargs[ "yearIndex" ]		
		self.selectedPublisherIndex = kwargs[ "publisherIndex" ]
		self.selectedGameIndex = kwargs[ "selectedGameIndex" ]		
		self.selectedControlIdMainView = kwargs["controlIdMainView"]
		
		
	def onInit(self):
		self.showGameList()
		self.showGameInfo()
		
		control = self.getControlById(CONTROL_GAME_LIST_GROUP)
		if(control == None):
			return
			
		self.setFocus(control)
		self.selectedControlId = CONTROL_GAME_LIST_GROUP
		self.setCurrentListPosition(self.selectedGameIndex)	
		
		
		
	def onClick( self, controlId ):
		if (controlId == CONTROL_BUTTON_PLAYGAME):			
			self.launchEmu()
			

	def onFocus( self, controlId ):
		self.selectedControlId = controlId

	def onAction( self, action ):		
		if(action.getId() in ACTION_CANCEL_DIALOG):
			#stop Player (if playing)
			xbmc.Player().stop()
			self.close()
		elif(action.getId() in ACTION_MOVEMENT_LEFT or action.getId() in ACTION_MOVEMENT_RIGHT):
			if(self.selectedControlId == CONTROL_GAME_LIST_GROUP):
				
				pos = self.getCurrentListPosition()
				if(pos == -1):
					pos = 0
				selectedGame = self.getListItem(pos)
				if(selectedGame == None):
					print "RCB_WARNING: selectedGame == None in showGameInfo"
					return
			
				self.selectedGameId = selectedGame.getLabel2()
				self.showGameInfo()
	
	
	def showGameList(self):
		games = Game(self.gdb).getFilteredGames(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId, self.selectedPublisherId)		
				
		self.writeMsg("loading games...")
		
		xbmcgui.lock()
		
		self.clearList()
		
		for game in games:
			images = helper.getFilesByControl(self.gdb, 'gameinfoviewgamelist', game[0], game[5])
			if(images != None and len(images) != 0):
				image = images[0]
			else:
				image = ""
			item = xbmcgui.ListItem(str(game[1]), str(game[0]), image, '')
			self.addItem(item, False)
				
		xbmcgui.unlock()
		self.writeMsg("")
	
		
	def showGameInfo(self):
		
		#stop video (if playing)
		xbmc.Player().stop()
		
		gameRow = Game(self.gdb).getObjectById(self.selectedGameId)
		if(gameRow == None):
			self.writeMsg('Selected game could not be read from database.')
			return
		
		genreString = ""
		genres = Genre(self.gdb).getGenresByGameId(gameRow[0])
		if (genres != None):
			for i in range(0, len(genres)):
				genre = genres[i]
				genreString += genre[1]
				if(i < len(genres) -1):
					genreString += ", "
				
		year = self.getItemName(Year(self.gdb), gameRow[9])
		publisher = self.getItemName(Publisher(self.gdb), gameRow[6])
		developer = self.getItemName(Developer(self.gdb), gameRow[7])
		reviewer = self.getItemName(Reviewer(self.gdb), gameRow[8])
				
		self.setLabel(CONTROL_LABEL_GENRE, genreString)
		self.setLabel(CONTROL_LABEL_YEAR, year)
		self.setLabel(CONTROL_LABEL_PUBLISHER, publisher)
		self.setLabel(CONTROL_LABEL_DEVELOPER, developer)
		self.setLabel(CONTROL_LABEL_REGION, gameRow[14])
		self.setLabel(CONTROL_LABEL_MEDIA, gameRow[15])
		self.setLabel(CONTROL_LABEL_CONTROLLER, gameRow[17])
		self.setLabel(CONTROL_LABEL_RATING, gameRow[11])
		self.setLabel(CONTROL_LABEL_VOTES, gameRow[12])
		self.setLabel(CONTROL_LABEL_PLAYERS, gameRow[10])
		self.setLabel(CONTROL_LABEL_PERSPECTIVE, gameRow[16])
		self.setLabel(CONTROL_LABEL_REVIEWER, reviewer)
		self.setLabel(CONTROL_LABEL_URL, gameRow[13])			
		
		self.setLabel(CONTROL_LABEL_LAUNCHCOUNT, gameRow[19])
		
		description = gameRow[2]
		if(description == None):
			description = ""		
		
		controlDesc = self.getControlById(CONTROL_LABEL_DESC)
		if(controlDesc == None):
			return
		controlDesc.setText(description)
				
		#gameRow[5] = romCollectionId
		background = os.path.join(RCBHOME, 'resources', 'skins', 'Default', 'media', 'rcb-background-black.png')	
		self.setImage(CONTROL_IMG_BACK, 'gameinfoviewbackground', gameRow[0], gameRow[5], background)
		self.setImage(CONTROL_IMG_GAMEINFO1, 'gameinfoview1', gameRow[0], gameRow[5], None)
		self.setImage(CONTROL_IMG_GAMEINFO2, 'gameinfoview2', gameRow[0], gameRow[5], None)
		self.setImage(CONTROL_IMG_GAMEINFO3, 'gameinfoview3', gameRow[0], gameRow[5], None)
		self.setImage(CONTROL_IMG_GAMEINFO4, 'gameinfoview4', gameRow[0], gameRow[5], None)
			
		
		videos = helper.getFilesByControl(self.gdb, 'gameinfoviewvideowindow', gameRow[0], gameRow[5])		
		#ingameVideos = File(self.gdb).getIngameVideosByGameId(self.selectedGameId)
		if(videos != None and len(videos) != 0):
			video = videos[0]
						
			playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO)
			playlist.clear()			
			xbmc.Player().play(video)
		
			
		
		
	def getItemName(self, object, itemId):
		itemRow = object.getObjectById(itemId)
		if(itemRow == None):
			return ""
		else:
			return itemRow[1]
			
	
	def setLabel(self, controlId, value):
		if(value == None):
			value = ""	
		
		control = self.getControlById(controlId)
		if(control == None):
			return
		control.setLabel(str(value))
		
		
	def setImage(self, controlId, controlName, gameId, romCollectionId, defaultImage):
				
		images = helper.getFilesByControl(self.gdb, controlName, gameId, romCollectionId)
		
		control = self.getControlById(controlId)
		if(control == None):
			return
				
		#TODO more than one image?
		if(images != None and len(images) != 0):
			image = images[0]			
			control.setImage(image)
			control.setVisible(1)
		else:
			if(defaultImage == None):
				control.setVisible(0)
			else:						
				control.setImage(defaultImage)
	
	
	def launchEmu(self):
		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0
		selectedGame = self.getListItem(pos)
		
		if(selectedGame == None):
			print "RCB_WARNING: selectedGame == None in launchEmu"
			return
			
		gameId = selectedGame.getLabel2()
		
		helper.launchEmu(self.gdb, self, gameId)
		
	
	def saveViewState(self, isOnExit):
		selectedGameIndex = self.getCurrentListPosition()
		if(selectedGameIndex == -1):
			selectedGameIndex = 0
		if(selectedGameIndex == None):
			print "RCB_WARNING: selectedGameIndex == None in saveViewState"
			return
		
		helper.saveViewState(self.gdb, isOnExit, 'gameInfoView', selectedGameIndex, self.selectedConsoleIndex, self.selectedGenreIndex, self.selectedPublisherIndex, 
			self.selectedYearIndex, self.selectedControlIdMainView, self.selectedControlId)
			
			
	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except: 
			print("RCB ERROR: Control with id: %s could not be found. Check WindowXML file." %str(controlId))
			self.writeMsg("Control with id: %s could not be found. Check WindowXML file." %str(controlId))
			return None
		
		return control


	def writeMsg(self, msg):
		control = self.getControlById(CONTROL_LABEL_MSG)
		if(control == None):
			return
			
		control.setLabel(msg)
		