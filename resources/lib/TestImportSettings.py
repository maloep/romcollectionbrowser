

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


class TestImportSettings(unittest.TestCase):
	
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
		self.assertEqual(rcbSetting[10], 'V0.4')
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
		console = Console(self.gdb).getObjectById(collV1[2])
		self.assertEqual(console[1], 'Amiga')
		self.assertEqual(collV1[3], 'E:\Emulatoren\WINUAE\winuae.exe -f "E:\Emulatoren\WINUAE\Configurations\Host\Amiga 500.uae" {-%I% "%ROM%"}')
		self.assertEqual(collV1[4], 'True')
		self.assertEqual(collV1[5], 'True')
		self.assertEqual(collV1[6], 'TestDataBase\Collection V1\parserConfig.xml')
		self.assertEqual(collV1[7], 'True')
		self.assertEqual(collV1[8], 'False')
		self.assertEqual(collV1[9], 'False')
		self.assertEqual(collV1[10], '_Disk')
		self.assertEqual(collV1[11], 'Text')
		self.assertEqual(collV1[12], 'False')
		self.assertEqual(collV1[13], 'False')
		self.assertEqual(collV1[14], 'True')
		self.assertEqual(collV1[15], 'False')
		self.assertEqual(collV1[16], 'True')
		
		collV2 = romCollectionRows[1]
		self.assertEqual(collV2[1], 'Collection V2')
		console = Console(self.gdb).getObjectById(collV2[2])
		self.assertEqual(console[1], 'Amiga')
		self.assertEqual(collV2[3], 'E:\Emulatoren\WINUAE\winuae.exe {-%I% "%ROM%"}')
		self.assertEqual(collV2[4], 'True')
		self.assertEqual(collV2[5], 'True')
		self.assertEqual(collV2[6], 'TestDataBase\Collection V2\parserConfig.xml')
		self.assertEqual(collV2[7], 'True')
		self.assertEqual(collV2[8], 'False')
		self.assertEqual(collV2[9], 'True')
		self.assertEqual(collV2[10], '_Disk')
		self.assertEqual(collV2[11], 'Text')
		self.assertEqual(collV2[12], 'False')
		self.assertEqual(collV2[13], 'False')
		self.assertEqual(collV2[14], 'True')
		self.assertEqual(collV2[15], 'False')
		self.assertEqual(collV2[16], 'False')
		
		collV3 = romCollectionRows[2]
		self.assertEqual(collV3[1], 'Collection V3')
		console = Console(self.gdb).getObjectById(collV3[2])
		self.assertEqual(console[1], 'Super Nintendo')
		self.assertEqual(collV3[3], 'E:\Emulatoren\SNES\zsnes.exe -m "%ROM%"')	
		self.assertEqual(collV3[4], 'True')
		self.assertEqual(collV3[5], 'True')
		self.assertEqual(collV3[6], 'TestDataBase\Collection V3\parserConfig.xml')
		self.assertEqual(collV3[7], 'True')
		self.assertEqual(collV3[8], 'False')
		self.assertEqual(collV3[9], 'False')
		self.assertEqual(collV3[10], '_Disk')
		self.assertEqual(collV3[11], 'Text')
		self.assertEqual(collV3[12], 'False')
		self.assertEqual(collV3[13], 'False')
		self.assertEqual(collV2[14], 'True')
		self.assertEqual(collV2[15], 'False')
		self.assertEqual(collV2[16], 'False')


		fileTypes = FileType(self.gdb).getAll()
		self.assertEqual(fileTypes[0][1], 'rcb_rom')
		self.assertEqual(fileTypes[1][1], 'rcb_manual')
		self.assertEqual(fileTypes[2][1], 'rcb_description')
		self.assertEqual(fileTypes[3][1], 'rcb_configuration')		
		
		self.assertEqual(fileTypes[4][1], 'cover')
		self.assertEqual(fileTypes[5][1], 'screenshotingame')		
		self.assertEqual(fileTypes[6][1], 'screenshottitle')
		self.assertEqual(fileTypes[7][1], 'cartridge')		
		self.assertEqual(fileTypes[8][1], '3dbox')
		self.assertEqual(fileTypes[9][1], 'hyperspin')
		
		
		paths = Path(self.gdb).getAll()
		self.assertTrue(paths != None)
		self.assertEqual(len(paths), 56)
				
		
		self.assertEqual(paths[0][1], 'TestDataBase\Collection V1\\roms\*.adf')		
		self.pathTest(paths[1][1], 'TestDataBase\Collection V1\\roms\*.ADF', paths[1][2], 'rcb_rom', paths[1][3], 'Collection V1')
		self.pathTest(paths[2][1], 'TestDataBase\Collection V1\synopsis\synopsis.txt', paths[2][2], 'rcb_description', paths[1][3], 'Collection V1')
		self.pathTest(paths[5][1], 'TestDataBase\Collection V1\cover\%GAME%.png', paths[5][2], 'cover', paths[1][3], 'Collection V1')
		self.pathTest(paths[9][1], 'TestDataBase\Collection V2\\roms\*.adf', paths[9][2], 'rcb_rom', paths[9][3], 'Collection V2')
		self.pathTest(paths[14][1], 'TestDataBase\Collection V2\cover\%GAME%\*.png', paths[14][2], 'cover', paths[14][3], 'Collection V2')
		self.pathTest(paths[17][1], 'TestDataBase\Collection V2\screens\%GAME%\*.png', paths[17][2], 'screenshotingame', paths[17][3], 'Collection V2')
		self.pathTest(paths[21][1], 'TestDataBase\Collection V3\cover\%GAME%.jpg', paths[21][2], 'cover', paths[21][3], 'Collection V3')
		self.pathTest(paths[24][1], 'TestDataBase\Collection V3\screens\%GAME%.jpg', paths[24][2], 'screenshotingame', paths[24][3], 'Collection V3')
		self.pathTest(paths[26][1], 'TestDataBase\Collection V3\screens\%GAME%.png', paths[26][2], 'screenshotingame', paths[26][3], 'Collection V3')
		self.pathTest(paths[28][1], 'TestDataBase\Collection V3\\titles\%GAME%.jpg', paths[28][2], 'screenshottitle', paths[28][3], 'Collection V3')
		self.pathTest(paths[30][1], 'TestDataBase\Collection V3\cartridge\%GAME%.gif', paths[30][2], 'cartridge', paths[30][3], 'Collection V3')
		self.pathTest(paths[32][1], 'TestDataBase\Collection V3\cartridge\%GAME%.jpg', paths[32][2], 'cartridge', paths[32][3], 'Collection V3')
		self.pathTest(paths[33][1], 'TestDataBase\Collection V3\ingameVids\%GAME%.wmv', paths[33][2], 'gameplay', paths[33][3], 'Collection V3')
		
		
		fileTypesForControl = FileTypeForControl(self.gdb).getAll()
		self.assertTrue(paths != None)
		numFileTypes = len(fileTypesForControl)
		self.assertEqual(numFileTypes, 29)
		
		self.fileTypeForControlTestTest(fileTypesForControl[0][1], 'gamelist', fileTypesForControl[0][2], 0, fileTypesForControl[0][4], 'cover', fileTypesForControl[0][3], 'Collection V1')
		self.fileTypeForControlTestTest(fileTypesForControl[2][1], 'gameinfoviewbackground', fileTypesForControl[2][2], 0, fileTypesForControl[2][4], 'cover', fileTypesForControl[2][3], 'Collection V1')
		self.fileTypeForControlTestTest(fileTypesForControl[5][1], 'gameinfoview3', fileTypesForControl[5][2], 0, fileTypesForControl[5][4], 'cover', fileTypesForControl[5][3], 'Collection V1')
		self.fileTypeForControlTestTest(fileTypesForControl[8][1], 'gameinfoviewbackground', fileTypesForControl[8][2], 0, fileTypesForControl[8][4], 'cover', fileTypesForControl[8][3], 'Collection V2')
		self.fileTypeForControlTestTest(fileTypesForControl[11][1], 'gameinfoview3', fileTypesForControl[11][2], 0, fileTypesForControl[11][4], 'cover', fileTypesForControl[11][3], 'Collection V2')
		self.fileTypeForControlTestTest(fileTypesForControl[15][1], 'gameinfoviewbackground', fileTypesForControl[15][2], 1, fileTypesForControl[15][4], 'cover', fileTypesForControl[15][3], 'Collection V3')
		self.fileTypeForControlTestTest(fileTypesForControl[16][1], 'gameinfoviewgamelist', fileTypesForControl[16][2], 0, fileTypesForControl[16][4], 'cover', fileTypesForControl[16][3], 'Collection V3')
		self.fileTypeForControlTestTest(fileTypesForControl[18][1], 'gameinfoview2', fileTypesForControl[18][2], 0, fileTypesForControl[18][4], 'screenshotingame', fileTypesForControl[18][3], 'Collection V3')
		self.fileTypeForControlTestTest(fileTypesForControl[20][1], 'gameinfoview4', fileTypesForControl[20][2], 0, fileTypesForControl[20][4], 'cartridge', fileTypesForControl[20][3], 'Collection V3')
		self.fileTypeForControlTestTest(fileTypesForControl[21][1], 'gameinfoviewvideowindow', fileTypesForControl[21][2], 0, fileTypesForControl[21][4], 'gameplay', fileTypesForControl[21][3], 'Collection V3')
		
		
		
	def pathTest(self, pathActual, pathExpected, fileTypeId, fileTypeExpected, romCollId, romCollExpected):
		self.assertEqual(pathActual, pathExpected)
		fileType = FileType(self.gdb).getObjectById(fileTypeId)
		self.assertEqual(fileType[1], fileTypeExpected)
		romCollection = RomCollection(self.gdb).getObjectById(romCollId)
		self.assertEqual(romCollection[1], romCollExpected)
		
		
	def fileTypeForControlTestTest(self, nameActual, nameExpected, priority, priorityExpected, fileTypeId, fileTypeExpected, romCollId, romCollExpected):
		self.assertEqual(nameActual, nameExpected)
		fileType = FileType(self.gdb).getObjectById(fileTypeId)
		self.assertEqual(priority, priorityExpected)
		self.assertEqual(fileType[1], fileTypeExpected)
		romCollection = RomCollection(self.gdb).getObjectById(romCollId)
		self.assertEqual(romCollection[1], romCollExpected)
		

class RCBMock():
	def writeMsg(self, msg):
		pass
	

unittest.main()