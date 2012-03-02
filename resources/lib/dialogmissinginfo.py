import xbmc, xbmcgui

import os

import util, config, dialogbase
from util import *

ACTION_CANCEL_DIALOG = (9,10,51,92,110)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_SAVE = 6000
CONTROL_BUTTON_CANCEL = 6010

CONTROL_LIST_SHOWHIDEMISSING = 5200

CONTROL_LABEL_ARTWORK_ORGROUP = 5220
CONTROL_BUTTON_ADD_ARTWORK_ORGROUP = 5230
CONTROL_BUTTON_REMOVE_ARTWORK_ORGROUP = 5240
CONTROL_LABEL_ARTWORK_ANDGROUP = 5250
CONTROL_BUTTON_ADD_ARTWORK_ANDGROUP = 5260
CONTROL_BUTTON_REMOVE_ARTWORK_ANDGROUP = 5270

CONTROL_LABEL_INFO_ORGROUP = 5280
CONTROL_BUTTON_ADD_INFO_ORGROUP = 5290
CONTROL_BUTTON_REMOVE_INFO_ORGROUP = 5300
CONTROL_LABEL_INFO_ANDGROUP = 5310
CONTROL_BUTTON_ADD_INFO_ANDGROUP = 5320
CONTROL_BUTTON_REMOVE_INFO_ANDGROUP = 5330



class MissingInfoDialog(dialogbase.DialogBaseEdit):
	
	artworkAndList = []
	artworkOrList = []
	infoAndList = []
	infoOrList = []
	
	def __init__(self, *args, **kwargs):
		Logutil.log('init dialog missing info', util.LOG_LEVEL_INFO)
		
		self.gui = kwargs[ "gui" ]
		
		self.doModal()
	
	
	def onInit(self):
		Logutil.log('onInit dialog missing info', util.LOG_LEVEL_INFO)
		
		self.artworkAndList = []
		self.artworkOrList = []
		self.infoAndList = []
		self.infoOrList = []
		
		Logutil.log('add show/hide missing info options', util.LOG_LEVEL_INFO)
		showHideOptions = ['Ignore filter', 'Show only games with missing items', 'Hide games with missing items']
		self.addItemsToList(CONTROL_LIST_SHOWHIDEMISSING, showHideOptions)
		
		
	def onAction(self, action):		
		if (action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
		
	
	def onClick(self, controlID):
		
		Logutil.log('onClick', util.LOG_LEVEL_INFO)
		
		if (controlID == CONTROL_BUTTON_EXIT): # Close window button
			Logutil.log('close', util.LOG_LEVEL_INFO)
			self.close()
		elif (controlID == CONTROL_BUTTON_ADD_ARTWORK_ORGROUP):
			Logutil.log('Add artwork or', util.LOG_LEVEL_INFO)
			self.artworkOrList = self.addItemToMissingArtworkList(self.artworkOrList, CONTROL_LABEL_ARTWORK_ORGROUP)			
			
		elif (controlID == CONTROL_BUTTON_REMOVE_ARTWORK_ORGROUP):
			Logutil.log('Remove artwork or', util.LOG_LEVEL_INFO)
			self.artworkOrList = self.removeFromMissingArtworkList(self.artworkOrList, CONTROL_LABEL_ARTWORK_ORGROUP)
			
		elif (controlID == CONTROL_BUTTON_ADD_ARTWORK_ANDGROUP):
			Logutil.log('Add artwork and', util.LOG_LEVEL_INFO)
			self.artworkAndList = self.addItemToMissingArtworkList(self.artworkAndList, CONTROL_LABEL_ARTWORK_ANDGROUP)

		elif (controlID == CONTROL_BUTTON_REMOVE_ARTWORK_ANDGROUP):
			Logutil.log('Remove artwork and', util.LOG_LEVEL_INFO)
			self.artworkAndList = self.removeFromMissingArtworkList(self.artworkAndList, CONTROL_LABEL_ARTWORK_ANDGROUP)
			
		#Save
		elif (controlID == CONTROL_BUTTON_SAVE):			
			Logutil.log('save', util.LOG_LEVEL_INFO)
			self.close()
		
		#Cancel
		elif (controlID == CONTROL_BUTTON_CANCEL):
			Logutil.log('cancel', util.LOG_LEVEL_INFO)
			self.close()
						
	
	def onFocus(self, controlId):
		pass
	
	
	def addItemToMissingArtworkList(self, inList, labelId):
		tempList = []
		for romCollection in self.gui.config.romCollections.values():
			for mediaPath in romCollection.mediaPaths:
				if(not mediaPath.fileType.name in tempList and not mediaPath.fileType.name in inList):
					tempList.append(mediaPath.fileType.name)
		
		dialog = xbmcgui.Dialog()
		index = dialog.select('Select Artwork type', tempList)
		del dialog
		if(index == -1):
			return inList
		
		inList.append(tempList[index])
		label = self.getControlById(labelId)
		label.setLabel(', '.join(inList))
		
		return inList
	
	
	def removeFromMissingArtworkList(self, inList, labelId):
		dialog = xbmcgui.Dialog()
		artworkIndex = dialog.select('Remove Artwork type', inList)
		del dialog
		if(artworkIndex == -1):
			return inList
		inList.remove(inList[artworkIndex])
		label = self.getControlById(labelId)
		label.setLabel(', '.join(inList))
		
		return inList