
import os, sys, string, re
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *
from xml.dom.minidom import Document, parseString

class ImportSettings:
	
	def importSettings(self, configFile, gdb):
		
		fh=open(configFile,"r")
		xmlDoc = fh.read()
		fh.close()
		#Strip tidyness
		#xmlDoc = re.sub(r"[\t\n\r]",r"",xmlDoc)
		#xmlDoc = xmlDoc.strip()
		xmlDoc = parseString(xmlDoc)
		
		#print xmlDoc
		
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
			emuCmd = self.getElementValue(romCollection, 'emulatorCmd')
			emuSolo = self.getElementValue(romCollection, 'useEmuSolo')
			escapeCmd = self.getElementValue(romCollection, 'escapeCommand')
			relyOnNaming = self.getElementValue(romCollection, 'relyOnNaming')
			startWithDescFile = self.getElementValue(romCollection, 'startWithDescFile')
			descFilePerGame = self.getElementValue(romCollection, 'DescFilePerGame')
			descParserFile = self.getElementValue(romCollection, 'descriptionParserFile')
			diskPrefix = self.getElementValue(romCollection, 'diskPrefix')			
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
				descFilePerGame, descParserFile, diskPrefix)
				
			
			
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
		
	
	def insertConsole(self, gdb, consoleName, consoleDesc, consoleImage):
		consoleRow = Console(gdb).getOneByName(consoleName)		
		if(consoleRow == None):				
			Console(gdb).insert((consoleName, consoleDesc, consoleImage))
	
	
	def insertRomCollection(self, gdb, consoleName, romCollName, emuCmd, emuSolo, escapeCmd, relyOnNaming, startWithDescFile, 
				descFilePerGame, descParserFile, diskPrefix):		
		romCollectionRow = RomCollection(gdb).getOneByName(romCollName)		
		if(romCollectionRow == None):
			consoleRow = Console(gdb).getOneByName(consoleName)
			if(consoleRow == None):
				return
			consoleId = consoleRow[0] 
			RomCollection(gdb).insert((romCollName, consoleId, emuCmd, emuSolo, escapeCmd, descParserFile, relyOnNaming, 
			startWithDescFile, descFilePerGame, diskPrefix))
			romCollectionId = self.gdb.cursor.lastrowid
		else:
			romCollectionId = romCollectionRow[0]
			
		return romCollectionId
		
	
	def insertFileType(self, gdb, fileTypeName):
		fileTypeRow = FileType(gdb).getOneByName(fileTypeName)
		if(fileTypeRow == None):				
			FileType(gdb).insert((fileTypeName,))
			


gdb = GameDataBase(os.path.join(os.getcwd(), '..', 'database'))
gdb.connect()
file = os.path.join( os.getcwd(), "..", "database", "config.xml")
iS = ImportSettings()
iS.importSettings(file, gdb)
gdb.close()
del iS
del gdb