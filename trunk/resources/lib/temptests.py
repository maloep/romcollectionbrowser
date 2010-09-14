
import os, sys
import time
from descriptionparserfactory import DescriptionParserFactory


print "start parsing"

BASE_RESOURCE_PATH = os.path.join( os.getcwd())
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "pyparsing" ) )

#descFile = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\SMSGG.txt"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\_parserConfig.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\Sega 32 - After Burner.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\xmlParserConfig.xml"

descFile = "F:\\Emulatoren\\data\\Synopsis\\SEGA 32 - complete.xml"
parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\Access - parserConfig.xml"

from descriptionparserfactory import *
descParser = DescriptionParserFactory.getParser(parseInstruction)

#result = descParser.parseDescription(descFile)
#print result

descParser.prepareScan(descFile, parseInstruction)
for result in descParser.scanDescription(descFile, parseInstruction):
	print result


