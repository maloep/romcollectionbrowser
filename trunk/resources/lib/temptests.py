# coding=utf-8

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


#descFile = "http://www.mobygames.com/search/quick?game=Actraiser&p=15"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.01 - mobygames - gamesearch_old.xml"

#descFile = "http://www.mobygames.com/game/sega-32x/metal-head"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.02 - mobygames - details.xml"

#descFile = "http://www.mobygames.com/game/atari-5200/gyruss"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.02 - mobygames - details.xml"

#descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.03 - mobygames - coverlink front.xml"

#descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art/gameCoverId,170207"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.04 - mobygames - coverdetail front.xml"

#descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.05 - mobygames - coverlink back.xml"

#descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art/gameCoverId,170208"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.06 - mobygames - coverdetail back.xml"

#descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.07 - mobygames - coverlink media.xml"

#descFile = "http://www.mobygames.com/game/snes/actraiser/cover-art/gameCoverId,17623"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.08 - mobygames - coverdetail media.xml"

#descFile = "http://www.mobygames.com/game/snes/actraiser/screenshots"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.09 - mobygames - screenshotlink.xml"

#descFile = "http://www.mobygames.com/game/snes/actraiser/screenshots/gameShotId,27458/"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\04.10 - mobygames - screenshot detail.xml"


#descFile = "http://www.mobygames.com/game/sega-32x/blackthorne"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\scraper\\04.02 - mobygames - details.xml"

#descFile = "http://thegamesdb.net/api/GetGame.php?name=NBA%20Live%20%2798&platform=Super%20Nintendo%20%28SNES%29"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\02 - thegamesdb.xml"

#descFile = "http://api.giantbomb.com/search/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&query=Actraiser&resources=game&format=xml"
#descFile = "F:\\Emulatoren\\data\\Synopsis\\giantbomb\\Actraisersearch.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\giantbomb\\giantbomb - parserConfig.xml"

#descFile = "E:\\Games\\Testsets\\RCB Testset\\Testdata - online scraping\\Roms\\SNES\\Super Mario Kart.nfo"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\00 - local nfo.xml"

#descFile = "http://maws.mameworld.info/maws/romset/88games"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\script.games.rom.collection.browser.dev\\resources\\scraper\\06 - maws.xml"


#descFile = "http://api.archive.vg/1.0/Game.getInfoByCRC/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/b710561b"
#parseInstruction = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\scraper\\05.01 - archive - search.xml"

#descFile = "http://api.archive.vg/1.0/Archive.search/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/Alien+Breed"
#http://api.archive.vg/1.0/Game.getInfoByID/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/19970

#http://api.archive.vg/1.0/System.getGames/VT7RJ960FWD4CC71L0Z0K4KQYR4PJNW8/SYSTEM

descFile = "E:\\Games\\RCB TestDataBase\\Scraping\\V2 - Amiga - ff - descpergame\\synopsis\\Dogfight\\synopsis.txt"
parseInstruction = "E:\\Games\\RCB TestDataBase\\Scraping\\V2 - Amiga - ff - descpergame\\parserConfig.xml"

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
configFile = 'C:\\Users\\lom\\AppData\\Roaming\\XBMC\\userdata\\script_data\\script.games.rom.collection.browser\\config.xml'

from elementtree.ElementTree import *
tree = ElementTree().parse(configFile)

romCollectionsXml = tree.find('RomCollections')

print romCollectionsXml
print tree
"""


"""
configFile = util.getConfigXmlPath()

myConfig = Config(configFile)
statusOk, errorMsg = myConfig.readXml()
"""

"""
#file = 'E:\Games\RCB TestDataBase\Scraping\V12 - A2600 - \Artwork\boxfront\3-D Tic-Tac-Toe Test.jpg'
file = '3-D Tic-Tac-Toe [Test].jpg'

diskPrefix = "3-D Tic-Tac-Toe [[]Test[]].*"


import fnmatch
print fnmatch.fnmatch(file, diskPrefix)
"""

"""

dirname = os.path.dirname('E:\\Games\\Testsets\\Import\\multidisc\\PS1\\artwork\\boxfront\\test.img')
print dirname

#parent = os.path.join(dirname, '..')
parent = os.path.dirname(dirname)
print parent

"""

"""
def walklevel(some_dir, level=1):
	some_dir = some_dir.rstrip(os.path.sep)	
	assert os.path.isdir(some_dir)
	num_sep = len([x for x in some_dir if x == os.path.sep])
	for root, dirs, files in os.walk(some_dir):
		yield root, dirs, files
		num_sep_this = len([x for x in root if x == os.path.sep])
		if num_sep + level <= num_sep_this:
			del dirs[:]

import glob
files = []


myConfig = Config('C:\Users\lom\AppData\Roaming\XBMC\userdata\Addon_data\script.games.rom.collection.browser\config.xml')
statusOk, errorMsg = myConfig.readXml()


#dirname = "E:\\Games\\Testsets\\Scraper Tests\\SNES\\Roms#[]é()'.-_ü"
#basename = "*.zip"

dirname = os.path.dirname(myConfig.romCollections["1"].romPaths[0])
basename = os.path.basename(myConfig.romCollections["1"].romPaths[0])
					
dirname = dirname.decode('utf-8')
#dirname = dirname.decode(sys.getfilesystemencoding()).encode('utf-8')
for walkRoot, walkDirs, walkFiles in walklevel(dirname, 99):
	newRomPath = os.path.join(walkRoot, basename)	
	#glob is same as "os.listdir(romPath)" but it can handle wildcards like *.adf
	allFiles = [f.decode(sys.getfilesystemencoding()).encode('utf-8') for f in glob.glob(newRomPath)]

	#did not find appendall or something like this
	files.extend(allFiles)
	
print str(files)

"""

from guppy import hpy
h = hpy()
h.setref()

"""
diskPrefix = "disc.*"
game1 = "FF7 disc 1.iso"
game2 = "FF7 disc 2.iso"
#game3 = "Metal Gear Solid_Disk1 PT-BR.bin"

game = game2

match = re.search(diskPrefix, game)
if(match):
	disk = game[match.start():match.end()]
	print disk
else:
	print "no match"
"""

print h.heap()