import unittest
import os, sys

# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), ".." )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
if env == 'Windows_NT':
	env = 'win32'
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

import re, string
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *
import dbupdate, importsettings


class TestAlterTable(unittest.TestCase):
	def setUp(self):
		self.databasedir = os.path.join( os.getcwd(), 'TestDataBase')
		self.gdb = GameDataBase(self.databasedir)
		self.gdb.connect()
		self.gdb.dropTables()		
	
	
	"""
	
	def test_V04toV05(self):
		#create Table V0.4
		self.gdb.executeSQLScript(os.path.join(self.databasedir, 'SQL_CREATE_TESTDB_V0.4.txt'))
		
		#convert V0.4 to V0.5
		self.gdb.checkDBStructure()
		
		#Test
		rcbSettingRows = RCBSetting(self.gdb).getAll()
		self.assertTrue(rcbSettingRows != None)
		self.assertTrue(len(rcbSettingRows) == 1)
		
		rcbSetting = rcbSettingRows[0]
		self.assertEqual(rcbSetting[10], 'V0.5')
		self.assertEqual(rcbSetting[11], 'True')
		self.assertEqual(rcbSetting[12], 'True')
		self.assertEqual(rcbSetting[13], 'True')
		self.assertEqual(rcbSetting[14], 'True')
		self.assertEqual(rcbSetting[15], 'True')
		self.assertEqual(rcbSetting[16], 'True')
		
		consoleRows = Console(self.gdb).getAll()
		self.assertTrue(consoleRows != None)
		self.assertTrue(len(consoleRows) == 2)
		
		amiga = consoleRows[0]
		self.assertEqual(amiga[1], 'Amiga')		
		self.assertEqual(amiga[2], 'The Amiga 500 is also known as the A500 (or its code name Rock Lobster).')
		self.assertEqual(amiga[3], 'E:\Emulatoren\data\Testdata V0.4\consoleImages\Amiga.png')
		
		superNintendo = consoleRows[1]
		self.assertEqual(superNintendo[1], 'Super Nintendo')
		self.assertEqual(superNintendo[2], 'The Super Nintendo (SNES) is a 16-bit video game console released in 1990.')
		self.assertEqual(superNintendo[3], 'E:\Emulatoren\data\Testdata V0.4\consoleImages\SNES.png')
		
		romCollectionRows = RomCollection(self.gdb).getAll()
		self.assertTrue(romCollectionRows != None)
		self.assertEqual(len(romCollectionRows), 3)
		
		collV1 = romCollectionRows[0]
		self.assertEqual(collV1[1], 'Collection V1')
		console = Console(self.gdb).getObjectById(collV1[2])
		self.assertEqual(console[1], 'Amiga')
		self.assertEqual(collV1[3], 'E:\Emulatoren\WINUAE\winuae.exe {-%I% "%ROM%"}')
		self.assertEqual(collV1[4], 'True')
		self.assertEqual(collV1[5], 'True')
		self.assertEqual(collV1[6], 'E:\Emulatoren\data\Testdata V0.4\Collection V1\parserConfig.xml')
		self.assertEqual(collV1[7], 'True')
		self.assertEqual(collV1[8], 'False')
		self.assertEqual(collV1[9], 'False')
		self.assertEqual(collV1[10], '_Disk')
		self.assertEqual(collV1[11], 'Text')
		self.assertEqual(collV1[12], 'True')
		self.assertEqual(collV1[13], 'False')
		
		collV2 = romCollectionRows[1]
		self.assertEqual(collV2[1], 'Collection V2')
		console = Console(self.gdb).getObjectById(collV2[2])
		self.assertEqual(console[1], 'Amiga')
		self.assertEqual(collV2[3], 'E:\Emulatoren\WINUAE\winuae.exe {-%I% "%ROM%"}')
		self.assertEqual(collV2[4], 'True')
		self.assertEqual(collV2[5], 'True')
		self.assertEqual(collV2[6], 'E:\Emulatoren\data\Testdata V0.4\Collection V2\parserConfig.xml')
		self.assertEqual(collV2[7], 'True')
		self.assertEqual(collV2[8], 'False')
		self.assertEqual(collV2[9], 'True')
		self.assertEqual(collV2[10], '_Disk')
		self.assertEqual(collV2[11], 'Text')
		self.assertEqual(collV2[12], 'True')
		self.assertEqual(collV2[13], 'False')
		
		collV3 = romCollectionRows[2]
		self.assertEqual(collV3[1], 'Collection V3')
		console = Console(self.gdb).getObjectById(collV3[2])
		self.assertEqual(console[1], 'Super Nintendo')
		self.assertEqual(collV3[3], 'E:\Emulatoren\zsnes\zsnesw.exe -m "%ROM%"')
		self.assertEqual(collV3[4], 'True')
		self.assertEqual(collV3[5], 'True')
		self.assertEqual(collV3[6], 'E:\Emulatoren\data\Testdata V0.4\Collection V3\parserConfig.xml')
		self.assertEqual(collV3[7], 'True')
		self.assertEqual(collV3[8], 'False')
		self.assertEqual(collV3[9], 'False')
		self.assertEqual(collV3[10], '_Disk')
		self.assertEqual(collV3[11], 'Text')
		self.assertEqual(collV3[12], 'True')
		self.assertEqual(collV3[13], 'False')
		
		fileTypes = FileType(self.gdb).getAll()
		self.assertEqual(fileTypes[0][1], 'rcb_rom')		
		self.assertEqual(fileTypes[1][1], 'rcb_manual')
		self.assertEqual(fileTypes[2][1], 'rcb_description')
		self.assertEqual(fileTypes[3][1], 'rcb_configuration')		
		self.assertEqual(fileTypes[4][1], 'cover')
		self.assertEqual(fileTypes[4][2], 'image')
		self.assertEqual(fileTypes[4][3], 'game')
		self.assertEqual(fileTypes[5][1], 'screenshotingame')
		self.assertEqual(fileTypes[5][2], 'image')
		self.assertEqual(fileTypes[5][3], 'game')
		self.assertEqual(fileTypes[6][1], 'screenshottitle')				
		self.assertEqual(fileTypes[7][1], 'cartridge')		
		self.assertEqual(fileTypes[8][1], 'gameplay')	
	"""
	
	def test_V05toV06(self):
		#create Table V0.5
		self.gdb.executeSQLScript(os.path.join(self.databasedir, 'SQL_CREATE_TESTDB_V0.5.txt'))
		
		#convert V0.5 to V0.6
		self.gdb.checkDBStructure()
		
		
	def gameTest(self, game, name, descStart, gameCmd, alternateGameCmd, romCollectionId, publisherId, developerId, reviewerId,
			yearId, maxPlayers, rating, numVotes, url, region, media, perspective, controllerType, isFavorite, launchCount,
			numRoms, numCovers, numIngameScreens, numTitleScreens, numCartridges, numVideos):
		
		print name
		self.assertEqual(game[1], name)		
		description = game[2]		
		descStart = descStart		
		self.assertTrue(description.startswith(descStart))
		self.assertEqual(game[3], gameCmd)
		self.assertEqual(game[4], alternateGameCmd)
		self.assertEqual(game[5], romCollectionId)
		self.assertEqual(game[6], publisherId)
		self.assertEqual(game[7], developerId)
		self.assertEqual(game[8], reviewerId)
		self.assertEqual(game[9], yearId)
		self.assertEqual(game[10], maxPlayers)
		self.assertEqual(game[11], rating)
		self.assertEqual(game[12], numVotes)
		self.assertEqual(game[13], url)
		self.assertEqual(game[14], region)
		self.assertEqual(game[15], media)
		self.assertEqual(game[16], perspective)
		self.assertEqual(game[17], controllerType)
		self.assertEqual(game[18], isFavorite)
		self.assertEqual(game[19], launchCount)
		
		roms = File(self.gdb).getRomsByGameId(game[0])
		self.assertTrue(roms != None)
		numRomsActual = len(roms)
		self.assertEqual(numRomsActual, numRoms)
		
		self.fileTypeTest('cover', numCovers, game[0])
		self.fileTypeTest('screenshotingame', numIngameScreens, game[0])
		self.fileTypeTest('screenshottitle', numTitleScreens, game[0])
		self.fileTypeTest('cartridge', numCartridges, game[0])		
		
		
	
	def pathTest(self, pathActual, pathExpected, fileTypeId, fileTypeExpected, romCollId, romCollExpected):
		self.assertEqual(pathActual, pathExpected)
		fileType = FileType(self.gdb).getObjectById(fileTypeId)
		self.assertEqual(fileType[1], fileTypeExpected)
		romCollection = RomCollection(self.gdb).getObjectById(romCollId)
		self.assertEqual(romCollection[1], romCollExpected)
		
	def fileTypeTest(self, typeName, numFilesExpected, gameId):
		fileTypeRow = FileType(self.gdb).getOneByName(typeName)
		files = File(self.gdb).getFilesByGameIdAndTypeId(gameId, fileTypeRow[0])		
		self.assertTrue(files != None)
		numfiles = len(files)
		self.assertEqual(numfiles, numFilesExpected)
		
			
		
unittest.main()