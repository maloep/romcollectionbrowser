
import os, sys
import time

"""
file = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\userdata\\addon_data\\script.games.rom.collection.browser\\config.xml"
modifyTime = os.path.getmtime(file)

print modifyTime

print time.ctime(0)
"""


print "start parsing"

BASE_RESOURCE_PATH = os.path.join( os.getcwd())
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "pyparsing" ) )

from descriptionparser import *
descParser = DescriptionParser()

#descFile = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\SMSGG.txt"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\_parserConfig.xml"

descFile = "F:\\Emulatoren\\data\\Synopsis\\Sega 32 - After Burner.xml"
parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\xmlParserConfig.xml"

results = descParser.parseDescription(descFile, parseInstruction)

#for result in results:
#	print result.asDict()

print len(results)
