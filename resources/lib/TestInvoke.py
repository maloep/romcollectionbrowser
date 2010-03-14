

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


class TestRCB(unittest.TestCase):
	
	def setUp(self):
		self.databasedir = os.path.join( os.getcwd(), 'TestDataBase')
		self.gdb = GameDataBase(self.databasedir)
		self.gdb.connect()
		self.gdb.dropTables()		
		self.gdb.createTables()		
	
	def test_ImportSettings(self):		
		si = importsettings.SettingsImporter()
		si.importSettings(self.gdb, self.databasedir, RCBMock())
		
		rcbSettingRows = RCBSetting(self.gdb).getAll()
		self.assertTrue(rcbSettingRows != None)
		self.assertTrue(len(rcbSettingRows) == 1)
			
		rcbSetting = rcbSettingRows[0]
		self.assertEqual(rcbSetting[10], 'V0.3')
		self.assertEqual(rcbSetting[11], 'False')
		self.assertEqual(rcbSetting[12], 'False')
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
		self.assertEqual(collV1[3], 'E:\Emulatoren\WINUAE\winuae.exe -f "E:\Emulatoren\WINUAE\Configurations\Host\Amiga 500.uae" {-%I% "%ROM%"}')
		
		collV2 = romCollectionRows[1]
		self.assertEqual(collV2[1], 'Collection V2')
		self.assertEqual(collV2[3], 'E:\Emulatoren\WINUAE\winuae.exe {-%I% "%ROM%"}')
		
		collV3 = romCollectionRows[2]
		self.assertEqual(collV3[1], 'Collection V3')
		self.assertEqual(collV3[3], 'E:\Emulatoren\SNES\zsnes.exe -m "%ROM%"')

	
	def test_UpdateDB(self):				
		si = importsettings.SettingsImporter()
		si.importSettings(self.gdb, self.databasedir, RCBMock())
		
		dbupdate.DBUpdate().updateDB(self.gdb, RCBMock())
				
		#Amiga Action
		gameRows = Game(self.gdb).getFilteredGames(1, 1, 0, 0)
		self.assertTrue(gameRows != None)
		self.assertTrue(len(gameRows) == 3)
		
		#Amiga 1994
		gameRows = Game(self.gdb).getFilteredGames(1, 0, 6, 0)		
		self.assertTrue(gameRows != None)
		self.assertTrue(len(gameRows) == 2)
		
		#Amiga Black Legend Ltd.
		gameRows = Game(self.gdb).getFilteredGames(1, 0, 0, 6)
		self.assertTrue(gameRows != None)
		self.assertTrue(len(gameRows) == 1)		
		
		#Amiga Sports, 1994, Black Legend Ltd.
		gameRows = Game(self.gdb).getFilteredGames(1, 4, 6, 6)
		self.assertTrue(gameRows != None)
		self.assertTrue(len(gameRows) == 1)
		
		#NES 1st person shooter
		gameRows = Game(self.gdb).getFilteredGames(2, 8, 0, 0)
		self.assertTrue(gameRows != None)		
		self.assertTrue(len(gameRows) == 1)
		
		#NES 1992
		gameRows = Game(self.gdb).getFilteredGames(2, 0, 7, 0)
		self.assertTrue(gameRows != None)
		self.assertTrue(len(gameRows) == 4)
		
		#NES Nintendo
		gameRows = Game(self.gdb).getFilteredGames(2, 0, 0, 11)
		self.assertTrue(gameRows != None)
		self.assertTrue(len(gameRows) == 3)
		
		#NES 1992 Racing Nintendo 
		gameRows = Game(self.gdb).getFilteredGames(2, 11, 7, 11)
		self.assertTrue(gameRows != None)
		self.assertTrue(len(gameRows) == 1)
		
		gameRows = Game(self.gdb).getAllOrdered()	
		self.assertTrue(gameRows != None)
		self.assertTrue(len(gameRows) == 15)
		
		
		self.gameTest(gameRows[0], 'Airborne Ranger', 'In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger.', 1, 1, 1)
		self.gameTest(gameRows[1], 'California Games II',  '"At least it ends..."', 1, 1, 1)
		self.gameTest(gameRows[2], 'Demolition Man', 'Demolition Man is a multiplatform, run and gun action game based on the film of the same name.', 1, 1, 1)
		self.gameTest(gameRows[3], 'Dogfight', 'Dogfight is a two-player game with roots in the same primordial soup as Ataris Combat and other basic dogfighting games.', 3, 1, 2)
		self.gameTest(gameRows[4], 'Doom', 'Doom on the PC was without a doubt my favorite first person shooter "back in the day', 1, 1, 1)
		self.gameTest(gameRows[5], 'Eliminator', 'A shoot em up set on a patchwork-quilt coloured road, Eliminator puts you in control of a ship with a basic weapon, flying along at breakneck speed.', 1, 1, 1)		
		self.gameTest(gameRows[6], 'Football Glory', 'From Croatia came this overhead view football game resembling Sensible Soccer.', 3, 1, 1)
		self.gameTest(gameRows[7], 'Formula One Grand Prix', 'F1 is an Official Formula One Racing Game.', 4, 1, 1)
		self.gameTest(gameRows[8], 'Hanse - Die Expedition', 'Hanse makes you a trader in the 13th Century.', 3, 1, 1)
		self.gameTest(gameRows[9], 'Legend of Zelda - A Link to the Past', 'This installment in the Zelda series was my favorite.', 1, 1, 1)
		self.gameTest(gameRows[10], 'Madden NFL \'98', 'Madden NFL 98 is a football video game.', 1, 1, 1)
		self.gameTest(gameRows[11], 'Ports Of Call', 'Ports of Call gives you the job of a shipowner.', 1, 1, 1)
		self.gameTest(gameRows[12], 'Space Invaders', 'Taito and Nintendo have brought back the classic Space Invaders game, with very little modification.', 1, 1, 1)
		self.gameTest(gameRows[13], 'Street Fighter II - The World Warrior', 'Eight fighters from across the globe have come together to see which of them has the strength, skill and courage to challenge the mysterious Grand Masters.', 1, 1, 1)
		self.gameTest(gameRows[14], 'Super Mario Kart', 'Hi everybody! Thanks for dropping to by the Super Mario Kart race track.', 1, 1, 1)
		
		
		
	def gameTest(self, game, name, descStart, numRoms, numCovers, numIngameScreens):
		self.assertEqual(game[1], name)
		description = game[2]
		descStart = descStart
		self.assertTrue(description.startswith(descStart))
		
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
		


class RCBMock():
	def writeMsg(self, msg):
		pass
	

unittest.main()