
import os, sys

sys.path.append( os.path.join( os.path.join( os.getcwd(), ".." ), "platform_libraries", "win32") )


from elementtree.ElementTree import *

databasedir = os.path.join( os.getcwd(), 'TestDataBase')
configFile = os.path.join(databasedir, 'config.xml')	

if(os.path.isfile(configFile)):					
	tree = ElementTree().parse(configFile)
	
	value = tree.findtext('*/RomCollection/name')
	print str(value)
	
	elements = tree.findall('*/RomCollection/name')
	for element in elements:
		print element.text
		
	value = tree.findtext('Consoles/Console/name')
	print str(value)
	
	#this does not work
	#value = tree.find('Consoles/Console[./name=\'Super Nintendo\']')
	#print str(value)
		
	value = tree.findtext('*/RomCollection/mediaPath[@type]')
	print str(value)
	
	value = tree.findtext('*/RomCollection/mediaPath[@type=\'cover\']')
	print str(value)
	

	