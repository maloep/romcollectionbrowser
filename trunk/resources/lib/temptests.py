

import os, sys, re
import time, datetime
import urllib
import difflib


BASE_RESOURCE_PATH = os.path.join(os.getcwd())
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "pyparsing"))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "pyscraper"))

env = (os.environ.get("OS", "win32"), "win32",)[ os.environ.get("OS", "win32") == "xbox" ]
if env == 'Windows_NT':
	env = 'win32'
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "..", "platform_libraries", env))

import util
from descriptionparserfactory import DescriptionParserFactory

import config
from config import *

#"http://thevideogamedb.com/API/GameDetail.aspx?apikey=Zx5m2Y9Ndj6B4XwTf83JyKz7r8WHt3i4&name=After%20burner"
#descFile = "http://thevideogamedb.com/API/GameDetail.aspx?apikey=Zx5m2Y9Ndj6B4XwTf83JyKz7r8WHt3i4&name=After%20burner"
#parseInstruction = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\01 - thevideogamedb.xml"

#descFile = "http://romcollectionbrowser.googlecode.com/svn/trunk/resources/lib/TestDataBase/Collection%20V3/description/synopsis.txt"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\_parserConfig.xml"


#descFile = "http://www.mobygames.com/search/quick?game=Actraiser&p=15"
#descFile = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\mobysearch - Actraiser.htm"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\01 - mobygames - gamesearch.xml"

#descFile = "http://www.mobygames.com/game/sega-32x/blackthorne"
#parseInstruction = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\04.02 - mobygames - details.xml"

#descFile = "http://thegamesdb.net/api/GetGame.php?name=zelda&platform=Nintendo%20DS"
#descFile = "http://thegamesdb.net/api/GetGame.php?name=new%20super%20mario&platform=Nintendo%20Wii"
#descFile = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\thegamesdb\\thegamesdb - legend of zelda.xml"
#parseInstruction = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\02 - thegamesdb.xml"

#descFile = "http://api.giantbomb.com/search/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&query=Actraiser&resources=game&format=xml"
#descFile = "F:\\Emulatoren\\data\\Synopsis\\giantbomb\\Actraisersearch.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\giantbomb\\giantbomb - parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Scraper Tests\\Roms\\Sega32\\32x - Motocross Championship.nfo"
#parseInstruction = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\00 - local nfo.xml"

#descFile = "http://maws.mameworld.info/maws/romset/88games"
#parseInstruction = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\addons\script.games.rom.collection.browser.dev\\resources\\scraper\\06 - maws.xml"


#descFile = "http://api.archive.vg/1.0/Game.getInfoByCRC/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/b710561b"
#parseInstruction = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\05.01 - archive - search.xml"

#descFile = "http://api.archive.vg/1.0/Archive.search/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/Alien+Breed"
#http://api.archive.vg/1.0/Game.getInfoByID/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/19970

#http://api.archive.vg/1.0/System.getGames/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/SYSTEM

descFile = "F:\\Games\\MAME test\\Synopsis\\MAME - short.txt"
parseInstruction = "F:\\Games\\MAME test\\Synopsis\\parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\synopsis\\XTRAS-RCB\\NGPC.txt"
#parseInstruction = "F:\\Emulatoren\\data\\synopsis\\XTRAS-RCB\\_parserConfig.xml"


"""
from descriptionparserfactory import *
descParser = DescriptionParserFactory.getParser(parseInstruction)

results = descParser.parseDescription(str(descFile), 'iso-8859-15')
for result in results:
	print result
	
print len(results)
"""



"""
import glob

def getFilesByWildcard(pathName):
		
	files = []
	
	try:
		# try glob with * wildcard
		files = glob.glob(pathName)	
		
		if(len(files) == 0):				
			squares = re.findall('\[.*\]',pathName)				
			if(squares != None and len(squares) >= 1):
				print('Replacing [...] with *')
				for square in squares:						
					pathName = pathName.replace(square, '*')
			
				print('new pathname: ' +str(pathName))
				try:
					files = glob.glob(pathName)
				except Exception, (exc):
					print("Error using glob function in resolvePath " +str(exc))
	except Exception, (exc):
		print("Error using glob function in resolvePath " +str(exc))
	
	# glob can't handle []-characters - try it with listdir
	if(len(files)  == 0):
		try:
			if(os.path.isfile(pathName)):
				files.append(pathName)
			else:
				files = os.listdir(pathName)					
		except:
			pass
	print("resolved files: " +str(files))
	return files	

pathName = 'F:\\Emulatoren\\data\\Scraper Tests\\Artwork RCB\\Sega32\\boxback\\[32x] - Doom.*'
#pathName = 'F:\\Emulatoren\\data\\Scraper Tests\\Artwork RCB\\Amiga\\screenshot\\Metal Gear Solid [!].*'

squares = re.findall('\[.*\]',pathName)
print len(squares)

getFilesByWildcard(pathName)

#print os.path.isfile(pathName)
#print os.listdir(pathName)

"""

"""
str = '{-%I% "%rom%"} -s use_gui=no %GAMECMD%'
regex = '(?i)%rom%'
replace = 'C:\\temp\\abc.zip'

str = re.sub(regex, replace, str)
print str
"""

"""
configFile = 'C:\\Users\\malte\\AppData\\Roaming\\XBMC\\userdata\\script_data\\script.games.rom.collection.browser\\config.xml'

from elementtree.ElementTree import *
tree = ElementTree().parse(configFile)

romCollectionsXml = tree.find('RomCollections')

print romCollectionsXml
print tree
"""


"""
configFile = util.getConfigXmlPath()

myConfig = Config()
statusOk, errorMsg = myConfig.readXml()
"""

"""
diskPrefix = '\(Disc .*\)'
file = 'E:\\Games\\Testsets\\Import\\multidisc\\PS1\\roms\\Alone in the Dark - The New Nightmare (Disc 2)(Disk 3).img'
match = re.search(diskPrefix.lower(), file.lower())
print match.group()
"""


dirname = os.path.dirname('E:\\Games\\Testsets\\Import\\multidisc\\PS1\\artwork\\boxfront\\test.img')
print dirname

#parent = os.path.join(dirname, '..')
parent = os.path.dirname(dirname)
print parent




