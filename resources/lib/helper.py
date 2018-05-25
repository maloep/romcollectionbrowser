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
        result = unicode(prop)
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
    Logutil.log("begin get_file_for_control_from_db", util.LOG_LEVEL_DEBUG)

    for file_type in file_types:
        prop = 'COL_fileType%s' %file_type.id
        file = game[getattr(GameView, prop)]
        if file:
            return file
    return ""


def saveViewState(gdb, isOnExit, selectedView, selectedGameIndex, selectedConsoleId, selectedGenreId,
                  selectedPublisherId, selectedYearId, selectedCharacter,
                  selectedControlIdMainView, selectedControlIdGameInfoView, settings):
    Logutil.log("Begin helper.saveViewState", util.LOG_LEVEL_INFO)

    if isOnExit:
        #saveViewStateOnExit
        saveViewState = settings.getSetting(util.SETTING_RCB_SAVEVIEWSTATEONEXIT).upper() == 'TRUE'
    else:
        #saveViewStateOnLaunchEmu
        saveViewState = settings.getSetting(util.SETTING_RCB_SAVEVIEWSTATEONLAUNCHEMU).upper() == 'TRUE'

    rcbSetting = getRCBSetting(gdb)
    if rcbSetting == None:
        Logutil.log("rcbSetting == None in helper.saveViewState", util.LOG_LEVEL_WARNING)
        return

    if saveViewState:
        RCBSetting(gdb).update(('lastSelectedView', 'lastSelectedConsoleIndex', 'lastSelectedGenreIndex',
                                'lastSelectedPublisherIndex', 'lastSelectedYearIndex', 'lastSelectedGameIndex',
                                'lastFocusedControlMainView', 'lastFocusedControlGameInfoView',
                                'lastSelectedCharacterIndex'),
                               (selectedView, selectedConsoleId, selectedGenreId, selectedPublisherId,
                                selectedYearId, selectedGameIndex, selectedControlIdMainView,
                                selectedControlIdGameInfoView, selectedCharacter), rcbSetting[0], True)
    else:
        RCBSetting(gdb).update(('lastSelectedView', 'lastSelectedConsoleIndex', 'lastSelectedGenreIndex',
                                'lastSelectedPublisherIndex', 'lastSelectedYearIndex', 'lastSelectedGameIndex',
                                'lastFocusedControlMainView', 'lastFocusedControlGameInfoView',
                                'lastSelectedCharacterIndex'),
                               (None, None, None, None, None, None, None, None, None), rcbSetting[DataBaseObject.COL_ID], True)

    gdb.commit()

    Logutil.log("End helper.saveViewState", util.LOG_LEVEL_INFO)


def createArtworkDirectories(romCollections):
    Logutil.log('Begin createArtworkDirectories', util.LOG_LEVEL_INFO)

    for romCollection in romCollections.values():
        for mediaPath in romCollection.mediaPaths:
            # Add the trailing slash that xbmcvfs.exists expects
            dirname = os.path.join(os.path.dirname(mediaPath.path), '')
            Logutil.log('Check if directory exists: %s' % dirname, util.LOG_LEVEL_INFO)
            if xbmcvfs.exists(dirname):
                Logutil.log('Directory exists.', util.LOG_LEVEL_INFO)
                continue

            Logutil.log('Directory does not exist. Try to create it', util.LOG_LEVEL_INFO)
            success = xbmcvfs.mkdirs(dirname)
            Logutil.log("Directory successfully created: %s" % success, util.LOG_LEVEL_INFO)
            if not success:
                #HACK: check if directory was really not created.
                directoryExists = xbmcvfs.exists(dirname)
                Logutil.log("2nd check if directory exists: %s" % directoryExists, util.LOG_LEVEL_INFO)
                if not directoryExists:
                    Logutil.log("Could not create artwork directory: '%s'" % dirname, util.LOG_LEVEL_ERROR)
                    #32010: Error: Could not create artwork directory.
                    #32011: Check kodi.log for details.
                    xbmcgui.Dialog().ok(util.localize(32010), dirname, util.localize(32011))
                    return False

    return True


def getRCBSetting(gdb):
    rcbSettingRows = RCBSetting(gdb).getAll()
    if rcbSettingRows == None or len(rcbSettingRows) != 1:
        #TODO raise error
        return None

    return rcbSettingRows[DataBaseObject.COL_ID]


def isRetroPlayerSupported():
    Logutil.log("Begin isRetroPlayerSupported", util.LOG_LEVEL_INFO)

    kodiVersion = KodiVersions.getKodiVersion()
    Logutil.log("Kodi Version = " + str(kodiVersion), util.LOG_LEVEL_INFO)

    try:
        if KodiVersions.getKodiVersion() > KodiVersions.KRYPTON:
            Logutil.log("RetroPlayer is supported", util.LOG_LEVEL_INFO)
            return True
    except:
        Logutil.log("RetroPlayer is not supported", util.LOG_LEVEL_INFO)
        return False

    Logutil.log("RetroPlayer is not supported", util.LOG_LEVEL_INFO)
    return False


def selectlibretrocore(platform):
    selectedCore = ''
    addons = ['None']

    items = []
    addonsJson = xbmc.executeJSONRPC(
        '{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddons", "params": { "type": "kodi.gameclient" } }')
    jsonResult = json.loads(addonsJson)

    Logutil.log("selectlibretrocore: jsonresult = " + str(jsonResult), util.LOG_LEVEL_INFO)
    if str(jsonResult.keys()).find('error') >= 0:
        Logutil.log("Error while reading gameclient addons via json. Assume that we are not in RetroPlayer branch.",
                    util.LOG_LEVEL_WARNING)
        return False, None

    try:
        for addonObj in jsonResult[u'result'][u'addons']:
            addonid = addonObj[u'addonid']
            addonDetails = xbmc.executeJSONRPC(
                '{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": { "addonid": "%s", "properties" : ["name", "thumbnail"] } }' % addonid)
            jsonResultDetails = json.loads(addonDetails)
            Logutil.log("selectlibretrocore: jsonResultDetails = " + str(jsonResultDetails), util.LOG_LEVEL_INFO)

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
    Logutil.log("readLibretroCores", util.LOG_LEVEL_INFO)

    addons = []
    addonsJson = xbmc.executeJSONRPC(
        '{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddons", "params": { "type": "kodi.gameclient" } }')
    jsonResult = json.loads(addonsJson)
    Logutil.log("readLibretroCores: jsonresult = " + str(jsonResult), util.LOG_LEVEL_INFO)
    if str(jsonResult.keys()).find('error') >= 0:
        Logutil.log("Error while reading gameclient addons via json. Assume that we are not in RetroPlayer branch.",
                    util.LOG_LEVEL_WARNING)
        return False, None

    try:
        for addonObj in jsonResult[u'result'][u'addons']:
            addonid = addonObj[u'addonid']
            addons.append(addonid)
    except KeyError:
        #no addons installed or found
        return True, addons
    Logutil.log("addons: %s" % str(addons), util.LOG_LEVEL_INFO)
    return True, addons
