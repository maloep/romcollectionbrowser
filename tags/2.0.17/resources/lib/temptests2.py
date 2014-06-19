
import os, sys

'''
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
'''


from emulatorautoconfig.autoconfig import EmulatorAutoconfig


config = EmulatorAutoconfig('C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\script.games.rom.collection.browser.dev\\resources\\emu_autoconfig.xml')

'''
config.readXml()
for op in config.operatingSystems:
    print op.name
    for platform in op.platforms:
        print platform.name
        for alias in platform.aliases:
            print alias
        for emulator in platform.emulators:
            print emulator.name
            print emulator.emuCmd
            print emulator.emuParams
            for detection in emulator.detectionMethods:
                print detection.name
                print detection.command
''' 


emulators = config.findEmulators('Android', 'Super Nintendo', True);

if(emulators):
    for emulator in emulators:
        print emulator.name
        print emulator.os
        print emulator.platform
        print emulator.emuCmd
        print emulator.emuParams
        print emulator.detectionMethods
        print emulator.isInstalled

