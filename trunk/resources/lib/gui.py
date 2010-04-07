
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
		self.isInit = True
		
		self.gdb.connect()
		#check if we have an actual database
		#create new one or alter existing one
		self.gdb.checkDBStructure()		
		self.gdb.commit()		
		
		
		
	def onInit(self):
		#only init once
		if(not self.isInit):
			return
			
		self.isInit = False
		
		self.updateControls()
		self.loadViewState()
		self.checkAutoExec()		
		

	def updateControls(self):
		#prepare FilterControls	
		self.showConsoles()		
		self.showGenre()		
		self.showYear()
		self.showPublisher()
		self.showGames()
		self.showGameInfo()
		

	def onAction(self, action):		
		if(action.getId() in ACTION_CANCEL_DIALOG):
			self.exit()
		elif(action.getId() in ACTION_MOVEMENT_UP or action.getId() in ACTION_MOVEMENT_DOWN):
			
			control = self.getControlById(self.selectedControlId)
			if(control == None):
				print "RCB_WARNING: control == None in onAction"
				return
				
			if(CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END):
				self.showGameInfo()
			
			elif(self.selectedControlId in FILTER_CONTROLS):
				
				#self.saveViewMode()
				
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
					
				#xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_OnLoad')
				
		elif(action.getId() in ACTION_MOVEMENT_LEFT or action.getId() in ACTION_MOVEMENT_RIGHT):
			control = self.getControlById(self.selectedControlId)
			if(control == None):
				print "RCB_WARNING: control == None in onAction"
				return
				
			if(CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END):
				self.showGameInfo()
		elif(action.getId() in ACTION_INFO):			
			control = self.getControlById(self.selectedControlId)
			if(control == None):
				print "RCB_WARNING: control == None in onAction"
				return
			if(CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END):
				self.showGameInfoDialog()



	def onClick(self, controlId):
		"""
		Notice: onClick not onControl
		Notice: it gives the ID of the control not the control object
		"""
		if (controlId == CONTROL_BUTTON_SETTINGS):			
			self.importSettings()
		elif (controlId == CONTROL_BUTTON_UPDATEDB):			
			self.updateDB()		
		elif (controlId in FILTER_CONTROLS):
			self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))
			self.showGameInfo()
		elif (controlId in GAME_LISTS):
			self.launchEmu()
		
		"""
		elif (controlId in (3200,)):
			changeViewButton = self.getControlById(CONTROL_BUTTON_CHANGE_VIEW)		
			buttonText = changeViewButton.getLabel()
			
			lastView = ''
			if(buttonText.find('Thumbs') >= 0):
				lastView = 'rcb_thumbs_view'
			elif(buttonText.find('Info 2') >= 0):
				lastView = 'rcb_info2_view'
			else:
				lastView = 'rcb_info_view'	
			
			xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_thumbs_view')
			xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_info_view')
			xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_info2_view')
			
			if(lastView == 'rcb_thumbs_view'):
				xbmc.executebuiltin( "Skin.SetBool(%s)" %'rcb_info_view')
				#self.currentView = 'rcb_info_view'
				changeViewButton.setLabel('Info')
				self.getControlById(50).setVisible(1)
				self.getControlById(51).setVisible(0)
				self.getControlById(52).setVisible(0)
			elif(lastView == 'rcb_info_view'):
				xbmc.executebuiltin( "Skin.SetBool(%s)" %'rcb_info2_view')
				#self.currentView = 'rcb_info2_view'
				changeViewButton.setLabel('Info 2')
				self.getControlById(52).setVisible(1)
				self.getControlById(50).setVisible(0)
				self.getControlById(51).setVisible(0)
			elif(lastView == 'rcb_info2_view'):
				xbmc.executebuiltin( "Skin.SetBool(%s)" %'rcb_thumbs_view')
				#self.currentView = 'rcb_thumbs_view'
				changeViewButton.setLabel('Thumbs')
				self.getControlById(51).setVisible(1)
				self.getControlById(50).setVisible(0)
				self.getControlById(52).setVisible(0)
				
			"""
				
			#self.showGames()
			#self.showGameInfo()			
			#self.showGames()
			#self.setCurrentListPosition(0)
		"""		
		elif (controlId in (2,)):				
		
			xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_thumbs_view')
			xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_info_view')
			xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_info2_view')
			
			if(self.currentView == 'rcb_thumbs_view'):
				xbmc.executebuiltin( "Skin.SetBool(%s)" %'rcb_info_view')
				self.currentView = 'rcb_info_view'
				#self.getControlById(50).setVisible(1)
			elif(self.currentView == 'rcb_info_view'):
				xbmc.executebuiltin( "Skin.SetBool(%s)" %'rcb_info2_view')
				self.currentView = 'rcb_info2_view'
				#self.getControlById(52).setVisible(1)
			elif(self.currentView == 'rcb_info2_view'):
				xbmc.executebuiltin( "Skin.SetBool(%s)" %'rcb_thumbs_view')
				self.currentView = 'rcb_thumbs_view'
				#self.getControlById(51).setVisible(1)
			
			#print self.getControlById(51).getVisible()
			#self.showGames()
			#self.showGameInfo()			
			#self.showGames()
			#self.setCurrentListPosition(0)			
		"""


	def onFocus(self, controlId):
		self.selectedControlId = controlId
	
	
	def showFilterControl(self, dbo, controlId, showEntryAllItems):
		#xbmcgui.lock()
		rows = dbo.getAllOrdered()
		
		control = self.getControlById(controlId)
		if(control == None):
			print "RCB_WARNING: control == None in showFilterControl"
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
		
		
	def showConsoles(self):
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):
			showEntryAllItems = 'True'
		else:
			showEntryAllItems = rcbSetting[11]
		self.selectedConsoleId = self.showFilterControl(Console(self.gdb), CONTROL_CONSOLES, showEntryAllItems)


	def showGenre(self):
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):
			showEntryAllItems = 'True'
		else:
			showEntryAllItems = rcbSetting[12]
		self.selectedGenreId = self.showFilterControl(Genre(self.gdb), CONTROL_GENRE, showEntryAllItems)
		
	
	def showYear(self):
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):
			showEntryAllItems = 'True'
		else:
			showEntryAllItems = rcbSetting[13]
		self.selectedYearId = self.showFilterControl(Year(self.gdb), CONTROL_YEAR, showEntryAllItems)
		
		
	def showPublisher(self):
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):
			showEntryAllItems = 'True'
		else:
			showEntryAllItems = rcbSetting[14]
		self.selectedPublisherId = self.showFilterControl(Publisher(self.gdb), CONTROL_PUBLISHER, showEntryAllItems)


	def showGames(self):
		
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
			item = xbmcgui.ListItem(str(game[1]), str(game[0]), image, '')				
			self.addItem(item, False)
				
		xbmcgui.unlock()
		
		
		self.writeMsg("")	
		

	def showConsoleInfo(self):	
		
		if(self.getListSize() == 0):
			return
		
		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0
		selectedGame = self.getListItem(pos)
		if(selectedGame == None):
			print "RCB_WARNING: selectedGame == None in showGameInfo"
			return
		
		consoleRow = Console(self.gdb).getObjectById(self.selectedConsoleId)
		
		if(consoleRow == None):
			print "RCB_WARNING: consoleRow == None in showConsoleInfo"
			return
			
		image = consoleRow[3]		
		description = consoleRow[2]		
		
		""" TODO no console ionfo atm
		selectedGame.setProperty('mainviewgameinfo', image)
		selectedGame.setProperty('gamedesc', description)
		"""
		
	
	def showGameInfo(self):
		
		if(self.getListSize() == 0):
			print "RCB_WARNING: ListSize == 0 in showGameInfo"
			return
					
		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0
		selectedGame = self.getListItem(pos)
		if(selectedGame == None):
			print "RCB_WARNING: selectedGame == None in showGameInfo"
			return
			
		gameId = selectedGame.getLabel2()
		gameRow = Game(self.gdb).getObjectById(gameId)		
		
		if(gameRow == None):
			print "RCB_WARNING: gameRow == None in showGameInfo"
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
			


	def launchEmu(self):		

		if(self.getListSize() == 0):
			return

		pos = self.getCurrentListPosition()
		if(pos == -1):
			pos = 0
		selectedGame = self.getListItem(pos)
		
		if(selectedGame == None):
			print "RCB_WARNING: selectedGame == None in launchEmu"
			return
			
		gameId = selectedGame.getLabel2()		
		
		helper.launchEmu(self.gdb, self, gameId)
		
		
	def updateDB(self):		
		dbupdate.DBUpdate().updateDB(self.gdb, self)
		self.updateControls()		
		
	
	def importSettings(self):
		importsettings.SettingsImporter().importSettings(self.gdb, os.path.join(RCBHOME, 'resources', 'database'), self)
		self.updateControls()
		
			
	def checkAutoExec(self):
		
		autoexec = os.path.join(RCBHOME, '..', 'autoexec.py')		
		if (os.path.isfile(autoexec)):	
			lines = ""
			try:
				fh = fh=open(autoexec,"r")
				lines = fh.readlines()
				fh.close()
			except Exception, (exc):
				print("RCB ERROR: Cannot access autoexec.py: " +str(exc))
				return
				
			if(len(lines) > 0):
				firstLine = lines[0]
				#check if it is our autoexec
				if(firstLine.startswith('#Rom Collection Browser autoexec')):
					try:
						os.remove(autoexec)
					except Exception, (exc):
						print("RCB ERROR: Cannot remove autoexec.py: " +str(exc))
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
				print("RCB ERROR: Cannot rename autoexec.py: " +str(exc))
				return
			
		RCBSetting(self.gdb).update(('autoexecBackupPath',), (None,), rcbSetting[0])
		self.gdb.commit()
			
	
	def writeMsg(self, msg):
		control = self.getControlById(CONTROL_LABEL_MSG)
		if(control == None):
			print "RCB_WARNING: control == None in writeMsg"
			return
		control.setLabel(msg)
		
		
	def saveViewState(self, isOnExit):
		
		if(self.getListSize() == 0):
			return
		
		selectedGameIndex = self.getCurrentListPosition()
		if(selectedGameIndex == -1):
			selectedGameIndex = 0
		if(selectedGameIndex == None):
			print "RCB_WARNING: selectedGameIndex == None in saveViewState"
			return
		
		self.saveViewMode()
		
		helper.saveViewState(self.gdb, isOnExit, 'mainView', selectedGameIndex, self.selectedConsoleIndex, self.selectedGenreIndex, self.selectedPublisherIndex, 
			self.selectedYearIndex, self.selectedControlId, None)
			
			
	def saveViewMode(self):
		
		changeViewButton = self.getControlById(CONTROL_BUTTON_CHANGE_VIEW)		
		buttonText = changeViewButton.getLabel()
		
		lastView = ''
		if(buttonText.find('Thumbs') >= 0):
			lastView = 'rcb_thumbs_view'
		elif(buttonText.find('Info 2') >= 0):
			lastView = 'rcb_info2_view'
		elif(buttonText.find('Info') >= 0):
			lastView = 'rcb_info_view'
		else:
			print "RCB WARNING: Button Change View has unknown text"
			
		xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_thumbs_view')
		xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_info_view')
		xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_info2_view')	
		
		xbmc.executebuiltin( "Skin.SetBool(%s)" %lastView)
		xbmc.executebuiltin( "Skin.SetBool(%s)" %'rcb_OnLoad')

	
	def loadViewState(self):
		rcbSetting = helper.getRCBSetting(self.gdb)
		if(rcbSetting == None):			
			print "RCB_WARNING: rcbSetting == None in loadViewState"
			focusControl = self.getControlById(CONTROL_BUTTON_SETTINGS)
			self.setFocus(focusControl)
			return
		
		"""
		xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_thumbs_view')
		xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_info_view')
		xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_info2_view')		
		
		if(rcbSetting[1] in ('rcb_thumbs_view', 'rcb_info_view', 'rcb_info2_view')):
			xbmc.executebuiltin( "Skin.SetBool(%s)" %rcbSetting[1])
		else:
			xbmc.executebuiltin( "Skin.SetBool(%s)" %'rcb_info2_view')
		"""
		
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
				print "RCB_WARNING: focusControl == None in loadViewState"
				return
			self.setFocus(focusControl)
			if(rcbSetting[17] == CONTROL_CONSOLES):
				self.showConsoleInfo()
			elif(CONTROL_GAMES_GROUP_START <= rcbSetting[17] <= CONTROL_GAMES_GROUP_END):
				self.showGameInfo()
		else:
			focusControl = self.getControlById(CONTROL_CONSOLES)
			if(focusControl == None):
				print "RCB_WARNING: focusControl == None (2) in loadViewState"
				return
			self.setFocus(focusControl)
		
		xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_OnLoad')
		
		#lastSelectedView
		if(rcbSetting[1] == 'gameInfoView'):
			self.showGameInfoDialog()
			
			
			
	def setFilterSelection(self, controlId, selectedIndex):
		if(selectedIndex != None):
			control = self.getControlById(controlId)
			if(control == None):
				print "RCB_WARNING: control == None in setFilterSelection"
				return
			
			if(controlId == CONTROL_GAMES_GROUP_START):
				self.setCurrentListPosition(selectedIndex)
				selectedItem = self.getListItem(selectedIndex)
				
			else:
				control.selectItem(selectedIndex)
				selectedItem = control.getSelectedItem()
				
			if(selectedItem == None):
				return 0
			label2 = selectedItem.getLabel2()
			return label2
		else:
			return 0
			
	
	def showGameInfoDialog(self):		
		
		if(self.getListSize() == 0):
			return
		
		selectedGameIndex = self.getCurrentListPosition()		
		if(selectedGameIndex == -1):
			selectedGameIndex = 0
		selectedGame = self.getListItem(selectedGameIndex)		
		if(selectedGame == None):
			print "RCB_WARNING: selectedGame == None in showGameInfoDialog"
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
		
		xbmc.executebuiltin( "Skin.Reset(%s)" %'rcb_OnLoad')
		
		
	
	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except: 
			#HACK there seems to be a problem with recognizing the scrollbar controls
			if(controlId not in (CONROL_SCROLLBARS)):
				print("RCB ERROR: Control with id: %s could not be found. Check WindowXML file." %str(controlId))
				self.writeMsg("Control with id: %s could not be found. Check WindowXML file." %str(controlId))
			return None
		
		return control
	
	
	def exit(self):				
		
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