

import unittest
import os, sys

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
		
		airborneRanger = gameRows[0]
		self.assertEqual(airborneRanger[1], 'Airborne Ranger')		
		calGames = gameRows[1]
		self.assertEqual(calGames[1], 'California Games II')				
		demolitionMan = gameRows[2]
		self.assertEqual(demolitionMan[1], 'Demolition Man')
		dogFight = gameRows[3]
		self.assertEqual(dogFight[1], 'Dogfight')
		doom = gameRows[4]
		self.assertEqual(doom[1], 'Doom')
		eliminator = gameRows[5]
		self.assertEqual(eliminator[1], 'Eliminator')		
		footballGlory = gameRows[6]
		self.assertEqual(footballGlory[1], 'Football Glory')
		formulaOne = gameRows[7]
		self.assertEqual(formulaOne[1], 'Formula One Grand Prix')
		hanse = gameRows[8]
		self.assertEqual(hanse[1], 'Hanse - Die Expedition')
		zelda = gameRows[9]
		self.assertEqual(zelda[1], 'Legend of Zelda - A Link to the Past')
		madden = gameRows[10]
		self.assertEqual(madden[1], 'Madden NFL \'98')		
		ports = gameRows[11]
		self.assertEqual(ports[1], 'Ports Of Call')
		spaceInvaders = gameRows[12]
		self.assertEqual(spaceInvaders[1], 'Space Invaders')
		streetFighter = gameRows[13]
		self.assertEqual(streetFighter[1], 'Street Fighter II - The World Warrior')
		superMario = gameRows[14]
		self.assertEqual(superMario[1], 'Super Mario Kart')
		
		


class RCBMock():
	def writeMsg(self, msg):
		pass
	

unittest.main()