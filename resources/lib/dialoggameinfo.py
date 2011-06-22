
import xbmc, xbmcgui
import os, sys
import helper, util, dbupdate, launcher
from util import *
from gamedatabase import *



ACTION_CANCEL_DIALOG = ( 9, 10, 11)
ACTION_MOVEMENT_LEFT = ( 1, )
ACTION_MOVEMENT_RIGHT = ( 2, )
ACTION_MOVEMENT_UP = ( 3, )
ACTION_MOVEMENT_DOWN = ( 4, )
ACTION_MOVEMENT = ( 1, 2, 3, 4, )

CONTROL_BUTTON_PLAYGAME = 3000

CONTROL_GAME_LIST_GROUP = 1000
CONTROL_GAME_LIST = 59

CONTROL_LABEL_MSG = 4000

RCBHOME = util.getAddonInstallPath()


class UIGameInfoView(xbmcgui.WindowXMLDialog):
	
	def __init__(self, *args, **kwargs):		
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )		
		
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
		self.fileDict = kwargs["fileDict"]
		
		self.doModal()
		
		
	def onInit(self):
		
		Logutil.log("Begin OnInit", util.LOG_LEVEL_DEBUG)
		
		self.addItem(self.selectedGame, False)
		
		self.showGameInfo()
		
		Logutil.log("End OnInit", util.LOG_LEVEL_DEBUG)		
		
		
	def onClick( self, controlId ):
		Logutil.log("Begin onClick", util.LOG_LEVEL_DEBUG)
		
		if (controlId == CONTROL_BUTTON_PLAYGAME):			
			self.launchEmu()
			
		Logutil.log("End onClick", util.LOG_LEVEL_DEBUG)
		

	def onFocus( self, controlId ):
		Logutil.log("onFocus", util.LOG_LEVEL_DEBUG)		
		self.selectedControlId = controlId

	def onAction( self, action ):		
		
		if(action.getId() in ACTION_CANCEL_DIALOG):
			Logutil.log("onAction exit", util.LOG_LEVEL_DEBUG)
			self.close()
	
		
	def showGameInfo(self):
		
		Logutil.log("Begin showGameInfo", util.LOG_LEVEL_DEBUG)
				
		gameRow = Game(self.gdb).getObjectById(self.selectedGameId)
		if(gameRow == None):
			self.writeMsg('Selected game could not be read from database.')
			return
		
		fileDict = self.getFileDictByGameRow(self.gdb, gameRow)
		
		romCollection = None
		try:
			romCollection = self.config.romCollections[str(gameRow[util.GAME_romCollectionId])]
		except:
			Logutil.log('Cannot get rom collection with id: ' +str(gameRow[util.GAME_romCollectionId]), util.LOG_LEVEL_ERROR)
				
		background = os.path.join(RCBHOME, 'resources', 'skins', 'Default', 'media', 'rcb-background-black.png')					
		
		self.setImage(util.IMAGE_CONTROL_GIV_BACKGROUND, romCollection.imagePlacing.fileTypesForGameInfoViewBackground, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], background, self.selectedGame, fileDict)
		self.setImage(util.IMAGE_CONTROL_GIV_Img1, romCollection.imagePlacing.fileTypesForGameInfoView1, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], '', self.selectedGame, fileDict)
		self.setImage(util.IMAGE_CONTROL_GIV_Img2, romCollection.imagePlacing.fileTypesForGameInfoView2, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], None, self.selectedGame, fileDict)
		self.setImage(util.IMAGE_CONTROL_GIV_Img3, romCollection.imagePlacing.fileTypesForGameInfoView3, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], None, self.selectedGame, fileDict)
		self.setImage(util.IMAGE_CONTROL_GIV_Img4, romCollection.imagePlacing.fileTypesForGameInfoView4, gameRow[util.ROW_ID], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId], gameRow[util.GAME_romCollectionId], None, self.selectedGame, fileDict)
		
		Logutil.log("End showGameInfo", util.LOG_LEVEL_DEBUG)
		
		
	def getItemName(self, object, itemId):
		
		Logutil.log("Begin getItemName", util.LOG_LEVEL_DEBUG)
		
		itemRow = object.getObjectById(itemId)
		if(itemRow == None):
			Logutil.log("End getItemName", util.LOG_LEVEL_DEBUG)
			return ""
		else:
			Logutil.log("End getItemName", util.LOG_LEVEL_DEBUG)
			return itemRow[1]
			
	
	def getGameProperty(self, property):				
		
		if(property == None):
			return ""
		
		try:				
			result = str(property)
		except:
			result = ""		
			
		return result
		
	
	def getFileDictByGameRow(self, gdb, gameRow):
		
		files = File(gdb).getFilesByParentIds(gameRow[util.ROW_ID], gameRow[util.GAME_romCollectionId], gameRow[util.GAME_publisherId], gameRow[util.GAME_developerId])
				
		fileDict = self.cacheFiles(files)
		
		return fileDict
	
	
	def cacheFiles(self, fileRows):
		
		Logutil.log("Begin cacheFiles" , util.LOG_LEVEL_DEBUG)
		
		fileDict = {}
		for fileRow in fileRows:
			key = '%i;%i' % (fileRow[util.FILE_parentId] , fileRow[util.FILE_fileTypeId])
			item = None
			try:
				item = fileDict[key]
			except:
				pass
			if(item == None):
				fileRowList = []
				fileRowList.append(fileRow)
				fileDict[key] = fileRowList
			else:				
				fileRowList = fileDict[key]
				fileRowList.append(fileRow)
				fileDict[key] = fileRowList
				
		Logutil.log("End cacheFiles" , util.LOG_LEVEL_DEBUG)
		return fileDict
	
	
	def getFileForControl(self, controlName, gameId, publisherId, developerId, romCollectionId, fileDict):
		files = helper.getFilesByControl_Cached(self.gdb, controlName, gameId, publisherId, developerId, romCollectionId, self.fileTypeForControlDict, self.fileTypeDict, fileDict, self.romCollectionDict)		
		if(files != None and len(files) != 0):
			file = files[0]
		else:
			file = ""
			
		return file
	
	
	
	def setImage(self, controlName, fileTypes, gameId, publisherId, developerId, romCollectionId, defaultImage, selectedGame, fileDict):
		
		Logutil.log("Begin setImage", util.LOG_LEVEL_DEBUG)						
				
		images = helper.getFilesByControl_Cached(self.gdb, fileTypes, gameId, publisherId, developerId, romCollectionId, fileDict)
								
		#TODO more than one image?
		image = ''
		if(images != None and len(images) != 0):
			image = images[0]						
			#control.setVisible(1)
		else:
			if(defaultImage == None):
				pass
				#control.setVisible(0)
			else:						
				image = defaultImage
				
		selectedGame.setProperty(controlName, image)
				
		Logutil.log("End setImage", util.LOG_LEVEL_DEBUG)
	
	
	
	def launchEmu(self):
		
		Logutil.log("Begin launchEmu", util.LOG_LEVEL_INFO)				
		
		launcher.launchEmu(self.gdb, self, self.selectedGameId, self.config, self.settings)
		Logutil.log("End launchEmu", util.LOG_LEVEL_INFO)
		
	
	def saveViewState(self, isOnExit):
		
		Logutil.log("Begin saveViewState", util.LOG_LEVEL_INFO)
		
		#TODO: save selectedGameIndex from main view
		selectedGameIndex = 0
		
		helper.saveViewState(self.gdb, isOnExit, 'gameInfoView', selectedGameIndex, self.selectedConsoleIndex, self.selectedGenreIndex, self.selectedPublisherIndex, 
			self.selectedYearIndex, self.selectedCharacterIndex, self.selectedControlIdMainView, self.selectedControlId)
			
		Logutil.log("End saveViewState", util.LOG_LEVEL_INFO)
			
			
	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except: 
			Logutil.log("Control with id: %s could not be found. Check WindowXML file." %str(controlId), util.LOG_LEVEL_ERROR)
			self.writeMsg("Control with id: %s could not be found. Check WindowXML file." %str(controlId))
			return None
		
		return control


	def writeMsg(self, msg):
		control = self.getControlById(CONTROL_LABEL_MSG)
		if(control == None):
			return
			
		control.setLabel(msg)
		