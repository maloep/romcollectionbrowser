
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
				#TODO support for more than one path
				romPath = Path(self.gdb).getRomPathByRomCollectionId(romCollectionRow[0])
				print "RomPath: " +str(romPath)
				screenshotPath = Path(self.gdb).getScreenshotPathByRomCollectionId(romCollectionRow[0])
				print "screenPath: " +str(screenshotPath)
				descriptionPath = Path(self.gdb).getDescriptionPathByRomCollectionId(romCollectionRow[0])
				print "descriptionPath: " +str(descriptionPath)				
				
				# read ROMs from disk
				if os.path.isdir(os.path.dirname(romPath)):
					#glob is same as "os.listdir(romPath)" but it can handle wildcards like *.adf
					files = glob.glob(romPath)
					files.sort()
				else:
					files = []
					
				print "files " +str(files)
					
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
					
					#TODO Handle subrom
					
					#repeat for every path
					screenshotfile = screenshotPath.replace("%GAME%", gamename)
					print "screenPath: " +screenshotfile
					print "screenPath exists: " +str(os.path.exists(screenshotfile))
										
					descriptionfile = descriptionPath.replace("%GAME%", gamename)
					print "descriptionPath: " +descriptionfile
					print "descriptionPath exists: " +str(os.path.exists(descriptionfile))
										
					if(os.path.exists(descriptionfile)):
						dp = DescriptionParser()
						results = dp.parseDescriptionSearch(descriptionfile, '', gamename)
						
						for result in results:
							#sreader = codecs.getreader('iso-8859-15')
							#lines = sreader.readLines()
							print result.encode('iso-8859-15')
							
						#TODO delete objects?
						del dp
					



#gdb = GameDataBase(os.path.join(os.getcwd(), '..', 'database'))
#dbupdate = DBUpdate()
#gdb.connect()
#dbupdate.updateDB(gdb)
#gdb.close()
#del dbupdate
#del gdb