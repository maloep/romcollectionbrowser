
import os, sys
import time
import urllib
from descriptionparserfactory import DescriptionParserFactory

print "start parsing"

BASE_RESOURCE_PATH = os.path.join( os.getcwd())
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "pyparsing" ) )

env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
if env == 'Windows_NT':
	env = 'win32'
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "..", "platform_libraries", env ) )

import util 

#descFile = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\SMSGG.txt"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\_parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\Sega 32 - After Burner.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\VideoGameDB - parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\SEGA 32 - complete.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\Access - parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\MAME v0.138.dat"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\MameDat - parserConfig.xml"

#"http://thevideogamedb.com/API/GameDetail.aspx?apikey=Zx5m2Y9Ndj6B4XwTf83JyKz7r8WHt3i4&name=After%20burner"

#descFile = "http://thevideogamedb.com/API/GameDetail.aspx?apikey=Zx5m2Y9Ndj6B4XwTf83JyKz7r8WHt3i4&name=After%20burner"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\VideoGameDB - parserConfig.xml"

#descFile = "http://romcollectionbrowser.googlecode.com/svn/trunk/resources/lib/TestDataBase/Collection%20V3/description/synopsis.txt"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\_parserConfig.xml"

#descFile = "http://www.mobygames.com/game/gamecube/animal-crossing/cover-art"
#descFile = "F:\\Emulatoren\\data\\Synopsis\\actraiser-2-cover-art.htm"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\mobygames - parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\spyvsspy\\amiga_rom_synopsis_big_for_xbmc_rcb_addon\\amiga_rom_synopsis_big_for_xbmc_rcb_addon\\AMIGA_big.txt"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\spyvsspy\\amiga_rom_synopsis_big_for_xbmc_rcb_addon\\amiga_rom_synopsis_big_for_xbmc_rcb_addon\\parserConfig.xml"


#descFile = "http://www.mobygames.com/search/quick?game=3%20Ninjas%20Kick%20Back&p=15"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\01 - parseinstruction - mobygames - gamesearch.xml"

descFile = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\moby gameshot.htm"
parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\07 - mobygames - screenshots.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\moby coverart.htm"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\mobyCoverart - parserConfig.xml"


#descFile = "F:\\Emulatoren\\data\\Synopsis\\thegamesdb - halo.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\thegamesdb - parserConfig.xml"


from descriptionparserfactory import *
descParser = DescriptionParserFactory.getParser(parseInstruction)


results = descParser.parseDescription(str(descFile))
for result in results:
	print result

#timestamp1 = time.clock()

#descParser.prepareScan(descFile, parseInstruction)
#for result in descParser.scanDescription(descFile, parseInstruction):
#	print result


#timestamp2 = time.clock()
#diff = (timestamp2 - timestamp1) * 1000		
#print "parsed in %d ms" % (diff)

