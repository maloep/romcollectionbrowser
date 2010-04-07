
import os, sys, string, re
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *
from xml.dom.minidom import Document, parseString

class SettingsImporter:
	
	def importSettings(self, gdb, databaseDir, gui):
		
		self.gdb = gdb
		configFile = os.path.join(databaseDir, 'config.xml')
		fh=open(configFile,"r")
		xmlDoc = fh.read()
		fh.close()		
		xmlDoc = parseString(xmlDoc)
		
		gui.writeMsg("Importing Settings...")
		
		
		rcbSettings = xmlDoc.getElementsByTagName('RCBSettings')
		#TODO only 1 Setting allowed
		for rcbSetting in rcbSettings:
			favoriteConsole = self.getElementValue(rcbSetting, 'favoriteConsole')
			favoriteGenre = self.getElementValue(rcbSetting, 'favoriteGenre')
			showEntryAllConsoles = self.getElementValue(rcbSetting, 'showEntryAllConsoles')
			showEntryAllGenres = self.getElementValue(rcbSetting, 'showEntryAllGenres')
			showEntryAllYears = self.getElementValue(rcbSetting, 'showEntryAllYears')
			showEntryAllPublisher = self.getElementValue(rcbSetting, 'showEntryAllPublisher')
			saveViewStateOnExit = self.getElementValue(rcbSetting, 'saveViewStateOnExit')
			saveViewStateOnLaunchEmu = self.getElementValue(rcbSetting, 'saveViewStateOnLaunchEmu')
			
			self.insertRCBSetting(favoriteConsole, favoriteGenre, showEntryAllConsoles, showEntryAllGenres, showEntryAllYears, showEntryAllPublisher, 
				saveViewStateOnExit, saveViewStateOnLaunchEmu)
			
		gui.writeMsg("Importing Console Info...")
		
		consoles = xmlDoc.getElementsByTagName('Console')
		for console in consoles:			
			consoleName = self.getElementValue(console, 'name')
			consoleDesc = self.getElementValue(console, 'desc')
			consoleImage =  self.getElementValue(console, 'imgFile')
			
			self.insertConsole(consoleName, consoleDesc, consoleImage)
		
		
		gui.writeMsg("Importing File Types...")				
		
		#import internal file types
		self.insertFileType('rcb_rom', 'image', 'game')
		self.insertFileType('rcb_manual', 'image', 'game')
		self.insertFileType('rcb_description', 'image', 'game')
		self.insertFileType('rcb_configuration', 'image', 'game')
		
		#import user defined file types
		fileTypes = xmlDoc.getElementsByTagName('FileType')
		for fileType in fileTypes:
			name = self.getElementValue(fileType, 'name')
			type = self.getElementValue(fileType, 'type')
			parent = self.getElementValue(fileType, 'parent')
			
			self.insertFileType(name, type, parent)
		
		
		gui.writeMsg("Importing Rom Collections...")
		
		#fileTypesForControl must be deleted. There is no useful unique key
		FileTypeForControl(self.gdb).deleteAll()
		
		romCollections = xmlDoc.getElementsByTagName('RomCollection')
		for romCollection in romCollections:			
			romCollName = self.getElementValue(romCollection, 'name')
			gui.writeMsg("Importing Rom Collection: " +romCollName)
			consoleName = self.getElementValue(romCollection, 'consoleName')
			emuCmd = self.getElementValue(romCollection, 'emulatorCmd')
			emuSolo = self.getElementValue(romCollection, 'useEmuSolo')
			escapeCmd = self.getElementValue(romCollection, 'escapeCommand')
			relyOnNaming = self.getElementValue(romCollection, 'relyOnNaming')
			startWithDescFile = self.getElementValue(romCollection, 'startWithDescFile')
			descFilePerGame = self.getElementValue(romCollection, 'descFilePerGame')			
			descParserFile = self.getElementValue(romCollection, 'descriptionParserFile')			
			diskPrefix = self.getElementValue(romCollection, 'diskPrefix')
			typeOfManual = self.getElementValue(romCollection, 'typeOfManual')
			allowUpdate = self.getElementValue(romCollection, 'allowUpdate')
			ignoreOnScan = self.getElementValue(romCollection, 'ignoreOnScan')
			searchGameByCRC = self.getElementValue(romCollection, 'searchGameByCRC')
			searchGameByCRCIgnoreRomName = self.getElementValue(romCollection, 'searchGameByCRCIgnoreRomName')
			ignoreGameWithoutDesc = self.getElementValue(romCollection, 'ignoreGameWithoutDesc')
				
			
			romPaths = self.getElementValues(romCollection, 'romPath')
			descFilePaths = self.getElementValues(romCollection, 'descFilePath')
			configFilePaths = self.getElementValues(romCollection, 'configFilePath')
			manualPaths = self.getElementValues(romCollection, 'manualPath')
			
			
			#import romCollection first to obtain the id
			romCollectionId = self.insertRomCollection(consoleName, romCollName, emuCmd, emuSolo, escapeCmd, relyOnNaming, startWithDescFile, 
				descFilePerGame, descParserFile, diskPrefix, typeOfManual, allowUpdate, ignoreOnScan, searchGameByCRC, 
				searchGameByCRCIgnoreRomName, ignoreGameWithoutDesc)
			
			
			self.insertPaths(romCollectionId, romPaths, 'rcb_rom')
			self.insertPaths(romCollectionId, descFilePaths, 'rcb_description')
			self.insertPaths(romCollectionId, configFilePaths, 'rcb_configuration')
			self.insertPaths(romCollectionId, manualPaths, 'rcb_manual')
			
			
			self.handleTypedElements(romCollection, 'mediaPath', romCollectionId)
			
			fileTypesForGameList = self.getElementValues(romCollection, 'fileTypeForGameList')
			fileTypesForGameListSelected = self.getElementValues(romCollection, 'fileTypeForGameListSelected')
			fileTypesForMainViewBackground = self.getElementValues(romCollection, 'fileTypeForMainViewBackground')
			fileTypesForMainViewGameInfo = self.getElementValues(romCollection, 'fileTypeForMainViewGameInfo')
			fileTypesForGameInfoViewBackground = self.getElementValues(romCollection, 'fileTypeForGameInfoViewBackground')
			fileTypesForGameInfoViewGamelist = self.getElementValues(romCollection, 'fileTypeForGameInfoViewGamelist')
			fileTypesForGameInfoView1 = self.getElementValues(romCollection, 'fileTypeForGameInfoView1')
			fileTypesForGameInfoView2 = self.getElementValues(romCollection, 'fileTypeForGameInfoView2')
			fileTypesForGameInfoView3 = self.getElementValues(romCollection, 'fileTypeForGameInfoView3')
			fileTypesForGameInfoView4 = self.getElementValues(romCollection, 'fileTypeForGameInfoView4')
			fileTypesForGameInfoViewVideoWindow = self.getElementValues(romCollection, 'fileTypeForGameInfoViewVideoWindow')
			
			
			
			self.insertFileTypeForControl(romCollectionId, fileTypesForGameList, 'gamelist')
			self.insertFileTypeForControl(romCollectionId, fileTypesForGameListSelected, 'gamelistselected')
			self.insertFileTypeForControl(romCollectionId, fileTypesForMainViewBackground, 'mainviewbackground')
			self.insertFileTypeForControl(romCollectionId, fileTypesForMainViewGameInfo, 'mainviewgameinfo')
			self.insertFileTypeForControl(romCollectionId, fileTypesForGameInfoViewBackground, 'gameinfoviewbackground')
			self.insertFileTypeForControl(romCollectionId, fileTypesForGameInfoViewGamelist, 'gameinfoviewgamelist')
			self.insertFileTypeForControl(romCollectionId, fileTypesForGameInfoView1, 'gameinfoview1')
			self.insertFileTypeForControl(romCollectionId, fileTypesForGameInfoView2, 'gameinfoview2')
			self.insertFileTypeForControl(romCollectionId, fileTypesForGameInfoView3, 'gameinfoview3')
			self.insertFileTypeForControl(romCollectionId, fileTypesForGameInfoView4, 'gameinfoview4')
			self.insertFileTypeForControl(romCollectionId, fileTypesForGameInfoViewVideoWindow, 'gameinfoviewvideowindow')
				
			
			
		#TODO Transaction?
		gdb.commit()
		gui.writeMsg("Done.")
		
	
	
	def getElementValue(self, parentNode, elementName):
		nodeList = parentNode.getElementsByTagName(elementName)
		if(nodeList == None):
			return ""
				
		node = nodeList[0]
		if(node == None):
			return ""
		
		firstChild = node.firstChild
		if(firstChild == None):
			return ""
			
		return firstChild.nodeValue
		
	
	def getElementValues(self, parentNode, elementName):
		valueList = []
		nodeList = parentNode.getElementsByTagName(elementName)
		for node in nodeList:
			if(node == None):
				continue
			if(node.firstChild == None):
				continue
			valueList.append(node.firstChild.nodeValue)
			
		return valueList
		
		
	def handleTypedElements(self, parentNode, elementName, romCollectionId):
		
		nodeList = parentNode.getElementsByTagName(elementName)
		for node in nodeList:
			if(node == None):				
				continue
			if(node.firstChild == None):				
				continue
			
			path = node.firstChild.nodeValue
			
			if(not node.hasAttributes()):
				#TODO raiseException				
				continue
				
			fileType = node.getAttribute('type')			
			fileTypeRow = FileType(self.gdb).getOneByName(fileType)			
			if(fileTypeRow == None):				
				continue
			
			"""
			if(elementName == 'videoPath'):
				fileType = 'video_' +fileType
			fileTypeId = self.insertFileType(fileType)
			"""
						
			self.insertPath(node.firstChild.nodeValue, fileType, fileTypeRow[0], romCollectionId)
			
		
	
	def insertRCBSetting(self, favoriteConsole, favoriteGenre, showEntryAllConsoles, showEntryAllGenres, showEntryAllYears, showEntryAllPublisher, saveViewStateOnExit, saveViewStateOnLaunchEmu):
		
		rcbSettingRows = RCBSetting(self.gdb).getAll()
		
		if(favoriteConsole == ''):
			favoriteConsole = None
		if(favoriteGenre == ''):
			favoriteGenre = None
		if(showEntryAllConsoles == ''):
			showEntryAllConsoles = None
		if(showEntryAllGenres == ''):
			showEntryAllGenres = None
		if(showEntryAllYears == ''):
			showEntryAllYears = None
		if(showEntryAllPublisher == ''):
			showEntryAllPublisher = None
		if(saveViewStateOnExit == ''):
			saveViewStateOnExit = None
		if(saveViewStateOnLaunchEmu == ''):
			saveViewStateOnLaunchEmu = None
		
		if(rcbSettingRows == None or len(rcbSettingRows) == 0):			
			RCBSetting(self.gdb).insert((None, None, None, None, None, None, favoriteConsole, favoriteGenre, None, CURRENT_SCRIPT_VERSION, 
				showEntryAllConsoles, showEntryAllGenres, showEntryAllYears, showEntryAllPublisher, saveViewStateOnExit, saveViewStateOnLaunchEmu, None, None))
		else:
			rcbSetting = rcbSettingRows[0]
			RCBSetting(self.gdb).update(('dbVersion', 'favoriteConsoleId', 'favoriteGenreId', 'showEntryAllConsoles', 'showEntryAllGenres', 'showEntryAllYears', 'showEntryAllPublisher', 'saveViewStateOnExit', 'saveViewStateOnLaunchEmu'),
				(CURRENT_SCRIPT_VERSION, favoriteConsole, favoriteGenre, showEntryAllConsoles, showEntryAllGenres, showEntryAllYears, showEntryAllPublisher, saveViewStateOnExit, saveViewStateOnLaunchEmu), rcbSetting[0])
	
	
	def insertConsole(self, consoleName, consoleDesc, consoleImage):
		consoleRow = Console(self.gdb).getOneByName(consoleName)		
		if(consoleRow == None):			
			Console(self.gdb).insert((consoleName, consoleDesc, consoleImage))
		else:
			Console(self.gdb).update(('name', 'description', 'imageFileName'), (consoleName, consoleDesc, consoleImage), consoleRow[0])
	
	
	def insertRomCollection(self, consoleName, romCollName, emuCmd, emuSolo, escapeCmd, relyOnNaming, startWithDescFile, 
				descFilePerGame, descParserFile, diskPrefix, typeOfManual, allowUpdate, ignoreOnScan, searchGameByCRC, 
				searchGameByCRCIgnoreRomName, ignoreGameWithoutDesc):		
		
		consoleRow = Console(self.gdb).getOneByName(consoleName)
		if(consoleRow == None):
			return
		consoleId = consoleRow[0] 
				
		romCollectionRow = RomCollection(self.gdb).getOneByName(romCollName)
		if(romCollectionRow == None):		
			RomCollection(self.gdb).insert((romCollName, consoleId, emuCmd, emuSolo, escapeCmd, descParserFile, relyOnNaming, 
			startWithDescFile, descFilePerGame, diskPrefix, typeOfManual, allowUpdate, ignoreOnScan, searchGameByCRC, searchGameByCRCIgnoreRomName, 
			ignoreGameWithoutDesc))
			romCollectionId = self.gdb.cursor.lastrowid
		else:
			RomCollection(self.gdb).update(('name', 'consoleId', 'emuCommandline', 'useEmuSolo', 'escapeEmuCmd', 'descriptionParserFile', 'relyOnFileNaming', 'startWithDescFile',
								'descFilePerGame', 'diskPrefix', 'typeOfManual', 'allowUpdate', 'ignoreOnScan', 'searchGameByCRC', 'searchGameByCRCIgnoreRomName', 'ignoreGameWithoutDesc'),
								(romCollName, consoleId, emuCmd, emuSolo, escapeCmd, descParserFile, relyOnNaming, startWithDescFile, descFilePerGame, diskPrefix, typeOfManual, allowUpdate, 
								ignoreOnScan, searchGameByCRC, searchGameByCRCIgnoreRomName, ignoreGameWithoutDesc),
								romCollectionRow[0])
			
			romCollectionId = romCollectionRow[0]
			
		return romCollectionId
		
	
	def insertFileType(self, fileTypeName, type, parent):
		fileTypeRow = FileType(self.gdb).getOneByName(fileTypeName)
		if(fileTypeRow == None):				
			FileType(self.gdb).insert((fileTypeName, type, parent))
			return self.gdb.cursor.lastrowid
		return fileTypeRow[0]
		
			

	def insertPaths(self, romCollectionId, paths, fileType):
		fileTypeRow = FileType(self.gdb).getOneByName(fileType)
		if(fileTypeRow == None):				
			return
			
		for path in paths:
			self.insertPath(path, fileType, fileTypeRow[0], romCollectionId)			
				
	
	def insertPath(self, path, fileTypeName, fileTypeId, romCollectionId):
		
		pathRow = Path(self.gdb).getPathByNameAndTypeAndRomCollectionId(path, fileTypeName, romCollectionId)
		if(pathRow == None):				
			Path(self.gdb).insert((path, fileTypeId, romCollectionId))
				
	
	def insertFileTypeForControl(self, romCollectionId, fileTypes, control):
		for i in range(0, len(fileTypes)):
			fileType = fileTypes[i]
				
			fileTypeRow = FileType(self.gdb).getOneByName(fileType)			
			if(fileTypeRow == None):				
				return						
			
			fileTypeForControlRow = FileTypeForControl(self.gdb).getFileTypeForControlByKey(romCollectionId, fileType, control, str(i))
			if(fileTypeForControlRow == None):
				FileTypeForControl(self.gdb).insert((control, str(i), romCollectionId, fileTypeRow[0]))
