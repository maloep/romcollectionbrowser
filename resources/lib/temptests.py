
import os, sys
import time
import urllib
import difflib
from descriptionparserfactory import DescriptionParserFactory

print "start parsing"

BASE_RESOURCE_PATH = os.path.join( os.getcwd())
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "pyparsing" ) )

env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
if env == 'Windows_NT':
	env = 'win32'
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "..", "platform_libraries", env ) )

import util 


#"http://thevideogamedb.com/API/GameDetail.aspx?apikey=Zx5m2Y9Ndj6B4XwTf83JyKz7r8WHt3i4&name=After%20burner"
#descFile = "http://thevideogamedb.com/API/GameDetail.aspx?apikey=Zx5m2Y9Ndj6B4XwTf83JyKz7r8WHt3i4&name=After%20burner"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\VideoGameDB - parserConfig.xml"

#descFile = "http://romcollectionbrowser.googlecode.com/svn/trunk/resources/lib/TestDataBase/Collection%20V3/description/synopsis.txt"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\gamedesc\\_parserConfig.xml"


#descFile = "http://www.mobygames.com/search/quick?game=Actraiser&p=15"
descFile = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\mobysearch - Actraiser.htm"
parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\01 - mobygames - gamesearch.xml"

#descFile = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\moby gameshot.htm"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\mobygames\\07 - mobygames - screenshots.xml"

#descFile = "http://thegamesdb.net/api/GetGame.php?name=Legend%20of%20zelda"
#descFile = "F:\\Emulatoren\\data\\Synopsis\\thegamesdb\\thegamesdb - legend of zelda.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\thegamesdb\\thegamesdb - parserConfig.xml"

#descFile = "http://api.giantbomb.com/search/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&query=Actraiser&resources=game&format=xml"
#descFile = "F:\\Emulatoren\\data\\Synopsis\\giantbomb\\Actraisersearch.xml"
#parseInstruction = "F:\\Emulatoren\\data\\Synopsis\\giantbomb\\giantbomb - parserConfig.xml"

from descriptionparserfactory import *
descParser = DescriptionParserFactory.getParser(parseInstruction)


results = descParser.parseDescription(str(descFile))
for result in results:
	print result
	print difflib.SequenceMatcher(None, 'ActRaiser', str(result['SearchKey'])).ratio()
	#print lev()	


#timestamp1 = time.clock()

#descParser.prepareScan(descFile, parseInstruction)
#for result in descParser.scanDescription(descFile, parseInstruction):
#	print result


#timestamp2 = time.clock()
#diff = (timestamp2 - timestamp1) * 1000		
#print "parsed in %d ms" % (diff)


"""
def lev(a, b):
    if not a: return len(b)
    if not b: return len(a)
    return min(lev(a[1:], b[1:])+(a[0] != b[0]), \
    lev(a[1:], b)+1, lev(a, b[1:])+1)
"""