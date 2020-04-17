from __future__ import print_function
from __future__ import absolute_import
from builtins import str
import xbmc, xbmcgui
import helper, util
from base_launcher import AbstractLauncher
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
        print ('RCB: onPlaybackEnded')

        if (self.gui == None):
            print ("RCB_WARNING: gui == None in MyPlayer")
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
        self.selectedDeveloperId = kwargs["developerId"]
        self.selectedCharacter = kwargs["selectedCharacter"]
        self.selectedMaxPlayers = kwargs["selectedMaxPlayers"]
        self.selectedRating = kwargs["selectedRating"]
        self.selectedRegion = kwargs["selectedRegion"]
        self.sortMethod = kwargs["sortMethod"]
        self.sortDirection = kwargs["sortDirection"]
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
            Logutil.log("onAction exit UIGameInfoView", util.LOG_LEVEL_INFO)

            #stop Player (if playing)
            if (xbmc.Player().isPlayingVideo()):
                xbmc.Player().stop()

            self.close()

    def showGame(self):

        Logutil.log("Begin showGameList UIGameInfoView", util.LOG_LEVEL_INFO)

        self.clearList()

        game = GameView(self.gdb).getGameById(self.selectedGameId)

        item = xbmcgui.ListItem(game[DataBaseObject.COL_NAME], str(game[GameView.COL_ID]))

        romcollection_id = str(game[GameView.COL_romCollectionId])
        try:
            romCollection = self.config.romCollections[romcollection_id]
        except KeyError:
            Logutil.log('Cannot get rom collection with id: ' + romcollection_id,
                        util.LOG_LEVEL_ERROR)

        item.setProperty('romCollectionId', romcollection_id)
        item.setProperty('romcollection', romCollection.name)
        item.setProperty('console', romCollection.name)
        item.setProperty('gameId', str(game[GameView.COL_ID]))
        item.setProperty('plot', game[GameView.COL_description])
        item.setProperty('developer', game[GameView.COL_developer])
        item.setProperty('publisher', game[GameView.COL_publisher])
        item.setProperty('year', game[GameView.COL_year])
        item.setProperty('genre', game[GameView.COL_genre])
        item.setProperty('gameCmd', game[GameView.COL_gameCmd])
        item.setProperty('alternateGameCmd', game[GameView.COL_alternateGameCmd])
        item.setProperty('playcount', str(game[GameView.COL_launchCount]))
        item.setProperty('originalTitle', game[GameView.COL_originalTitle])
        item.setProperty('alternateTitle', game[GameView.COL_alternateTitle])

        item.setProperty('rating', str(game[GameView.COL_rating]))
        item.setProperty('media', str(game[GameView.COL_media]))
        item.setProperty('controllertype', str(game[GameView.COL_controllerType]))
        item.setProperty('region', str(game[GameView.COL_region]))
        item.setProperty('maxplayers', str(game[GameView.COL_maxPlayers]))
        item.setProperty('url', str(game[GameView.COL_url]))

        if game[GameView.COL_isFavorite] == 1:
            item.setProperty('isfavorite', '1')
        else:
            item.setProperty('isfavorite', '')

        item.setArt({
            'icon': helper.get_file_for_control_from_db(
                romCollection.imagePlacingMain.fileTypesForGameList, game),
            'thumb': helper.get_file_for_control_from_db(
                romCollection.imagePlacingMain.fileTypesForGameListSelected, game),

            IMAGE_CONTROL_BACKGROUND: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewBackground, game),
            IMAGE_CONTROL_GAMEINFO_BIG: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoBig, game),

            IMAGE_CONTROL_GAMEINFO_UPPERLEFT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoUpperLeft, game),
            IMAGE_CONTROL_GAMEINFO_UPPERRIGHT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoUpperRight, game),
            IMAGE_CONTROL_GAMEINFO_LOWERLEFT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLowerLeft, game),
            IMAGE_CONTROL_GAMEINFO_LOWERRIGHT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLowerRight, game),

            IMAGE_CONTROL_GAMEINFO_UPPER: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoUpper, game),
            IMAGE_CONTROL_GAMEINFO_LOWER: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLower, game),
            IMAGE_CONTROL_GAMEINFO_LEFT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoLeft, game),
            IMAGE_CONTROL_GAMEINFO_RIGHT: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainViewGameInfoRight, game),

            IMAGE_CONTROL_1: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainView1, game),
            IMAGE_CONTROL_2: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainView2, game),
            IMAGE_CONTROL_3: helper.get_file_for_control_from_db(
                romCollection.imagePlacingInfo.fileTypesForMainView3, game)
        })

        #add item to listcontrol
        listcontrol = self.getControlById(CONTROL_GAME_LIST)
        listcontrol.addItem(item)

        self.writeMsg("")

        Logutil.log("End showGameList UIGameInfoView", util.LOG_LEVEL_INFO)

    def launchEmu(self):

        Logutil.log("Begin launchEmu UIGameInfoView", util.LOG_LEVEL_INFO)

        AbstractLauncher(self.gdb, self.config, self).launch_game(self.selectedGameId, self.selectedGame)

        self.saveViewState(False)
        self.close()

        Logutil.log("End launchEmu UIGameInfoView", util.LOG_LEVEL_INFO)

    def saveViewState(self, isOnExit):

        Logutil.log("Begin saveViewState UIGameInfoView", util.LOG_LEVEL_INFO)

        helper.saveViewState(self.gdb, isOnExit, 'gameInfoView', self.selectedGameIndex, self.selectedConsoleId,
                             self.selectedGenreId, self.selectedPublisherId, self.selectedDeveloperId,
                             self.selectedYearId, self.selectedCharacter, self.selectedMaxPlayers,
                             self.selectedRating, self.selectedRegion, self.sortMethod, self.sortDirection,
                             self.selectedControlIdMainView, self.selectedControlId, self.settings)

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
