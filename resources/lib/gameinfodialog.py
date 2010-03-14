
import os, sys
import xbmc, xbmcgui
import dbupdate, importsettings
from gamedatabase import *


ACTION_EXIT_SCRIPT = ( 10, )
ACTION_CANCEL_DIALOG = ACTION_EXIT_SCRIPT + ( 9, )
ACTION_MOVEMENT_LEFT = ( 1, )
ACTION_MOVEMENT_RIGHT = ( 2, )
ACTION_MOVEMENT_UP = ( 3, )
ACTION_MOVEMENT_DOWN = ( 4, )
ACTION_MOVEMENT = ( 1, 2, 3, 4, )

CONTROL_LABEL_GAME = 6000
CONTROL_LABEL_GENRE = 6100
CONTROL_LABEL_YEAR = 6200
CONTROL_LABEL_PUBLISHER = 6300
CONTROL_LABEL_MSG = 4000


class UIGameInfoView(xbmcgui.WindowXMLDialog):
	def __init__(self, *args, **kwargs):		
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )		
		
		self.gdb = kwargs[ "gdb" ]
		self.selectedGameId = kwargs[ "gameId" ]
		self.selectedConsoleId = kwargs[ "consoleId" ]
		self.selectedGenreId = kwargs[ "genreId" ]		
		self.selectedYearId = kwargs[ "yearId" ]		
		self.selectedPublisherId = kwargs[ "publisherId" ]		
		
		self.doModal()
		
		
	def onInit(self):		
		self.showGameInfo()
		
		
	def onClick( self, controlId ):
		return		

	def onFocus( self, controlId ):
		return

	def onAction( self, action ):
		if(action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
		
		
	def showGameInfo(self):				
		gameRow = Game(self.gdb).getObjectById(self.selectedGameId)
		if(gameRow == None):
			self.writeMsg('Selected game could not be read from database.')
			return
		
		print "gameId: " +str(gameRow[0])
		
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
		
		self.getControl(CONTROL_LABEL_GAME).setLabel(gameRow[1])
		self.getControl(CONTROL_LABEL_GENRE).setLabel(genreString)
		self.getControl(CONTROL_LABEL_YEAR).setLabel(year)
		self.getControl(CONTROL_LABEL_PUBLISHER).setLabel(publisher)
		
		
	def getItemName(self, object, itemId):
		itemRow = object.getObjectById(itemId)
		if(itemRow == None):
			return ""
		else:
			return itemRow[1]
		
		
	def writeMsg(self, msg):
		print "writeMsg: " +msg
		self.getControl(CONTROL_LABEL_MSG).setLabel(msg)