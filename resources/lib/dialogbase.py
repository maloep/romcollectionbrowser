from builtins import str
from builtins import range
import xbmc, xbmcgui
import os

import util
from util import *

ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)
CONTROL_BUTTON_EXIT = 5101


class DialogBase(xbmcgui.WindowXMLDialog):

    def getControlById(self, controlId):
        try:
            control = self.getControl(controlId)
        except RuntimeError:
            return None

        return control

    def addItemsToList(self, controlId, options):
        Logutil.log('addItemsToList: ID = ' + str(controlId) + ', values = ' + str(options), util.LOG_LEVEL_INFO)

        control = self.getControlById(controlId)
        control.setVisible(1)
        control.reset()

        items = []
        for option in options:
            items.append(xbmcgui.ListItem(option))

        control.addItems(items)

    def editTextProperty(self, controlId, name):
        control = self.getControlById(controlId)
        textValue = util.getLabel(control)

        keyboard = xbmc.Keyboard()
        keyboard.setHeading(util.localize(32132) % name)
        keyboard.setDefault(textValue)
        keyboard.doModal()
        if keyboard.isConfirmed():
            textValue = keyboard.getText()

        util.setLabel(textValue, control)

        return textValue

    def editPathWithFileMask(self, controlId, enterString, controlIdFilemask):

        dialog = xbmcgui.Dialog()

        #get new value
        pathValue = dialog.browse(0, enterString, 'files')

        control = self.getControlById(controlId)

        util.setLabel(pathValue, control)

        control = self.getControlById(controlIdFilemask)
        filemask = util.getLabel(control)
        pathComplete = os.path.join(pathValue, filemask.strip())

        return pathComplete

    def editFilemask(self, controlId, enterString, pathComplete):
        control = self.getControlById(controlId)
        filemask = util.getLabel(control)

        keyboard = xbmc.Keyboard()
        keyboard.setHeading(util.localize(32132) % enterString)
        keyboard.setDefault(filemask)
        keyboard.doModal()
        if keyboard.isConfirmed():
            filemask = keyboard.getText()

        util.setLabel(filemask, control)

        pathParts = os.path.split(pathComplete)
        path = pathParts[0]
        pathComplete = os.path.join(path, filemask.strip())

        return pathComplete

    def selectScrapersInList(self, sitesInRomCollection, controlId):

        Logutil.log('selectScrapersInList', util.LOG_LEVEL_INFO)

        for site in sitesInRomCollection:
            if site.default:
                self.selectItemInList(site.name, controlId)
                break

    def selectItemInList(self, itemName, controlId):

        Logutil.log('selectItemInList', util.LOG_LEVEL_INFO)

        control = self.getControlById(controlId)

        for i in range(0, control.size()):
            item = control.getListItem(i)
            if item.getLabel() == itemName:
                control.selectItem(i)
                break
