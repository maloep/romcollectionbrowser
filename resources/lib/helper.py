import logging
from builtins import str
import json
import os, re
import glob

from gamedatabase import *
from config import FileType
from util import Logutil
import util
import xbmc, xbmcgui


def saveReadString(prop):
    try:
        result = str(prop)
    except:
        result = u''

    return result


def get_file_for_control_from_db(file_types, game):
    """
    Read media files from db entry. Media files are stored as fileType1, fileType2, ... in db with the filetype id at the end of the name
    :param file_types:
    :param game:
    :return:
    """
    log.debug("begin get_file_for_control_from_db")

    for file_type in file_types:
        prop = 'COL_fileType%s' %file_type.id
        file = game[getattr(GameView, prop)]
        if file:
            return file
    return ""


def saveViewState(gdb, isOnExit, selectedView, selectedGameIndex, selectedConsoleId, selectedGenreId,
                  selectedPublisherId, selectedDeveloperId, selectedYearId, selectedCharacter, selectedMaxPlayers,
                  selectedRating, selectedRegion, sortMethod, sortDirection,
                  selectedControlIdMainView, selectedControlIdGameInfoView, settings):
    log.info("Begin helper.saveViewState")

    if isOnExit:
        #saveViewStateOnExit
        saveViewState = settings.getSetting(util.SETTING_RCB_SAVEVIEWSTATEONEXIT).upper() == 'TRUE'
    else:
        #saveViewStateOnLaunchEmu
        saveViewState = settings.getSetting(util.SETTING_RCB_SAVEVIEWSTATEONLAUNCHEMU).upper() == 'TRUE'

    rcbSetting = getRCBSetting(gdb)
    if rcbSetting == None:
        log.warn("rcbSetting == None in helper.saveViewState")
        return

    if saveViewState:
        RCBSetting(gdb).update(('lastSelectedView', 'lastSelectedConsoleId', 'lastSelectedGenreId',
                                'lastSelectedPublisherId', 'lastSelectedDeveloperId', 'lastSelectedYearId',
                                'lastSelectedGameIndex', 'lastFocusedControlMainView', 'lastFocusedControlGameInfoView',
                                'lastSelectedCharacter', 'lastSelectedMaxPlayers', 'lastSelectedRating',
                                'lastSelectedRegion', 'sortMethod', 'sortDirection'),
                               (selectedView, selectedConsoleId, selectedGenreId, selectedPublisherId,
                                selectedDeveloperId, selectedYearId, selectedGameIndex, selectedControlIdMainView,
                                selectedControlIdGameInfoView, selectedCharacter, selectedMaxPlayers,
                                selectedRating, selectedRegion, sortMethod, sortDirection), rcbSetting[0], True)
    else:
        RCBSetting(gdb).update(('lastSelectedView', 'lastSelectedConsoleId', 'lastSelectedGenreId',
                                'lastSelectedPublisherId', 'lastSelectedDeveloperId', 'lastSelectedYearId',
                                'lastSelectedGameIndex', 'lastFocusedControlMainView', 'lastFocusedControlGameInfoView',
                                'lastSelectedCharacter', 'lastSelectedMaxPlayers', 'lastSelectedRating',
                                'lastSelectedRegion', 'sortMethod', 'sortDirection'),
                               (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'name', 'ASC'),
                               rcbSetting[DataBaseObject.COL_ID], True)

    gdb.commit()

    log.info("End helper.saveViewState")


def createArtworkDirectories(romCollections):
    log.info('Begin createArtworkDirectories')

    for romCollection in list(romCollections.values()):
        for mediaPath in romCollection.mediaPaths:
            # Add the trailing slash that xbmcvfs.exists expects
            dirname = os.path.join(os.path.dirname(mediaPath.path), '')
            log.info('Check if directory exists: %s' % dirname)
            if xbmcvfs.exists(dirname):
                log.info('Directory exists.')
                continue

            log.info('Directory does not exist. Try to create it')
            success = xbmcvfs.mkdirs(dirname)
            log.info("Directory successfully created: %s" % success)
            if not success:
                #HACK: check if directory was really not created.
                directoryExists = xbmcvfs.exists(dirname)
                log.info("2nd check if directory exists: %s" % directoryExists)
                if not directoryExists:
                    log.error("Could not create artwork directory: '%s'" % dirname)
                    #32010: Error: Could not create artwork directory.
                    #32011: Check kodi.log for details.
                    message = "%s[CR]%s" %(dirname, util.localize(32011))
                    xbmcgui.Dialog().ok(util.localize(32010), message)
                    return False

    return True


def getRCBSetting(gdb):
    rcbSettingRows = RCBSetting(gdb).getAll()
    if rcbSettingRows == None or len(rcbSettingRows) != 1:
        #TODO raise error
        return None

    return rcbSettingRows[DataBaseObject.COL_ID]


def isRetroPlayerSupported():
    log.info("Begin isRetroPlayerSupported")

    kodiVersion = KodiVersions.getKodiVersion()
    log.info("Kodi Version = " + str(kodiVersion))

    try:
        if KodiVersions.getKodiVersion() > KodiVersions.KRYPTON:
            log.info("RetroPlayer is supported")
            return True
    except:
        log.info("RetroPlayer is not supported")
        return False

    log.info("RetroPlayer is not supported")
    return False


def selectlibretrocore(platform):
    selectedCore = ''
    addons = ['None']

    items = []
    addonsJson = xbmc.executeJSONRPC(
        '{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddons", "params": { "type": "kodi.gameclient" } }')
    jsonResult = json.loads(addonsJson)

    log.info("selectlibretrocore: jsonresult = " + str(jsonResult))
    if str(list(jsonResult.keys())).find('error') >= 0:
        log.warn("Error while reading gameclient addons via json. Assume that we are not in RetroPlayer branch.")
        return False, None

    try:
        for addonObj in jsonResult[u'result'][u'addons']:
            addonid = addonObj[u'addonid']
            addonDetails = xbmc.executeJSONRPC(
                '{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": { "addonid": "%s", "properties" : ["name", "thumbnail"] } }' % addonid)
            jsonResultDetails = json.loads(addonDetails)
            log.info("selectlibretrocore: jsonResultDetails = " + str(jsonResultDetails))

            name = jsonResultDetails[u'result'][u'addon'][u'name']
            thumbnail = jsonResultDetails[u'result'][u'addon'][u'thumbnail']
            item = xbmcgui.ListItem(name, addonid, thumbnail)
            items.append(item)
    except KeyError:
        #no addons installed or found
        return True, addons

    index = xbmcgui.Dialog().select('Select core', items, useDetails=True)

    if index == -1:
        return False, ""
    elif index == 0:
        return True, ""
    else:
        selectedCore = items[index].getLabel2()
        return True, selectedCore


def readLibretroCores():
    log.info("readLibretroCores")

    addons = []
    addonsJson = xbmc.executeJSONRPC(
        '{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddons", "params": { "type": "kodi.gameclient" } }')
    jsonResult = json.loads(addonsJson)
    log.info("readLibretroCores: jsonresult = " + str(jsonResult))
    if str(list(jsonResult.keys())).find('error') >= 0:
        log.warn("Error while reading gameclient addons via json. Assume that we are not in RetroPlayer branch.")
        return False, None

    try:
        for addonObj in jsonResult[u'result'][u'addons']:
            addonid = addonObj[u'addonid']
            addons.append(addonid)
    except KeyError:
        #no addons installed or found
        return True, addons
    log.info("addons: %s" % str(addons))
    return True, addons
