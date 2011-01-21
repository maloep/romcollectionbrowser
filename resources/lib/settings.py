

import os, sys
import xbmc

from elementtree.ElementTree import *

from gamedatabase import *
from util import *


class RCBSettingsXml:
	
	configxmls = {}
	
	
	def getSetting(self, source, key):
		
		if(source == 'DB'):
			#add db logic here
			pass
		elif(source == 'settings.xml'):
			#add xbmc settings here
			pass		
		else:
			
			try:
				configfile = self.configxmls[source]
			except:
				pathToXml = os.path.join(util.RCBHOME, 'resources', source)
				configfile = self.openXmlFile(pathToXml)
				self.configxmls[source] = configfile 
			
			
	
	def openXmlFile(self, pathToXml):
		
		if(os.path.isfile(pathToXml)):		
			return ElementTree().parse(pathToXml)
		else:
			Logutil.log('File %s does not exist.' %(pathToXml), util.LOG_LEVEL_ERROR)
			return None
			
			
			