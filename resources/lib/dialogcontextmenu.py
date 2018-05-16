import xbmcgui

import util, nfowriter, wizardconfigxml, helper
import dialogeditromcollection, dialogdeleteromcollection, dialogupdateartwork
from nfowriter import *
from gamedatabase import *
from util import *
from config import *
from util import Logutil as log

ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)
CONTROL_BUTTON_SETFAVORITE_GAME = 5118
CONTROL_BUTTON_SETFAVORITE_SELECTION = 5119


class ContextMenuDialog(xbmcgui.WindowXMLDialog):
    selectedGame = None
    gameRow = None

    def __init__(self, *args, **kwargs):
        # Don't put GUI sensitive stuff here (as the xml hasn't been read yet)
        log.info("init ContextMenu")

        self.gui = kwargs["gui"]

        self.doModal()

    def onInit(self):
        log.info("onInit ContextMenu")

        self.selectedGame = self.gui.getSelectedItem()

        # Set mark favorite text
        if self.selectedGame is not None:
            if self.selectedGame.getProperty('isfavorite') == '1':
                buttonMarkFavorite = self.getControlById(CONTROL_BUTTON_SETFAVORITE_GAME)
                if buttonMarkFavorite is not None:
                    buttonMarkFavorite.setLabel(util.localize(32133))
                buttonMarkFavorite = self.getControlById(CONTROL_BUTTON_SETFAVORITE_SELECTION)
                if buttonMarkFavorite is not None:
                    buttonMarkFavorite.setLabel(util.localize(32134))

        # Hide Set Gameclient option
        if not helper.isRetroPlayerSupported():
            control = self.getControlById(5224)
            control.setVisible(False)
            control.setEnabled(False)

    def onAction(self, action):
        if action.getId() in ACTION_CANCEL_DIALOG:
            self.close()

    def onClick(self, controlId):
        if controlId == 5101:  # Close window button
            self.close()
        elif controlId == 5110:  # Import games
            self.close()
            self.gui.updateDB()
        elif controlId == 5125:  # Update artwork cache
            self.close()
            dialog = dialogupdateartwork.UpdateArtworkDialog("script-RCB-updateartwork.xml",
                                                      util.getAddonInstallPath(),
                                                      "Default", "720p", gui=self.gui)
            del dialog

        elif controlId == 5121:  # Rescrape single games
            self.close()

            if self.selectedGame is None:
                xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32013), util.localize(32014))
                return

            romCollectionId = self.selectedGame.getProperty('romCollectionId')
            romCollection = self.gui.config.romCollections[str(romCollectionId)]
            files = File(self.gui.gdb).getRomsByGameId(self.selectedGame.getProperty('gameId'))
            filename = files[0][0]
            romCollection.romPaths = (filename,)

            romCollections = {}
            romCollections[romCollection.id] = romCollection

            self.gui.rescrapeGames(romCollections)

        elif controlId == 5122:  # Rescrape selection
            self.close()

            romCollections = {}
            listSize = self.gui.getListSize()
            for i in range(0, listSize):
                listItem = self.gui.getListItem(i)

                romCollectionId = listItem.getProperty('romCollectionId')

                try:
                    romCollection = romCollections[str(romCollectionId)]
                except:
                    romCollection = self.gui.config.romCollections[str(romCollectionId)]
                    romCollection.romPaths = []

                files = File(self.gui.gdb).getRomsByGameId(listItem.getProperty('gameId'))
                try:
                    filename = files[0][0]
                    romCollection.romPaths.append(filename)
                    romCollections[romCollection.id] = romCollection
                except:
                    log.info("Error getting filename for romCollectionId: {0}".format(romCollectionId))

            self.gui.rescrapeGames(romCollections)

        #self.gui.updateDB()
        elif controlId == 5111:  # Add Rom Collection
            self.close()
            statusOk, errorMsg = wizardconfigxml.ConfigXmlWizard().addRomCollection(self.gui.config)
            if statusOk is False:
                xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32001), errorMsg)
                log.info("Error updating config.xml: {0}".format(errorMsg))
                return

            #update self.config
            statusOk, errorMsg = self.gui.config.readXml()
            if statusOk is False:
                xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32002), errorMsg)
                log.info("Error reading config.xml: {0}".format(errorMsg))
                return

            #import Games
            self.gui.updateDB()

        elif controlId == 5112:  # Edit Rom Collection
            self.close()
            constructorParam = "720p"
            try:
                editRCdialog = dialogeditromcollection.EditRomCollectionDialog("script-RCB-editromcollection.xml",
                                                                               util.getAddonInstallPath(),
                                                                               util.getConfiguredSkin(),
                                                                               constructorParam, gui=self.gui)
            except:
                editRCdialog = dialogeditromcollection.EditRomCollectionDialog("script-RCB-editromcollection.xml",
                                                                               util.getAddonInstallPath(),
                                                                               "Default",
                                                                               constructorParam, gui=self.gui)
            del editRCdialog

            self.gui.config = Config(None)
            self.gui.config.readXml()

        elif controlId == 5113:  # Edit Game Command
            self.close()

            if self.selectedGame == None:
                xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32015), util.localize(32014))
                return

            origCommand = self.selectedGame.getProperty('gameCmd')
            command = xbmcgui.Dialog().input(util.localize(32135), defaultt=origCommand, type=xbmcgui.INPUT_ALPHANUM)

            if command != origCommand:
                log.info("Updating game '{0}' with command '{1}'".format(self.selectedGame.getLabel(), command))
                Game(self.gui.gdb).update(('gameCmd',), (command,), self.selectedGame.getProperty('gameId'), True)
                self.gui.gdb.commit()

        elif controlId == 5118:  # (Un)Mark as Favorite
            self.close()

            if self.selectedGame is None:
                xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32016), util.localize(32014))
                return

            isFavorite = '1'
            if self.selectedGame.getProperty('isfavorite') == '1':
                isFavorite = '0'

            log.info("Updating game '{0}' set isFavorite = {1}".format(self.selectedGame.getLabel(), isFavorite))
            Game(self.gui.gdb).update(('isfavorite',), (isFavorite,), self.selectedGame.getProperty('gameId'), True)
            self.gui.gdb.commit()

            if isFavorite == '0':
                isFavorite = ''
            self.selectedGame.setProperty('isfavorite', str(isFavorite))

        elif controlId == 5119:  # (Un)Mark as Favorite
            self.close()

            if self.selectedGame is None:
                xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32016), util.localize(32014))
                return

            isFavorite = '1'
            if self.selectedGame.getProperty('isfavorite') == '1':
                isFavorite = '0'

            listSize = self.gui.getListSize()
            for i in range(0, listSize):
                listItem = self.gui.getListItem(i)

                log.info("Updating game '{0}' set isfavorite = {1}".format(listItem.getLabel(), isFavorite))
                Game(self.gui.gdb).update(('isfavorite',), (isFavorite,), listItem.getProperty('gameId'), True)
                listItem.setProperty('isfavorite', str(isFavorite))
            self.gui.gdb.commit()

            #HACK: removing favorites does not update the UI. So do it manually.
            if isFavorite == 0:
                self.gui.loadViewState()

        elif controlId == 5120:  # Export nfo files
            self.close()
            nfowriter.NfoWriter().exportLibrary(self.gui.gdb, self.gui.config.romCollections)

        elif controlId == 5114:  # Delete Rom
            self.close()

            pos = self.gui.getCurrentListPosition()
            if pos == -1:
                xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32017), util.localize(32018))
                return
            dialog = xbmcgui.Dialog()
            if dialog.yesno(util.localize(32510), util.localize(32136)):
                gameID = self.selectedGame.getProperty('gameId')
                self.gui.deleteGame(gameID)
                self.gui.showGames()
                if pos > 0:
                    pos = pos - 1
                    self.gui.setFilterSelection(self.gui.CONTROL_GAMES_GROUP_START, pos)
                else:
                    self.gui.setFilterSelection(self.gui.CONTROL_GAMES_GROUP_START, 0)

        elif controlId == 5115:  # Remove Rom Collection
            self.close()

            constructorParam = "720p"
            try:
                removeRCDialog = dialogdeleteromcollection.RemoveRCDialog("script-RCB-removeRC.xml",
                                                                          util.getAddonInstallPath(),
                                                                          util.getConfiguredSkin(),
                                                                          constructorParam,
                                                                          gui=self.gui)
            except:
                removeRCDialog = dialogdeleteromcollection.RemoveRCDialog("script-RCB-removeRC.xml",
                                                                          util.getAddonInstallPath(),
                                                                          "Default",
                                                                          constructorParam, gui=self.gui)
            rDelStat = removeRCDialog.getDeleteStatus()
            if rDelStat:
                selectedRCId = removeRCDialog.getSelectedRCId()
                rcDelStat = removeRCDialog.getRCDeleteStatus()
                self.gui.deleteRCGames(selectedRCId, rcDelStat, rDelStat)
                del removeRCDialog

        elif controlId == 5116:  # Clean DB
            self.close()
            self.gui.cleanDB()

        elif controlId == 5223:  # Open Settings
            self.close()
            self.gui.Settings.openSettings()

        elif controlId == 5224:  # Set gameclient
            self.close()

            if not helper.isRetroPlayerSupported():
                log.info("This RetroPlayer branch does not support selecting gameclients.")
                return

            if self.selectedGame is None or self.gameRow is None:
                xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32015), util.localize(32014))
                return

            #HACK: use alternateGameCmd to store gameclient information
            origGameClient = self.selectedGame.getProperty('alternateGameCmd')
            gameclient = ''

            romCollectionId = self.selectedGame.getProperty('romCollectionId')
            romCollection = self.gui.config.romCollections[str(romCollectionId)]

            success, selectedcore = helper.selectlibretrocore(romCollection.name)
            if success:
                gameclient = selectedcore
            else:
                log.info("No libretro core was chosen. Won't update game command.")
                return

            if gameclient != origGameClient:
                log.info("Updating game '{0}' with gameclient '{1}'".format(self.selectedGame.getLabel(), gameclient))
                Game(self.gui.gdb).update(('alternateGameCmd',), (gameclient,), self.selectedGame.getProperty('gameId'),
                                          True)
                self.gui.gdb.commit()

    def onFocus(self, controlId):
        pass

    def getControlById(self, controlId):
        try:
            control = self.getControl(controlId)
        except Exception:
            return None

        return control
