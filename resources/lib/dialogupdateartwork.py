from __future__ import absolute_import
from builtins import str
from config import *
from util import *
import util
import helper
import dialogprogress
import xbmc
from dialogbase import DialogBase
from artworkupdater import ArtworkUpdater


ACTION_MOVEMENT_UP = (3,)
ACTION_MOVEMENT_DOWN = (4,)
ACTION_MOVEMENT = (3, 4, 5, 6, 159, 160)

ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_OK = 5300
CONTROL_BUTTON_CANCEL = 5310

CONTROL_LIST_ROMCOLLECTIONS = 5210
CONTROL_LIST_ARTWORKTYPES = 5270

CONTROL_BUTTON_RC_DOWN = 5211
CONTROL_BUTTON_RC_UP = 5212

CONTROL_BUTTON_SCRAPER_DOWN = 5271


class UpdateArtworkDialog(DialogBase):
    def __init__(self, *args, **kwargs):
        # Don't put GUI sensitive stuff here (as the xml hasn't been read yet)
        Logutil.log('init ImportOptions', util.LOG_LEVEL_INFO)

        self.gui = kwargs["gui"]
        self.doModal()

    def onInit(self):
        log.info('onInit ImportOptions')
        # 32120 = All
        romCollectionList = [util.localize(32120)] + self.gui.config.getRomCollectionNames()
        log.debug("Adding list of RC names: {0}".format(romCollectionList))
        self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, romCollectionList)

        artworktypes = []
        for filetype in self.gui.config.get_filetypes():
            artworktypes.append(filetype.name)

        artworktypes = [util.localize(32120)] +sorted(artworktypes)

        self.addItemsToList(CONTROL_LIST_ARTWORKTYPES, sorted(artworktypes))
        self.selectItemInList(util.localize(32120), CONTROL_LIST_ARTWORKTYPES)

    def onAction(self, action):
        if action.getId() in ACTION_CANCEL_DIALOG:
            self.close()

    def onClick(self, controlID):
        if controlID == CONTROL_BUTTON_EXIT:  # Close window button
            self.close()
        elif controlID == CONTROL_BUTTON_OK:
            self.close()
            self.update_artwork()
        elif controlID == CONTROL_BUTTON_CANCEL:
            self.close()
        elif controlID in (CONTROL_BUTTON_RC_DOWN, CONTROL_BUTTON_RC_UP):  # Rom Collection list

            # HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
            xbmc.sleep(util.WAITTIME_UPDATECONTROLS)

            control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
            selectedRomCollectionName = str(control.getSelectedItem().getLabel())

            #32120 = All
            if selectedRomCollectionName == util.localize(32120):
                artworktypes = []
                for filetype in self.gui.config.get_filetypes():
                    artworktypes.append(filetype.name)
                artworktypes = [util.localize(32120)] + sorted(artworktypes)

                self.addItemsToList(CONTROL_LIST_ARTWORKTYPES, sorted(artworktypes))
                self.selectItemInList(util.localize(32120), CONTROL_LIST_ARTWORKTYPES)
            else:
                artworktypes = []
                rom_collection = self.gui.config.getRomCollectionByName(selectedRomCollectionName)
                for mediaPath in rom_collection.mediaPaths:
                    artworktypes.append(mediaPath.fileType.name)
                artworktypes = [util.localize(32120)] + sorted(artworktypes)

                self.addItemsToList(CONTROL_LIST_ARTWORKTYPES, sorted(artworktypes))
                self.selectItemInList(util.localize(32120), CONTROL_LIST_ARTWORKTYPES)

    def update_artwork(self):
        log.info('update_artwork')

        control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
        selected_romcollection_name = control.getSelectedItem().getLabel()
        romcollection_id = 0
        #32120 = All
        if selected_romcollection_name != util.localize(32120):
            romcollection = self.gui.config.getRomCollectionByName(selected_romcollection_name)
            romcollection_id = romcollection.id

        control = self.getControlById(CONTROL_LIST_ARTWORKTYPES)
        selected_filetype_name = control.getSelectedItem().getLabel()
        filetype_id = 0
        #32120 = All
        if selected_filetype_name != util.localize(32120):
            filetype, errormessage = self.gui.config.get_filetype_by_name(selected_filetype_name, self.gui.config.tree)
            filetype_id = filetype.id

        progressDialog = dialogprogress.ProgressDialogGUI()
        #32950 = Scan Artwork
        progressDialog.create(util.localize(32950))

        updater = ArtworkUpdater(progressDialog, self.gui.gdb, self.gui.config)
        updater.update_artwork_cache(romcollection_id, filetype_id)
