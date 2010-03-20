import unittest
import os, sys

# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), ".." )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
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
		
		
	def test_V03toV04(self):
		#create Table V0.3
		self.gdb.executeSQLScript(os.path.join(self.databasedir, 'SQL_CREATE_V0.3.txt'))
		#insert data
		self.gdb.executeSQLScript(os.path.join(self.databasedir, 'SQL_INSERT_TEST_DATA_V0.3.txt'))

		#convert V0.3 to V0.4
		#self.gdb.checkDBStructure()
		
		#Test
		rcbSettingRows = RCBSetting(self.gdb).getAll()
		self.assertTrue(rcbSettingRows != None)
		self.assertTrue(len(rcbSettingRows) == 1)
			
		rcbSetting = rcbSettingRows[0]
		self.assertEqual(rcbSetting[10], 'V0.4')
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
		self.assertEqual(amiga[3], 'E:\Emulatoren\data\consoleImages\uae.png')
		
		superNintendo = consoleRows[1]
		self.assertEqual(superNintendo[1], 'Super Nintendo')
		self.assertEqual(superNintendo[2], 'The Super Nintendo (SNES) is a 16-bit video game console released in 1990.')
		self.assertEqual(superNintendo[3], 'E:\Emulatoren\data\consoleImages\zsnes.png')
		
		romCollectionRows = RomCollection(self.gdb).getAll()
		self.assertTrue(consoleRows != None)
		self.assertTrue(len(consoleRows) == 2)
		
		collV1 = romCollectionRows[0]
		self.assertEqual(collV1[1], 'Collection V1')
		console = Console(self.gdb).getObjectById(collV1[2])
		self.assertEqual(console[1], 'Amiga')
		self.assertEqual(collV1[3], 'winuae.exe {-%I% "%ROM%"}')
		self.assertEqual(collV1[4], 'True')
		self.assertEqual(collV1[5], 'True')
		self.assertEqual(collV1[6], 'DescriptionParser.xml')
		self.assertEqual(collV1[7], 'True')
		self.assertEqual(collV1[8], 'False')
		self.assertEqual(collV1[9], 'True')
		self.assertEqual(collV1[10], '_Disk')
		self.assertEqual(collV1[11], 'Text')
		self.assertEqual(collV1[12], 'True')
		self.assertEqual(collV1[13], 'True')
				
		
		collV2 = romCollectionRows[1]
		self.assertEqual(collV2[1], 'Collection V2')
		console = Console(self.gdb).getObjectById(collV2[2])
		self.assertEqual(console[1], 'Super Nintendo')
		self.assertEqual(collV2[3], 'zsnes.exe -m "%ROM%"')	
		self.assertEqual(collV2[4], 'True')
		self.assertEqual(collV2[5], 'True')
		self.assertEqual(collV2[6], 'DescriptionParser.xml')
		self.assertEqual(collV2[7], 'True')
		self.assertEqual(collV2[8], 'False')
		self.assertEqual(collV2[9], 'True')
		self.assertEqual(collV2[10], '_Disk')
		self.assertEqual(collV2[11], 'Text')
		self.assertEqual(collV2[12], 'True')
		self.assertEqual(collV2[13], 'True')
		
		
		fileTypes = FileType(self.gdb).getAll()
		self.assertEqual(fileTypes[0][1], 'rom')
		self.assertEqual(fileTypes[1][1], 'screenshottitle')
		self.assertEqual(fileTypes[2][1], 'screenshotingame')
		self.assertEqual(fileTypes[3][1], 'cover')
		self.assertEqual(fileTypes[4][1], 'cartridge')
		self.assertEqual(fileTypes[5][1], 'manual')
		self.assertEqual(fileTypes[6][1], 'ingamevideo')
		self.assertEqual(fileTypes[7][1], 'trailer')
		self.assertEqual(fileTypes[8][1], 'description')
		self.assertEqual(fileTypes[9][1], 'configuration')
		
		paths = Path(self.gdb).getAll()
		self.assertTrue(paths != None)
		self.assertTrue(len(paths) == 11)
		
		self.assertEqual(paths[0][1], 'E:\Emulatoren\data\Amiga\Collection V1\\roms\*.adf')		
		self.pathTest(paths[1][1], 'E:\Emulatoren\data\Amiga\Collection V1\synopsis\synopsis.txt', paths[1][2], 'description', paths[1][3], 'Collection V1')
		self.pathTest(paths[2][1], 'E:\Emulatoren\data\Amiga\Collection V1\screens\%GAME%.jpg', paths[2][2], 'screenshotingame', paths[2][3], 'Collection V1')
		self.pathTest(paths[3][1], 'E:\Emulatoren\data\Amiga\Collection V1\screens\%GAME%.gif', paths[3][2], 'screenshotingame', paths[3][3], 'Collection V1')
		self.pathTest(paths[4][1], 'E:\Emulatoren\data\Amiga\Collection V1\screens\%GAME%.png', paths[4][2], 'screenshotingame', paths[4][3], 'Collection V1')
		self.pathTest(paths[5][1], 'E:\Emulatoren\data\Amiga\Collection V1\cover\%GAME%.jpg', paths[5][2], 'cover', paths[5][3], 'Collection V1')
		self.pathTest(paths[6][1], 'E:\Emulatoren\data\Amiga\Collection V1\ingameVideo\%GAME%.wmv', paths[6][2], 'ingamevideo', paths[6][3], 'Collection V1')
		self.pathTest(paths[7][1], 'E:\Emulatoren\data\Amiga\Collection V1\manuals\%GAME%.txt', paths[7][2], 'manual', paths[7][3], 'Collection V1')
		self.pathTest(paths[8][1], 'E:\Emulatoren\data\Amiga\Collection V1\\trailer\%GAME%.wmv', paths[8][2], 'trailer', paths[8][3], 'Collection V1')
		self.pathTest(paths[9][1], 'E:\Emulatoren\data\Amiga\Collection V2\\roms\*.smc', paths[9][2], 'rom', paths[9][3], 'Collection V2')
		self.pathTest(paths[10][1], 'E:\Emulatoren\data\Amiga\Collection V2\screens\*.png', paths[10][2], 'screenshotingame', paths[10][3], 'Collection V2')
		
		
		gameRows = Game(self.gdb).getAllOrdered()	
		self.assertTrue(gameRows != None)
		self.assertTrue(len(gameRows) == 6)
				
		self.gameTest(gameRows[0], 'Airborne Ranger', 'In this action/simulation game by Microprose the player takes the role of an U.S. Army Airborne ranger.', 
			'',  '', 1, 2, 2, 4, 3, '4', '5', 15, 'www', 'USA', 'Disk', '1st Person', 'Joystick', 0, 0,
			1, 1, 1)				
		self.gameTest(gameRows[1], 'Dogfight', 'Dogfight is a two-player game with roots in the same primordial soup as Ataris Combat and other basic dogfighting games.', 	
			'',  '', 1, 2, 2, 1, 4, '2', '4', 10, 'www', 'USA', 'Disk', '1st Person', 'Joystick', 0, 0,
			3, 1, 1)				
		self.gameTest(gameRows[2], 'Football Glory', 'From Croatia came this overhead view football game resembling Sensible Soccer.', 
			'',  '', 1, 4, 4, 2, 6, '2', '2', 7, 'www', 'USA', 'Disk', 'Top', 'Joystick', 0, 0,
			3, 1, 1)
		self.gameTest(gameRows[3], 'Formula One Grand Prix', 'F1 is an Official Formula One Racing Game.', 
			'',  '', 1, 5, 5, 1, 5, '2', '7', 32, 'www', 'USA', 'Disk', 'Top', 'Joystick', 0, 0,
			4, 1, 1)
		self.gameTest(gameRows[4], 'Hanse - Die Expedition', 'Hanse makes you a trader.', 
			'',  '', 1, 6, 6, 5, 6, '2', '2', 7, 'www', 'USA', 'Disk', 'Top', 'Joystick', 0, 0,
			3, 1, 1)
		self.gameTest(gameRows[5], 'Legends of Zelda', 'This installment in the Zelda series was my favorite.', 
			'', '', 2, 6, 6, 3, 6, '4', '10', 35, 'www', 'USA', 'Cartridge', 'Top', 'Gamepad', 0, 0,
			1, 1, 1)		
		
		
	def gameTest(self, game, name, descStart, gameCmd, alternateGameCmd, romCollectionId, publisherId, developerId, reviewerId,
			yearId, maxPlayers, rating, numVotes, url, region, media, perspective, controllerType, isFavorite, launchCount,
			numRoms, numCovers, numIngameScreens):
		
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
		
		cover = File(self.gdb).getCoversByGameId(game[0])
		self.assertTrue(cover != None)
		numCoversActual = len(cover)
		self.assertEqual(numCoversActual, numCovers)
		
		ingameScreens = File(self.gdb).getIngameScreenshotsByGameId(game[0])
		self.assertTrue(ingameScreens != None)
		numIngameScreensActual = len(ingameScreens)
		self.assertEqual(numIngameScreensActual, numIngameScreens)
		
	
	def pathTest(self, pathActual, pathExpected, fileTypeId, fileTypeExpected, romCollId, romCollExpected):
		self.assertEqual(pathActual, pathExpected)
		fileType = FileType(self.gdb).getObjectById(fileTypeId)
		self.assertEqual(fileType[1], fileTypeExpected)
		romCollection = RomCollection(self.gdb).getObjectById(romCollId)
		self.assertEqual(romCollection[1], romCollExpected)
		
			
		
unittest.main()