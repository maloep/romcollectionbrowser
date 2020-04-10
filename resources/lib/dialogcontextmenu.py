from __future__ import absolute_import
from builtins import str
from builtins import range
from builtins import object
import xbmcgui

import util, helper

from gamedatabase import *
from util import *
from config import *
from util import Logutil as log

ACTION_CANCEL_DIALOG = (9, 10, 51, 92, 110)
CONTROL_BUTTON_SETFAVORITE_GAME = 5118
CONTROL_BUTTON_SETFAVORITE_SELECTION = 5119


class ContextMenuDialog(object):
    selectedGame = None
    gameRow = None

    def __init__(self, *args, **kwargs):
        log.info("init ContextMenu")

        self.gui = kwargs["gui"]

        self.selectedGame = self.gui.getSelectedItem()

        game_favorites_option = util.localize(32507) # Add Game To Favorites
        selection_favorites_option = util.localize(32508) # Add Selection To Favorites

        if self.selectedGame is not None:
            if self.selectedGame.getProperty('isfavorite') == '1':
                game_favorites_option = util.localize(32133) # Remove Game From Favorites
                selection_favorites_option = util.localize(32134) # Remove Selection From Favorites

        options = [
            util.localize(32501), # Rescrape selected Game
            util.localize(32502), # Rescrape Selection
            util.localize(32506), # Edit Game Command
            game_favorites_option,
            selection_favorites_option,
            util.localize(32510)  # Delete Game
        ]

        # add set gameclient option
        if helper.isRetroPlayerSupported():
            log.info("RetroPlayer is supported: add option set Gameclient")
            options.append(util.localize(32514)) # Set Gameclient (per Game)

        dialog = xbmcgui.Dialog()
        choice = dialog.contextmenu(options)
        log.info("Selected option from Context Menu: %s" %choice)

        if choice < 0:
            return

        if choice == 0:
            self.rescrape_game()
        elif choice == 1:
            self.rescrape_selection()
        elif choice == 2:
            self.edit_game_command()
        elif choice == 3:
            self.gui.set_isfavorite_for_game(self.selectedGame)
        elif choice == 4:
            self.gui.set_isfavorite_for_selection(self.selectedGame)
        elif choice == 5:
            self.delete_game()
        elif choice == 6:
            self.set_gameclient()

    def rescrape_game(self):
        log.info("rescrape_game")
        if self.selectedGame is None:
            #32013 = Rescrape game error
            #32014 = Can't load selected Game
            message = "%s[CR]%s" %(util.localize(32013), util.localize(32014))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            return

        romCollectionId = self.selectedGame.getProperty('romCollectionId')
        romCollection = self.gui.config.romCollections[str(romCollectionId)]
        files = File(self.gui.gdb).getRomsByGameId(self.selectedGame.getProperty('gameId'))
        filename = files[0][0]
        romCollection.romPaths = (filename,)

        romCollections = {}
        romCollections[romCollection.id] = romCollection

        self.gui.rescrapeGames(romCollections)

    def rescrape_selection(self):
        log.info("rescrape_selection")
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

    def edit_game_command(self):
        log.info("edit_game_command")
        if self.selectedGame == None:
            #32014 = Can't load selected Game
            #32015 = Edit Game Command Error
            message = "%s[CR]%s" % (util.localize(32015), util.localize(32014))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            return

        origCommand = self.selectedGame.getProperty('gameCmd')
        command = xbmcgui.Dialog().input(util.localize(32135), defaultt=origCommand, type=xbmcgui.INPUT_ALPHANUM)

        if command != origCommand:
            log.info("Updating game '{0}' with command '{1}'".format(self.selectedGame.getLabel(), command))
            Game(self.gui.gdb).update(('gameCmd',), (command,), self.selectedGame.getProperty('gameId'), True)
            self.gui.gdb.commit()

    def delete_game(self):
        log.info("delete_game")
        pos = self.gui.getCurrentListPosition()
        if pos == -1:
            #32017 = Delete Game Error
            #32018 = Can't delete selected Game
            message = "%s[CR]%s" % (util.localize(32017), util.localize(32018))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            return
        dialog = xbmcgui.Dialog()
        #32510 = Delete Game
        #32136 = "Are you sure you want to delete this game?
        if dialog.yesno(util.localize(32510), util.localize(32136)):
            gameID = self.selectedGame.getProperty('gameId')
            self.gui.deleteGame(gameID)
            self.gui.showGames()
            from gui import CONTROL_GAMES_GROUP_START
            if pos > 0:
                pos = pos - 1
                self.gui.setFilterSelection(CONTROL_GAMES_GROUP_START, pos)
            else:
                self.gui.setFilterSelection(CONTROL_GAMES_GROUP_START, 0)

    def set_gameclient(self):
        log.info("set_gameclient")
        if not helper.isRetroPlayerSupported():
            log.info("This RetroPlayer branch does not support selecting gameclients.")
            return

        if self.selectedGame is None or self.gameRow is None:
            # 32014 = Can't load selected Game
            # 32015 = Edit Game Command Error
            message = "%s[CR]%s" % (util.localize(32015), util.localize(32014))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
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
