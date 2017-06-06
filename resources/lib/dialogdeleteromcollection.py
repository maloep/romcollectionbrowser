import xbmc
import xbmcgui

from util import Logutil as log
from configxmlwriter import *

ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_SAVE = 6000
CONTROL_BUTTON_CANCEL = 6010

CONTROL_LIST_ROMCOLLECTIONS = 5410
CONTROL_BUTTON_RC_DOWN = 5411
CONTROL_BUTTON_RC_UP = 5412

CONTROL_LIST_DELETEOPTIONS = 5490
CONTROL_BUTTON_DEL_DOWN = 5491
CONTROL_BUTTON_DEL_UP = 5492


class RemoveRCDialog(xbmcgui.WindowXMLDialog):
		
	selectedControlId = 0
	selectedRomCollection = None
	romCollections = None
	romDelete = 'RCollection'
	_deleteCollection = False
	_rcDeleteCollection = False

	def _getRomCollectionNames(self):
		rcname_list = []
		for k, v in self.romCollections.items():
			rcname_list.append(v.name)

		log.debug('List of rom collection names: {0}'.format(rcname_list))
		return rcname_list

	def _getRomCollectionByName(self, name):
		for k, v in self.romCollections.items():
			if v.name == name:
				log.debug('Found rom collection by name {0}: {1}'.format(name, v))
				return v
		log.debug('Did not find rom collection for name {0}'.format(name))
		return None

	def __init__(self, *args, **kwargs):
		log.info('init Edit RC Basic')
		
		self.gui = kwargs["gui"]
		self.romCollections = self.gui.config.romCollections
		self.doModal()

	def onInit(self):
		log.info('onInit Remove Rom Collection')

		# Rom Collections
		log.info('build rom collection list')

		self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, self._getRomCollectionNames())
		
		# Delete Options
		rcDeleteOptions = [util.localize(32137), util.localize(32138)]
		self.addItemsToList(CONTROL_LIST_DELETEOPTIONS, rcDeleteOptions, properties=['RCollection', 'Roms'])
		self.updateControls()
		
	def onAction(self, action):		
		if (action.getId() in ACTION_CANCEL_DIALOG):
			self.close()
	
	def onClick(self, controlID):
		
		log.info('onClick')

		if controlID == CONTROL_BUTTON_EXIT:
			# Close window button
			log.info('Close')
			self.close()
		elif controlID == CONTROL_BUTTON_CANCEL:
			# Cancel button
			self.close()
		elif controlID == CONTROL_BUTTON_SAVE:
			# OK
			log.info('Save')

			# Store selectedRomCollection
			if self.selectedRomCollection is not None:
				# Code to Remove Roms
				log.info('Removing Roms')
				self._setDeleteStatus(True)
				# Code to Remove Collection
				if self.romDelete == 'RCollection':
					self._setRCDeleteStatus(True)
					Logutil.log('Removing Rom Collection', util.LOG_LEVEL_INFO)
					configWriterRCDel = ConfigXmlWriter(False)
					RCName = str(self.selectedRomCollection.name)
					success, message = configWriterRCDel.removeRomCollection(RCName)
					if success is False:
						log.error(message)
						xbmcgui.Dialog().ok(util.localize(32019), util.localize(32020))
			log.info('Click Close')
			self.close()

		elif self.selectedControlId in (CONTROL_BUTTON_RC_DOWN, CONTROL_BUTTON_RC_UP):
			# Changing selection in Rom Collection list
			if self.selectedRomCollection is not None:
				# Store previous selectedRomCollections state
				self.romCollections[self.selectedRomCollection.id] = self.selectedRomCollection
			
			# HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
			xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
			self.updateControls()
		elif self.selectedControlId in (CONTROL_BUTTON_DEL_DOWN, CONTROL_BUTTON_DEL_UP):
			# Changing selection in Delete Option list
			control = self.getControlById(CONTROL_LIST_DELETEOPTIONS)
			selectedDeleteOption = str(control.getSelectedItem().getLabel2())
			log.info('selectedDeleteOption = {0}'.format(selectedDeleteOption))
			self.romDelete = selectedDeleteOption
	
	def onFocus(self, controlId):
		self.selectedControlId = controlId
	
	def updateControls(self):
		
		log.info('updateControls')
		
		control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
		selectedRomCollectionName = str(control.getSelectedItem().getLabel())

		self.selectedRomCollection = self._getRomCollectionByName(selectedRomCollectionName)
	
	def getSelectedRCId(self):
		return self.selectedRomCollection.id

	def getControlById(self, controlId):
		try:
			control = self.getControl(controlId)
		except:
			return None
		
		return control
	
	def addItemsToList(self, controlId, options, properties=None):
		Logutil.log('addItemsToList', util.LOG_LEVEL_INFO)
		
		control = self.getControlById(controlId)
		control.setVisible(1)
		control.reset()
				
		items = []		
		for i in range(0, len(options)):
			option = options[i]
			p = ''
			if properties:
				p = properties[i]
			items.append(xbmcgui.ListItem(option, p, '', ''))
							
		control.addItems(items)

	def selectItemInList(self, options, itemName, controlId):				
		
		log.info('selectItemInList')
		
		for i in range(0, len(options)):			
			option = options[i]
			if itemName == option:
				control = self.getControlById(controlId)
				control.selectItem(i)
				break

	def getDeleteStatus(self):
		return self._deleteCollection

	def _setDeleteStatus(self, status):
		self._deleteCollection = status
		
	def getRCDeleteStatus(self):
		return self._rcDeleteCollection

	def _setRCDeleteStatus(self, status):
		self._rcDeleteCollection = status
