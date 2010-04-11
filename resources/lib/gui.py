
import os, sys

import getpass, ntpath, re, string, glob, xbmc, xbmcgui
from xml.dom.minidom import Document, parseString
from pysqlite2 import dbapi2 as sqlite

import dbupdate, importsettings
from gamedatabase import *
import helper

__language__ = xbmc.Language( os.getcwd() ).getLocalizedString

#Action Codes
# See guilib/Key.h
ACTION_EXIT_SCRIPT = ( 10, )
ACTION_CANCEL_DIALOG = ACTION_EXIT_SCRIPT + ( 9, )
ACTION_MOVEMENT_LEFT = ( 1, )
ACTION_MOVEMENT_RIGHT = ( 2, )
ACTION_MOVEMENT_UP = ( 3, )
ACTION_MOVEMENT_DOWN = ( 4, )
ACTION_MOVEMENT = ( 1, 2, 3, 4, )
ACTION_INFO = ( 11, )


#ControlIds
CONTROL_CONSOLES = 500
CONTROL_GENRE = 600
CONTROL_YEAR = 700
CONTROL_PUBLISHER = 800
FILTER_CONTROLS = (500, 600, 700, 800,)
GAME_LISTS = (50, 51, 52, 53,)
CONROL_SCROLLBARS = (2200, 2201,)

CONTROL_IMG_BACK = 75

CONTROL_GAMES_GROUP = 200
CONTROL_GAMES_GROUP_START = 50
CONTROL_GAMES_GROUP_END = 59
CONTROL_CONSOLE_IMG = 2000
CONTROL_CONSOLE_DESC = 2100
CONTROL_BUTTON_SETTINGS = 3000
CONTROL_BUTTON_UPDATEDB = 3100
CONTROL_BUTTON_CHANGE_VIEW = 2

CONTROL_LABEL_MSG = 4000

LOG_LEVEL_ERROR = 0
LOG_LEVEL_WARNING = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_DEBUG = 3

CURRENT_LOG_LEVEL = LOG_LEVEL_INFO

RCBHOME = os.getcwd()

class UIGameDB(xbmcgui.WindowXML):	

	gdb = GameDataBase(os.path.join(RCBHOME, 'resources', 'database'))
	
	selectedControlId = 0
	selectedConsoleId = 0
	selectedGenreId = 0
	selectedYearId = 0
	selectedPublisherId = 0
	
	selectedConsoleIndex = 0
	selectedGenreIndex = 0
	selectedYearIndex = 0
	selectedPublisherIndex = 0
	
	currentView = ''
	
	def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback):
		# Changing the three varibles passed won't change, anything
		# Doing strXMLname = "bah.xml" will not change anything.
		# don't put GUI sensitive stuff here (as the xml hasn't been read yet
		# Idea to initialize your variables here
		
		self.log("Init Rom Collection Browser: " +RCBHOME, LOG_LEVEL_INFO)
		
		self.isInit = True
		
		self.gdb.connect()
		#check if we have an actual database
		#create new one or alter existing one
		self.gdb.checkDBStructure()		
		self.gdb.commit()
		
		self.Settings = xbmc.Settings(RCBHOME)		
		
		
		
	def onInit(self):
		
		self.log("Begin onInit", LOG_LEVEL_DEBUG)
		
		#only init once
		if(not self.isInit):
			return
			
		self.isInit = False
		
		self.updateControls()
		self.loadViewState()
		self.checkAutoExec()

		self.log("End onInit", LOG_LEVEL_DEBUG)
		

	def updateControls(self):
		
		self.log("Begin updateControls", LOG_LEVEL_DEBUG)
		
		#prepare FilterControls	
		self.showConsoles()		
		self.showGenre()		
		self.showYear()
		self.showPublisher()
		self.showGames()
		self.showGameInfo()
		
		self.log("End updateControls", LOG_LEVEL_DEBUG)

	
	def onAction(self, action):		
		if(action.getId() in ACTION_CANCEL_DIALOG):
			self.log("onAction: ACTION_CANCEL_DIALOG", LOG_LEVEL_DEBUG)
			self.exit()
		elif(action.getId() in ACTION_MOVEMENT_UP or action.getId() in ACTION_MOVEMENT_DOWN):
			
			self.log("onAction: ACTION_MOVEMENT_UP / ACTION_MOVEMENT_DOWN", LOG_LEVEL_DEBUG)
			
			control = self.getControlById(self.selectedControlId)
			if(control == None):
				self.log("control == None in onAction", LOG_LEVEL_WARNING)
				return
				
			if(CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END):				
				self.showGameInfo()
			
			elif(self.selectedControlId in FILTER_CONTROLS):								
				
				label = str(control.getSelectedItem().getLabel())
				label2 = str(control.getSelectedItem().getLabel2())
					
				filterChanged = False
				
				if (self.selectedControlId == CONTROL_CONSOLES):
					if(self.selectedConsoleIndex != control.getSelectedPosition()):
						self.selectedConsoleId = int(label2)
						self.selectedConsoleIndex = control.getSelectedPosition()
						filterChanged = True
					
					"""
					#consoleId 0 = Entry "All"					
					if (self.selectedConsoleId == 0):
						pass
						#self.getControl(CONTROL_CONSOLE_IMG).setVisible(0)
						#self.getControl(CONTROL_CONSOLE_DESC).setVisible(0)
					else:
						self.showConsoleInfo()
					"""
				elif (self.selectedControlId == CONTROL_GENRE):
					if(self.selectedGenreIndex != control.getSelectedPosition()):
						self.selectedGenreId = int(label2)
						self.selectedGenreIndex = control.getSelectedPosition()
						filterChanged = True
				elif (self.selectedControlId == CONTROL_YEAR):
					if(self.selectedYearIndex != control.getSelectedPosition()):
						self.selectedYearId = int(label2)
						self.selectedYearIndex = control.getSelectedPosition()
						filterChanged = True
				elif (self.selectedControlId == CONTROL_PUBLISHER):
					if(self.selectedPublisherIndex != control.getSelectedPosition()):
						self.selectedPublisherId = int(label2)
						self.selectedPublisherIndex = control.getSelectedPosition()
						filterChanged = True
				if(filterChanged):					
					self.showGames()								
				
		elif(action.getId() in ACTION_MOVEMENT_LEFT or action.getId() in ACTION_MOVEMENT_RIGHT):
			self.log("onAction: ACTION_MOVEMENT_LEFT / ACTION_MOVEMENT_RIGHT", LOG_LEVEL_DEBUG)
			
			control = self.getControlById(self.selectedControlId)
			if(control == None):
				self.log("control == None in onAction", LOG_LEVEL_WARNING)
				return
				
			if(CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END):
				self.showGameInfo()
		elif(action.getId() in ACTION_INFO):
			self.log("onAction: ACTION_INFO", LOG_LEVEL_DEBUG)
			
			control = self.getControlById(self.selectedControlId)
			if(control == None):
				self.log("control == None in onAction", LOG_LEVEL_WARNING)
				return
			if(CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END):
				self.showGameInfoDialog()



	def onClick(self, controlId):
		
		self.log("onClick: " +str(controlId), LOG_LEVEL_DEBUG)
		
		if (controlId == CONTROL_BUTTON_SETTINGS):
			self.log("onClick: Import Settings", LOG_LEVEL_DEBUG)
			self.importSettings()
		elif (controlId == CONTROL_BUTTON_UPDATEDB):
			self.log("onClick: Update DB", LOG_LEVEL_DEBUG)
			self.updateDB()		
		elif (controlId in FILTER_CONTROLS):
			self.log("onClick: Show Game Info", LOG_LEVEL_DEBUG)
			self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))
			self.showGameInfo()
		elif (controlId in GAME_LISTS):
			self.log("onClick: Launch Emu", LOG_LEVEL_DEBUG)
			self.launchEmu()		


	def onFocus(self, controlId):
		self.log("onFocus: " +str(controlId), LOG_LEVEL_DEBUG)
		self.selectedControlId = controlId
	
	
	def showFilterControl(self, dbo, controlId, showEntryAllItems):
		
		self.log("begin showFilterControl: " +str(controlId), LOG_LEVEL_DEBUG)
		
		#xbmcgui.lock()
		rows = dbo.getAllOrdered()
		
		control = self.getControlById(controlId)
		if(control == None):
			self.log("control == None in showFilterControl", LOG_LEVEL_WARNING)
			return
		
		control.setVisible(1)
		control.reset()
		
		items = []
		if(showEntryAllItems == 'True'):
			items.append(xbmcgui.ListItem("All", "0", "", ""))		
		
		for row in rows:
			items.append(xbmcgui.ListItem(str(row[1]), str(row[0]), "", ""))
			
		control.addItems(items)
			
		label2 = str(control.getSelectedItem().getLabel2())
		return int(label2)
		#xbmcgui.unlock
		
		self.log("End showFilterControl", LOG_LEVEL_DEBUG)
		
		
	def showConsoles(self):
		self.log("Begin showConsoles" , LOG_LEVEL_DEBUG)
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):
			showEntryAllItems = 'True'
		else:
			showEntryAllItems = rcbSetting[11]
		self.selectedConsoleId = self.showFilterControl(Console(self.gdb), CONTROL_CONSOLES, showEntryAllItems)
		
		self.log("End showConsoles" , LOG_LEVEL_DEBUG)


	def showGenre(self):
		self.log("Begin showGenre" , LOG_LEVEL_DEBUG)
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):
			showEntryAllItems = 'True'
		else:
			showEntryAllItems = rcbSetting[12]
		self.selectedGenreId = self.showFilterControl(Genre(self.gdb), CONTROL_GENRE, showEntryAllItems)
		
		self.log("End showGenre" , LOG_LEVEL_DEBUG)
		
	
	def showYear(self):
		self.log("Begin showYear" , LOG_LEVEL_DEBUG)
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):
			showEntryAllItems = 'True'
		else:
			showEntryAllItems = rcbSetting[13]
		self.selectedYearId = self.showFilterControl(Year(self.gdb), CONTROL_YEAR, showEntryAllItems)
		self.log("End showYear" , LOG_LEVEL_DEBUG)
		
		
	def showPublisher(self):
		self.log("Begin showPublisher" , LOG_LEVEL_DEBUG)
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):
			showEntryAllItems = 'True'
		else:
			showEntryAllItems = rcbSetting[14]
		self.selectedPublisherId = self.showFilterControl(Publisher(self.gdb), CONTROL_PUBLISHER, showEntryAllItems)
		
		self.log("End showPublisher" , LOG_LEVEL_DEBUG)


	def showGames(self):
		self.log("Begin showGames" , LOG_LEVEL_DEBUG)
		
		games = Game(self.gdb).getFilteredGames(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId, self.selectedPublisherId)
		
		self.writeMsg("loading games...")
		
		xbmcgui.lock()		
		
		self.clearList()
				
		for game in games:
			#consoleId, publisherId, developerId
			images = helper.getFilesByControl(self.gdb, 'gamelist', game[0], game[6], game[7], game[5])
			if(images != None and len(images) != 0):
				image = images[0]
			else:
				image = ""
				
			selectedImages = helper.getFilesByControl(self.gdb, 'gamelistselected', game[0], game[6], game[7], game[5])
			if(selectedImages != None and len(selectedImages) != 0):
				selectedImage = selectedImages[0]
			else:
				selectedImage = ""
			item = xbmcgui.ListItem(str(game[1]), str(game[0]), image, selectedImage)
			self.addItem(item, False)
				
		xbmcgui.unlock()
				
		self.writeMsg("")	
		
		self.log("End showGames" , LOG_LEVEL_DEBUG)
		

	def showConsoleInfo(self):	
		self.log("Begin showConsoleInfo" , LOG_LEVEL_DEBUG)
		
		if(self.getListSize() == 0):
			self.log("ListSize == 0 in showGameInfo", LOG_LEVEL_WARNING)
			return
		
		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0
		selectedGame = self.getListItem(pos)
		if(selectedGame == None):
			self.log("selectedGame == None in showGameInfo", LOG_LEVEL_WARNING)
			return
		
		consoleRow = Console(self.gdb).getObjectById(self.selectedConsoleId)
		
		if(consoleRow == None):
			self.log("consoleRow == None in showConsoleInfo", LOG_LEVEL_WARNING)
			return
			
		image = consoleRow[3]		
		description = consoleRow[2]		
		
		""" TODO no console ionfo atm
		selectedGame.setProperty('mainviewgameinfo', image)
		selectedGame.setProperty('gamedesc', description)
		"""
		
		self.log("End showConsoleInfo" , LOG_LEVEL_DEBUG)
		
	
	def showGameInfo(self):
		self.log("Begin showGameInfo" , LOG_LEVEL_DEBUG)
		
		if(self.getListSize() == 0):
			self.log("ListSize == 0 in showGameInfo", LOG_LEVEL_WARNING)
			return
					
		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0
		selectedGame = self.getListItem(pos)
		if(selectedGame == None):
			self.log("selectedGame == None in showGameInfo", LOG_LEVEL_WARNING)
			return
			
		gameId = selectedGame.getLabel2()
		gameRow = Game(self.gdb).getObjectById(gameId)		
		
		if(gameRow == None):
			self.log("gameRow == None in showGameInfo", LOG_LEVEL_WARNING)
			return
				
		bgimages = helper.getFilesByControl(self.gdb, 'mainviewbackground', gameRow[0], gameRow[6], gameRow[7], gameRow[5])
		if(bgimages != None and len(bgimages) != 0):
			bgimage = bgimages[0]
		else:
			bgimage = os.path.join(RCBHOME, 'resources', 'skins', 'Default', 'media', 'rcb-background-black.png')		
		controlBg = self.getControlById(CONTROL_IMG_BACK)
		controlBg.setImage(bgimage)
		
		
		images = helper.getFilesByControl(self.gdb, 'mainviewgameinfo', gameRow[0], gameRow[6], gameRow[7], gameRow[5])
		if(images != None and len(images) != 0):
			image = images[0]
		else:
			image = ""
		
		description = gameRow[2]
		if(description == None):
			description = ""
		
		selectedGame.setProperty('mainviewgameinfo', image)
		selectedGame.setProperty('gamedesc', description)
		
		self.log("End showGameInfo" , LOG_LEVEL_DEBUG)


	def launchEmu(self):

		self.log("Begin launchEmu" , LOG_LEVEL_INFO)

		if(self.getListSize() == 0):
			self.log("ListSize == 0 in launchEmu", LOG_LEVEL_WARNING)
			return

		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0
		selectedGame = self.getListItem(pos)
		
		if(selectedGame == None):
			self.log("selectedGame == None in launchEmu", LOG_LEVEL_WARNING)
			return
			
		gameId = selectedGame.getLabel2()
		self.log("launching game with id: " +str(gameId), LOG_LEVEL_INFO)
		
		helper.launchEmu(self.gdb, self, gameId)
		self.log("End launchEmu" , LOG_LEVEL_INFO)
		
		
	def updateDB(self):
		self.log("Begin updateDB" , LOG_LEVEL_INFO)
		
		dbupdate.DBUpdate().updateDB(self.gdb, self)
		self.updateControls()
		self.log("End updateDB" , LOG_LEVEL_INFO)
		
	
	def importSettings(self):
		self.log("Begin importSettings" , LOG_LEVEL_INFO)
		
		importsettings.SettingsImporter().importSettings(self.gdb, os.path.join(RCBHOME, 'resources', 'database'), self)
		self.updateControls()
		self.log("End importSettings" , LOG_LEVEL_INFO)
		
			
	def checkAutoExec(self):
		self.log("Begin checkAutoExec" , LOG_LEVEL_INFO)
		
		autoexec = os.path.join(RCBHOME, '..', 'autoexec.py')		
		if (os.path.isfile(autoexec)):	
			lines = ""
			try:
				fh = fh=open(autoexec,"r")
				lines = fh.readlines()
				fh.close()
			except Exception, (exc):
				self.log("Cannot access autoexec.py: " +str(exc), LOG_LEVEL_ERROR)
				return
				
			if(len(lines) > 0):
				firstLine = lines[0]
				#check if it is our autoexec
				if(firstLine.startswith('#Rom Collection Browser autoexec')):
					try:
						os.remove(autoexec)
					except Exception, (exc):
						self.log("Cannot remove autoexec.py: " +str(exc), LOG_LEVEL_ERROR)
						return
				else:
					return
		
		rcbSetting = helper.getRCBSetting(self.gdb)
		if (rcbSetting == None):
			print "RCB_WARNING: rcbSetting == None in checkAutoExec"
			return
					
		autoExecBackupPath = rcbSetting[9]
		if (autoExecBackupPath == None):
			return
			
		if (os.path.isfile(autoExecBackupPath)):
			try:
				os.rename(autoExecBackupPath, autoexec)
			except Exception, (exc):
				self.log("Cannot rename autoexec.py: " +str(exc), LOG_LEVEL_ERROR)
				return
			
		RCBSetting(self.gdb).update(('autoexecBackupPath',), (None,), rcbSetting[0])
		self.gdb.commit()
		
		self.log("End checkAutoExec" , LOG_LEVEL_INFO)
		
	
	def writeMsg(self, msg):
		control = self.getControlById(CONTROL_LABEL_MSG)
		if(control == None):
			self.log("RCB_WARNING: control == None in writeMsg", LOG_LEVEL_WARNING)
			return
		control.setLabel(msg)
		
		
	def saveViewState(self, isOnExit):
		
		self.log("Begin saveViewState" , LOG_LEVEL_INFO)
		
		if(self.getListSize() == 0):
			self.log("ListSize == 0 in saveViewState", LOG_LEVEL_WARNING)
			return
		
		selectedGameIndex = self.getCurrentListPosition()
		if(selectedGameIndex == -1):
			selectedGameIndex = 0
		if(selectedGameIndex == None):
			self.log("selectedGameIndex == None in saveViewState", LOG_LEVEL_WARNING)
			return
		
		self.saveViewMode()
		
		helper.saveViewState(self.gdb, isOnExit, 'mainView', selectedGameIndex, self.selectedConsoleIndex, self.selectedGenreIndex, self.selectedPublisherIndex, 
			self.selectedYearIndex, self.selectedControlId, None)
		
		self.log("End saveViewState" , LOG_LEVEL_INFO)


	def saveViewMode(self):
		
		self.log("Begin saveViewMode" , LOG_LEVEL_INFO)
		
		view_mode = ""
		for id in range( CONTROL_GAMES_GROUP_START, CONTROL_GAMES_GROUP_END + 1 ):
			try:			
				if xbmc.getCondVisibility( "Control.IsVisible(%i)" % id ):
					view_mode = repr( id )					
					break
			except:
				pass
				
		self.Settings.setSetting( "rcb_view_mode", view_mode)
		
		self.log("End saveViewMode" , LOG_LEVEL_INFO)

	
	def loadViewState(self):
		
		self.log("Begin loadViewState" , LOG_LEVEL_INFO)
		
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):			
			self.log("rcbSetting == None in loadViewState", LOG_LEVEL_WARNING)
			focusControl = self.getControlById(CONTROL_BUTTON_SETTINGS)
			self.setFocus(focusControl)
			return		
		
		if(rcbSetting[2] != None):
			self.selectedConsoleId = int(self.setFilterSelection(CONTROL_CONSOLES, rcbSetting[2]))	
			self.selectedConsoleIndex = rcbSetting[2]
		if(rcbSetting[3] != None):
			self.selectedGenreId = int(self.setFilterSelection(CONTROL_GENRE, rcbSetting[3]))
			self.selectedGenreIndex = rcbSetting[3]
		if(rcbSetting[4] != None):
			self.selectedPublisherId = int(self.setFilterSelection(CONTROL_PUBLISHER, rcbSetting[4]))
			self.selectedPublisherIndex = rcbSetting[4]
		if(rcbSetting[5] != None):
			self.selectedYearId = int(self.setFilterSelection(CONTROL_YEAR, rcbSetting[5]))
			self.selectedYearIndex = rcbSetting[5]

		self.showGames()
		self.setFilterSelection(CONTROL_GAMES_GROUP_START, rcbSetting[6])
						
		#lastFocusedControl
		if(rcbSetting[17] != None):
			focusControl = self.getControlById(rcbSetting[17])
			if(focusControl == None):
				self.log("focusControl == None in loadViewState". LOG_LEVEL_WARNING)
				return
			self.setFocus(focusControl)
			if(rcbSetting[17] == CONTROL_CONSOLES):
				self.showConsoleInfo()
			elif(CONTROL_GAMES_GROUP_START <= rcbSetting[17] <= CONTROL_GAMES_GROUP_END):
				self.showGameInfo()
		else:
			focusControl = self.getControlById(CONTROL_CONSOLES)
			if(focusControl == None):
				self.log("focusControl == None (2) in loadViewState", LOG_LEVEL_WARNING)
				return
			self.setFocus(focusControl)		
		
		id = self.Settings.getSetting( "rcb_view_mode")
		xbmc.executebuiltin( "Container.SetViewMode(%i)" % int(id) )
		
		#lastSelectedView
		if(rcbSetting[1] == 'gameInfoView'):
			self.showGameInfoDialog()
			
		self.log("End loadViewState" , LOG_LEVEL_INFO)
			
			
			
	def setFilterSelection(self, controlId, selectedIndex):
		
		self.log("Begin setFilterSelection" , LOG_LEVEL_DEBUG)
		
		if(selectedIndex != None):
			control = self.getControlById(controlId)
			if(control == None):
				self.log("control == None in setFilterSelection", LOG_LEVEL_WARNING)
				return
			
			if(controlId == CONTROL_GAMES_GROUP_START):
				self.setCurrentListPosition(selectedIndex)
				selectedItem = self.getListItem(selectedIndex)
				
			else:
				control.selectItem(selectedIndex)
				selectedItem = control.getSelectedItem()
				
			if(selectedItem == None):
				self.log("End setFilterSelection" , LOG_LEVEL_DEBUG)
				return 0
			label2 = selectedItem.getLabel2()
			self.log("End setFilterSelection" , LOG_LEVEL_DEBUG)
			return label2
		else:
			self.log("End setFilterSelection" , LOG_LEVEL_DEBUG)
			return 0
			
	
	def showGameInfoDialog(self):

		self.log("Begin showGameInfoDialog", LOG_LEVEL_INFO)
		
		if(self.getListSize() == 0):
			self.log("ListSize == 0 in saveViewState", LOG_LEVEL_WARNING)
			return
		
		selectedGameIndex = self.getCurrentListPosition()		
		if(selectedGameIndex == -1):
			selectedGameIndex = 0
		selectedGame = self.getListItem(selectedGameIndex)		
		if(selectedGame == None):
			self.log("selectedGame == None in showGameInfoDialog", LOG_LEVEL_WARNING)
			return
		gameId = selectedGame.getLabel2()
		
		self.saveViewMode()
		
		import gameinfodialog
		gid = gameinfodialog.UIGameInfoView("script-Rom_Collection_Browser-gameinfo.xml", os.getcwd(), "Default", 1, gdb=self.gdb, gameId=gameId, 
			consoleId=self.selectedConsoleId, genreId=self.selectedGenreId, yearId=self.selectedYearId, publisherId=self.selectedPublisherId, selectedGameIndex=selectedGameIndex,
			consoleIndex=self.selectedConsoleIndex, genreIndex=self.selectedGenreIndex, yearIndex=self.selectedYearIndex, publisherIndex=self.selectedPublisherIndex, 
			controlIdMainView=self.selectedControlId)		
		del gid
				
		
		self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))
		self.showGames()
		self.setCurrentListPosition(selectedGameIndex)
		self.showGameInfo()
		
		self.log("End showGameInfoDialog", LOG_LEVEL_INFO)
		
		
	
	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except: 
			#HACK there seems to be a problem with recognizing the scrollbar controls
			if(controlId not in (CONROL_SCROLLBARS)):
				self.log("Control with id: %s could not be found. Check WindowXML file." %str(controlId), LOG_LEVEL_ERROR)
				self.writeMsg("Control with id: %s could not be found. Check WindowXML file." %str(controlId))
			return None
		
		return control
		
	
	def log(self, message, logLevel):
		
		if(logLevel > CURRENT_LOG_LEVEL):
			return
			
		prefix = ''
		if(logLevel == LOG_LEVEL_DEBUG):
			prefix = 'RCB_DEBUG: '
		elif(logLevel == LOG_LEVEL_INFO):
			prefix = 'RCB_INFO: '
		elif(logLevel == LOG_LEVEL_WARNING):
			prefix = 'RCB_WARNING: '
		elif(logLevel == LOG_LEVEL_ERROR):
			prefix = 'RCB_ERROR: '

		print prefix + message
	
	
	def exit(self):				
		
		self.log("exit" , LOG_LEVEL_INFO)
		
		self.saveViewState(True)
		
		self.gdb.close()
		self.close()
		


def main():
    #_progress_dialog( len( modules ) + 1, _( 55 ) )
    #settings = Settings().get_settings()
    #force_fallback = settings[ "skin" ] != "Default"
    #ui = GameDB( "script-%s-main.xml" % ( __scriptname__.replace( " ", "_" ), ), os.getcwd(), settings[ "skin" ], force_fallback )
    #xmlFile = os.path.join(os.getcwd() + '/resources/skins/Default/720p/script-GameDB-main.xml' )
    #print xmlFile
    ui = UIGameDB("script-Rom_Collection_Browser-main.xml", os.getcwd(), "Default", 1)
    #_progress_dialog( -1 )
    ui.doModal()
    del ui

main()