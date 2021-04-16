

from base_launcher import AbstractLauncher
from util import Logutil as log
from gamedatabase import *

import xbmcgui

class RetroPlayer_Launcher(AbstractLauncher):

    def __init__(self):
        pass

    def launch(self, romCollection, gameRow, cmd, roms, listitem):
        log.info("launching game with internal emulator")
        rom = roms[0]
        gameclient = romCollection.gameclient
        # HACK: use alternateGameCmd as gameclient
        if gameRow[GameView.COL_alternateGameCmd] is not None and gameRow[GameView.COL_alternateGameCmd] != "":
            gameclient = str(gameRow[GameView.COL_alternateGameCmd])
        log.info("Preferred gameclient: " + gameclient)
        log.info("Setting platform: " + romCollection.name)

        # if game is launched from RCB widget there is no listitem
        if listitem is None:
            listitem = xbmcgui.ListItem(rom)

        parameters = {"platform": romCollection.name}
        if gameclient != "":
            parameters["gameclient"] = gameclient
        listitem.setInfo(type="game", infoLabels=parameters)
        log.info("launching rom: " + rom)

        self.gui.player.play(rom, listitem)
        # xbmc.executebuiltin('PlayMedia(\"%s\", platform=%s, gameclient=%s)' %(rom, romCollection.name, romCollection.gameclient))
        return