
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

class UIGameDB(xbmcgui.WindowXML):
	
	gdb = GameDataBase(os.path.join(os.getcwd(), 'resources', 'database'))
	
	selectedControlId = 0	
	selectedConsoleId = 0
	selectedGenreId = 0
	selectedYearId = 0
	selectedPublisherId = 0
	
	def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback):
		# Changing the three varibles passed won't change, anything
		# Doing strXMLname = "bah.xml" will not change anything.
		# don't put GUI sensitive stuff here (as the xml hasn't been read yet
		# Idea to initialize your variables here
		pass

	def onInit(self):
		self.gdb.connect()
		
		self.updateControls()
		
		self.setFocus(self.getControl(CONTROL_CONSOLES))
		self.showGames()


	def updateControls(self):
		#prepare FilterControls	
		self.showConsoles()		
		self.showGenre()		
		self.showYear()
		self.showPublisher()
		

	def onAction(self, action):
		if(action.getId() in ACTION_CANCEL_DIALOG):
			self.gdb.close()
			self.close()
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
					if (self.selectedConsoleId == 0):
						self.getControl(CONTROL_CONSOLE_IMG).setVisible(0)
						self.getControl(CONTROL_CONSOLE_DESC).setVisible(0)
					else:
						self.showConsoleInfo()
				elif (self.selectedControlId == CONTROL_GENRE):
					self.selectedGenreId = int(label2)
				elif (self.selectedControlId == CONTROL_YEAR):
					self.selectedYearId = int(label2)
				elif (self.selectedControlId == CONTROL_PUBLISHER):
					self.selectedPublisherId = int(label2)
					
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
			print "Button Import Settings"
			self.importSettings()
		elif (controlId == CONTROL_BUTTON_UPDATEDB):
			print "Button UpdateDB"
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
	
	
	def showFilterControl(self, dbo, controlId):
		#xbmcgui.lock()
		rows = dbo.getAll()
		
		self.getControl(controlId).setVisible(1)
		self.getControl(controlId).reset()
		
		self.getControl(controlId).addItem(xbmcgui.ListItem("All", "0", "", ""))
		
		for row in rows:
			self.getControl(controlId).addItem(xbmcgui.ListItem(str(row[1]), str(row[0]), "", ""))
			
		#xbmcgui.unlock
		
		#TODO index nach neustart
		#self.lstMain.selectItem(0)		
		#self.setEmuDesc()
		#self.setFocus(self.lstMain)
		
	def showConsoles(self):
		self.showFilterControl(Console(self.gdb), CONTROL_CONSOLES)


	def showGenre(self):
		self.showFilterControl(Genre(self.gdb), CONTROL_GENRE)
		
	
	def showYear(self):
		self.showFilterControl(Year(self.gdb), CONTROL_YEAR)
		
		
	def showPublisher(self):
		self.showFilterControl(Publisher(self.gdb), CONTROL_PUBLISHER)


	def showGames(self):
		#xbmcgui.lock()		
		print "Begin ShowGames"
			
		games = Game(self.gdb).getFilteredGames(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId, self.selectedPublisherId)
		print str(games)
			
		self.getControl(CONTROL_GAMES).setVisible(1)
		self.getControl(CONTROL_GAMES).reset()
		
		for game in games:			
			coverFile = File(self.gdb).getCoverByGameId(game[0])			
			self.getControl(CONTROL_GAMES).addItem(xbmcgui.ListItem(str(game[1]), str(game[0]), coverFile, coverFile))
		
		#xbmcgui.unlock()	

	def showConsoleInfo(self):
		print "show Console Info"
		consoleRow = Console(self.gdb).getObjectById(self.selectedConsoleId)
		image = consoleRow[3]		
		description = consoleRow[2]
		self.getControl(CONTROL_CONSOLE_IMG).setVisible(1)
		self.getControl(CONTROL_CONSOLE_IMG).setImage(image)
		self.getControl(CONTROL_CONSOLE_DESC).setVisible(1)
		self.getControl(CONTROL_CONSOLE_DESC).setText(description)
		
	
	def showGameInfo(self):
		print "show Game Info"
		selectedGame = self.getControl(CONTROL_GAMES).getSelectedItem()
		gameId = selectedGame.getLabel2()
		gameRow = Game(self.gdb).getObjectById(gameId)
		screenshotFile = File(self.gdb).getIngameScreenshotByGameId(gameId)		
		description = gameRow[2]
		#print "Screenshot: " +screenshotFile
		#print "Screenshot exists: " +str(os.path.exists(screenshotFile))		
		self.getControl(CONTROL_CONSOLE_IMG).setVisible(1)		
		self.getControl(CONTROL_CONSOLE_IMG).setImage(screenshotFile)
		self.getControl(CONTROL_CONSOLE_DESC).setVisible(1)
		self.getControl(CONTROL_CONSOLE_DESC).setText(description)


	def launchEmu(self):
		selectedGame = self.getControl(CONTROL_GAMES).getSelectedItem()
		gameId = selectedGame.getLabel2()
		
		gameRow = Game(self.gdb).getObjectById(gameId)		
		print "Selected Game = " +str(gameRow)
		
		romPath = Path(self.gdb).getRomPathByRomCollectionId(gameRow[5])
		romCollectionRow = RomCollection(self.gdb).getObjectById(gameRow[5])
		cmd = romCollectionRow[3]
		print "Cmd = " +str(cmd)
		
		#handle multi rom scenario
		filenameRows = File(self.gdb).getRomsByGameId(gameRow[0])
		fileindex = int(0)
		for fileNameRow in filenameRows:
			fileName = fileNameRow[0]
			rom = os.path.join(romPath, fileName)
			print "Rom = " +rom
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
		if (romCollectionRow[4] == 1):
			# Backup original autoexec.py		
			#autoexec = SCRIPTUSR+'/autoexec.py'
			#self.doBackup(autoexec)

			# Write new autoexec.py
			#fh = open(autoexec,'w') # truncate to 0
			#fh.write("import xbmc\n")
			#fh.write("xbmc.executescript('"+HOMEDIR+"default.py')\n")
			#fh.close()

			# Remember selection
			#self.saveState()
			
			cmd = os.path.join(re.escape(os.getcwd()), 'applaunch.sh ') +cmd
		
		print "cmd: " +cmd
		env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
		print "Env: " +env
		#os.system(cmd)
		
		
	def updateDB(self):		
		dbupdate.DBUpdate().updateDB(self.gdb, )
		self.updateControls()
		
	
	def importSettings(self):
		importsettings.SettingsImporter().importSettings(self.gdb, os.path.join(os.getcwd(), 'resources', 'database'))
		self.updateControls()


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