
import os, sys
import time
from descriptionparserfactory import DescriptionParserFactory


print "start parsing"

BASE_RESOURCE_PATH = os.path.join( os.getcwd())
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "pyparsing" ) )

#descFile = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\SMSGG.txt"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\_parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\Sega 32 - After Burner.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\VideoGameDB - parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\SEGA 32 - complete.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\Access - parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\MAME v0.138.dat"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\MameDat - parserConfig.xml"

#descFile = "http://thevideogamedb.com/API/GameDetail.aspx?apikey=Zx5m2Y9Ndj6B4XwTf83JyKz7r8WHt3i4&crc=ed7648ac"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\VideoGameDB - parserConfig.xml"

descFile = "http://romcollectionbrowser.googlecode.com/svn/trunk/resources/lib/TestDataBase/Collection%20V3/description/synopsis.txt"
parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\_parserConfig.xml"

from descriptionparserfactory import *
descParser = DescriptionParserFactory.getParser(parseInstruction)

#result = descParser.parseDescription(descFile)
#print result

descParser.prepareScan(descFile, parseInstruction)
for result in descParser.scanDescription(descFile, parseInstruction):
	print result


