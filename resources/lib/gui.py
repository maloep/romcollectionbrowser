from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from builtins import chr
from builtins import str
from builtins import range
import xbmc, xbmcgui, xbmcaddon
import time, os

from util import *
import util
import helper, config
import dialogprogress
import dialogupdateartwork
import nfowriter
import dialogeditromcollection
from config import *
from gamedatabase import *

#Action Codes
# See guilib/Key.h
ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110, 122)
ACTION_MOVEMENT_LEFT = (1,)
ACTION_MOVEMENT_RIGHT = (2,)
ACTION_MOVEMENT_UP = (3,)
ACTION_MOVEMENT_DOWN = (4,)
ACTION_MOVEMENT = (1, 2, 3, 4, 5, 6, 159, 160)
ACTION_INFO = (11,)
ACTION_CONTEXT = (117,)
ACTION_F = (77,)
ACTION_R = (78,)
ACTION_CTRL_F = (14,)


#ControlIds
CONTROL_CONSOLES = 500
CONTROL_GENRE = 600
CONTROL_YEAR = 700
CONTROL_PUBLISHER = 800
CONTROL_DEVELOPER = 1200
CONTROL_CHARACTER = 900
CONTROL_MAXPLAYERS = 1300
CONTROL_RATING = 1400
CONTROL_REGION = 1500
FILTER_CONTROLS = (500, 600, 700, 800, 900, 1200, 1300, 1400, 1500)
GAME_LISTS = (50, 52, 53, 57, 58, 59)
VIEWS_VERTICAL = (52, 53, 59)
VIEWS_HORIZONTAL = (50, 57, 58)

CONTROL_SCROLLBARS = (2200, 2201, 60, 61, 62, 67, 68, 69)

CONTROL_GAMES_GROUP_START = 50
CONTROL_GAMES_GROUP_END = 59

CONTROL_BUTTON_CHANGE_VIEW = 2
CONTROL_BUTTON_FAVORITE = 1000
CONTROL_BUTTON_SEARCH = 1100
CONTROL_BUTTON_SORTBY = 1600
CONTROL_LABEL_SORTBY = 1601
CONTROL_LABEL_SORTBY_FOCUS = 1602
CONTROL_BUTTON_ORDER = 1700
CONTROL_LABEL_ORDER = 1701
CONTROL_LABEL_ORDER_FOCUS = 1702
NON_EXIT_RCB_CONTROLS = (2, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700,
                         4001, 4002, 4003, 4004, 4005, 4006, 4007, 4008)

CONTROL_LABEL_MSG = 4000

CONTROL_BUTTON_MISSINGINFODIALOG = 4001
CONTROL_BUTTON_SELECTCOLORFILE = 4002
CONTROL_BUTTON_IMPORT_GAMES = 4003
CONTROL_BUTTON_EXPORT_LIBRARY = 4004
CONTROL_BUTTON_CLEAN_LIBRARY = 4005
CONTROL_BUTTON_SCAN_ARTWORK = 4006
CONTROL_BUTTON_EDIT_ROM_COLLECTION = 4007
CONTROL_BUTTON_OPEN_ADDON_SETTINGS = 4008


class MyPlayer(xbmc.Player):
    gui = None

    def onPlayBackEnded(self):
        xbmc.log('RCB MyPlayer: onPlaybackEnded')

        if self.gui == None:
            print ("RCB_WARNING: gui == None in MyPlayer")
            return

        self.gui.setFocus(self.gui.getControl(CONTROL_GAMES_GROUP_START))


class UIGameDB(xbmcgui.WindowXML):
    gdb = None

    selectedControlId = 0
    selectedConsoleId = 0
    selectedGenreId = 0
    selectedYearId = 0
    selectedPublisherId = 0
    selectedDeveloperId = 0
    selectedCharacter = 0
    selectedMaxPlayers = 0
    selectedRating = 0
    selectedRegion = 0

    SORT_METHODS = {
        GameView.FIELDNAMES[GameView.COL_NAME]: util.localize(32421),
        GameView.FIELDNAMES[GameView.COL_rating]: util.localize(32422),
        GameView.FIELDNAMES[GameView.COL_launchCount]: util.localize(32423),
        GameView.FIELDNAMES[GameView.COL_ID]: util.localize(32424),
        GameView.FIELDNAMES[GameView.COL_year]: util.localize(32425),
    }

    SORT_DIRECTIONS = {
        'ASC': util.localize(32419),
        'DESC': util.localize(32420),
    }

    sortMethod = ''
    sortDirection = ''
    searchTerm = ''

    filterChanged = False

    #last selected game position (prevent invoke showgameinfo twice)
    lastPosition = -1

    #dummy to be compatible with ProgressDialogGUI
    itemCount = 0

    # set flag if we opened GID
    gameinfoDialogOpen = False

    def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback, isMedia=True):
        Logutil.log("Init Rom Collection Browser: " + util.RCBHOME, util.LOG_LEVEL_INFO)

        addon = xbmcaddon.Addon(id='%s' % util.SCRIPTID)
        Logutil.log("RCB version: " + addon.getAddonInfo('version'), util.LOG_LEVEL_INFO)

        # Check if RCB service is available
        try:
            serviceAddon = xbmcaddon.Addon(id=util.SCRIPTID)
            Logutil.log("RCB service addon: " + str(serviceAddon), util.LOG_LEVEL_INFO)
        except:
            Logutil.log("No RCB service addon available.", util.LOG_LEVEL_INFO)

        self.initialized = False
        self.Settings = util.getSettings()

        # Make sure that we don't start RCB in cycles
        self.Settings.setSetting('rcb_launchOnStartup', 'false')

        # Check if background game import is running
        if self.checkUpdateInProgress():
            self.quit = True
            return

        # timestamp1 = time.clock()

        self.quit = False

        self.config, success = self.initializeConfig()
        if not success:
            self.quit = True
            return

        success = self.initializeDataBase()
        if not success:
            self.quit = True
            return

        #load video fileType for later use in showGameInfo
        self.fileTypeGameplay, errorMsg = self.config.get_filetype_by_name('gameplay', self.config.tree)
        if self.fileTypeGameplay == None:
            Logutil.log("Error while loading fileType gameplay: " + errorMsg, util.LOG_LEVEL_WARNING)

        #load fileType clearlogo for later use in showGameInfo
        self.fileTypeClearlogo, errorMsg = self.config.get_filetype_by_name('clearlogo', self.config.tree)
        if self.fileTypeClearlogo == None:
            Logutil.log("Error while loading fileType gameplay: " + errorMsg, util.LOG_LEVEL_WARNING)

        #timestamp2 = time.clock()
        #diff = (timestamp2 - timestamp1) * 1000
        #print "RCB startup time: %d ms" % (diff)

        self.player = MyPlayer()
        self.player.gui = self

        self.initialized = True

    # FIXME TODO Move to config.py
    def initializeConfig(self):
        Logutil.log("initializeConfig", util.LOG_LEVEL_INFO)

        config = Config(None)
        createNewConfig = False

        #check if we have config file
        configFile = util.getConfigXmlPath()
        if not os.path.isfile(configFile):
            Logutil.log("No config file available. Create new one.", util.LOG_LEVEL_INFO)
            dialog = xbmcgui.Dialog()
            #32100 = No config file found.
            #32101 = Do you want to create one?
            message = "%s[CR]%s" %(util.localize(32100), util.localize(32101))
            createNewConfig = dialog.yesno(util.SCRIPTNAME, message)
            if not createNewConfig:
                return config, False
        else:
            rcAvailable, message = config.checkRomCollectionsAvailable()
            if not rcAvailable:
                Logutil.log("No Rom Collections found in config.xml.", util.LOG_LEVEL_INFO)
                dialog = xbmcgui.Dialog()
                # 32100 = No config file found.
                # 32101 = Do you want to create one?
                message = "%s[CR]%s" % (util.localize(32100), util.localize(32101))
                createNewConfig = dialog.yesno(util.SCRIPTNAME, message)
                if not createNewConfig:
                    return config, False

        if createNewConfig:
            import wizardconfigxml
            statusOk, errorMsg = wizardconfigxml.ConfigXmlWizard().createConfigXml(configFile)
            if statusOk == False:
                #32001 = Error while updating config.xml.
                message = "%s[CR]%s" % (util.localize(32001), errorMsg)
                xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
                return config, False
        else:
            from configxmlupdater import ConfigxmlUpdater
            #check if config.xml is up to date
            returnCode, message = ConfigxmlUpdater().updateConfig(configFile)
            if returnCode == False:
                # 32001 = Error while updating config.xml.
                message = "%s[CR]%s" % (util.localize(32001), message)
                xbmcgui.Dialog().ok(util.SCRIPTNAME, message)

        #read config.xml
        statusOk, errorMsg = config.readXml()
        if statusOk == False:
            #32001 = Error reading config.xml.
            message = "%s[CR]%s" % (util.localize(32002), errorMsg)
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)

        self.set_skin_flags()

        return config, statusOk

    # FIXME TODO Move to gamedatabase.py
    def initializeDataBase(self):
        try:
            self.gdb = GameDataBase(util.getAddonDataPath())
            self.gdb.connect()
        except Exception as exc:
            #32000 = Error: Can not access database.
            message = "%s[CR]%s" % (util.localize(32000), str(exc))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            Logutil.log('Error accessing database: ' + str(exc), util.LOG_LEVEL_ERROR)
            return False

        #check if database is up to date
        #create new one or alter existing one
        doImport, errorMsg = self.gdb.checkDBStructure()

        if doImport == -1:
            xbmcgui.Dialog().ok(util.SCRIPTNAME, errorMsg)
            return False

        if doImport == 2:
            #32102 = Database and config.xml updated to new version.
            #32103 = Please read the wiki and changelog if you encounter any problems.
            message = "%s[CR]%s" % (util.localize(32102), util.localize(32103))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)

        self.checkImport(doImport, None, False)
        return True

    def onInit(self):

        Logutil.log("Begin onInit", util.LOG_LEVEL_INFO)

        if self.quit:
            Logutil.log("RCB decided not to run. Bye.", util.LOG_LEVEL_INFO)
            self.close()
            return

        self.load_color_schemes()

        self.clearList()
        xbmc.sleep(util.WAITTIME_UPDATECONTROLS)

        #reset last view
        self.loadViewState()

        Logutil.log("End onInit", util.LOG_LEVEL_INFO)

    def onAction(self, action):

        Logutil.log("onAction: " + str(action.getId()), util.LOG_LEVEL_INFO)

        if action.getId() == 0:
            Logutil.log("actionId == 0. Input ignored", util.LOG_LEVEL_INFO)
            return

        #clear any messages
        self.writeMsg("")

        try:
            if action.getId() in ACTION_CANCEL_DIALOG:
                Logutil.log("onAction: ACTION_CANCEL_DIALOG", util.LOG_LEVEL_INFO)

                #don't exit RCB here. Just close the filters
                if self.selectedControlId in NON_EXIT_RCB_CONTROLS:
                    Logutil.log("selectedControl in NON_EXIT_RCB_CONTROLS: %s" % self.selectedControlId,
                                util.LOG_LEVEL_INFO)
                    #HACK: when list is empty, focus sits on other controls than game list
                    if self.getListSize() > 0:
                        self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))
                        return

                    Logutil.log("ListSize == 0 in onAction. Assume that we have to exit.", util.LOG_LEVEL_WARNING)

                if self.player.isPlayingVideo():
                    self.player.stop()
                    xbmc.sleep(util.WAITTIME_PLAYERSTOP)

                self.exit()
            elif action.getId() in ACTION_MOVEMENT:

                Logutil.log("onAction: ACTION_MOVEMENT", util.LOG_LEVEL_DEBUG)

                control = self.getControlById(self.selectedControlId)
                if control == None:
                    Logutil.log("control == None in onAction", util.LOG_LEVEL_WARNING)
                    return

                if CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END:
                    #HACK: check last position in list (prevent loading game info)
                    pos = self.getCurrentListPosition()
                    Logutil.log('onAction: current position = ' + str(pos), util.LOG_LEVEL_DEBUG)
                    Logutil.log('onAction: last position = ' + str(self.lastPosition), util.LOG_LEVEL_DEBUG)
                    if pos != self.lastPosition:
                        self.showGameInfo()

                    self.lastPosition = pos

            elif action.getId() in ACTION_INFO:
                Logutil.log("onAction: ACTION_INFO", util.LOG_LEVEL_DEBUG)

                control = self.getControlById(self.selectedControlId)
                if control == None:
                    Logutil.log("control == None in onAction", util.LOG_LEVEL_WARNING)
                    return
                if CONTROL_GAMES_GROUP_START <= self.selectedControlId <= CONTROL_GAMES_GROUP_END:
                    self.showGameInfoDialog()
            elif action.getId() in ACTION_CONTEXT:
                Logutil.log('onAction: ACTION_CONTEXT', util.LOG_LEVEL_INFO)
                if self.player.isPlayingVideo():
                    self.player.stop()
                    xbmc.sleep(util.WAITTIME_PLAYERSTOP)

                self.showContextMenu()

                self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))
            elif action.getId() in ACTION_R:
                Logutil.log('onAction: ACTION_R', util.LOG_LEVEL_INFO)
                filter_changed = self.apply_filter(CONTROL_CONSOLES)
                if filter_changed:
                    self.showGames()
            elif action.getId() in ACTION_F:
                Logutil.log('onAction: ACTION_F', util.LOG_LEVEL_INFO)
                self.set_isfavorite_for_game(self.getSelectedItem())
            elif action.getId() in ACTION_CTRL_F:
                Logutil.log('onAction: ACTION_CTRL_F', util.LOG_LEVEL_INFO)
                self.set_isfavorite_for_selection(self.getSelectedItem())

        except Exception as exc:
            Logutil.log("RCB_ERROR: unhandled Error in onAction: " + str(exc), util.LOG_LEVEL_ERROR)

    def onClick(self, controlId):
        log.debug("onClick: {0}".format(controlId))
        if controlId in FILTER_CONTROLS:
            filter_changed = self.apply_filter(controlId)
            if filter_changed:
                self.showGames()
        elif controlId in GAME_LISTS:
            log.debug("onClick: Launch Emu")
            self.launchEmu()
        elif controlId == CONTROL_BUTTON_FAVORITE:
            log.debug("onClick: Button Favorites")
            self.showGames()
        elif controlId == CONTROL_BUTTON_SEARCH:
            log.debug("onClick: Button Search")

            searchButton = self.getControlById(CONTROL_BUTTON_SEARCH)
            if searchButton is None:
                return

            self.searchTerm = xbmcgui.Dialog().input(util.localize(32116), type=xbmcgui.INPUT_ALPHANUM)
            lbl = util.localize(32117) if self.searchTerm == '' else util.localize(32117) + ': ' + self.searchTerm
            searchButton.setLabel(lbl)

            self.showGames()

        elif controlId == CONTROL_BUTTON_SORTBY:
            log.debug("onClick: Button Sort by")

            options = []
            for key in list(self.SORT_METHODS.keys()):
                item = xbmcgui.ListItem(self.SORT_METHODS[key])
                item.setProperty('column', key)
                options.append(item)

            index = xbmcgui.Dialog().select(util.localize(32417), options)
            if index < 0:
                return

            self.sortMethod = options[index].getProperty('column')
            label = self.getControlById(CONTROL_LABEL_SORTBY)
            if label:
                label.setLabel(options[index].getLabel())
            label = self.getControlById(CONTROL_LABEL_SORTBY_FOCUS)
            if label:
                label.setLabel(options[index].getLabel())
            self.showGames()

        elif controlId == CONTROL_BUTTON_ORDER:
            log.debug("onClick: Button Order")

            options = []
            for key in list(self.SORT_DIRECTIONS.keys()):
                item = xbmcgui.ListItem(self.SORT_DIRECTIONS[key])
                item.setProperty('direction', key)
                options.append(item)

            index = xbmcgui.Dialog().select(util.localize(32418), options)
            if index < 0:
                return

            self.sortDirection = options[index].getProperty('direction')
            label = self.getControlById(CONTROL_LABEL_ORDER)
            label.setLabel(options[index].getLabel())
            label = self.getControlById(CONTROL_LABEL_ORDER_FOCUS)
            label.setLabel(options[index].getLabel())
            self.showGames()

        elif controlId == CONTROL_BUTTON_MISSINGINFODIALOG:
            import dialogmissinginfo
            try:
                missingInfoDialog = dialogmissinginfo.MissingInfoDialog("script-RCB-missinginfo.xml",
                                                                        util.getAddonInstallPath(),
                                                                        util.getConfiguredSkin(), "720p", gui=self)
            except:
                missingInfoDialog = dialogmissinginfo.MissingInfoDialog("script-RCB-missinginfo.xml",
                                                                        util.getAddonInstallPath(),
                                                                        "Default", "720p", gui=self)
            if missingInfoDialog.saveConfig:
                self.config = Config(None)
                self.config.readXml()
                self.showGames()

            del missingInfoDialog

        elif controlId == CONTROL_BUTTON_CHANGE_VIEW:
            # Need to change viewmode manually since Frodo
            xbmc.executebuiltin('Container.NextViewMode')

        elif controlId == CONTROL_BUTTON_SELECTCOLORFILE:
            color_path = os.path.join(util.getAddonInstallPath(), 'resources', 'skins', util.getConfiguredSkin(), 'colors')
            dirs, files = xbmcvfs.listdir(color_path)
            index = xbmcgui.Dialog().select('Colors', files)
            if index >= 0:
                color_file = os.path.join(color_path, files[index])

            #color_file = xbmcgui.Dialog().browse(1, 'RCB', 'files', '.xml', defaultt=color_path)
            if color_file:
                self.Settings.setSetting(util.SETTING_RCB_COLORFILE, color_file)

            self.load_color_schemes()

        elif controlId == CONTROL_BUTTON_IMPORT_GAMES:
            self.updateDB()

        elif controlId == CONTROL_BUTTON_EXPORT_LIBRARY:
            nfowriter.NfoWriter().exportLibrary(self.gdb, self.config.romCollections)

        elif controlId == CONTROL_BUTTON_CLEAN_LIBRARY:
            self.cleanDB()

        elif controlId == CONTROL_BUTTON_SCAN_ARTWORK:
            try:
                dialog = dialogupdateartwork.UpdateArtworkDialog("script-RCB-updateartwork.xml",
                                                        util.getAddonInstallPath(),
                                                        util.getConfiguredSkin(), "720p", gui=self)
            except:
                dialog = dialogupdateartwork.UpdateArtworkDialog("script-RCB-updateartwork.xml",
                                                        util.getAddonInstallPath(),
                                                        "Default", "720p", gui=self)
            del dialog

        elif controlId == CONTROL_BUTTON_EDIT_ROM_COLLECTION:
            constructorParam = "720p"
            try:
                editRCdialog = dialogeditromcollection.EditRomCollectionDialog("script-RCB-editromcollection.xml",
                                                                               util.getAddonInstallPath(),
                                                                               util.getConfiguredSkin(),
                                                                               constructorParam, gui=self)
            except:
                editRCdialog = dialogeditromcollection.EditRomCollectionDialog("script-RCB-editromcollection.xml",
                                                                               util.getAddonInstallPath(),
                                                                               "Default",
                                                                               constructorParam, gui=self)
            del editRCdialog

            self.config = Config(None)
            self.config.readXml()

        elif controlId == CONTROL_BUTTON_OPEN_ADDON_SETTINGS:
            self.Settings.openSettings()



    def set_skin_flags(self):

        #set flag if the skin should display clearlogo as title in lists
        self.set_skin_flag(util.SETTING_RCB_USECLEARLOGOASTITLE)
        #set flag if the skin should display scrollbars in game lists
        self.set_skin_flag(util.SETTING_RCB_SHOWSCROLLBARS)

    def set_skin_flag(self, flag):
        if self.Settings.getSetting(flag).upper() == "TRUE":
            xbmc.executebuiltin('Skin.SetBool(%s)' % flag)
        else:
            xbmc.executebuiltin('Skin.Reset(%s)' % flag)

    def load_color_schemes(self):
        log.info('load_color_schemes')

        color_file = self.Settings.getSetting(util.SETTING_RCB_COLORFILE)
        if not color_file \
            or not xbmcvfs.exists(color_file) \
            or util.getConfiguredSkin() not in color_file:
            log.info('setting "rcb_colorfile" not found or color file not readable. using "defaults.xml"')
            color_file = os.path.join(util.getAddonInstallPath(), 'resources', 'skins', util.getConfiguredSkin(), 'colors', 'defaults.xml')

        tree = ElementTree()
        if sys.version_info >= (2, 7):
            parser = XMLParser(encoding='utf-8')
        else:
            parser = XMLParser()

        log.info('Reading color file: %s' %color_file)
        tree.parse(color_file, parser)

        for color in tree.findall('color'):
            log.debug('set color: %s: %s' % (color.attrib.get('name'), color.text))
            xbmc.executebuiltin("Skin.SetString(%s, %s)" % (color.attrib.get('name'), color.text))


    def apply_filter(self, control_id):

        filter_changed = False
        if control_id == CONTROL_CONSOLES:
            consoles = []
            for romCollection in list(self.config.romCollections.values()):
                consoles.append([romCollection.id, romCollection.name])

            showEntryAllItems = getSettings().getSetting(util.SETTING_RCB_SHOWENTRYALLCONSOLES).upper() == 'TRUE'
            self.selectedConsoleId, filter_changed = self.filter_id_values(consoles, util.localize(32406), control_id,
                                                                           self.selectedConsoleId, showEntryAllItems)
        elif control_id == CONTROL_GENRE:
            genres = []
            rows = Genre(self.gdb).getFilteredGenres(self.selectedConsoleId, self.selectedYearId, self.selectedPublisherId,
                                                     self.selectedDeveloperId, self.selectedMaxPlayers, self.selectedRating,
                                                     self.selectedRegion,
                                                     self._buildLikeStatement(self.selectedCharacter, ''))
            for row in rows:
                genres.append([row[Genre.COL_ID], row[Genre.COL_NAME]])

            self.selectedGenreId, filter_changed = self.filter_id_values(genres, util.localize(32401), control_id,
                                                                         self.selectedGenreId, True)
        elif control_id == CONTROL_YEAR:
            years = []
            rows = Year(self.gdb).getFilteredYears(self.selectedConsoleId, self.selectedGenreId, self.selectedPublisherId,
                                                     self.selectedDeveloperId, self.selectedMaxPlayers, self.selectedRating,
                                                     self.selectedRegion,
                                                     self._buildLikeStatement(self.selectedCharacter, ''))
            for row in rows:
                years.append([row[Year.COL_ID], row[Year.COL_NAME]])

            self.selectedYearId, filter_changed = self.filter_id_values(years, util.localize(32400), control_id,
                                                                        self.selectedYearId, True)
        elif control_id == CONTROL_PUBLISHER:
            publishers = []
            rows = Publisher(self.gdb).getFilteredPublishers(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId,
                                                     self.selectedDeveloperId, self.selectedMaxPlayers, self.selectedRating,
                                                     self.selectedRegion,
                                                     self._buildLikeStatement(self.selectedCharacter, ''))
            for row in rows:
                publishers.append([row[Publisher.COL_ID], row[Publisher.COL_NAME]])

            self.selectedPublisherId, filter_changed = self.filter_id_values(publishers, util.localize(32402), control_id,
                                                                             self.selectedPublisherId, True)
        elif control_id == CONTROL_DEVELOPER:
            developers = []
            rows = Developer(self.gdb).getFilteredDevelopers(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId,
                                                     self.selectedPublisherId, self.selectedMaxPlayers, self.selectedRating,
                                                     self.selectedRegion,
                                                     self._buildLikeStatement(self.selectedCharacter, ''))
            for row in rows:
                developers.append([row[Developer.COL_ID], row[Developer.COL_NAME]])

            self.selectedDeveloperId, filter_changed = self.filter_id_values(developers, util.localize(32403),
                                                                             control_id, self.selectedDeveloperId, True)
        elif control_id == CONTROL_MAXPLAYERS:
            maxplayers = [util.localize(32120)]
            rows = GameView(self.gdb).getFilteredMaxPlayers(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId,
                                                     self.selectedPublisherId, self.selectedDeveloperId, self.selectedRating,
                                                     self.selectedRegion,
                                                     self._buildLikeStatement(self.selectedCharacter, ''))
            for row in rows:
                if row[0]:
                    maxplayers.append(row[0])

            self.selectedMaxPlayers, filter_changed = self.filter_text_values(maxplayers, util.localize(32414),
                                                                              control_id, self.selectedMaxPlayers)

        elif control_id == CONTROL_RATING:
            ratings = [util.localize(32120)]
            for i in range(1,10):
                ratings.append(str(i))

            rating, filter_changed = self.filter_text_values(ratings, util.localize(32415), control_id,
                                                          self.selectedRating)
            if(rating == util.localize(32120)):
                rating = 0
            self.selectedRating = rating

        elif control_id == CONTROL_REGION:
            regions = [util.localize(32120)]
            rows = GameView(self.gdb).getFilteredRegions(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId,
                                                         self.selectedPublisherId, self.selectedDeveloperId,
                                                         self.selectedMaxPlayers, self.selectedRating,
                                                         self._buildLikeStatement(self.selectedCharacter, ''))
            for row in rows:
                if row[0]:
                    regions.append(row[0])

            self.selectedRegion, filter_changed = self.filter_text_values(regions, util.localize(32416), control_id,
                                                          self.selectedRegion)

        elif control_id == CONTROL_CHARACTER:
            characters = [util.localize(32120)]
            characters.append('0-9')
            for i in range(0, 26):
                char = chr(ord('A') + i)
                characters.append(char)

            self.selectedCharacter, filter_changed = self.filter_text_values(characters, util.localize(32407), control_id,
                                                             self.selectedCharacter)
        return filter_changed

    def filter_text_values(self, filter_items, header_text, control_id, current_value):
        index = xbmcgui.Dialog().select(header_text, filter_items)
        if index < 0:
            return current_value, False

        button = self.getControlById(control_id)
        result = filter_items[index]
        button.setLabel(result)
        if result == util.localize(32120):
            result = 0
        return result, True

    def filter_id_values(self, filter_items, header_text, control_id, current_value, show_entry_all_items):
        # Sort the consoles by name
        filter_items = sorted(filter_items, key=lambda filter_item: filter_item[1])

        if show_entry_all_items:
            filter_items = [('0', util.localize(32120))] + filter_items
        items = []
        for filter_item in filter_items:
            item = xbmcgui.ListItem(filter_item[1])
            item.setProperty('id', str(filter_item[0]))
            items.append(item)
        index = xbmcgui.Dialog().select(header_text, items)
        if index < 0:
            return current_value, False
        item = items[index]
        button = self.getControlById(control_id)
        button.setLabel(item.getLabel())
        return int(item.getProperty('id')), True

    def onFocus(self, controlId):
        Logutil.log("onFocus: " + str(controlId), util.LOG_LEVEL_DEBUG)
        self.selectedControlId = controlId

    def _getMaxGamesToDisplay(self):
        # Set a limit of games to show
        maxNumGamesIndex = self.Settings.getSetting(util.SETTING_RCB_MAXNUMGAMESTODISPLAY)
        return util.MAXNUMGAMES_ENUM[int(maxNumGamesIndex)]

    # Functions for generating query strings for filtering

    def _buildLikeStatement(self, selectedCharacter, searchTerm):
        log.debug("buildLikeStatement")

        likeStatement = ''

        if selectedCharacter == 0:  # All
            likeStatement = "0 = 0"
        elif selectedCharacter == '0-9':
            likeStatement = "(substr(name, 1, 1) IN ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'))"
        else:
            likeStatement = "name LIKE '{0}%'".format(selectedCharacter)

        if searchTerm != '':
            likeStatement += " AND name LIKE '%{0}%'".format(searchTerm)

        return likeStatement

    def _buildMissingFilterStatement(self, configobject):

        #32157 = ignore
        if configobject.showHideOption.lower() == util.localize(32157):
            return ''

        statement = ''

        andStatementInfo = self._buildInfoStatement(configobject.missingFilterInfo.andGroup, ' AND ')
        if andStatementInfo != '':
            statement = andStatementInfo

        orStatementInfo = self._buildInfoStatement(configobject.missingFilterInfo.orGroup, ' OR ')
        if orStatementInfo != '':
            if statement != '':
                statement = statement + ' OR '
            statement = statement + orStatementInfo

        andStatementArtwork = self._buildArtworkStatement(configobject, configobject.missingFilterArtwork.andGroup, ' AND ')
        if andStatementArtwork != '':
            if statement != '':
                statement = statement + ' OR '
            statement = statement + andStatementArtwork

        orStatementArtwork = self._buildArtworkStatement(configobject, configobject.missingFilterArtwork.orGroup, ' OR ')
        if orStatementArtwork != '':
            if statement != '':
                statement = statement + ' OR '
            statement = statement + orStatementArtwork

        if statement != '':
            statement = '(%s)' % (statement)
            #32161 = hide
            if configobject.showHideOption.lower() == util.localize(32161):
                statement = 'NOT ' + statement

        return statement

    def _buildInfoStatement(self, group, operator):
        statement = ''
        for item in group:
            if statement == '':
                statement = '('
            else:
                statement = statement + operator
            statement = statement + config.gameproperties[item][1]
        if statement != '':
            statement = statement + ')'

        return statement

    def _buildArtworkStatement(self, configobject, group, operator):
        statement = ''
        for item in group:
            if statement == '':
                statement = '('
            else:
                statement = statement + operator
            typeId = ''
            fileTypeRows = configobject.tree.findall('FileTypes/FileType')
            for element in fileTypeRows:
                if element.attrib.get('name') == item:
                    typeId = element.attrib.get('id')
                    break
            statement = statement + 'fileType%s IS NULL' % str(typeId)

        if statement != '':
            statement = statement + ')'
        return statement

    def _getGamesListQueryStatement(self):
        # Build statement for character search (where name LIKE 'A%')
        likeStatement = self._buildLikeStatement(self.selectedCharacter, self.searchTerm)

        # Build statement for missing filters
        missingFilterStatement = self._buildMissingFilterStatement(self.config)
        if missingFilterStatement != '':
            likeStatement = likeStatement + ' AND ' + missingFilterStatement

        return likeStatement

    # End of Functions for generating query strings for filtering

    def _isGameFavourite(self):
        try:
            if self.getControlById(CONTROL_BUTTON_FAVORITE).isSelected():
                return 1
        except AttributeError:
            pass

        return 0

    def showGames(self):
        Logutil.log("Begin showGames", util.LOG_LEVEL_INFO)

        self.lastPosition = -1

        preventUnfilteredSearch = self.Settings.getSetting(util.SETTING_RCB_PREVENTUNFILTEREDSEARCH).upper() == 'TRUE'
        if preventUnfilteredSearch:
            if self.selectedCharacter == util.localize(32120) \
                    and self.selectedConsoleId == 0 and self.selectedGenreId == 0 and self.selectedYearId == 0 \
                    and self.selectedPublisherId == 0 and self.selectedDeveloperId == 0:
                Logutil.log("preventing unfiltered search", util.LOG_LEVEL_WARNING)
                return

        self.clearList()
        #32121 = Loading games...
        self.writeMsg(util.localize(32121))

        isFavorite = self._isGameFavourite()

        showFavoriteStars = self.Settings.getSetting(util.SETTING_RCB_SHOWFAVORITESTARS).upper() == 'TRUE'

        timestamp1 = time.clock()

        likeStatement = self._getGamesListQueryStatement()
        order_by = "ORDER BY %s COLLATE NOCASE %s" %(self.sortMethod, self.sortDirection)
        maxNumGames = self._getMaxGamesToDisplay()

        games = GameView(self.gdb).getFilteredGames(self.selectedConsoleId, self.selectedGenreId, self.selectedYearId,
                                                self.selectedPublisherId, self.selectedDeveloperId,
                                                self.selectedMaxPlayers, self.selectedRating, self.selectedRegion,
                                                isFavorite, likeStatement, order_by, maxNumGames)

        timestamp2 = time.clock()
        diff = (timestamp2 - timestamp1) * 1000
        print ("showGames: load %d games from db in %d ms" % (len(games), diff))

        #used to show percentage during game loading
        divisor = len(games) / 10
        counter = 0

        items = []
        for game in games:

            romcollection_id = str(game[GameView.COL_romCollectionId])

            try:
                romCollection = self.config.romCollections[romcollection_id]
            except KeyError:
                Logutil.log('Cannot get rom collection with id: ' + romcollection_id, util.LOG_LEVEL_ERROR)
                # Won't be able to get game images, move to next game
                continue

            item = xbmcgui.ListItem(game[GameView.COL_NAME], str(game[GameView.COL_ID]))
            item.setProperty('romCollectionId', romcollection_id)
            item.setProperty('romcollection', romCollection.name)
            item.setProperty('console', romCollection.name)
            item.setProperty('gameId', str(game[GameView.COL_ID]))
            item.setProperty('plot', game[GameView.COL_description])
            item.setProperty('playcount', str(game[GameView.COL_launchCount]))
            item.setProperty('originalTitle', game[GameView.COL_originalTitle])
            item.setProperty('alternateTitle', game[GameView.COL_alternateTitle])
            item.setProperty('developer', game[GameView.COL_developer])
            item.setProperty('publisher', game[GameView.COL_publisher])
            item.setProperty('year', game[GameView.COL_year])
            item.setProperty('genre', game[GameView.COL_genre])
            item.setProperty('gameCmd', game[GameView.COL_gameCmd])
            item.setProperty('alternateGameCmd', game[GameView.COL_alternateGameCmd])

            if game[GameView.COL_isFavorite] == 1 and showFavoriteStars:
                item.setProperty('isfavorite', '1')
            else:
                item.setProperty('isfavorite', '')

            #set gamelist artwork at startup
            item.setArt({
                        'icon': helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForGameList, game),
                        'thumb': helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForGameListSelected, game),
                        IMAGE_CONTROL_CLEARLOGO: helper.get_file_for_control_from_db(
                            [self.fileTypeClearlogo], game),
                        IMAGE_CONTROL_BACKGROUND: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewBackground, game),
                        IMAGE_CONTROL_GAMEINFO_BIG: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewGameInfoBig, game),
                        IMAGE_CONTROL_GAMEINFO_UPPERLEFT: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewGameInfoUpperLeft, game),
                        IMAGE_CONTROL_GAMEINFO_UPPERRIGHT: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewGameInfoUpperRight, game),
                        IMAGE_CONTROL_GAMEINFO_LOWERLEFT: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLowerLeft, game),
                        IMAGE_CONTROL_GAMEINFO_LOWERRIGHT: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLowerRight, game),
                        IMAGE_CONTROL_GAMEINFO_UPPER: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewGameInfoUpper, game),
                        IMAGE_CONTROL_GAMEINFO_LOWER: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLower, game),
                        IMAGE_CONTROL_GAMEINFO_LEFT: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewGameInfoLeft, game),
                        IMAGE_CONTROL_GAMEINFO_RIGHT: helper.get_file_for_control_from_db(
                            romCollection.imagePlacingMain.fileTypesForMainViewGameInfoRight, game)
                         })

            if romCollection.autoplayVideoMain:
                self.loadVideoFiles(item, romCollection, game)
            else:
                item.setProperty('autoplayvideomain', '')

            # Add the listitem to the list
            items.append(item)

            #add progress to "loading games" message
            if len(games) > 1000:
                if counter >= divisor and counter % divisor == 0:
                    percent = (old_div(len(games), divisor)) * (old_div(counter, divisor))
                    #32121 = Loading games...
                    self.writeMsg('%s (%i%%)' % (util.localize(32121), percent))
                counter = counter + 1

        #add dummy item to keep the list navigable
        if len(items) == 0:
            #32412 = No Games found
            item = xbmcgui.ListItem(util.localize(32412), '')
            items.append(item)

        #Add list to window
        self.addItems(items)

        self.writeMsg("")

        #show navigation hint
        if self.Settings.getSetting(util.SETTING_RCB_SHOWNAVIGATIONHINT).upper() == 'TRUE':
            view_mode = self.get_selected_view_mode()
            print ('view_mode = %s' %view_mode)
            if int(view_mode) in VIEWS_VERTICAL:
                self.writeMsg(util.localize(32208))
            elif int(view_mode) in VIEWS_HORIZONTAL:
                self.writeMsg(util.localize(32209))

        timestamp3 = time.clock()
        diff = (timestamp3 - timestamp2) * 1000
        Logutil.log("showGames: load %i games to list in %d ms" % (self.getListSize(), diff), util.LOG_LEVEL_INFO)

        Logutil.log("End showGames", util.LOG_LEVEL_INFO)

    def showGameInfo(self):
        """ Called when a game is selected in the list;
            Only used to stop video playback if current game has no video
        """
        selectedGame = self.getSelectedItem()
        try:
            romCollection = self.config.romCollections[selectedGame.getProperty('romCollectionId')]
        except Exception as err:
            Logutil.log(err, util.LOG_LEVEL_ERROR)
            Logutil.log('Cannot get rom collection with id: ' + str(selectedGame.getProperty('romCollectionId')),
                        util.LOG_LEVEL_ERROR)

        video = selectedGame.getProperty('gameplaymain')

        if video == "" or video is None or not romCollection.autoplayVideoMain:
            if self.player.isPlayingVideo():
                self.player.stop()

    def getSelectedItem(self):
        if self.getListSize() == 0:
            Logutil.log("ListSize == 0 in getSelectedItem", util.LOG_LEVEL_WARNING)
            return

        pos = self.getCurrentListPosition()
        if pos == -1:
            pos = 0

        return self.getListItem(pos)

    def launchEmu(self):

        Logutil.log("Begin launchEmu", util.LOG_LEVEL_INFO)

        if self.getListSize() == 0:
            Logutil.log("ListSize == 0 in launchEmu", util.LOG_LEVEL_WARNING)
            return

        pos = self.getCurrentListPosition()
        if pos == -1:
            pos = 0
        selectedGame = self.getListItem(pos)

        if selectedGame == None:
            Logutil.log("selectedGame == None in launchEmu", util.LOG_LEVEL_WARNING)
            return

        gameId = selectedGame.getProperty('gameId')
        Logutil.log("launching game with id: " + str(gameId), util.LOG_LEVEL_INFO)

        #stop video (if playing)
        if self.player.isPlayingVideo():
            #self.player.stoppedByRCB = True
            self.player.stop()

        from launcher import RCBLauncher
        launcher = RCBLauncher()
        launcher.launchEmu(self.gdb, self, gameId, self.config, selectedGame)
        Logutil.log("End launchEmu", util.LOG_LEVEL_INFO)

    def updateDB(self):
        Logutil.log("Begin updateDB", util.LOG_LEVEL_INFO)
        self.importGames(None, False)
        Logutil.log("End updateDB", util.LOG_LEVEL_INFO)

    def rescrapeGames(self, romCollections):
        Logutil.log("Begin rescrapeGames", util.LOG_LEVEL_INFO)
        self.importGames(romCollections, True)
        self.config.readXml()
        Logutil.log("End rescrapeGames", util.LOG_LEVEL_INFO)

    def importGames(self, romCollections, isRescrape):
        self.saveViewState(False)
        self.clearList()
        self.checkImport(3, romCollections, isRescrape)
        self.loadViewState()

    def deleteGame(self, gameID):
        Logutil.log("Begin deleteGame", util.LOG_LEVEL_INFO)

        Logutil.log("Delete Year", util.LOG_LEVEL_INFO)
        Year(self.gdb).delete(gameID)
        Logutil.log("Delete Publisher", util.LOG_LEVEL_INFO)
        Publisher(self.gdb).delete(gameID)
        Logutil.log("Delete Developer", util.LOG_LEVEL_INFO)
        Developer(self.gdb).delete(gameID)
        Logutil.log("Delete Genre", util.LOG_LEVEL_INFO)
        Genre(self.gdb).delete(gameID)
        Logutil.log("Delete File", util.LOG_LEVEL_INFO)
        File(self.gdb).delete(gameID)
        Logutil.log("Delete Game", util.LOG_LEVEL_INFO)
        Game(self.gdb).delete(gameID)

        Logutil.log("End deleteGame", util.LOG_LEVEL_INFO)

    def deleteRCGames(self, rcID, rcDelete, rDelete):
        Logutil.log("begin Delete Games", util.LOG_LEVEL_INFO)
        count = 0

        rcList = GameView(self.gdb).getFilteredGames(rcID, 0, 0, 0, 0, 0, 0, 0, 0, '0 = 0', '', 0)
        progressDialog = dialogprogress.ProgressDialogGUI()
        progressDialog.itemCount = len(rcList)
        progressDialog.create(util.localize(32105))

        if rcList != None:
            #32104 = Deleting Rom
            message = util.localize(32104) + " (%i / %i)" % (count, progressDialog.itemCount)
            progressDialog.writeMsg(message, count)
            for items in rcList:
                count = count + 1
                message = util.localize(32104) + " (%i / %i)" % (count, progressDialog.itemCount)
                progressDialog.writeMsg(message, count)
                self.deleteGame(items[Game.COL_ID])

            #32106 = Deleting Roms Complete
            progressDialog.writeMsg(util.localize(32106), count)

            time.sleep(1)
            self.gdb.commit()
            xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
            if rDelete:
                self.setFilterSelection(CONTROL_GAMES_GROUP_START, 0)

        rcList = None
        Logutil.log("end Delete Games", util.LOG_LEVEL_INFO)

    def cleanDB(self):
        Logutil.log("Begin cleanDB", util.LOG_LEVEL_INFO)

        count = 0
        removeCount = 0
        filelist = File(self.gdb).getFilesList()
        progressDialog2 = dialogprogress.ProgressDialogGUI()
        progressDialog2.itemCount = len(filelist)
        #32108 = Cleaning Database...
        progressDialog2.create(util.localize(32108))
        #32107 = Checking File
        message = "%s (%i / %i)" % (util.localize(32107), count, progressDialog2.itemCount)
        progressDialog2.writeMsg(message, count)
        if filelist != None:
            for items in filelist:
                count = count + 1
                message = "%s (%i / %i)" % (util.localize(32107), count, progressDialog2.itemCount)
                progressDialog2.writeMsg(message, count)
                if os.path.exists(items[File.COL_NAME]) != True:
                    if items[File.COL_fileTypeId] == 0:
                        self.deleteGame(items[File.COL_parentId])
                    else:
                        File(self.gdb).deleteByFileId(items[File.COL_ID])
                    removeCount = removeCount + 1
            #32109 = Compressing Database...
            progressDialog2.writeMsg(util.localize(32109), count)
            self.gdb.compact()
            time.sleep(.5)
            #32110 = Database Clean-up Complete
            progressDialog2.writeMsg(util.localize(32110), count)
            time.sleep(1)
            self.showGames()
        Logutil.log("End cleanDB", util.LOG_LEVEL_INFO)

    def showGameInfoDialog(self):
        """ Called when a game is opened in the GameInfo dialog """
        Logutil.log("Begin showGameInfoDialog", util.LOG_LEVEL_INFO)

        if self.getListSize() == 0:
            Logutil.log("ListSize == 0 in saveViewState", util.LOG_LEVEL_WARNING)
            return

        selectedGameIndex = self.getCurrentListPosition()
        if selectedGameIndex == -1:
            selectedGameIndex = 0
        selectedGame = self.getListItem(selectedGameIndex)
        if selectedGame == None:
            Logutil.log("selectedGame == None in showGameInfoDialog", util.LOG_LEVEL_WARNING)
            return

        gameId = selectedGame.getProperty('gameId')

        self.saveViewMode()

        if self.player.isPlayingVideo():
            self.player.stop()

        self.gameinfoDialogOpen = True

        constructorParam = "720p"

        import dialoggameinfo
        try:
            gid = dialoggameinfo.UIGameInfoView("script-RCB-gameinfo.xml", util.getAddonInstallPath(),
                                                util.getConfiguredSkin(), constructorParam, gdb=self.gdb, gameId=gameId,
                                                listItem=selectedGame,
                                                consoleId=self.selectedConsoleId, genreId=self.selectedGenreId,
                                                yearId=self.selectedYearId, publisherId=self.selectedPublisherId,
                                                developerId=self.selectedDeveloperId,
                                                selectedGameIndex=selectedGameIndex,
                                                selectedCharacter=self.selectedCharacter,
                                                selectedMaxPlayers=self.selectedMaxPlayers,
                                                selectedRating=self.selectedRating, selectedRegion=self.selectedRegion,
                                                sortMethod=self.sortMethod, sortDirection=self.sortDirection,
                                                controlIdMainView=self.selectedControlId, config=self.config,
                                                settings=self.Settings,
                                                fileTypeGameplay=self.fileTypeGameplay)
        except:
            gid = dialoggameinfo.UIGameInfoView("script-RCB-gameinfo.xml", util.getAddonInstallPath(), "Default",
                                                constructorParam, gdb=self.gdb, gameId=gameId, listItem=selectedGame,
                                                consoleId=self.selectedConsoleId, genreId=self.selectedGenreId,
                                                yearId=self.selectedYearId, publisherId=self.selectedPublisherId,
                                                developerId=self.selectedDeveloperId,
                                                selectedGameIndex=selectedGameIndex,
                                                selectedCharacter=self.selectedCharacter,
                                                selectedMaxPlayers=self.selectedMaxPlayers,
                                                selectedRating=self.selectedRating, selectedRegion=self.selectedRegion,
                                                sortMethod=self.sortMethod, sortDirection=self.sortDirection,
                                                controlIdMainView=self.selectedControlId, config=self.config,
                                                settings=self.Settings,
                                                fileTypeGameplay=self.fileTypeGameplay)

        del gid

        self.gameinfoDialogOpen = False

        #force restart of video if available
        #selectedGame.setProperty('gameplaymain', video)
        self.setFocus(self.getControl(CONTROL_GAMES_GROUP_START))

        Logutil.log("End showGameInfoDialog", util.LOG_LEVEL_INFO)

    def showContextMenu(self):

        import dialogcontextmenu

        """
        constructorParam = "720p"
        try:
            cm = dialogcontextmenu.ContextMenuDialog("script-RCB-contextmenu.xml", util.getAddonInstallPath(),
                                                     util.getConfiguredSkin(), constructorParam, gui=self)
        except:
            cm = dialogcontextmenu.ContextMenuDialog("script-RCB-contextmenu.xml", util.getAddonInstallPath(),
                                                     "Default", constructorParam, gui=self)
        """
        cm = dialogcontextmenu.ContextMenuDialog(gui=self)

        del cm

    def loadVideoFiles(self, listItem, romCollection, game):

        #check if we should use autoplay video
        if romCollection.autoplayVideoMain:
            listItem.setProperty('autoplayvideomain', 'true')
        else:
            listItem.setProperty('autoplayvideomain', '')

        #get video window size
        if romCollection.imagePlacingMain.name.startswith('gameinfosmall'):
            listItem.setProperty('videosizesmall', 'small')
            listItem.setProperty('videosizebig', '')
        else:
            listItem.setProperty('videosizebig', 'big')
            listItem.setProperty('videosizesmall', '')

        if self.fileTypeGameplay == None:
            Logutil.log("fileType gameplay == None. No video loaded.", util.LOG_LEVEL_INFO)

        #load gameplay videos
        video = helper.get_file_for_control_from_db((self.fileTypeGameplay,), game)
        if video:
            listItem.setProperty('gameplaymain', video)

    def checkImport(self, doImport, romCollections, isRescrape):

        #doImport: 0=nothing, 1=import Settings and Games, 2=import Settings only, 3=import games only
        if doImport == 0:
            return

        #Show options dialog if user wants to see it
        #Import is started from dialog
        showImportOptionsDialog = self.Settings.getSetting(util.SETTING_RCB_SHOWIMPORTOPTIONSDIALOG).upper() == 'TRUE'
        if showImportOptionsDialog:
            import dialogimportoptions
            constructorParam = "720p"
            try:
                iod = dialogimportoptions.ImportOptionsDialog("script-RCB-importoptions.xml",
                                                              util.getAddonInstallPath(),
                                                              util.getConfiguredSkin(),
                                                              constructorParam, gui=self,
                                                              romCollections=romCollections,
                                                              isRescrape=isRescrape)
            except:
                iod = dialogimportoptions.ImportOptionsDialog("script-RCB-importoptions.xml",
                                                              util.getAddonInstallPath(),
                                                              "Default",
                                                              constructorParam, gui=self,
                                                              romCollections=romCollections,
                                                              isRescrape=isRescrape)
            del iod
        else:
            dialog = xbmcgui.Dialog()

            #32500 = Import Games
            # 32118 = Do you want to import Games now?
            message = "%s[CR]%s" % (util.localize(32500), util.localize(32118))
            retGames = dialog.yesno(util.SCRIPTNAME, message)
            if retGames == True:
                #Import Games
                if romCollections == None:
                    self.doImport(self.config.romCollections, isRescrape, False)
                else:
                    self.doImport(romCollections, isRescrape, False)

    def doImport(self, romCollections, isRescrape, scrapeInBackground, selectedRomCollection=None,
                 selectedScraper=None):

        if scrapeInBackground:
            path = os.path.join(self.Settings.getAddonInfo('path'), 'dbUpLauncher.py')
            log.info('Launch external update script: %s' % path)
            xbmc.executebuiltin("RunScript(%s, selectedRomCollection=%s, selectedScraper=%s)"
                                % (path, selectedRomCollection, selectedScraper))
            #exit RCB
            self.quit = True
            self.exit()
        else:
            import dbupdate

            progressDialog = dialogprogress.ProgressDialogGUI()
            #32111 = Import Games...
            progressDialog.create(util.localize(32111))

            updater = dbupdate.DBUpdate()
            updater.updateDB(self.gdb, progressDialog, romCollections, isRescrape)
            del updater
            progressDialog.writeMsg("", -1)
            del progressDialog

    def checkUpdateInProgress(self):

        Logutil.log("checkUpdateInProgress", util.LOG_LEVEL_INFO)

        scrapeOnStartupAction = self.Settings.getSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION)
        Logutil.log("scrapeOnStartupAction = " + str(scrapeOnStartupAction), util.LOG_LEVEL_INFO)

        if scrapeOnStartupAction == 'update':
            #32112 = Import in Progress
            #32113 = Do you want to cancel current import?
            message = "%s[CR]%s" % (util.localize(32112), util.localize(32113))
            retCancel = xbmcgui.Dialog().yesno(util.SCRIPTNAME, message)
            if retCancel == True:
                self.Settings.setSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION, 'cancel')
            return True

        elif scrapeOnStartupAction == 'cancel':
            #32114 = Cancelling in Progress
            #32205 = Do you want to force cancel current import?
            message = "%s[CR]%s" % (util.localize(32114), util.localize(32205))
            retForceCancel = xbmcgui.Dialog().yesno(util.SCRIPTNAME, message)

            #HACK: Assume that there is a problem with canceling the action
            if retForceCancel == True:
                self.Settings.setSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION, 'nothing')

            return True

        return False

    def saveViewState(self, isOnExit):

        Logutil.log("Begin saveViewState", util.LOG_LEVEL_INFO)

        if self.getListSize() == 0:
            Logutil.log("ListSize == 0 in saveViewState", util.LOG_LEVEL_WARNING)
            return

        selectedGameIndex = self.getCurrentListPosition()
        if selectedGameIndex == -1:
            selectedGameIndex = 0
        if selectedGameIndex == None:
            Logutil.log("selectedGameIndex == None in saveViewState", util.LOG_LEVEL_WARNING)
            return

        self.saveViewMode()

        helper.saveViewState(self.gdb, isOnExit, util.VIEW_MAINVIEW, selectedGameIndex, self.selectedConsoleId,
                             self.selectedGenreId, self.selectedPublisherId, self.selectedDeveloperId,
                             self.selectedYearId, self.selectedCharacter, self.selectedMaxPlayers,
                             self.selectedRating, self.selectedRegion, self.sortMethod, self.sortDirection,
                             self.selectedControlId, None, self.Settings)

        Logutil.log("End saveViewState", util.LOG_LEVEL_INFO)

    def get_selected_view_mode(self):

        view_mode = ""
        for control_id in range(CONTROL_GAMES_GROUP_START, CONTROL_GAMES_GROUP_END + 1):
            try:
                if xbmc.getCondVisibility("Control.IsVisible(%i)" % control_id):
                    view_mode = repr(control_id)
                    break
            except:
                pass

        return view_mode

    def saveViewMode(self):

        Logutil.log("Begin saveViewMode", util.LOG_LEVEL_INFO)

        view_mode = self.get_selected_view_mode()

        self.Settings.setSetting(util.SETTING_RCB_VIEW_MODE, view_mode)

        #favorites
        controlFavorites = self.getControlById(CONTROL_BUTTON_FAVORITE)
        if controlFavorites != None:
            self.Settings.setSetting(util.SETTING_RCB_FAVORITESSELECTED, str(controlFavorites.isSelected()))

        #searchText
        controlSearchText = self.getControlById(CONTROL_BUTTON_SEARCH)
        if controlSearchText != None:
            self.Settings.setSetting(util.SETTING_RCB_SEARCHTEXT, self.searchTerm)

        Logutil.log("End saveViewMode", util.LOG_LEVEL_INFO)

    def loadViewState(self):

        Logutil.log("Begin loadViewState", util.LOG_LEVEL_INFO)

        rcbSetting = helper.getRCBSetting(self.gdb)
        if rcbSetting == None:
            Logutil.log("rcbSetting == None in loadViewState", util.LOG_LEVEL_WARNING)
            return

        #load filter settings
        rcid = rcbSetting[RCBSetting.COL_lastSelectedConsoleId]
        button = self.getControlById(CONTROL_CONSOLES)
        try:
            if rcid > 0:
                romcollection = self.config.getRomCollectionById(str(rcid))
                button.setLabel(romcollection.name)
                self.selectedConsoleId = int(romcollection.id)
            else:
                button.setLabel(util.localize(32120))
        except AttributeError as e:
            log.error('An error occured while loading the filter settings: %s' %e)

        genreid = rcbSetting[RCBSetting.COL_lastSelectedGenreId]
        self.set_filter_foreign_key_object(genreid, CONTROL_GENRE, Genre(self.gdb))
        self.selectedGenreId = genreid

        yearid = rcbSetting[RCBSetting.COL_lastSelectedYearId]
        self.set_filter_foreign_key_object(yearid, CONTROL_YEAR, Year(self.gdb))
        self.selectedYearId = yearid

        publisherid = rcbSetting[RCBSetting.COL_lastSelectedPublisherId]
        self.set_filter_foreign_key_object(publisherid, CONTROL_PUBLISHER, Publisher(self.gdb))
        self.selectedPublisherId = publisherid

        developerid = rcbSetting[RCBSetting.COL_lastSelectedDeveloperId]
        self.set_filter_foreign_key_object(developerid, CONTROL_DEVELOPER, Developer(self.gdb))
        self.selectedDeveloperId = developerid

        maxPlayers = rcbSetting[RCBSetting.COL_lastSelectedMaxPlayers]
        self.selectedMaxPlayers = self.set_filter_text_value(maxPlayers, CONTROL_MAXPLAYERS)

        rating = rcbSetting[RCBSetting.COL_lastSelectedRating]
        button = self.getControlById(CONTROL_RATING)
        try:
            if rating > 0:
                button.setLabel(str(rating))
                self.selectedRating = rating
            else:
                button.setLabel(util.localize(32120))
                self.selectedRating = 0
        except AttributeError as e:
            log.error('An error occured while loading the filter settings: %s' %e)

        region = rcbSetting[RCBSetting.COL_lastSelectedRegion]
        self.selectedRegion = self.set_filter_text_value(region, CONTROL_REGION)

        character = rcbSetting[RCBSetting.COL_lastSelectedCharacter]
        self.selectedCharacter = self.set_filter_text_value(character, CONTROL_CHARACTER)

        #reset view mode
        viewModeId = self.Settings.getSetting(util.SETTING_RCB_VIEW_MODE)
        if viewModeId != None and viewModeId != '':
            xbmc.executebuiltin("Container.SetViewMode(%i)" % int(viewModeId))
            # HACK: This second line is required to reset the viewmode at startup in Kodi 18 (Leia)
            # more info here: https://forum.kodi.tv/showthread.php?tid=329208
            if KodiVersions.getKodiVersion() >= KodiVersions.LEIA:
                xbmc.executebuiltin("Container.SetViewMode(%i)" % int(viewModeId))

        #searchText
        self.searchTerm = self.Settings.getSetting(util.SETTING_RCB_SEARCHTEXT)
        searchButton = self.getControlById(CONTROL_BUTTON_SEARCH)
        if self.searchTerm != '' and searchButton != None:
            searchButton.setLabel(util.localize(32117) + ': ' + self.searchTerm)

        #favorites
        isFavoriteButton = self.getControlById(CONTROL_BUTTON_FAVORITE)
        if isFavoriteButton != None:
            favoritesSelected = self.Settings.getSetting(util.SETTING_RCB_FAVORITESSELECTED)
            isFavoriteButton.setSelected(favoritesSelected == '1')

        #sort method
        self.sortMethod = rcbSetting[RCBSetting.COL_sortMethod]
        if not self.sortMethod:
            self.sortMethod = GameView.FIELDNAMES[GameView.COL_NAME]

        label = self.getControlById(CONTROL_LABEL_SORTBY)
        if label:
            label.setLabel(self.SORT_METHODS[self.sortMethod])
        label = self.getControlById(CONTROL_LABEL_SORTBY_FOCUS)
        if label:
            label.setLabel(self.SORT_METHODS[self.sortMethod])

        #sort direction
        self.sortDirection = rcbSetting[RCBSetting.COL_sortDirection]
        if not self.sortDirection:
            self.sortDirection = 'ASC'

        label = self.getControlById(CONTROL_LABEL_ORDER)
        if label:
            label.setLabel(self.SORT_DIRECTIONS[self.sortDirection])
        label = self.getControlById(CONTROL_LABEL_ORDER_FOCUS)
        if label:
            label.setLabel(self.SORT_DIRECTIONS[self.sortDirection])

        # Reset game list
        self.showGames()

        self.setFilterSelection(CONTROL_GAMES_GROUP_START, rcbSetting[RCBSetting.COL_lastSelectedGameIndex])

        #always set focus on game list on start
        focusControl = self.getControlById(CONTROL_GAMES_GROUP_START)
        if focusControl != None:
            self.setFocus(focusControl)

        self.showGameInfo()

        Logutil.log("End loadViewState", util.LOG_LEVEL_INFO)

    def set_filter_text_value(self, filter_value, control_id):
        button = self.getControlById(control_id)
        try:
            if filter_value != '0':
                button.setLabel(filter_value)
                return filter_value
            else:
                button.setLabel(util.localize(32120))
                return 0
        except AttributeError as e:
            log.error('An error occured while loading the filter settings: %s' % e)
            return 0

    def set_filter_foreign_key_object(self, obj_id, control_id, db_obj):
        button = self.getControlById(control_id)
        try:
            if obj_id > 0:
                row = db_obj.getObjectById(obj_id)
                button.setLabel(row[Genre.COL_NAME])
            else:
                button.setLabel(util.localize(32120))
        except AttributeError as e:
            log.error('An error occured while loading the filter settings: %s' % e)

    def setFilterSelection(self, controlId, selectedIndex):

        Logutil.log("Begin setFilterSelection", util.LOG_LEVEL_DEBUG)

        if selectedIndex != None:
            control = self.getControlById(controlId)
            if control == None:
                Logutil.log("control == None in setFilterSelection", util.LOG_LEVEL_WARNING)
                return 0

            if controlId == CONTROL_GAMES_GROUP_START:
                listSize = self.getListSize()
                if listSize == 0 or selectedIndex > listSize - 1:
                    Logutil.log("ListSize == 0 or index out of range in setFilterSelection", util.LOG_LEVEL_WARNING)
                    return 0

                self.setCurrentListPosition(selectedIndex)
                #HACK: selectItem takes some time and we can't read selectedItem immediately
                xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
                selectedItem = self.getListItem(selectedIndex)

            else:
                if selectedIndex > control.size() - 1:
                    Logutil.log("Index out of range in setFilterSelection", util.LOG_LEVEL_WARNING)
                    return 0

                control.selectItem(selectedIndex)
                #HACK: selectItem takes some time and we can't read selectedItem immediately
                xbmc.sleep(util.WAITTIME_UPDATECONTROLS)
                selectedItem = control.getSelectedItem()

            if selectedItem == None:
                Logutil.log("End setFilterSelection", util.LOG_LEVEL_DEBUG)
                return 0
            label2 = selectedItem.getLabel2()
            Logutil.log("End setFilterSelection", util.LOG_LEVEL_DEBUG)
            return label2
        else:
            Logutil.log("End setFilterSelection", util.LOG_LEVEL_DEBUG)
            return 0

    def set_isfavorite_for_game(self, selected_game):
        log.info("set_isfavorite_for_game")
        if selected_game is None:
            #32014 = Can't load selected Game
            #32016 = Add To Favorites Error
            message = "%s[CR]%s" % (util.localize(32016), util.localize(32014))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            return

        isFavorite = '1'
        if selected_game.getProperty('isfavorite') == '1':
            isFavorite = '0'

        log.info("Updating game '{0}' set isFavorite = {1}".format(selected_game.getLabel(), isFavorite))
        Game(self.gdb).update(('isfavorite',), (isFavorite,), selected_game.getProperty('gameId'), True)
        self.gdb.commit()

        if isFavorite == '0':
            isFavorite = ''
        selected_game.setProperty('isfavorite', str(isFavorite))

    def set_isfavorite_for_selection(self, selected_game):
        log.info("set_isfavorite_for_selection")
        if selected_game is None:
            # 32014 = Can't load selected Game
            # 32016 = Add To Favorites Error
            message = "%s[CR]%s" % (util.localize(32016), util.localize(32014))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            return

        isFavorite = '1'
        if selected_game.getProperty('isfavorite') == '1':
            isFavorite = '0'

        listSize = self.getListSize()
        for i in range(0, listSize):
            listItem = self.getListItem(i)

            log.info("Updating game '{0}' set isfavorite = {1}".format(listItem.getLabel(), isFavorite))
            Game(self.gdb).update(('isfavorite',), (isFavorite,), listItem.getProperty('gameId'), True)
            listItem.setProperty('isfavorite', str(isFavorite))
        self.gdb.commit()

        #HACK: removing favorites does not update the UI. So do it manually.
        if str(isFavorite) == '0':
            self.showGames()

    def getControlById(self, controlId):
        try:
            control = self.getControl(controlId)
        except Exception as exc:
            #HACK there seems to be a problem with recognizing the scrollbar controls
            if controlId not in (CONTROL_SCROLLBARS):
                Logutil.log("Control with id: %s could not be found. Check WindowXML file. Error: %s" % (
                str(controlId), str(exc)), util.LOG_LEVEL_ERROR)
                self.writeMsg(util.localize(32025) % str(controlId))
            return None

        return control

    def writeMsg(self, msg, count=0):

        control = self.getControlById(CONTROL_LABEL_MSG)
        if control == None:
            Logutil.log("RCB_WARNING: control == None in writeMsg", util.LOG_LEVEL_WARNING)
            return
        try:
            control.setLabel(msg)
        except:
            pass

    def exit(self):

        Logutil.log("exit", util.LOG_LEVEL_INFO)

        self.saveViewState(True)

        self.gdb.close()
        self.close()


def main():
    skin = util.getConfiguredSkin()

    kodiVersion = KodiVersions.getKodiVersion()
    Logutil.log("Kodi Version = " + str(kodiVersion), util.LOG_LEVEL_INFO)

    if KodiVersions.getKodiVersion() > KodiVersions.KRYPTON:
        ui = UIGameDB("script-Rom_Collection_Browser-main.xml", util.getAddonInstallPath(), skin, "720p", True)
    else:
        ui = UIGameDB("script-Rom_Collection_Browser-main.xml", util.getAddonInstallPath(), skin, "720p")

    ui.doModal()
    del ui


main()
