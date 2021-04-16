from __future__ import absolute_import
from builtins import str
from builtins import range
import xbmc, xbmcgui

import os

import util, helper, config
from util import *
from util import Logutil as log
from dialogbase import DialogBase
import dialogdeleteromcollection
from configxmlwriter import *
import wizardconfigxml
from emulatorautoconfig.autoconfig import EmulatorAutoconfig
from pyscraper.scraper import AbstractScraper

ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)

CONTROL_BUTTON_EXIT = 5101
CONTROL_BUTTON_SAVE = 6000
CONTROL_BUTTON_CANCEL = 6010
CONTROL_BUTTON_ADD_RC = 6020
CONTROL_BUTTON_REMOVE_RC = 6030

CONTROL_LIST_ROMCOLLECTIONS = 5210
CONTROL_BUTTON_RC_DOWN = 5211
CONTROL_BUTTON_RC_UP = 5212

# Import Games
CONTROL_BUTTON_ROMPATH = 5240
CONTROL_BUTTON_FILEMASK = 5250
CONTROL_BUTTON_IGNOREONSCAN = 5330
CONTROL_BUTTON_ALLOWUPDATE = 5400
CONTROL_BUTTON_MAXFOLDERDEPTH = 5410
CONTROL_BUTTON_DISKINDICATOR = 5420
CONTROL_BUTTON_USEFOLDERASGAMENAME = 5430

# Import Game data
CONTROL_LIST_DEFAULT_SCRAPER = 5290
CONTROL_LIST_OFFLINE_SCRAPER = 5570

#Artwork
CONTROL_LIST_MEDIATYPES = 5260
CONTROL_BUTTON_MEDIA_DOWN = 5261
CONTROL_BUTTON_MEDIA_UP = 5262
CONTROL_BUTTON_MEDIAPATH = 5270
CONTROL_BUTTON_MEDIAFILEMASK = 5280
CONTROL_BUTTON_REMOVEMEDIAPATH = 5490
CONTROL_BUTTON_ADDMEDIAPATH = 5500

# Browse Games
CONTROL_LIST_IMAGEPLACING_MAIN = 5320
CONTROL_LIST_IMAGEPLACING_INFO = 5340
CONTROL_BUTTON_AUTOPLAYVIDEO_MAIN = 5350
CONTROL_BUTTON_AUTOPLAYVIDEO_INFO = 5360

# Launch Games
CONTROL_BUTTON_USERETROPLAYER = 5540
CONTROL_BUTTON_GAMECLIENT = 5550

CONTROL_BUTTON_EMUCMD = 5220
CONTROL_BUTTON_PARAMS = 5230
CONTROL_BUTTON_USEEMUSOLO = 5440
CONTROL_BUTTON_USEPOPEN = 5530
CONTROL_BUTTON_DONTEXTRACTZIP = 5450
CONTROL_BUTTON_SAVESTATEPATH = 5460
CONTROL_BUTTON_SAVESTATEMASK = 5470
CONTROL_BUTTON_SAVESTATEPARAMS = 5480
CONTROL_BUTTON_PRECMD = 5510
CONTROL_BUTTON_POSTCMD = 5520
CONTROL_BUTTON_MAKELOCALCOPY = 5560


class EditRomCollectionDialog(DialogBase):
    selectedControlId = 0
    selectedRomCollection = None
    romCollections = None
    scraperSites = None

    # Mapping between widget ID and RomCollection attribute - buttons
    _control_buttons = [
        {'control': CONTROL_BUTTON_IGNOREONSCAN, 'value': 'ignoreOnScan'},
        {'control': CONTROL_BUTTON_ALLOWUPDATE, 'value': 'allowUpdate'},
        {'control': CONTROL_BUTTON_USEFOLDERASGAMENAME, 'value': 'useFoldernameAsGamename'},
        {'control': CONTROL_BUTTON_AUTOPLAYVIDEO_MAIN, 'value': 'autoplayVideoMain'},
        {'control': CONTROL_BUTTON_AUTOPLAYVIDEO_INFO, 'value': 'autoplayVideoInfo'},
        {'control': CONTROL_BUTTON_USERETROPLAYER, 'value': 'useBuiltinEmulator'},
        {'control': CONTROL_BUTTON_USEEMUSOLO, 'value': 'useEmuSolo'},
        {'control': CONTROL_BUTTON_USEPOPEN, 'value': 'usePopen'},
        {'control': CONTROL_BUTTON_DONTEXTRACTZIP, 'value': 'doNotExtractZipFiles'},
        {'control': CONTROL_BUTTON_MAKELOCALCOPY, 'value': 'makeLocalCopy'},
    ]

    # Mapping between widget ID and RomCollection attribute - labels
    _control_labels = [
        {'control': CONTROL_BUTTON_DISKINDICATOR, 'value': 'diskPrefix'},
        {'control': CONTROL_BUTTON_MAXFOLDERDEPTH, 'value': 'maxFolderDepth'},
        {'control': CONTROL_BUTTON_GAMECLIENT, 'value': 'gameclient'},
        {'control': CONTROL_BUTTON_EMUCMD, 'value': 'emulatorCmd'},
        {'control': CONTROL_BUTTON_PARAMS, 'value': 'emulatorParams'},
        {'control': CONTROL_BUTTON_SAVESTATEPATH, 'value': 'pathSaveState'},
        {'control': CONTROL_BUTTON_SAVESTATEMASK, 'value': 'maskSaveState'},
        {'control': CONTROL_BUTTON_SAVESTATEPARAMS, 'value': 'saveStateParams'},
        {'control': CONTROL_BUTTON_PRECMD, 'value': 'preCmd'},
        {'control': CONTROL_BUTTON_POSTCMD, 'value': 'postCmd'},
    ]


    def __init__(self, *args, **kwargs):
        log.info("init Edit Rom Collection")

        self.gui = kwargs["gui"]
        self.romCollections = self.gui.config.romCollections
        self.scraperSites = self.gui.config.scraperSites

        self.doModal()

    def onInit(self):
        log.info("onInit Edit Rom Collection")

        # Rom Collections
        self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, self.gui.config.getRomCollectionNames())

        log.info("build imagePlacing list")
        self.imagePlacingList = []
        imagePlacingRows = self.gui.config.tree.findall('ImagePlacing/fileTypeFor')
        for imagePlacing in imagePlacingRows:
            log.info("add image placing: {0}".format(imagePlacing.attrib.get('name')))
            option = imagePlacing.attrib.get('name')
            # HACK: remove all video options from config
            if option.upper().find('VIDEO') >= 0:
                continue
            try:
                option = config.imagePlacingDict[option]
            except IndexError:
                pass
            self.imagePlacingList.append(option)
        self.addItemsToList(CONTROL_LIST_IMAGEPLACING_MAIN, self.imagePlacingList)
        self.addItemsToList(CONTROL_LIST_IMAGEPLACING_INFO, self.imagePlacingList)

        if not helper.isRetroPlayerSupported():
            for ctrl_id in [CONTROL_BUTTON_USERETROPLAYER, CONTROL_BUTTON_GAMECLIENT]:
                try:
                    control = self.getControlById(ctrl_id)
                    control.setEnabled(False)
                    control.setVisible(False)
                except AttributeError:
                    pass

        self.updateRomCollectionControls()

    def onAction(self, action):
        if action.getId() in ACTION_CANCEL_DIALOG:
            self.close()

    def onClick(self, controlID):
        log.info("onClick")

        if controlID == CONTROL_BUTTON_EXIT:  # Close window button
            log.info("close")
            self.close()
        # OK
        elif controlID == CONTROL_BUTTON_SAVE:
            log.info("save")
            # Store selectedRomCollection
            if self.selectedRomCollection is not None:
                self.updateSelectedRomCollection()
                self.romCollections[self.selectedRomCollection.id] = self.selectedRomCollection

            configWriter = ConfigXmlWriter(False)
            success, message = configWriter.writeRomCollections(self.romCollections, True)

            if not success:
                xbmcgui.Dialog().ok(util.localize(32021), message)
            self.close()

        # Cancel
        elif controlID == CONTROL_BUTTON_CANCEL:
            self.close()
        elif controlID == CONTROL_BUTTON_ADD_RC:
            statusOk, errorMsg = wizardconfigxml.ConfigXmlWizard().addRomCollection(self.gui.config)
            if statusOk is False:
                #32001 = Error while updating config.xml.
                message = "%s[CR]%s" % (util.localize(32001), errorMsg)
                xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
                log.info("Error updating config.xml: {0}".format(errorMsg))
                return

            #update self.config
            self.gui.config = Config(None)
            statusOk, errorMsg = self.gui.config.readXml()
            if statusOk is False:
                #32002 = Error reading config.xml.
                message = "%s[CR]%s" % (util.localize(32002), errorMsg)
                xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
                log.info("Error reading config.xml: {0}".format(errorMsg))
                return

            self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, self.gui.config.getRomCollectionNames())
            self.updateRomCollectionControls()

        elif controlID == CONTROL_BUTTON_REMOVE_RC:
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

            self.gui.config = Config(None)
            statusOk, errorMsg = self.gui.config.readXml()
            if statusOk is False:
                #32002 = Error reading config.xml.
                message = "%s[CR]%s" %(util.localize(32002), errorMsg)
                xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
                log.info("Error reading config.xml: {0}".format(errorMsg))
                return

            self.addItemsToList(CONTROL_LIST_ROMCOLLECTIONS, self.gui.config.getRomCollectionNames())
            self.updateRomCollectionControls()

        # Rom Collection list
        elif self.selectedControlId in (CONTROL_BUTTON_RC_DOWN, CONTROL_BUTTON_RC_UP):
            if self.selectedRomCollection is not None:
                # Save current values to selected Rom Collection
                self.updateSelectedRomCollection()
                # Store previous selectedRomCollections state
                self.romCollections[self.selectedRomCollection.id] = self.selectedRomCollection

            # HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
            xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
            self.updateRomCollectionControls()

        # Media Path
        elif self.selectedControlId in (CONTROL_BUTTON_MEDIA_DOWN, CONTROL_BUTTON_MEDIA_UP):
            # HACK: add a little wait time as XBMC needs some ms to execute the MoveUp/MoveDown actions from the skin
            xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
            self.updateMediaPathControls()

        elif controlID == CONTROL_LIST_OFFLINE_SCRAPER:
            self.editOfflineScraper()

        elif controlID == CONTROL_BUTTON_GAMECLIENT:
            success, gameclient = helper.selectlibretrocore(self.selectedRomCollection.name)
            if success:
                self.selectedRomCollection.gameclient = gameclient

            control = self.getControlById(CONTROL_BUTTON_GAMECLIENT)
            if gameclient == "":
                control.setLabel("None")
            else:
                control.setLabel(gameclient)

        elif controlID == CONTROL_BUTTON_EMUCMD:
            self.editEmuCmd()

        elif controlID == CONTROL_BUTTON_PARAMS:
            emulatorParams = self.editTextProperty(CONTROL_BUTTON_PARAMS, util.localize(32625))
            self.selectedRomCollection.emulatorParams = emulatorParams

        elif controlID == CONTROL_BUTTON_ROMPATH:
            self.editRomPath()

        elif controlID == CONTROL_BUTTON_FILEMASK:
            self.editRomFileMask()

        elif controlID == CONTROL_BUTTON_MEDIAPATH:
            self.editMediaPath()

        elif controlID == CONTROL_BUTTON_MEDIAFILEMASK:
            self.editMediaFileMask()

        elif controlID == CONTROL_BUTTON_ADDMEDIAPATH:
            self.addMediaPath()

        elif controlID == CONTROL_BUTTON_REMOVEMEDIAPATH:
            self.removeMediaPath()

        elif controlID == CONTROL_BUTTON_MAXFOLDERDEPTH:
            maxFolderDepth = self.editTextProperty(CONTROL_BUTTON_MAXFOLDERDEPTH, util.localize(32610))
            self.selectedRomCollection.maxFolderDepth = maxFolderDepth

        elif controlID == CONTROL_BUTTON_DISKINDICATOR:
            diskIndicator = self.editTextProperty(CONTROL_BUTTON_DISKINDICATOR, util.localize(32611))
            self.selectedRomCollection.diskPrefix = diskIndicator

        elif controlID == CONTROL_BUTTON_SAVESTATEPATH:
            saveStatePathComplete = self.editPathWithFileMask(CONTROL_BUTTON_SAVESTATEPATH,
                                                              '%s ' % self.selectedRomCollection.name + util.localize(
                                                                  32629), CONTROL_BUTTON_SAVESTATEMASK)
            if saveStatePathComplete != '':
                self.selectedRomCollection.saveStatePath = saveStatePathComplete

        elif controlID == CONTROL_BUTTON_SAVESTATEMASK:
            self.selectedRomCollection.saveStatePath = self.editFilemask(CONTROL_BUTTON_SAVESTATEMASK,
                                                                         util.localize(32630),
                                                                         self.selectedRomCollection.saveStatePath)

        elif controlID == CONTROL_BUTTON_SAVESTATEPARAMS:
            saveStateParams = self.editTextProperty(CONTROL_BUTTON_SAVESTATEPARAMS, util.localize(32631))
            self.selectedRomCollection.saveStateParams = saveStateParams

        elif controlID == CONTROL_BUTTON_PRECMD:
            preCmd = self.editTextProperty(CONTROL_BUTTON_PRECMD, util.localize(32632))
            self.selectedRomCollection.preCmd = preCmd
            log.info("OnClick: precmd = {0}".format(self.selectedRomCollection.preCmd))

        elif controlID == CONTROL_BUTTON_POSTCMD:
            postCmd = self.editTextProperty(CONTROL_BUTTON_POSTCMD, util.localize(32633))
            self.selectedRomCollection.postCmd = postCmd

    def onFocus(self, controlId):
        self.selectedControlId = controlId

    def updateRomCollectionControls(self):
        log.info("updateRomCollectionControls")

        control = self.getControlById(CONTROL_LIST_ROMCOLLECTIONS)
        selectedRomCollectionName = str(control.getSelectedItem().getLabel())

        log.info("selected rom collection: {0}".format(selectedRomCollectionName))
        self.selectedRomCollection = self.gui.config.getRomCollectionByName(selectedRomCollectionName)
        if self.selectedRomCollection is None:
            return

        log.info("build scraper lists")
        self.availableScrapers = AbstractScraper().get_available_scrapers(self.selectedRomCollection.name)
        self.addItemsToList(CONTROL_LIST_DEFAULT_SCRAPER, self.availableScrapers)

        # Import Games
        self.updateRomParams()

        # Set the currently selected state for all the buttons
        for item in self._control_buttons:
            control = self.getControlById(item['control'])
            control.setSelected(getattr(self.selectedRomCollection, item['value']))
            log.info('Set button control ID ' + str(item['control']) + ' to value ' + str(
                getattr(self.selectedRomCollection, item['value'])))

        # Set the value for all the labels
        for item in self._control_labels:
            control = self.getControlById(item['control'])
            util.setLabel(getattr(self.selectedRomCollection, item['value']), control)
            log.info('Set label control ID ' + str(item['control']) + ' to value ' + str(
                getattr(self.selectedRomCollection, item['value'])))

        # preferred scraper
        self.selectScrapersInList(self.selectedRomCollection.scraperSites, CONTROL_LIST_DEFAULT_SCRAPER)

        self.addOfflineScrapersToList()

        # Artwork
        # Media Types
        self.updateMediaTypes()

        # Browse Games
        optionMain = self.selectedRomCollection.imagePlacingMain.name
        try:
            optionMain = config.imagePlacingDict[optionMain]
        except IndexError:
            pass
        self.selectItemInList(optionMain, CONTROL_LIST_IMAGEPLACING_MAIN)

        optionInfo = self.selectedRomCollection.imagePlacingInfo.name
        try:
            optionInfo = config.imagePlacingDict[optionInfo]
        except IndexError:
            pass
        self.selectItemInList(optionInfo, CONTROL_LIST_IMAGEPLACING_INFO)

    def updateRomParams(self):
        # HACK: split romPath and fileMask
        firstRomPath = ''
        fileMask = ''
        for romPath in self.selectedRomCollection.romPaths:
            pathParts = os.path.split(romPath)
            if firstRomPath == '':
                firstRomPath = pathParts[0]
                fileMask = pathParts[1]
            elif firstRomPath == pathParts[0]:
                # This is adding all the file masks for the *same* file path (i.e. where the path matches the first one)
                fileMask = fileMask + ',' + pathParts[1]

        control = self.getControlById(CONTROL_BUTTON_ROMPATH)
        util.setLabel(firstRomPath, control)

        control = self.getControlById(CONTROL_BUTTON_FILEMASK)
        util.setLabel(fileMask, control)

    def updateMediaTypes(self):
        mediaTypeList = []
        firstMediaPath = ''
        firstMediaFileMask = ''
        for mediaPath in self.selectedRomCollection.mediaPaths:
            mediaTypeList.append(mediaPath.fileType.name)
            if firstMediaPath == '':
                pathParts = os.path.split(mediaPath.path)
                firstMediaPath = pathParts[0]
                firstMediaFileMask = pathParts[1]

        self.addItemsToList(CONTROL_LIST_MEDIATYPES, mediaTypeList)

        control = self.getControlById(CONTROL_BUTTON_MEDIAPATH)
        util.setLabel(firstMediaPath, control)

        control = self.getControlById(CONTROL_BUTTON_MEDIAFILEMASK)
        util.setLabel(firstMediaFileMask, control)

    def updateMediaPathControls(self):

        control = self.getControlById(CONTROL_LIST_MEDIATYPES)
        selectedMediaType = str(control.getSelectedItem().getLabel())

        for mediaPath in self.selectedRomCollection.mediaPaths:
            if mediaPath.fileType.name == selectedMediaType:
                pathParts = os.path.split(mediaPath.path)
                control = self.getControlById(CONTROL_BUTTON_MEDIAPATH)
                control.setLabel(pathParts[0])
                control = self.getControlById(CONTROL_BUTTON_MEDIAFILEMASK)
                control.setLabel(pathParts[1])

                break

    def addOfflineScrapersToList(self):
        log.info('addOfflineScrapersToList')
        control = self.getControlById(CONTROL_LIST_OFFLINE_SCRAPER)
        control.reset()

        for scraper in self.selectedRomCollection.scraperSites:
            if scraper.path:
                listitem = xbmcgui.ListItem(scraper.name, scraper.path, '', '')
                control.addItem(listitem)
        #32641 = Click to add Offline Scraper
        listitem = xbmcgui.ListItem('', util.localize(32641))
        control.addItem(listitem)

    def updateSelectedRomCollection(self):

        log.info("updateSelectedRomCollection")

        self.addScrapersToSiteList()

        # Image Placing Main
        control = self.getControlById(CONTROL_LIST_IMAGEPLACING_MAIN)
        imgPlacingItem = control.getSelectedItem()
        imgPlacingName = imgPlacingItem.getLabel()
        # HACK search key by value
        for item in list(config.imagePlacingDict.items()):
            if item[1] == imgPlacingName:
                imgPlacingName = item[0]
        imgPlacing, errorMsg = self.gui.config.readImagePlacing(imgPlacingName, self.gui.config.tree)
        self.selectedRomCollection.imagePlacingMain = imgPlacing

        # Image Placing Info
        control = self.getControlById(CONTROL_LIST_IMAGEPLACING_INFO)
        imgPlacingItem = control.getSelectedItem()
        imgPlacingName = imgPlacingItem.getLabel()
        # HACK search key by value
        for item in list(config.imagePlacingDict.items()):
            if item[1] == imgPlacingName:
                imgPlacingName = item[0]
        imgPlacing, errorMsg = self.gui.config.readImagePlacing(imgPlacingName, self.gui.config.tree)
        self.selectedRomCollection.imagePlacingInfo = imgPlacing

        # Update values for each of the buttons
        for btn in self._control_buttons:
            control = self.getControlById(btn['control'])
            setattr(self.selectedRomCollection, btn['value'], bool(control.isSelected()))

    def editOfflineScraper(self):
        log.info('editOfflineScraper')
        control = self.getControlById(CONTROL_LIST_OFFLINE_SCRAPER)
        item = control.getSelectedItem()

        if item.getLabel() == '':
            scrapers = AbstractScraper().get_available_offline_scrapers(self.selectedRomCollection.name)
            scraperTypeIndex = xbmcgui.Dialog().select(util.localize(32642), scrapers)
            if scraperTypeIndex == -1:
                log.info('No Scraper Type selected.')
                return
            descfile = xbmcgui.Dialog().browse(1, util.localize(32643), 'files')
            if not descfile:
                log.info('No Scraper Path selected.')
                return

            scraper = Site()
            scraper.name = scrapers[scraperTypeIndex]
            scraper.path = descfile
            self.selectedRomCollection.scraperSites.append(scraper)
            self.addOfflineScrapersToList()
        else:
            path = os.path.dirname(item.getLabel2())
            descfile = xbmcgui.Dialog().browse(1, util.localize(32643), 'files', defaultt=path)
            item.setLabel2(descfile)

    def editEmuCmd(self):
        # Maybe there is autoconfig support
        preconfiguredEmulator = None
        emulatorPath = ''
        dialog = xbmcgui.Dialog()

        if self.selectedRomCollection.name == 'Linux' \
                or self.selectedRomCollection.name == 'Macintosh' \
                or self.selectedRomCollection.name == 'Windows':
            emulatorPath = self.editTextProperty(CONTROL_BUTTON_EMUCMD, util.localize(32624))
        else:
            autoconfig = EmulatorAutoconfig(util.getEmuAutoConfigPath())

            emulist = []

            log.info(u"Running on {0}. Trying to find emulator per autoconfig.".format(util.current_os()))
            emulators = autoconfig.findEmulators(util.current_os(), self.selectedRomCollection.name, True)

            for emulator in emulators:
                if emulator.isInstalled:
                    emulist.append(util.localize(32202) % emulator.name)
                else:
                    emulist.append(emulator.name)

            # Ask the user which emulator they want
            if len(emulist) > 0:
                emuIndex = dialog.select(util.localize(32203), emulist)
                try:
                    if (emuIndex >= 0):
                        preconfiguredEmulator = emulators[emuIndex]
                except IndexError:
                    log.info("No Emulator selected.")
                    preconfiguredEmulator = None

            if preconfiguredEmulator:
                emulatorPath = preconfiguredEmulator.emuCmd
                self.selectedRomCollection.emulatorParams = preconfiguredEmulator.emuParams
                control = self.getControlById(CONTROL_BUTTON_PARAMS)
                control.setLabel(self.selectedRomCollection.emulatorParams)
            else:
                emulatorPath = dialog.browse(1, '%s ' % self.selectedRomCollection.name + util.localize(32139), 'files')
                if emulatorPath == '':
                    return

        self.selectedRomCollection.emulatorCmd = emulatorPath
        control = self.getControlById(CONTROL_BUTTON_EMUCMD)
        control.setLabel(emulatorPath)

    def editRomPath(self):

        dialog = xbmcgui.Dialog()

        romPath = dialog.browse(0, '%s Roms' % self.selectedRomCollection.name, 'files')
        if romPath == '':
            return

        control = self.getControlById(CONTROL_BUTTON_FILEMASK)
        fileMaskInput = control.getLabel()
        fileMasks = fileMaskInput.split(',')
        romPaths = []
        for fileMask in fileMasks:
            romPathComplete = os.path.join(romPath, fileMask.strip())
            romPaths.append(romPathComplete)

        self.selectedRomCollection.romPaths = romPaths
        control = self.getControlById(CONTROL_BUTTON_ROMPATH)
        control.setLabel(romPath)

    def editRomFileMask(self):

        control = self.getControlById(CONTROL_BUTTON_FILEMASK)
        romFileMask = control.getLabel()

        romFileMask = xbmcgui.Dialog().input(util.localize(32140), defaultt=romFileMask, type=xbmcgui.INPUT_ALPHANUM)
        if romFileMask == '':
            romFileMask = ' '

        # HACK: this only handles 1 base rom path
        romPath = self.selectedRomCollection.romPaths[0]
        pathParts = os.path.split(romPath)
        romPath = pathParts[0]
        fileMasks = romFileMask.split(',')
        romPaths = []
        for fileMask in fileMasks:
            romPathComplete = os.path.join(romPath, fileMask.strip())
            romPaths.append(romPathComplete)

        self.selectedRomCollection.romPaths = romPaths
        control.setLabel(romFileMask)

    def editMediaPath(self):

        # get selected medias type
        control = self.getControlById(CONTROL_LIST_MEDIATYPES)
        selectedMediaType = str(control.getSelectedItem().getLabel())

        # get current media path
        currentMediaPath = None
        currentMediaPathIndex = -1
        for i in range(0, len(self.selectedRomCollection.mediaPaths)):
            mediaPath = self.selectedRomCollection.mediaPaths[i]
            if mediaPath.fileType.name == selectedMediaType:
                currentMediaPath = mediaPath
                currentMediaPathIndex = i
                break

        mediaPathComplete = self.editPathWithFileMask(CONTROL_BUTTON_MEDIAPATH,
                                                      '%s ' % currentMediaPath.fileType.name + util.localize(32141),
                                                      CONTROL_BUTTON_MEDIAFILEMASK)

        if mediaPathComplete != '':
            currentMediaPath.path = mediaPathComplete
            self.selectedRomCollection.mediaPaths[currentMediaPathIndex] = currentMediaPath

    def editMediaFileMask(self):

        # get selected medias type
        control = self.getControlById(CONTROL_LIST_MEDIATYPES)
        selectedMediaType = str(control.getSelectedItem().getLabel())

        # get current media path
        currentMediaPath = None
        currentMediaPathIndex = -1
        for i in range(0, len(self.selectedRomCollection.mediaPaths)):
            mediaPath = self.selectedRomCollection.mediaPaths[i]
            if mediaPath.fileType.name == selectedMediaType:
                currentMediaPath = mediaPath
                currentMediaPathIndex = i
                break

        mediaPathComplete = self.editFilemask(CONTROL_BUTTON_MEDIAFILEMASK, util.localize(32618), currentMediaPath.path)

        currentMediaPath.path = mediaPathComplete
        self.selectedRomCollection.mediaPaths[currentMediaPathIndex] = currentMediaPath

    def addMediaPath(self):

        mediaTypes = self.gui.config.tree.findall('FileTypes/FileType')

        mediaTypeList = []

        for mediaType in mediaTypes:
            name = mediaType.attrib.get('name')
            if name is not None:
                mtype = mediaType.find('type')
                if mtype is not None and mtype.text == 'video':
                    name = name + ' (video)'

                # check if media type is already in use for selected RC
                isMediaTypeInUse = False
                for mediaPath in self.selectedRomCollection.mediaPaths:
                    if mediaPath.fileType.name == name:
                        isMediaTypeInUse = True

                if not isMediaTypeInUse:
                    mediaTypeList.append(name)

        mediaTypeIndex = xbmcgui.Dialog().select(util.localize(32142), mediaTypeList)
        if mediaTypeIndex == -1:
            return

        mediaType = mediaTypeList[mediaTypeIndex]
        mediaType = mediaType.replace(' (video)', '')

        mediaPathComplete = self.editPathWithFileMask(CONTROL_BUTTON_MEDIAPATH,
                                                      '%s ' % mediaType + util.localize(32141),
                                                      CONTROL_BUTTON_MEDIAFILEMASK)
        # TODO: use default value in editFilemask
        control = self.getControlById(CONTROL_BUTTON_MEDIAFILEMASK)
        control.setLabel('%GAME%.*')
        mediaPathComplete = self.editFilemask(CONTROL_BUTTON_MEDIAFILEMASK, util.localize(32618), mediaPathComplete)

        mediaPath = MediaPath()
        fileType = FileType()
        fileType.name = mediaType
        mediaPath.fileType = fileType
        mediaPath.path = mediaPathComplete
        self.selectedRomCollection.mediaPaths.append(mediaPath)

        control = self.getControlById(CONTROL_LIST_MEDIATYPES)
        item = xbmcgui.ListItem(mediaType, '', '', '')
        control.addItem(item)

        self.selectItemInList(mediaType, CONTROL_LIST_MEDIATYPES)

        xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
        self.updateMediaPathControls()

    def removeMediaPath(self):

        mediaTypeList = []
        for mediaPath in self.selectedRomCollection.mediaPaths:
            mediaTypeList.append(mediaPath.fileType.name)

        mediaTypeIndex = xbmcgui.Dialog().select(util.localize(32143), mediaTypeList)
        if mediaTypeIndex == -1:
            return

        mediaType = mediaTypeList[mediaTypeIndex]
        for mediaPath in self.selectedRomCollection.mediaPaths:
            if mediaPath.fileType.name == mediaType:
                self.selectedRomCollection.mediaPaths.remove(mediaPath)
                break

        if self.selectedRomCollection is not None:
            # Save current values to selected Rom Collection
            self.updateSelectedRomCollection()
            # Store previous selectedRomCollections state
            self.romCollections[self.selectedRomCollection.id] = self.selectedRomCollection

        self.updateRomCollectionControls()

    def addScrapersToSiteList(self):

        log.info("addScrapersToSiteList")

        sites = []
        control = self.getControlById(CONTROL_LIST_OFFLINE_SCRAPER)

        for i in range(0, control.size()):
            item = control.getListItem(i)
            siteName = item.getLabel()
            if not siteName:
                continue
            sitePath = item.getLabel2()
            sites = self.addScraperToSiteList(siteName, sitePath, False, sites)

        #set default scraper
        control = self.getControlById(CONTROL_LIST_DEFAULT_SCRAPER)
        scraperItem = control.getSelectedItem()
        siteName = scraperItem.getLabel()
        sitePath = scraperItem.getLabel2()
        sites = self.addScraperToSiteList(siteName, sitePath, True, sites)

        self.selectedRomCollection.scraperSites = sites

    def addScraperToSiteList(self, siteName, sitePath, setDefault, sites):

        log.info("addScraperToSiteList")

        #check if this site is already available for current RC
        for site in sites:
            if site.name == siteName:
                site.default = setDefault
                return sites

        site = Site()
        site.name = siteName
        site.path = sitePath
        site.default = setDefault
        sites.append(site)

        return sites
