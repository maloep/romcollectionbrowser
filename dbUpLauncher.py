import os
import sys

import xbmc, xbmcgui, xbmcaddon

# Shared resources
addonPath = ''
addon = xbmcaddon.Addon(id='script.games.rom.collection.browser')
addonPath = addon.getAddonInfo('path')

BASE_RESOURCE_PATH = os.path.join(addonPath, "resources")

sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib", "pyscraper"))

from gamedatabase import GameDataBase
import util
import dbupdate
import config


class ProgressDialogBk(xbmcgui.DialogProgressBG):

    itemCount = 0

    def writeMsg(self, line1, line2, line3, count=0):
        xbmc.log('writeMsg')

        scrapeOnStartupAction = addon.getSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION)
        xbmc.log('scrapeOnStartupAction = ' + scrapeOnStartupAction)
        if (scrapeOnStartupAction == 'cancel'):
            self.update(100, 'Rom Collection Browser', 'Update canceled')
            return False

        if count > 0:
            percent = int(count * (float(100) / self.itemCount))
        else:
            percent = 0
        self.update(percent, line1, line2)

        return True


def runUpdate():
    xbmc.log('runUpdate')

    gdb = GameDataBase(util.getAddonDataPath())
    gdb.connect()
    #create db if not existent and maybe update to new version
    gdb.checkDBStructure()

    configFile = config.Config(None)
    statusOk, errorMsg = configFile.readXml()

    settings = util.getSettings()
    settings.setSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION, 'update')

    progress = ProgressDialogBk()
    progress.create('Rom Collection Browser', 'Update DB')

    dbupdate.DBUpdate().updateDB(gdb, progress, configFile.romCollections, False)

    settings.setSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION, 'nothing')
    progress.close()

if __name__ == "__main__":
    runUpdate()
