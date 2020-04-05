from builtins import str
from builtins import object
import os
import sys

import xbmc, xbmcgui, xbmcaddon

# Shared resources
addon = xbmcaddon.Addon(id='script.games.rom.collection.browser')
addonPath = addon.getAddonInfo('path')

BASE_RESOURCE_PATH = os.path.join(addonPath, "resources")

sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib", "pyscraper"))

from gamedatabase import GameDataBase
import util
import dbupdate
import config
from config import Site

monitor = xbmc.Monitor()


class HandleAbort(object):
    orig_scraping_mode = ''

    def __enter__(self):
        xbmc.log("HandleAbort enter")

        settings = util.getSettings()
        settings.setSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION, 'update')

        #set scraping mode to accurate
        self.orig_scraping_mode = settings.getSetting(util.SETTING_RCB_SCRAPINGMODE)
        settings.setSetting(util.SETTING_RCB_SCRAPINGMODE, util.SCRAPING_OPTION_AUTO_ACCURATE_TXT)

        return True

    def __exit__(self, type, value, traceback):
        xbmc.log("HandleAbort exit")

        settings = util.getSettings()
        settings.setSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION, 'nothing')

        #restore original scraping mode
        settings.setSetting(util.SETTING_RCB_SCRAPINGMODE, self.orig_scraping_mode)


class ProgressDialogBk(xbmcgui.DialogProgressBG):
    itemCount = 0
    heading = ""

    def writeMsg(self, message, count=0):
        xbmc.log('writeMsg')

        scrapeOnStartupAction = addon.getSetting(util.SETTING_RCB_SCRAPEONSTARTUPACTION)
        xbmc.log('scrapeOnStartupAction = ' + scrapeOnStartupAction)
        if scrapeOnStartupAction == 'cancel':
            self.update(100, 'Rom Collection Browser', 'Update canceled')
            return False

        if count > 0:
            percent = int(count * (float(100) / self.itemCount))
        else:
            percent = 0
        self.update(percent, self.heading, message)

        return True


def runUpdate():
    xbmc.log('RCB: runUpdate')

    gdb = GameDataBase(util.getAddonDataPath())
    gdb.connect()
    #create db if not existent and maybe update to new version
    gdb.checkDBStructure()

    configFile = config.Config(None)
    configFile.readXml()

    selectedRomCollection = ''
    selectedScraper = ''

    xbmc.log('RCB: parameters = %s' % sys.argv)
    for arg in sys.argv:
        param = str(arg)
        xbmc.log('RCB: param = %s' % param)

        if 'selectedRomCollection' in param:
            selectedRomCollection = param.replace('selectedRomCollection=', '')
        if 'selectedScraper' in param:
            selectedScraper = param.replace('selectedScraper=', '')

    romCollections = configFile.romCollections
    if selectedRomCollection and selectedScraper:
        romCollections = prepareRomCollections(configFile, selectedRomCollection, selectedScraper)

    progress = ProgressDialogBk()
    progress.heading = util.SCRIPTNAME
    progress.create(util.SCRIPTNAME, 'Update DB')

    with HandleAbort():
        dbupdate.DBUpdate().updateDB(gdb, progress, romCollections, False)

    progress.close()


def prepareRomCollections(config, selectedRC, siteName):
    xbmc.log('prepareRomCollections')

    #32120 = All
    if selectedRC == util.localize(32120):
        romCollections = config.romCollections
    else:
        romCollections = {}
        romCollection = config.getRomCollectionByName(selectedRC)
        romCollections[romCollection.id] = romCollection

    for rcId in list(romCollections.keys()):
        romCollection = config.romCollections[rcId]

        sites = []

        for site in romCollection.scraperSites:
            # check if it is the selected scraper or
            # 32804 = Use configured default scrapers
            # search for default scraper or check if we only have one scraper and use this one
            if site.name == siteName or (siteName == util.localize(32804) and
                                         (site.default or len(romCollection.scraperSites) == 1)):
                sites.append(site)
                break

        # if we did not find a scraper lets assume the selected scraper is not available in current rom collection
        # create it and set it to default
        if len(sites) == 0:
            site = Site()
            site.name = siteName
            site.default = True
            sites.append(site)

        romCollection.scraperSites = sites

    return romCollections


if __name__ == "__main__":
    runUpdate()
