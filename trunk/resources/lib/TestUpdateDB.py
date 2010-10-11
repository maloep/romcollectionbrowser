import unittest
import os, sys
import re, string


# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), ".." )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
if env == 'Windows_NT':
	env = 'win32'
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )


from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *
import dbupdate, importsettings
from util import Logutil

#adjust settings for tests
util.RCBHOME = os.path.join(os.getcwd(), '..', '..')
util.ISTESTRUN = True

Logutil.currentLogLevel = util.LOG_LEVEL_INFO



class TestUpdateDB(unittest.TestCase):
	
	def setUp(self):
		self.databasedir = os.path.join( os.getcwd(), 'TestDataBase')
		self.gdb = GameDataBase(self.databasedir)
		self.gdb.connect()
		self.gdb.dropTables()		
		self.gdb.createTables()	
		
		si = importsettings.SettingsImporter()
		si.importSettings(self.gdb, RCBMock())				
		
		
	def test_UpdateDB(self):

		dbupdate.DBUpdate().updateDB(self.gdb, RCBMock())
		
		#test some filters
		
		likeStmnt = '0 = 0'
				
		#Amiga Action
		gameRows = Game(self.gdb).getFilteredGames(1, 1, 0, 0, likeStmnt)
		self.assertTrue(gameRows != None)
		self.assertEqual(len(gameRows) , 3)
		
		#Amiga 1994
		gameRows = Game(self.gdb).getFilteredGames(1, 0, 6, 0, likeStmnt)		
		self.assertTrue(gameRows != None)
		self.assertEqual(len(gameRows), 2)
		
		#Amiga Black Legend Ltd.
		gameRows = Game(self.gdb).getFilteredGames(1, 0, 0, 6, likeStmnt)
		self.assertTrue(gameRows != None)
		self.assertEqual(len(gameRows), 1)		
		
		#Amiga Sports, 1994, Black Legend Ltd.
		gameRows = Game(self.gdb).getFilteredGames(1, 4, 6, 6, likeStmnt)
		self.assertTrue(gameRows != None)
		self.assertEqual(len(gameRows), 1)
		
		#NES 1st person shooter
		gameRows = Game(self.gdb).getFilteredGames(2, 8, 0, 0, likeStmnt)
		self.assertTrue(gameRows != None)		
		self.assertEqual(len(gameRows), 1)
		
		#NES 1992
		gameRows = Game(self.gdb).getFilteredGames(2, 0, 7, 0, likeStmnt)
		self.assertTrue(gameRows != None)
		self.assertEqual(len(gameRows), 4)
		
		#NES Nintendo
		gameRows = Game(self.gdb).getFilteredGames(2, 0, 0, 12, likeStmnt)
		self.assertTrue(gameRows != None)
		self.assertEqual(len(gameRows), 4)
		
		#NES 1992 Racing Nintendo 
		gameRows = Game(self.gdb).getFilteredGames(2, 11, 7, 12, likeStmnt)
		self.assertTrue(gameRows != None)
		self.assertEqual(len(gameRows), 1)
		
		gameRows = Game(self.gdb).getAllOrdered()	
		self.assertTrue(gameRows != None)
		self.assertEqual(len(gameRows), 27)				
		
		
		self.gameTest(gameRows[0], '007: Agent Under Fire', 'Get ready for the next generation of 007, as Her Majestys greatest secret agent embarks upon an all-new, action-packed adventure.', 
			None,  None, 5, 14, 11, None, 11, '1-4', '', '', '', '', 'DVD', '', 'Xbox Controller', 0, 0,
			1, 1, 0, 0, 0, 0)		
		self.gameTest(gameRows[1], 'After Burner', '', 
			None,  None, 6, 17, 18, None, 6, '', '', '', '', 'United States', '', '', '', 0, 0,
			1, 1, 0, 0, 0, 0)
		self.gameTest(gameRows[2], 'Airborne Ranger', 'In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger.', 
			None,  None, 1, 1, 1, None, 1, '????', '', '', 'http://www.mobygames.com/game/amiga/airborne-ranger', '', '', '', '', 0, 0,
			1, 1, 1, 0, 0, 0)
		self.gameTest(gameRows[3], 'AMF Bowling 2004', 'Experience the excitement of a night at the lanes with AMF Xtreme Bowling 2006.', 
			None,  None, 5, 15, 15, None, 12, '1-2', '', '', '', '', 'DVD', '', 'Xbox Controller', 0, 0,
			1, 1, 0, 0, 0, 0)
		self.gameTest(gameRows[4], 'Antz Extreme Racing', 'Handling dirt is not a rewarding career', 
			None,  None, 5, 16, 16, None, 11, '1-4', '', '', '', '', 'DVD', '', 'Xbox Controller', 0, 0,
			1, 1, 0, 0, 0, 0)
		self.gameTest(gameRows[5], 'Area 51', 'No synopsis information for this game.', 
			None,  None, 5, None, None, None, None, '', '', '', '', '', 'DVD', '', 'Xbox Controller', 0, 0,
			1, 1, 0, 0, 0, 0)
		self.gameTest(gameRows[6], 'BC Racers', '', 
			None,  None, 6, 18, 19, None, 8, '', '', '', '', 'United States', '', '', '', 0, 0,
			1, 1, 0, 0, 0, 0)
		self.gameTest(gameRows[7], 'Blackthorne', 'Blackthorne is an action-adventure game that takes place on the planet Tuul.', 
			None,  None, 7, 19, 20, None, 8, '1 Player', '', '', '', '', '', '', '', 0, 0,
			1, 1, 0, 0, 0, 0)
		self.gameTest(gameRows[8], 'Brutal: Above the Claw', 'As with the original Brutal: Paws of Fury, the game involves a martial arts tournament set up by the Dalai Llama.', 
			None,  None, 7, 20, 21, None, 8, '1-2 Players', '', '', '', '', '', '', '', 0, 0,
			1, 1, 0, 0, 0, 0)		
		self.gameTest(gameRows[9], 'California Games II',  '"At least it ends..."', 
			None,  None, 3, 8, 8, None, 7, '', '', '', '', 'USA', 'Cartridge', '', 'Gamepad', 0, 0,
			1, 1, 1, 1, 1, 1)
		self.gameTest(gameRows[10], 'Cosmic Carnage', 'Cosmic Carnage is a one-on-one fighting game set in outer space.', 
			None,  None, 7, 17, 22, None, 6, '1-2 Players', '', '', '', '', '', '', '', 0, 0,
			1, 1, 0, 0, 0, 0)
		self.gameTest(gameRows[11], 'Demolition Man', 'Demolition Man is a multiplatform, run and gun action game based on the film of the same name.', 
			None,  None, 3, 9, 9, None, 8, '', '', '', '', 'USA', 'Cartridge', '', 'Gamepad', 0, 0,
			1, 1, 1, 1, 1, 1)
		self.gameTest(gameRows[12], 'Dogfight', 'Dogfight is a two-player game with roots in the same primordial soup as Ataris Combat and other basic dogfighting games.', 	
			None,  None, 2, 5, 5, None, 5, '2 Players', '', '', 'http://www.mobygames.com/game/amiga/dogfight', '', '', '', '', 0, 0,
			3, 1, 2, 0, 0, 0)
		self.gameTest(gameRows[13], 'Doom', 'Doom on the PC was without a doubt my favorite first person shooter "back in the day', 
			None,  None, 3, 10, 10, None, 9, '1', '', '', '', 'USA', 'Cartridge', '', 'Gamepad', 0, 0,
			1, 1, 1, 1, 1, 1)
		self.gameTest(gameRows[14], 'Eliminator', 'A shoot em up set on a patchwork-quilt coloured road, Eliminator puts you in control of a ship with a basic weapon, flying along at breakneck speed.', 
			None,  None, 1, 2, 2, None, 2, '????', '', '', 'http://www.mobygames.com/game/amiga/eliminator-', '', '', '', '', 0, 0,
			1, 1, 1, 0, 0, 0)		
		self.gameTest(gameRows[15], 'Football Glory', 'From Croatia came this overhead view football game resembling Sensible Soccer.', 
			None,  None, 2, 6, 6, None, 6, '1-2 Players', '', '', 'http://www.mobygames.com/game/amiga/football-glory', '', '', '', '', 0, 0,
			3, 1, 1, 0, 0, 0)
		self.gameTest(gameRows[16], 'Formula One: Grand Prix', 'F1 is an Official Formula One Racing Game.', 
			None,  None, 1, 3, 3, None, 3, '????', '', '', 'http://www.mobygames.com/game/amiga/formula-one_', '', '', '', '', 0, 0,
			4, 1, 1, 0, 0, 0)
		self.gameTest(gameRows[17], 'Game without Desc', None, 
			None,  None, 2, None, None, None, None, None, None, None, None, None, None, None, None, 0, 0,
			1, 0, 0, 0, 0, 0)
		self.gameTest(gameRows[18], 'Golf Magazine Presents 36 Great Holes Starring Fred Couples', '', 
			None,  None, 6, 17, 17, None, 6, '', '', '', '', 'United States', '', '', '', 0, 0,
			1, 1, 0, 0, 0, 0)
		self.gameTest(gameRows[19], 'Hanse - Die Expedition', 'Hanse makes you a trader in the 13th Century.', 
			None,  None, 2, 7, 7, None, 6, '????', '', '', 'http://www.mobygames.com/game/amiga/hanse-die-expedition', '', '', '', '', 0, 0,
			3, 1, 1, 0, 0, 0)		
		self.gameTest(gameRows[20], 'Madden NFL \'98', 'Madden NFL 98 is a football video game.', 
			None,  None, 3, 11, 11, None, 10, '', '', '', '', 'USA', 'Cartridge', '', 'Gamepad', 0, 0,
			1, 1, 1, 1, 1, 0)
		self.gameTest(gameRows[21], 'Ports Of Call [Test]', 'Ports of Call gives you the job of a shipowner.', 
			None,  None, 1, 4, 4, None, 4, '4', '', '', 'http://www.mobygames.com/game/amiga/ports-of-call', 'USA', 'Disk', '', 'Joystick', 0, 0,
			1, 1, 1, 0, 0, 0)			
		self.gameTest(gameRows[22], 'Space Invaders', 'Taito and Nintendo have brought back the classic Space Invaders game, with very little modification.', 
			None,  None, 3, 12, 12, None, 9, '', '', '', '', 'USA', 'Cartridge', '', 'Gamepad', 0, 0,
			1, 1, 1, 1, 1, 0)
		self.gameTest(gameRows[23], 'Space Invaders', 'Taito and Nintendo have brought back the classic Space Invaders game, with very little modification.', 
			None,  None, 4, 12, 12, None, 9, '', '', '', '', 'USA', 'Cartridge', '', 'Gamepad', 0, 0,
			1, 1, 1, 1, 1, 0)
		self.gameTest(gameRows[24], 'Street Fighter II - The World Warrior', 'Eight fighters from across the globe have come together to see which of them has the strength, skill and courage to challenge the mysterious Grand Masters.', 
			None,  None, 3, 13, 13, None, 7, '1 or 2 VS', '', '', '', 'USA', 'Cartridge', '', 'Gamepad', 0, 0,
			1, 1, 1, 1, 1, 0)
		self.gameTest(gameRows[25], 'Super Mario Kart', 'Hi everybody! Thanks for dropping to by the Super Mario Kart race track.', 
			None,  None, 3, 12, 14, None, 7, '1 to 4 VS', '', '', '', 'USA', 'Cartridge', '', 'Gamepad', 0, 0,
			1, 1, 1, 1, 1, 0)
		self.gameTest(gameRows[26], 'The Legend of Zelda: A Link to the Past', 'This installment in the Zelda series was my favorite.', 
			None,  None, 4, 12, 14, None, 7, '1', '', '', '', 'USA', 'Cartridge', '', 'Gamepad', 0, 0,
			1, 1, 1, 1, 1, 1)
		
		
		#test additional file types
		self.fileTypeTest('developer', 1, gameRows[2][7])
		self.fileTypeTest('publisher', 1, gameRows[2][6])
		
		self.fileTypeTest('developer', 1, gameRows[19][7])
		self.fileTypeTest('publisher', 1, gameRows[19][6])
		
		
	def gameTest(self, game, name, descStart, gameCmd, alternateGameCmd, romCollectionId, publisherId, developerId, reviewerId,
			yearId, maxPlayers, rating, numVotes, url, region, media, perspective, controllerType, isFavorite, launchCount,
			numRoms, numCovers, numIngameScreens, numTitleScreens, numCartridges, numVideos):
		
		print name
		self.assertEqual(game[1], name)
		description = game[2]
		descStart = descStart
		if(description != None):
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
		self.fileTypeTest('gameplay', numVideos, game[0])
				
		
	def fileTypeTest(self, typeName, numFilesExpected, gameId):
		fileTypeRow = FileType(self.gdb).getOneByName(typeName)		
		files = File(self.gdb).getFilesByGameIdAndTypeId(gameId, fileTypeRow[0])		
		self.assertTrue(files != None)
		numfiles = len(files)
		self.assertEqual(numfiles, numFilesExpected)
		
		

class RCBMock:
	
	itemCount = 0
	
	def writeMsg(self, msg1, msg2, msg3, count=0):
		pass
	

unittest.main()