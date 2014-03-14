
import os, sys
BASE_RESOURCE_PATH = os.path.join(os.getcwd())
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "pyparsing"))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "pyscraper"))
from descriptionparserfactory import DescriptionParserFactory
from descriptionparserfactory import *


descFile = "E:\\XBMC\\RCB\\develop\\scraper\\offline\\mame\\astrowar.xml"
parseInstruction = "E:\\XBMC\\RCB\\develop\\scraper\\offline\\mame\\parserconfig.xml"

descParser = DescriptionParserFactory.getParser(parseInstruction)

results = descParser.parseDescription(str(descFile), 'iso-8859-15')
for result in results:
    print result
    
print len(results)