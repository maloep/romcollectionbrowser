
import os, sys, re
import time, datetime
import urllib
import difflib

print "start parsing"

BASE_RESOURCE_PATH = os.path.join(os.getcwd())
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "pyparsing"))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "pyscraper"))

env = (os.environ.get("OS", "win32"), "win32",)[ os.environ.get("OS", "win32") == "xbox" ]
if env == 'Windows_NT':
	env = 'win32'
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "..", "platform_libraries", env))

import util
from descriptionparserfactory import DescriptionParserFactory

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

#descFile = "http://thegamesdb.net/api/GetGame.php?name=Legend%20of%20zelda"
#descFile = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\thegamesdb\\thegamesdb - legend of zelda.xml"
#parseInstruction = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\thegamesdb\\thegamesdb.xml"

#descFile = "http://api.giantbomb.com/search/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&query=Actraiser&resources=game&format=xml"
#descFile = "F:\\Emulatoren\\data\\Synopsis\\giantbomb\\Actraisersearch.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\giantbomb\\giantbomb - parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Scraper Tests\\Roms\\Sega32\\32x - Motocross Championship.nfo"
#parseInstruction = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\00 - local nfo.xml"

descFile = "http://api.archive.vg/1.0/Game.getInfoByCRC/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/b710561b"
parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\Archive\\Archive - parserConfig.xml"

#http://api.archive.vg/1.0/Archive.search/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/Alien+Brees
#http://api.archive.vg/1.0/Game.getInfoByID/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/21565

#http://api.archive.vg/1.0/System.getGames/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/SYSTEM

"""
from descriptionparserfactory import *
descParser = DescriptionParserFactory.getParser(parseInstruction)

results = descParser.parseDescription(str(descFile))
for result in results:
	print result
"""

import py7zlib

rom = "F:\\downloads\\Emu\\Good\\Accele Brid.7z"

f = py7zlib.Archive7z(open(rom, 'rb'))
			
members = f.getmembers()
names = f.getnames()

print members
print names



"""
from config import *
util.ISTESTRUN = True
config = Config()
config.readXml()


for romCollection in config.romCollections.values():
	print romCollection.name
	print romCollection.diskPrefix
	
	for romPath in romCollection.romPaths:
		print romPath
		
	for mediaPath in romCollection.mediaPaths:
		print mediaPath.path
		print mediaPath.fileType.name
		print mediaPath.fileType.id
		print mediaPath.fileType.parent
	
	for scraperSite in romCollection.scraperSites:
		for scraper in scraperSite.scrapers:			
			print scraper.parseInstruction
			print scraper.replaceKeyString
			print scraper.replaceValueString
			
	for fileType in romCollection.imagePlacing.fileTypesForGameList:
		print fileType.name
"""




#ratio = difflib.SequenceMatcher(None, 'Enslaved: Odyssey to the West', 'An American Tail - Fievel Goes West').ratio()
#print ratio

#timestamp1 = time.clock()

#descParser.prepareScan(descFile, parseInstruction)
#for result in descParser.scanDescription(descFile, parseInstruction):
#	print result


#timestamp2 = time.clock()
#diff = (timestamp2 - timestamp1) * 1000		
#print "parsed in %d ms" % (diff)



"""
def lev(a, b):
    if not a: return len(b)
    if not b: return len(a)
    return min(lev(a[1:], b[1:])+(a[0] != b[0]), \
    lev(a[1:], b)+1, lev(a, b[1:])+1)
"""


