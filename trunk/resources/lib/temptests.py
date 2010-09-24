
import os, sys
import time
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

descFile = "F:\\Emulatoren\\data\\Synopsis\\SEGA 32 - complete.xml"
parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\Access - parserConfig.xml"

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

#"http://www.mobygames.com/game/snes/actraiser-2"


"""
from pyparsing import *
fh = open(str(descFile), 'r')
fileAsString = fh.read()
fileAsString = fileAsString.decode('iso-8859-15')

grammar = SkipTo("img alt=\"SNES Front Cover\" border=\"0\" src=\"").setDebug()
grammar += Suppress("img alt=\"SNES Front Cover\" border=\"0\" src=\"").setDebug()
grammar += SkipTo("\"").setDebug()
results = grammar.parseString(fileAsString)

print results
"""


from descriptionparserfactory import *
descParser = DescriptionParserFactory.getParser(parseInstruction)

results = descParser.parseDescription(str(descFile))
for result in results:
	print result

#descParser.prepareScan(descFile, parseInstruction)
#for result in descParser.scanDescription(descFile, parseInstruction):
#	print result




