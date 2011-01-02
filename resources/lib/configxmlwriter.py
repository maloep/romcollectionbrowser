import os

import util
from util import *
import config
from config import *
from elementtree.ElementTree import *


class ConfigXmlWriter:
	
	def init(self):
		pass
	
	
	def writeRomCollections(self, createNew, romCollections):
		
		if(createNew):
			configFile = os.path.join(util.getAddonInstallPath(), 'resources', 'database', 'config_template.xml')
		else:
			configFile = util.getConfigXmlPath()
		
		if(not os.path.isfile(configFile)):
			Logutil.log('File config.xml does not exist. Place a valid config file here: ' +str(configFile), util.LOG_LEVEL_ERROR)
			return False, 'Error: File config.xml does not exist'
		
		tree = ElementTree().parse(configFile)
				
		romCollectionsXml = tree.find('RomCollections')
		
		for romCollection in romCollections.values():
			romCollectionXml = SubElement(romCollectionsXml, 'RomCollection', {'id' : str(romCollection.id), 'name' : romCollection.name})
			SubElement(romCollectionXml, 'emulatorCmd').text = romCollection.emulatorCmd
			SubElement(romCollectionXml, 'emulatorParams').text = romCollection.emulatorParams
			
			for romPath in romCollection.romPaths:
				SubElement(romCollectionXml, 'romPath').text = str(romPath)
				
			for mediaPath in romCollection.mediaPaths:								
				SubElement(romCollectionXml, 'mediaPath', {'type' : mediaPath.type.name}).text = mediaPath.path
				
			#some default values
			SubElement(romCollectionXml, 'ignoreOnScan').text = str(romCollection.ignoreOnScan)
			SubElement(romCollectionXml, 'descFilePerGame').text = str(romCollection.descFilePerGame)
			SubElement(romCollectionXml, 'useFoldernameAsGamename').text = str(romCollection.useFoldernameAsGamename)
			SubElement(romCollectionXml, 'searchGameByCRC').text = str(romCollection.searchGameByCRC)
			SubElement(romCollectionXml, 'maxFolderDepth').text = str(romCollection.maxFolderDepth)
			
			if (os.environ.get( "OS", "xbox" ) == "xbox"):
				SubElement(romCollectionXml, 'xboxCreateShortcut').text = str(romCollection.xboxCreateShortcut)
				SubElement(romCollectionXml, 'xboxCreateShortcutAddRomfile').text = str(romCollection.xboxCreateShortcutAddRomfile)
				SubElement(romCollectionXml, 'xboxCreateShortcutUseShortGamename').text = str(romCollection.xboxCreateShortcutUseShortGamename)
				
			#TODO read from existing config
			SubElement(romCollectionXml, 'imagePlacing').text = 'gameinfobig'
			
			mobyConsoleId = '0'
			try:
				mobyConsoleId = config.consoleDict[romCollection.name]
			except:
				pass
						
			#TODO read from existing config
			if(romCollection.scraperSites == None or len(romCollection.scraperSites) == 0):
				#TODO: enable again when site is more complete and responses are faster
				#SubElement(romCollectionXml, 'scraper', {'name' : 'thevideogamedb.com'})
				SubElement(romCollectionXml, 'scraper', {'name' : 'thegamesdb.net', 'replaceKeyString' : '', 'replaceValueString' : ''})
				SubElement(romCollectionXml, 'scraper', {'name' : 'giantbomb.com', 'replaceKeyString' : '', 'replaceValueString' : ''})
				SubElement(romCollectionXml, 'scraper', {'name' : 'mobygames.com', 'replaceKeyString' : '', 'replaceValueString' : '', 'platform' : mobyConsoleId})
			else:
				SubElement(romCollectionXml, 'scraper', {'name' : romCollection.scraperSites[0].name})
				
				scrapersXml = tree.find('Scrapers')
				site = SubElement(scrapersXml, 'Site', {'name' : romCollection.scraperSites[0].name})
				SubElement(site, 'Scraper', {'parseInstruction' : romCollection.scraperSites[0].scrapers[0].parseInstruction, 'source' : romCollection.scraperSites[0].scrapers[0].source})

		#write file		
		try:
			configFile = util.getConfigXmlPath()
			
			util.indentXml(tree)
			tree = ElementTree(tree)			
			tree.write(configFile)
			
			return True, ""
			
		except Exception, (exc):
			print("Error: Cannot write config.xml: " +str(exc))
			return False, "Error: Cannot write config.xml: " +str(exc)