
import os, sys, string, re
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *
from xml.dom.minidom import Document, parseString

class ImportSettings:
	
	def importSettings(self, configFile):		
		
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
			name = console.getElementsByTagName('name')
			print name[0].firstChild.nodeValue
			desc = console.getElementsByTagName('desc')
			print desc[0].firstChild.nodeValue
			imgFile = console.getElementsByTagName('imgFile')
			print imgFile[0].firstChild.nodeValue
			
		
		romCollections = xmlDoc.getElementsByTagName('RomCollection')
		for romCollection in romCollections:
			name = romCollection.getElementsByTagName('name')
			print name[0].firstChild.nodeValue
			name = romCollection.getElementsByTagName('consoleName')
			print name[0].firstChild.nodeValue
			name = romCollection.getElementsByTagName('emulatorCmd')
			print name[0].firstChild.nodeValue
			name = romCollection.getElementsByTagName('useEmuSolo')
			print name[0].firstChild.nodeValue
			name = romCollection.getElementsByTagName('escapeCommand')			
			print name[0].firstChild.nodeValue
			name = romCollection.getElementsByTagName('relyOnNaming')
			print name[0].firstChild.nodeValue
			name = romCollection.getElementsByTagName('startWithDescFile')			
			print name[0].firstChild.nodeValue
			name = romCollection.getElementsByTagName('DescFilePerGame')			
			print name[0].firstChild.nodeValue
			name = romCollection.getElementsByTagName('descriptionParserFile')
			print name[0].firstChild.nodeValue
			name = romCollection.getElementsByTagName('diskPrefix')			
			print name[0].firstChild.nodeValue
			#TODO more than one
			name = romCollection.getElementsByTagName('romPath')
			print name[0].firstChild.nodeValue
			
		
		fileTypes= xmlDoc.getElementsByTagName('FileType')
		
		


#gdb = GameDataBase(os.path.join(os.getcwd(), '..', 'database'))
#dbupdate = DBUpdate()
#gdb.connect()
#file = os.path.join( os.getcwd(), "resources", "database", "config.xml")
file = os.path.join( os.getcwd(), "..", "database", "config.xml")
iS = ImportSettings()
iS.importSettings(file)
del iS