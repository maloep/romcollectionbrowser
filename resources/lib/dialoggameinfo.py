import xbmc, xbmcgui
import helper, util
from launcher import RCBLauncher
from util import *
from gamedatabase import *

ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)
ACTION_MOVEMENT_LEFT = (1,)
ACTION_MOVEMENT_RIGHT = (2,)
ACTION_MOVEMENT_UP = (3,)
ACTION_MOVEMENT_DOWN = (4,)
ACTION_MOVEMENT = (1, 2, 3, 4,)

CONTROL_BUTTON_PLAYGAME = 3000

CONTROL_GAME_LIST_GROUP = 1000
CONTROL_GAME_LIST = 8200

CONTROL_LABEL_MSG = 4000

RCBHOME = util.getAddonInstallPath()


class MyPlayer(xbmc.Player):
    gui = None

    def onPlayBackEnded(self):
        print 'RCB: onPlaybackEnded'

        if (self.gui == None):
            print "RCB_WARNING: gui == None in MyPlayer"
            return

        self.gui.setFocus(self.gui.getControl(CONTROL_BUTTON_PLAYGAME))


class UIGameInfoView(xbmcgui.WindowXMLDialog):
    __useRefactoredView = False

    def __init__(self, *args, **kwargs):
        Logutil.log("Init GameInfoView", util.LOG_LEVEL_INFO)

        self.gdb = kwargs["gdb"]
        self.selectedGameId = kwargs["gameId"]
        self.selectedGame = kwargs["listItem"]
        self.config = kwargs["config"]
        self.settings = kwargs["settings"]
        self.selectedConsoleId = kwargs["consoleId"]
        self.selectedGenreId = kwargs["genreId"]
        self.selectedYearId = kwargs["yearId"]
        self.selectedPublisherId = kwargs["publisherId"]
        self.selectedConsoleIndex = kwargs["consoleIndex"]
        self.selectedGenreIndex = kwargs["genreIndex"]
        self.selectedYearIndex = kwargs["yearIndex"]
        self.selectedPublisherIndex = kwargs["publisherIndex"]
        self.selectedCharacter = kwargs["selectedCharacter"]
        self.selectedCharacterIndex = kwargs["selectedCharacterIndex"]
        self.selectedGameIndex = kwargs["selectedGameIndex"]
        self.selectedControlIdMainView = kwargs["controlIdMainView"]
        self.fileTypeGameplay = kwargs["fileTypeGameplay"]

        self.player = MyPlayer()
        self.player.gui = self

        self.doModal()

    def onInit(self):

        Logutil.log("Begin OnInit UIGameInfoView", util.LOG_LEVEL_INFO)

        self.showGame()

        control = self.getControlById(CONTROL_BUTTON_PLAYGAME)
        if (control != None):
            self.setFocus(control)

        xbmc.sleep(util.WAITTIME_UPDATECONTROLS)

        Logutil.log("End OnInit UIGameInfoView", util.LOG_LEVEL_INFO)

    def onClick(self, controlId):
        Logutil.log("Begin onClick UIGameInfoView", util.LOG_LEVEL_DEBUG)

        if (controlId == CONTROL_BUTTON_PLAYGAME):
            self.launchEmu()

        Logutil.log("End onClick UIGameInfoView", util.LOG_LEVEL_DEBUG)

    def onFocus(self, controlId):
        Logutil.log("onFocus UIGameInfoView", util.LOG_LEVEL_DEBUG)
        self.selectedControlId = controlId

    def onAction(self, action):

        if (action.getId() in ACTION_CANCEL_DIALOG):
            Logutil.log("onAction exit UIGameInfoView", util.LOG_LEVEL_DEBUG)

            #stop Player (if playing)
            if (xbmc.Player().isPlayingVideo()):
                xbmc.Player().stop()

            self.close()

    def showGame(self):

        Logutil.log("Begin showGameList UIGameInfoView", util.LOG_LEVEL_INFO)

        self.clearList()

        item = xbmcgui.ListItem(self.selectedGame.getLabel(), self.selectedGame.getLabel2())
        item.setProperty('romCollectionId', self.selectedGame.getProperty('romCollectionId'))

        # Properties from the game object
        for var in ['maxplayers', 'rating', 'votes', 'url', 'region', 'media', 'perspective', 'controllertype',
                    'originalTitle', 'alternateTitle', 'translatedby', 'version', 'playcount', 'plot', 'year',
                    'publisher', 'developer', 'genre', 'firstRom']:
            try:
                item.setProperty(var, self.selectedGame.getProperty(var))
            except AttributeError as e:
                Logutil.log('Error retrieving property ' + var + ': ' + str(e), util.LOG_LEVEL_WARNING)
                item.setProperty(var, '')

        romCollection = None
        try:
            romCollection = self.config.romCollections[self.selectedGame.getProperty('romCollectionId')]
        except:
            Logutil.log(util.localize(32023) % self.selectedGame.getProperty('romCollectionId'), util.LOG_LEVEL_ERROR)

        # Rom Collection properties
        item.setProperty('romcollection', romCollection.name)
        item.setProperty('console', romCollection.name)

        item.setArt({
            'icon': helper.get_file_for_control_from_db(
                romCollection.imagePlacingMain.fileTypesForGameList, self.selectedGame),
            'thumb': helper.get_file_for_control_from_db(
                romCollection.imagePlacingMain.fileTypesForGameListSelected, self.selectedGame),

            IMAGE_CONTROL_BACKGROUND: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewBackground, self.selectedGame),
            IMAGE_CONTROL_GAMEINFO_BIG: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoBig, self.selectedGame),

            IMAGE_CONTROL_GAMEINFO_UPPERLEFT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoUpperLeft, self.selectedGame),
            IMAGE_CONTROL_GAMEINFO_UPPERRIGHT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoUpperRight, self.selectedGame),
            IMAGE_CONTROL_GAMEINFO_LOWERLEFT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLowerLeft, self.selectedGame),
            IMAGE_CONTROL_GAMEINFO_LOWERRIGHT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLowerRight, self.selectedGame),

            IMAGE_CONTROL_GAMEINFO_UPPER: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoUpper, self.selectedGame),
            IMAGE_CONTROL_GAMEINFO_LOWER: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLower, self.selectedGame),
            IMAGE_CONTROL_GAMEINFO_LEFT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLeft, self.selectedGame),
            IMAGE_CONTROL_GAMEINFO_RIGHT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoRight, self.selectedGame),

            IMAGE_CONTROL_1: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainView1, self.selectedGame),
            IMAGE_CONTROL_2: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainView2, self.selectedGame),
            IMAGE_CONTROL_3: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainView3, self.selectedGame)
        })

        #add item to listcontrol
        listcontrol = self.getControlById(CONTROL_GAME_LIST)
        listcontrol.addItem(item)

        self.writeMsg("")

        Logutil.log("End showGameList UIGameInfoView", util.LOG_LEVEL_INFO)

    def launchEmu(self):

        Logutil.log("Begin launchEmu UIGameInfoView", util.LOG_LEVEL_INFO)

        launcher = RCBLauncher()
        launcher.launchEmu(self.gdb, self, self.selectedGameId, self.config, self.selectedGame)

        self.saveViewState(False)
        self.close()

        Logutil.log("End launchEmu UIGameInfoView", util.LOG_LEVEL_INFO)

    def saveViewState(self, isOnExit):

        Logutil.log("Begin saveViewState UIGameInfoView", util.LOG_LEVEL_INFO)

        #TODO: save selectedGameIndex from main view
        selectedGameIndex = 0

        helper.saveViewState(self.gdb, isOnExit, 'gameInfoView', selectedGameIndex, self.selectedConsoleIndex,
                             self.selectedGenreIndex, self.selectedPublisherIndex,
                             self.selectedYearIndex, self.selectedCharacterIndex, self.selectedControlIdMainView,
                             self.selectedControlId, self.settings)

        Logutil.log("End saveViewState UIGameInfoView", util.LOG_LEVEL_INFO)

    def getControlById(self, controlId):
        try:
            control = self.getControl(controlId)
        except:
            Logutil.log("Control with id: %s could not be found. Check WindowXML file." % str(controlId),
                        util.LOG_LEVEL_ERROR)
            self.writeMsg(util.localize(32025) % str(controlId))
            return None

        return control

    def writeMsg(self, msg):
        control = self.getControlById(CONTROL_LABEL_MSG)
        if (control == None):
            return

        control.setLabel(msg)
