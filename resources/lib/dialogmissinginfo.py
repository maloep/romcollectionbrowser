import xbmc, xbmcgui

import os

import util, config, dialogbase
from util import *

ACTION_CANCEL_DIALOG = (9,10,51,92,110)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_SAVE = 6000
CONTROL_BUTTON_CANCEL = 6010

CONTROL_LIST_SHOWHIDEMISSING = 5200

CONTROL_LIST_ROMCOLLECTIONS = 5210
CONTROL_BUTTON_RC_DOWN = 5211
CONTROL_BUTTON_RC_UP = 5212


class MissingInfoDialog(dialogbase.DialogBaseEdit):
	
	romCollections = None
	
	def __init__(self, *args, **kwargs):
		Logutil.log('init dialog missing info', util.LOG_LEVEL_INFO)
		
		self.gui = kwargs[ "gui" ]
		self.romCollections = self.gui.config.romCollections
		
		self.doModal()
	
	
	def onInit(self):
		Logutil.log('onInit dialog missing info', util.LOG_LEVEL_INFO)
		
		Logutil.log('add show/hide missing info options', util.LOG_LEVEL_INFO)
		showHideOptions = ['Ignore filter', 'Show only games with missing items', 'Hide games with missing items']
		self.addItemsToList(CONTROL_LIST_SHOWHIDEMISSING, showHideOptions)
		
		#Rom Collections
		Logutil.log('build rom collection list', util.LOG_LEVEL_INFO)
		romCollectionList = []
		for rcId in self.romCollections.keys():
			romCollection = self.romCollections[rcId]
			romCollectionList.append(romCollection.name)
		self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, romCollectionList)
		
		
	def onAction(self, action):		
		if (action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
		
	
	def onClick(self, controlID):
		
		Logutil.log('onClick', util.LOG_LEVEL_INFO)
		
		if (controlID == CONTROL_BUTTON_EXIT): # Close window button
			Logutil.log('close', util.LOG_LEVEL_INFO)
			self.close()
		#OK
		elif (controlID == CONTROL_BUTTON_SAVE):			
			Logutil.log('save', util.LOG_LEVEL_INFO)
			self.close()
		
		#Cancel
		elif (controlID == CONTROL_BUTTON_CANCEL):
			Logutil.log('cancel', util.LOG_LEVEL_INFO)
			self.close()
						
	
	def onFocus(self, controlId):
		pass
	