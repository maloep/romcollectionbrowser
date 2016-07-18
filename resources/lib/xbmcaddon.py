"""
	This is a dummy file for testing and debugging XBMC plugins from the
	command line. The file contains definitions for the functions found
	in xbmc, xbmcgui and xbmcplugin built in modules
"""

import os, sys
import xml.etree.ElementTree as ET
import xbmc
#Addon = Addon()

_settings = {'rcb_fuzzyFactor': '3', 
			'rcb_enableFullReimport': 'true',
			'rcb_createNfoWhileScraping': 'false',
			'rcb_overwriteWithNullvalues': 'false',
			'rcb_ignoreGamesWithoutDesc': 'false',
			'rcb_ignoreGamesWithoutArtwork': 'false'}

class Addon:

	stringsroot = None

	def __init__(self, *args, **kwargs):
		pass

	def getAddonInfo(self, key):
		
		print 'getAddonInfo called with key: ' +str(key)
		
		if (key == 'path'):
			basepath = os.getcwd()
			#path = os.path.join(basepath, "..\..")
			print 'path = ' +str(basepath)
			return basepath
		elif (key == 'version'):
			# This should match a XBMC version number
			return "13.0"
		else:
			print "{0}: Unexpected key: '{1}'".format (__file__, key)
			return 'dummy'


	def getLocalizedString(self, id ):
		if self.root is None:
			# FIXME TODO Hard-coded to English
			strings_file = os.path.join(os.path.dirname(__file__), '..', 'language', 'English', 'strings.xml')

			try:
				tree = ET.parse(strings_file)
				self.stringsroot = tree.getroot()
			except Exception as err:
				return "Unable to load strings from file {0}".format (strings_file)

		# Iterate through until we find the right string
		for string in self.stringsroot.iter('string'):
			if string.get('id') == str(id):
				return string.text

		# Return default value
		return "String not found: {0}".format (id)


	def getSetting(self, id):
		"""
			Returns the value of a setting as a string.
	
			id		: string - id of the setting that the module needs to access.
	
			*Note, You can use the above as a keyword.
	
			example:
				apikey = xbmcplugin.getSetting('apikey')
		"""
		global _settings
		if _settings.has_key(id):
			return _settings[id]

	def setSetting(self, id, val):
		global _settings
		_settings[id] = val

