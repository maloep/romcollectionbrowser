
import os, sys
import getpass, string, glob
import codecs
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *

from pyparsing import *
from descriptionparser import *


class DBUpdate:
	
	def updateDB(self, gdb):
		
		self.gdb = gdb
		
		romCollectionRows = RomCollection(self.gdb).getAll()
		
		for romCollectionRow in romCollectionRows:
			print str(romCollectionRow)
			#romCollectionRow[8] = startWithDescFile
			if(romCollectionRow[8] == 1):
				pass
			else:				
				romPath = Path(self.gdb).getRomPathByRomCollectionId(romCollectionRow[0])
				print "RomPath: " +str(romPath)				
				descriptionPath = Path(self.gdb).getDescriptionPathByRomCollectionId(romCollectionRow[0])
				print "descriptionPath: " +str(descriptionPath)
				ingameScreenshotPaths = Path(self.gdb).getIngameScreenshotPathsByRomCollectionId(romCollectionRow[0])
				print "screenPathIngame: " +str(ingameScreenshotPaths)
				titleScreenshotPaths = Path(self.gdb).getTitleScreenshotPathsByRomCollectionId(romCollectionRow[0])
				print "screenPathTitle: " +str(titleScreenshotPaths)
				coverPaths = Path(self.gdb).getCoverPathsByRomCollectionId(romCollectionRow[0])
				print "coverPath: " +str(coverPaths)
				cartridgePaths = Path(self.gdb).getCartridgePathsByRomCollectionId(romCollectionRow[0])
				print "cartridgePath: " +str(cartridgePaths)
				manualPaths = Path(self.gdb).getManualPathsByRomCollectionId(romCollectionRow[0])
				print "manualPath: " +str(manualPaths)
				ingameVideoPaths = Path(self.gdb).getIngameVideoPathsByRomCollectionId(romCollectionRow[0])
				print "ingameVideoPath: " +str(ingameVideoPaths)
				trailerPaths = Path(self.gdb).getTrailerPathsByRomCollectionId(romCollectionRow[0])
				print "trailerPath: " +str(trailerPaths)
				configurationPaths = Path(self.gdb).getConfigurationPathsByRomCollectionId(romCollectionRow[0])
				print "configurationPath: " +str(configurationPaths)
				
				# read ROMs from disk
				if os.path.isdir(os.path.dirname(romPath)):
					#glob is same as "os.listdir(romPath)" but it can handle wildcards like *.adf
					files = glob.glob(romPath)
					files.sort()
				else:
					files = []
					
				lastgamename = ""
					
				for filename in files:
					subrom = False
			
					#build friendly romname
					gamename = os.path.basename(filename)
					#romCollectionRow[10] = DiskPrefix
					dpIndex = gamename.lower().find(romCollectionRow[10].lower())
					if dpIndex > -1:
						gamename = gamename[0:dpIndex]
					else:
						gamename = os.path.splitext(gamename)[0]
					print "gameName = " +gamename
					print "filename = " +filename
					
					if(gamename == lastgamename):
						continue
						
					lastgamename = gamename
					
					self.resolvePath(ingameScreenshotPaths, gamename)
					self.resolvePath(titleScreenshotPaths, gamename)
					self.resolvePath(coverPaths, gamename)
					self.resolvePath(cartridgePaths, gamename)
					self.resolvePath(manualPaths, gamename)
					self.resolvePath(ingameVideoPaths, gamename)
					self.resolvePath(trailerPaths, gamename)
					self.resolvePath(configurationPaths, gamename)
															
					self.parseDescriptionFile(descriptionPath, gamename)
					
					
					# Year
					# Publisher
					# Genre
					# Game
					# GenreGame
					# File
						
	
	def resolvePath(self, paths, gamename):
		#repeat for every path
		for path in paths:
			file = path[0].replace("%GAME%", gamename)
			#TODO Handle WildcardPaths
			print "File: " +file
			print "File exists: " +str(os.path.exists(file))
			
	
	def parseDescriptionFile(self, descriptionPath, gamename):
		descriptionfile = descriptionPath.replace("%GAME%", gamename)
		print "descriptionPath: " +descriptionfile
		print "descriptionPath exists: " +str(os.path.exists(descriptionfile))
							
		if(os.path.exists(descriptionfile)):
			dp = DescriptionParser()
			results = dp.parseDescriptionSearch(descriptionfile, '', gamename)			
			
			print "Result game = " +str(results['game'])
			print "Result desc = " +str(results['description'])
			print "Result year = " +str(results['year'])
			print "Result genre = " +str(results['genre'])
			print "Result publisher = " +str(results['publisher'])
			
			year = results.year
			yearRow = Year(self.gdb).getOneByName(year[0])
			print yearRow
			if(yearRow == None):
				print "add year: "+str(year)
				Year(self.gdb).insert(year)
				self.gdb.commit()
				
			genres = results.genre
			print genres
			#TODO itemDelimiter?			
			for genreItem in genres:
				print genreItem
				genreRow = Genre(self.gdb).getOneByName(genreItem)
				if(genreRow == None):
					Genre(self.gdb).insert((genreItem,))
					print "add genre: "+str(genreItem)
					self.gdb.commit()
					
				
				
			#TODO delete objects?
			del dp
		



gdb = GameDataBase(os.path.join(os.getcwd(), '..', 'database'))
dbupdate = DBUpdate()
gdb.connect()
dbupdate.updateDB(gdb)
gdb.close()
del dbupdate
del gdb