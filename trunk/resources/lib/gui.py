
import os, sys

import getpass, ntpath, re, string, glob, xbmc, xbmcgui
from xml.dom.minidom import Document, parseString
from pysqlite2 import dbapi2 as sqlite

import dbupdate, importsettings
from gamedatabase import *

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

ACTION_SHOW_INFO =		(11,) # GREEN - 195
ACTION_CONTEXT_MENU =	(117,) # RED - 229
ACTION_SHOW_GUI =		(18,) # YELLOW - 213
ACTION_SELECT_ITEM = ( 7, )


#ControlIds
CONTROL_CONSOLES = 500
CONTROL_GENRE = 600
CONTROL_YEAR = 700
CONTROL_PUBLISHER = 800
FILTER_CONTROLS = (500, 600, 700, 800,)

CONTROL_GAMES = 1500
CONTROL_CONSOLE_IMG = 2000
CONTROL_CONSOLE_DESC = 2100
CONTROL_BUTTON_SETTINGS = 3000
CONTROL_BUTTON_UPDATEDB = 3100
CONTROL_BUTTON_CHANGEVIEW = 3200

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
	
	def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback):
		# Changing the three varibles passed won't change, anything
		# Doing strXMLname = "bah.xml" will not change anything.
		# don't put GUI sensitive stuff here (as the xml hasn't been read yet
		# Idea to initialize your variables here
		pass

	def onInit(self):
		self.gdb.connect()
		
		self.updateControls()
		self.loadViewState()
		self.checkAutoExec()
		

	def updateControls(self):
		#prepare FilterControls	
		self.showConsoles()		
		self.showGenre()		
		self.showYear()
		self.showPublisher()
		

	def onAction(self, action):
		
		if(action.getId() in ACTION_CANCEL_DIALOG):
			self.exit()
		elif(action.getId() in ACTION_MOVEMENT_UP or action.getId() in ACTION_MOVEMENT_DOWN):
			try:
				control = self.getControl(self.selectedControlId)
			except: 
				return
			
			if(self.selectedControlId in FILTER_CONTROLS):
				label = str(control.getSelectedItem().getLabel())
				label2 = str(control.getSelectedItem().getLabel2())
					
				if (self.selectedControlId == CONTROL_CONSOLES):				
					self.selectedConsoleId = int(label2)
					self.selectedConsoleIndex = control.getSelectedPosition()
					if (self.selectedConsoleId == 0):
						self.getControl(CONTROL_CONSOLE_IMG).setVisible(0)
						self.getControl(CONTROL_CONSOLE_DESC).setVisible(0)
					else:
						self.showConsoleInfo()
				elif (self.selectedControlId == CONTROL_GENRE):
					self.selectedGenreId = int(label2)
					self.selectedGenreIndex = control.getSelectedPosition()
				elif (self.selectedControlId == CONTROL_YEAR):
					self.selectedYearId = int(label2)
					self.selectedYearIndex = control.getSelectedPosition()
				elif (self.selectedControlId == CONTROL_PUBLISHER):
					self.selectedPublisherId = int(label2)
					self.selectedPublisherIndex = control.getSelectedPosition()
					
				self.showGames()
		elif(action.getId() in ACTION_MOVEMENT_LEFT or action.getId() in ACTION_MOVEMENT_RIGHT):
			try:
				control = self.getControl(self.selectedControlId)
			except: 
				return
				
			if(self.selectedControlId == CONTROL_GAMES):
				self.showGameInfo()



	def onClick(self, controlId):
		"""
		Notice: onClick not onControl
		Notice: it gives the ID of the control not the control object
		"""
		if (controlId == CONTROL_BUTTON_SETTINGS):			
			self.importSettings()
		elif (controlId == CONTROL_BUTTON_UPDATEDB):			
			self.updateDB()
		elif (controlId == CONTROL_BUTTON_CHANGEVIEW):
			print "Button Change View"
		elif (controlId != CONTROL_GAMES):
			self.setFocus(self.getControl(CONTROL_GAMES))
			self.showGameInfo()
		else:
			self.launchEmu()


	def onFocus(self, controlId):		
		self.selectedControlId = controlId
	
	
	def showFilterControl(self, dbo, controlId, showEntryAllItems):
		#xbmcgui.lock()
		rows = dbo.getAllOrdered()
		
		control = self.getControl(controlId)
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
		rcbSetting = self.getRCBSetting()
		self.selectedConsoleId = self.showFilterControl(Console(self.gdb), CONTROL_CONSOLES, rcbSetting[11])


	def showGenre(self):
		rcbSetting = self.getRCBSetting()
		self.selectedGenreId = self.showFilterControl(Genre(self.gdb), CONTROL_GENRE, rcbSetting[12])
		
	
	def showYear(self):
		rcbSetting = self.getRCBSetting()
		self.selectedYearId = self.showFilterControl(Year(self.gdb), CONTROL_YEAR, rcbSetting[13])
		
		
	def showPublisher(self):
		rcbSetting = self.getRCBSetting()
		self.selectedPublisherId = self.showFilterControl(Publisher(self.gdb), CONTROL_PUBLISHER, rcbSetting[14])


	def showGames(self):
		#xbmcgui.lock()		
		
		games = Game(self.gdb).getFilteredGames(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId, self.selectedPublisherId)		
			
		self.getControl(CONTROL_GAMES).setVisible(1)
		self.getControl(CONTROL_GAMES).reset()
		
		self.writeMsg("loading games...")
		
		items = []
		for game in games:			
			coverFile = File(self.gdb).getCoverByGameId(game[0])		
			items.append(xbmcgui.ListItem(str(game[1]), str(game[0]), coverFile, ''))
				
		self.getControl(CONTROL_GAMES).addItems(items)
		self.writeMsg("")
		
		#xbmcgui.unlock()	

	def showConsoleInfo(self):		
		consoleRow = Console(self.gdb).getObjectById(self.selectedConsoleId)
		image = consoleRow[3]		
		description = consoleRow[2]
		self.getControl(CONTROL_CONSOLE_IMG).setVisible(1)
		self.getControl(CONTROL_CONSOLE_IMG).setImage(image)
		self.getControl(CONTROL_CONSOLE_DESC).setVisible(1)
		self.getControl(CONTROL_CONSOLE_DESC).setText(description)
		
	
	def showGameInfo(self):		
		selectedGame = self.getControl(CONTROL_GAMES).getSelectedItem()
		gameId = selectedGame.getLabel2()
		gameRow = Game(self.gdb).getObjectById(gameId)
		screenshotFile = File(self.gdb).getIngameScreenshotByGameId(gameId)		
		description = gameRow[2]		
		self.getControl(CONTROL_CONSOLE_IMG).setVisible(1)		
		self.getControl(CONTROL_CONSOLE_IMG).setImage(screenshotFile)
		self.getControl(CONTROL_CONSOLE_DESC).setVisible(1)
		self.getControl(CONTROL_CONSOLE_DESC).setText(description)


	def launchEmu(self):
		selectedGame = self.getControl(CONTROL_GAMES).getSelectedItem()
		gameId = selectedGame.getLabel2()
		
		gameRow = Game(self.gdb).getObjectById(gameId)		
		self.writeMsg("Launch Game " +str(gameRow))
		
		romPath = Path(self.gdb).getRomPathByRomCollectionId(gameRow[5])
		romCollectionRow = RomCollection(self.gdb).getObjectById(gameRow[5])
		cmd = romCollectionRow[3]		
		
		#handle multi rom scenario
		filenameRows = File(self.gdb).getRomsByGameId(gameRow[0])
		fileindex = int(0)
		for fileNameRow in filenameRows:
			fileName = fileNameRow[0]
			rom = os.path.join(romPath, fileName)			
			#cmd could be: uae {-%I% %ROM%}
			#we have to repeat the part inside the brackets and replace the %I% with the current index
			obIndex = cmd.find('{')
			cbIndex = cmd.find('}')			
			if obIndex > -1 and cbIndex > 1:
				replString = cmd[obIndex+1:cbIndex]
			cmd = cmd.replace("{", "")
			cmd = cmd.replace("}", "")
			if fileindex == 0:
				#romCollectionRow[5] = escapeCmd
				if (romCollectionRow[5] == 1):				
					cmd = cmd.replace('%ROM%', re.escape(rom))					
				else:					
					cmd = cmd.replace('%ROM%', rom)
				cmd = cmd.replace('%I%', str(fileindex))
			else:
				newrepl = replString
				if (romCollectionRow[5] == 1):
					newrepl = newrepl.replace('%ROM%', re.escape(rom))					
				else:					
					newrepl = newrepl.replace('%ROM%', rom)
				newrepl = newrepl.replace('%I%', str(fileindex))
				cmd += ' ' +newrepl			
			fileindex += 1
		#romCollectionRow[4] = useSolo
		if (romCollectionRow[4] == 'True'):
			# Backup original autoexec.py		
			autoexec = os.path.join(RCBHOME, '..', 'autoexec.py')
			self.doBackup(autoexec)			

			# Write new autoexec.py
			fh = open(autoexec,'w') # truncate to 0
			fh.write("#Rom Collection Browser autoexec\n")
			fh.write("import xbmc\n")
			fh.write("xbmc.executescript('"+ os.path.join(RCBHOME, 'default.py')+"')\n")
			fh.close()			

			# Remember selection
			self.saveViewState(False)
			
			#invoke batch file that kills xbmc before launching the emulator
			env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]				
			if(env == "win32"):
				#There is a problem with quotes passed as argument to windows command shell. This only works with "call"
				cmd = 'call \"' +os.path.join(RCBHOME, 'applaunch.bat') +'\" ' +cmd						
			else:
				cmd = os.path.join(re.escape(RCBHOME), 'applaunch.sh ') +cmd
		
		print "cmd: " +cmd
		os.system(cmd)		
		
		
	def updateDB(self):		
		dbupdate.DBUpdate().updateDB(self.gdb, self)
		self.updateControls()
		
	
	def importSettings(self):
		importsettings.SettingsImporter().importSettings(self.gdb, os.path.join(RCBHOME, 'resources', 'database'), self)
		self.updateControls()
		
		
	def doBackup(self,fName):
		if os.path.isfile(fName):
			newFileName = fName+'.bak'
			
			if os.path.isfile(newFileName):
				return
				
			os.rename(fName, newFileName)
			
			rcbSetting = self.getRCBSetting()
			if (rcbSetting == None):
				return
			
			RCBSetting(self.gdb).update(('autoexecBackupPath',), (newFileName,), rcbSetting[0])
			self.gdb.commit()
			
			
	def checkAutoExec(self):
		
		autoexec = os.path.join(RCBHOME, '..', 'autoexec.py')		
		if (os.path.isfile(autoexec)):			
			fh = fh=open(autoexec,"r")
			lines = fh.readlines()
			fh.close()
			if(len(lines) > 0):
				firstLine = lines[0]
				#check if it is our autoexec
				if(firstLine.startswith('#Rom Collection Browser autoexec')):
					os.remove(autoexec)
				else:
					return
		
		rcbSetting = self.getRCBSetting()
		if (rcbSetting == None):			
			return
					
		autoExecBackupPath = rcbSetting[9]
		if (autoExecBackupPath == None):
			return
			
		if (os.path.isfile(autoExecBackupPath)):
			os.rename(autoExecBackupPath, autoexec)
			
		RCBSetting(self.gdb).update(('autoexecBackupPath',), (None,), rcbSetting[0])
		self.gdb.commit()
			
	
	def writeMsg(self, msg):
		self.getControl(CONTROL_LABEL_MSG).setLabel(msg)
			
			
	def getRCBSetting(self):
		rcbSettingRows = RCBSetting(self.gdb).getAll()
		if(rcbSettingRows == None or len(rcbSettingRows) != 1):
			#TODO raise error
			return None
						
		return rcbSettingRows[0]
		
		
	def saveViewState(self, isOnExit):
		rcbSetting = self.getRCBSetting()
		
		if(isOnExit):
			#saveViewStateOnExit
			saveViewState = rcbSetting[15]
		else:
			#saveViewStateOnLaunchEmu
			saveViewState = rcbSetting[16]
		
		selectedGameIndex = self.getControl(CONTROL_GAMES).getSelectedPosition()
		
		if(saveViewState == 'True'):
			RCBSetting(self.gdb).update(('lastSelectedView', 'lastSelectedConsoleIndex', 'lastSelectedGenreIndex', 'lastSelectedPublisherIndex', 'lastSelectedYearIndex', 'lastSelectedGameIndex', 'lastFocusedControl'),
				('gameListAsIcons', self.selectedConsoleIndex, self.selectedGenreIndex, self.selectedPublisherIndex, self.selectedYearIndex, selectedGameIndex, self.selectedControlId), rcbSetting[0])
		else:
			RCBSetting(self.gdb).update(('lastSelectedView', 'lastSelectedConsoleIndex', 'lastSelectedGenreIndex', 'lastSelectedPublisherIndex', 'lastSelectedYearIndex', 'lastSelectedGameIndex', 'lastFocusedControl'),
				(None, None, None, None, None, None, None), rcbSetting[0])
				
		self.gdb.commit()
		
	
	def loadViewState(self):
		rcbSetting = self.getRCBSetting()
		
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
		self.setFilterSelection(CONTROL_GAMES, rcbSetting[6])
						
		#lastFocusedControl
		if(rcbSetting[17] != None):
			self.setFocus(self.getControl(rcbSetting[17]))
			if(rcbSetting[17] == CONTROL_CONSOLES):
				self.showConsoleInfo()
			elif(rcbSetting[17] == CONTROL_GAMES):
				self.showGameInfo()
		else:
			self.setFocus(self.getControl(CONTROL_CONSOLES))
			
			
			
	def setFilterSelection(self, controlId, selectedIndex):
		if(selectedIndex != None):
			control = self.getControl(controlId)
			control.selectItem(selectedIndex)
			selectedItem = control.getSelectedItem()
			label2 = selectedItem.getLabel2()
			return label2
		else:
			return 0
			
	
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
    ui = UIGameDB("script-GameDB-main.xml", os.getcwd(), "Default", 1)
    #_progress_dialog( -1 )
    ui.doModal()
    del ui

main()