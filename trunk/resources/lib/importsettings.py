
import os, sys, string, re
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *
from xml.dom.minidom import Document, parseString

class SettingsImporter:
	
	def importSettings(self, gdb, databaseDir):
		
		configFile = os.path.join(databaseDir, 'config.xml')
		fh=open(configFile,"r")
		xmlDoc = fh.read()
		fh.close()
		#Strip tidyness
		#xmlDoc = re.sub(r"[\t\n\r]",r"",xmlDoc)
		#xmlDoc = xmlDoc.strip()
		xmlDoc = parseString(xmlDoc)
		
		#print xmlDoc
		
		rcbSettings = xmlDoc.getElementsByTagName('RCBSettings')
		#TODO only 1 Setting allowed
		for rcbSetting in rcbSettings:
			favoriteConsole = self.getElementValue(rcbSetting, 'favoriteConsole')
			favoriteGenre = self.getElementValue(rcbSetting, 'favoriteGenre')
			
			self.insertRCBSetting(gdb, favoriteConsole, favoriteGenre)
		
		consoles = xmlDoc.getElementsByTagName('Console')
		for console in consoles:			
			consoleName = self.getElementValue(console, 'name')
			consoleDesc = self.getElementValue(console, 'desc')
			consoleImage =  self.getElementValue(console, 'imgFile')
			
			self.insertConsole(gdb, consoleName, consoleDesc, consoleImage)
			
			
		fileTypes= xmlDoc.getElementsByTagName('FileType')		
		for fileType in fileTypes:
			fileTypeName = self.getElementValue(fileType, 'name')
			self.insertFileType(gdb, fileTypeName)
			
		
		romCollections = xmlDoc.getElementsByTagName('RomCollection')
		for romCollection in romCollections:			
			romCollName = self.getElementValue(romCollection, 'name')
			consoleName = self.getElementValue(romCollection, 'consoleName')
			emuCmd = self.getElementValue(romCollection, 'emulatorCmd')
			emuSolo = self.getElementValue(romCollection, 'useEmuSolo')
			escapeCmd = self.getElementValue(romCollection, 'escapeCommand')
			relyOnNaming = self.getElementValue(romCollection, 'relyOnNaming')
			startWithDescFile = self.getElementValue(romCollection, 'startWithDescFile')
			descFilePerGame = self.getElementValue(romCollection, 'DescFilePerGame')
			descParserFile = self.getElementValue(romCollection, 'descriptionParserFile')
			diskPrefix = self.getElementValue(romCollection, 'diskPrefix')
			typeOfManual = self.getElementValue(romCollection, 'typeOfManual')
			romPaths = self.getElementValues(romCollection, 'romPath')
			descFilePaths = self.getElementValues(romCollection, 'descFilePath')
			coverPaths = self.getElementValues(romCollection, 'coverPath')
			titlescreenPaths = self.getElementValues(romCollection, 'titleScreenshotPath')
			ingamescreenPaths = self.getElementValues(romCollection, 'ingamescreenshotPath')
			cartridgePaths = self.getElementValues(romCollection, 'cartridgePath')
			configFilePaths = self.getElementValues(romCollection, 'configFilePath')
			ingamevidPaths = self.getElementValues(romCollection, 'ingamevidPath')			
			trailerPaths = self.getElementValues(romCollection, 'trailerPath')
			manualPaths = self.getElementValues(romCollection, 'manualPath')
						
			romCollectionId = self.insertRomCollection(gdb, consoleName, romCollName, emuCmd, emuSolo, escapeCmd, relyOnNaming, startWithDescFile, 
				descFilePerGame, descParserFile, diskPrefix, typeOfManual)
				
			self.insertPaths(gdb, romCollectionId, romPaths, 'rom')
			self.insertPaths(gdb, romCollectionId, descFilePaths, 'description')
			self.insertPaths(gdb, romCollectionId, coverPaths, 'cover')
			self.insertPaths(gdb, romCollectionId, titlescreenPaths, 'screenshottitle')
			self.insertPaths(gdb, romCollectionId, ingamescreenPaths, 'screenshotingame')
			self.insertPaths(gdb, romCollectionId, cartridgePaths, 'cartridge')
			self.insertPaths(gdb, romCollectionId, configFilePaths, 'configuration')
			self.insertPaths(gdb, romCollectionId, ingamevidPaths, 'ingamevideo')
			self.insertPaths(gdb, romCollectionId, trailerPaths, 'trailer')
			self.insertPaths(gdb, romCollectionId, manualPaths, 'manual')
				
			
			
		#TODO Transaction?
		gdb.commit()
		
	
	
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
		
	
	def insertRCBSetting(self, gdb, favoriteConsole, favoriteGenre):
		rcbSettingRows = RCBSetting(gdb).getAll()	
		if(rcbSettingRows == None or len(rcbSettingRows) == 0):
			if(favoriteConsole == ''):
				favoriteConsole = None
			if(favoriteGenre == ''):
				favoriteGenre = None
			RCBSetting(gdb).insert((None, None, None, None, None, None, favoriteConsole, favoriteGenre, None))
	
	
	def insertConsole(self, gdb, consoleName, consoleDesc, consoleImage):
		consoleRow = Console(gdb).getOneByName(consoleName)		
		if(consoleRow == None):				
			Console(gdb).insert((consoleName, consoleDesc, consoleImage))
	
	
	def insertRomCollection(self, gdb, consoleName, romCollName, emuCmd, emuSolo, escapeCmd, relyOnNaming, startWithDescFile, 
				descFilePerGame, descParserFile, diskPrefix, typeOfManual):		
		romCollectionRow = RomCollection(gdb).getOneByName(romCollName)		
		if(romCollectionRow == None):
			consoleRow = Console(gdb).getOneByName(consoleName)
			if(consoleRow == None):
				return
			consoleId = consoleRow[0] 
			RomCollection(gdb).insert((romCollName, consoleId, emuCmd, emuSolo, escapeCmd, descParserFile, relyOnNaming, 
			startWithDescFile, descFilePerGame, diskPrefix, typeOfManual))
			romCollectionId = gdb.cursor.lastrowid
		else:
			romCollectionId = romCollectionRow[0]
			
		return romCollectionId
		
	
	def insertFileType(self, gdb, fileTypeName):
		fileTypeRow = FileType(gdb).getOneByName(fileTypeName)
		if(fileTypeRow == None):				
			FileType(gdb).insert((fileTypeName,))
			

	def insertPaths(self, gdb, romCollectionId, paths, fileType):
		fileTypeRow = FileType(gdb).getOneByName(fileType)
		if(fileTypeRow == None):				
			return
			
		for path in paths:
			print path
			print fileType
			pathRow = Path(gdb).getPathByNameAndType(path, fileType)
			print pathRow
			if(pathRow == None):				
				Path(gdb).insert((path, fileTypeRow[0], romCollectionId))
			


def main():

	gdb = GameDataBase(os.path.join(os.getcwd(), '..', 'database'))
	gdb.connect()
	file = os.path.join( os.getcwd(), "..", "database")
	si = SettingsImporter()
	si.importSettings(gdb, file)
	gdb.close()
	del si
	del gdb

#main()