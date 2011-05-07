

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

#descFile = "http://maws.mameworld.info/maws/romset/88games"
#parseInstruction = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\06 - maws.xml"

#descFile = "http://api.archive.vg/1.0/Game.getInfoByCRC/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/b710561b"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\Archive\\Archive - parserConfig.xml"

#http://api.archive.vg/1.0/Archive.search/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/Alien+Brees
#http://api.archive.vg/1.0/Game.getInfoByID/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/19970

#http://api.archive.vg/1.0/System.getGames/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/SYSTEM



descFile = "F:\\Emulatoren\\data\\synopsis\\XTRAS-RCB\\NGPC.txt"
parseInstruction = "F:\\Emulatoren\\data\\synopsis\\XTRAS-RCB\\_parserConfig.xml"



from descriptionparserfactory import *
descParser = DescriptionParserFactory.getParser(parseInstruction)

results = descParser.parseDescription(str(descFile), 'iso-8859-15')
for result in results:
	print result
	
print len(results)



#print bool(re.search('(?i)%ASKNUM%', 'Test %asknum%'))


"""
str = '{-%I% "%rom%"} -s use_gui=no %GAMECMD%'
regex = '(?i)%rom%'
replace = 'C:\\temp\\abc.zip'

str = re.sub(regex, replace, str)
print str
"""

"""
path = 'C:\\Temp\\Test.zip'
print os.path.basename(path)
print os.path.splitext(os.path.basename(path))[0]
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
import py7zlib

rom = "F:\\downloads\\Emu\\Good\\Accele Brid.7z"

f = py7zlib.Archive7z(open(rom, 'rb'))
			
members = f.getmembers()
names = f.getnames()

print members
print names
"""



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

"""
from elementtree.ElementTree import *
try:
	file =  os.path.join(os.getcwd(), 'Test.xml')
	
	root = Element('root')
	test = SubElement(root, 'test')
	test.text = 'Brøderbund'	
	
	util.indentXml(root)
	treeToWrite = ElementTree(root)			
	treeToWrite.write(file)	
	
except Exception, (exc):
	print("Error: Cannot write config.xml: " +str(exc))	
"""

"""
import glob

def walklevel(some_dir, level=1):
	some_dir = some_dir.rstrip(os.path.sep)	
	assert os.path.isdir(some_dir)
	num_sep = len([x for x in some_dir if x == os.path.sep])
	for root, dirs, files in os.walk(some_dir):
		yield root, dirs, files
		num_sep_this = len([x for x in root if x == os.path.sep])
		if num_sep + level <= num_sep_this:
			del dirs[:]


romPath = 'F:\\Emulatoren\\data\\Scraper Tests\\Roms\\Genesis\\And*.zip'
dirname = os.path.dirname(romPath)
basename = os.path.basename(romPath)
dirname = dirname#.decode(sys.getfilesystemencoding()).encode('utf-8')
files = []
for walkRoot, walkDirs, walkFiles in walklevel(dirname, 1):
	newRomPath = os.path.join(walkRoot, basename)
	allFiles = [f.decode(sys.getfilesystemencoding()).encode('utf-8') for f in glob.glob(newRomPath)]
	#allFiles = [f for f in glob.glob(newRomPath)]
	files.extend(allFiles)

print files

for file in files:
	print str(file)
	print file.decode('utf-8')
	print file.decode('iso-8859-15')
	print file.decode('iso-8859-1')
	
	file = file.decode('utf-8')
	print str(file)
	
"""

#HACK: there may be encoding errors in the filename
#if(not os.path.isfile(filename)):
#	Logutil.log("File %s does not exist. Trying to find a new encoding." %filename, util.LOG_LEVEL_INFO)
#	filename = filename.decode('utf-8')
#	Logutil.log("new file name: " +str(filename.encode('utf-8')), util.LOG_LEVEL_INFO)


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


