# Copyright (C) 2009-2018 Malte Loepmann (maloep@googlemail.com)
#
# This program is free software; you can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation;
# either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program;
# if not, see <http://www.gnu.org/licenses/>.


from builtins import str
from builtins import object
import os, sys, re

import xbmc
import xbmcaddon

# Shared resources
addon = xbmcaddon.Addon(id='script.games.rom.collection.browser')
addonPath = addon.getAddonInfo('path')

BASE_RESOURCE_PATH = os.path.join(addonPath, "resources")

sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib", "pyscraper"))

# append the proper platforms folder to our path, xbox is the same as win32
env = (os.environ.get("OS", "win32"), "win32",)[os.environ.get("OS", "win32") == "xbox"]

# Check to see if using a 64bit version of Linux
if re.match("Linux", env):
    try:
        import platform

        env2 = platform.machine()
        if (env2 == "x86_64"):
            env = "Linux64"
    except ImportError:
        env = 'Linux'

sys.path.append(os.path.join(BASE_RESOURCE_PATH, "platform_libraries", env))


class dummyGUI(object):
    player = xbmc.Player()

    xbmcversion = xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')
    xbmcversionNo = xbmcversion[0:2]

    def writeMsg(self, message):
        pass

    def saveViewState(self, isOnExit):
        pass


class Main(object):

    def __init__(self):
        xbmc.log('RCB: sys.argv = ' + str(sys.argv))
        launchRCB = False
        for arg in sys.argv:
            param = str(arg)
            xbmc.log('RCB: param = ' + param)
            if param == '' or param == 'script.games.rom.collection.browser' or param == 'default.py':
                xbmc.log('RCB: setting launchRCB = True')
                launchRCB = True

            #provide data that skins can show on home screen
            if 'limit=' in param:
                xbmc.log('RCB: setting launchRCB = False')
                launchRCB = False
                #check if RCB should be launched at startup (via RCB Service)
                launchOnStartup = addon.getSetting('rcb_launchOnStartup')
                if (launchOnStartup.lower() == 'true'):
                    xbmc.log("RCB: RCB will be started via RCB service. Won't gather widget data on this run.")
                else:
                    self.gatherWidgetData(param)

            if 'launchid' in param:
                launchRCB = False
                self.launchGame(param)

        # Start the main gui
        xbmc.log('RCB: launchRCB = ' + str(launchRCB))
        if launchRCB:
            import gui

    def gatherWidgetData(self, param):
        xbmc.log('start gatherWidgetData')
        import util, helper
        from gamedatabase import DataBaseObject, GameView, GameDataBase
        from config import Config

        gdb = GameDataBase(util.getAddonDataPath())
        gdb.connect()

        doImport, errorMsg = gdb.checkDBStructure()
        if (doImport) > 0:
            xbmc.log("RCB: No database available. Won't gather any data.")
            gdb.close()
            return
        elif (doImport < 0):
            xbmc.log("RCB: Error occured while checking db structure: {0}" % errorMsg)

        limit = param.replace('limit=', '')
        query = 'Select * From GameView Where launchCount > 0 Order by launchCount desc Limit %s;' % str(limit)
        games = GameView(gdb).getGamesByQueryNoArgs(query)
        xbmc.log('most played games: %s' % games)

        config = Config(None)
        statusOk, errorMsg = config.readXml()

        if (not statusOk):
            xbmc.log('RCB: Error reading config.xml: {0}' % errorMsg)
            return

        import xbmcgui
        count = 0
        for game in games:

            count += 1
            try:
                xbmc.log("RCB widget: Gathering data for rom no %i: %s" % (count, game[GameView.COL_NAME]))

                romCollection = config.romCollections[str(game[GameView.COL_romCollectionId])]

                #get artwork that is chosen to be shown in gamelist
                thumb = helper.get_file_for_control_from_db(
                    romCollection.imagePlacingMain.fileTypesForGameList, game)
                fanart = helper.get_file_for_control_from_db(
                    romCollection.imagePlacingMain.fileTypesForMainViewBackground, game)

                url = "plugin://script.games.rom.collection.browser/?launchid=%s" % game[GameView.COL_ID]

                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Id" % count, str(game[GameView.COL_ID]))
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Console" % count, romCollection.name)
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Title" % count, game[GameView.COL_NAME])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Thumb" % count, thumb)
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Fanart" % count, fanart)
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Plot" % count, game[GameView.COL_description])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Year" % count, game[GameView.COL_year])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Publisher" % count, game[GameView.COL_publisher])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Developer" % count, game[GameView.COL_developer])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Genre" % count, game[GameView.COL_genre])

                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Maxplayers" % count, game[GameView.COL_maxPlayers])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Region" % count, game[GameView.COL_region])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Media" % count, game[GameView.COL_description])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Perspective" % count, game[GameView.COL_perspective])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Controllertype" % count, game[GameView.COL_controllerType])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Playcount" % count, game[GameView.COL_launchCount])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Rating" % count, game[GameView.COL_rating])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Votes" % count, game[GameView.COL_numVotes])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Url" % count, game[GameView.COL_url])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Originaltitle" % count, game[GameView.COL_originalTitle])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Alternatetitle" % count, game[GameView.COL_alternateTitle])
                xbmcgui.Window(10000).setProperty("MostPlayedROM.%d.Version" % count, game[GameView.COL_version])

            except Exception as exc:
                xbmc.log('RCB: Error while getting most played games: ' + str(exc))

        gdb.close()

    def launchGame(self, param):
        import util
        from launcher import RCBLauncher
        from gamedatabase import GameDataBase
        from config import Config

        gdb = GameDataBase(util.getAddonDataPath())
        gdb.connect()

        #HACK if invoked from widget addon there is an additional ? in param
        param = param.replace('?', '')
        gameId = int(param.replace('launchid=', ''))

        config = Config(None)
        config.readXml()

        gui = dummyGUI()

        RCBLauncher().launchEmu(gdb, gui, gameId, config, None)


if __name__ == "__main__":
    xbmc.log('RCB started')
    try:
        Main()
    except Exception as exc:
        message = 'Unhandled exception occured during execution of RCB:'
        message2 = str(exc)
        message3 = 'See xbmc.log for details'
        xbmc.log(message)
        xbmc.log(message2)
        import xbmcgui

        xbmcgui.Dialog().ok("Rom Collection Browser", "%s[CR]%s[CR]%s" %(message, message2, message3))
