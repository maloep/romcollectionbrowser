# coding=utf-8

import os, sys

from config import *


BASE_RESOURCE_PATH = os.path.join(os.getcwd())
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "pyscraper"))

env = (os.environ.get("OS", "win32"), "win32",)[ os.environ.get("OS", "win32") == "xbox" ]
if env == 'Windows_NT':
	env = 'win32'
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "..", "platform_libraries", env))



configFile = 'C:\\Users\\lom\\AppData\\Roaming\\Kodi\\userdata\\addon_data\\script.games.rom.collection.browser\\config.xml'

myConfig = Config(configFile)
statusOk, errorMsg = myConfig.readXml()

mediaDict = {}

for rc in myConfig.romCollections.values():
	for mediaPath in rc.mediaPaths:
		key = '%s:%s' %(rc.id, mediaPath.fileType.name)
		print key
		print mediaPath



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

#from guppy import hpy
#h = hpy()
#h.setref()

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

#print h.heap()
