"""
    This is a dummy file for testing and debugging XBMC plugins from the
    command line. The file contains definitions for the functions found
    in xbmc, xbmcgui and xbmcplugin built in modules
"""

import os, sys

#Addon = Addon()


class Addon:
	
	def __init__(self, *args, **kwargs):
		pass

	def getAddonInfo(self, key):
		
		print 'getAddonInfo called with key: ' +str(key)
		
		if(key == 'path'):
			basepath = os.getcwd()
			path = os.path.join(basepath, "..\..")
			print 'path = ' +str(path)
			return path
		
		return 'dummy'

