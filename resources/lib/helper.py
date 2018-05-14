import json
import os, re
import glob

from gamedatabase import *
from config import FileType
from util import *
import util
import xbmc, xbmcgui


def saveReadString(prop):
    try:
        result = unicode(prop)
    except:
        result = u''

    return result


def update_artwork_cache(console_id, file_type_id, gdb, config):
    Logutil.log('cache_artwork', util.LOG_LEVEL_INFO)

    #cache all available artwork
    media_dict = _cache_mediapaths_for_selection(console_id, {}, config)

    if console_id > 0:
        rom_collection = config.romCollections[str(console_id)]
        _update_artwork_cache_for_romcollection(rom_collection, file_type_id, media_dict, gdb, config)
    else:
        for rcid in config.romCollections.keys():
            rom_collection = config.romCollections[str(rcid)]
            _update_artwork_cache_for_romcollection(rom_collection, file_type_id, media_dict, gdb, config)

    Logutil.log('End cache_artwork', util.LOG_LEVEL_INFO)


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


def saveViewState(gdb, isOnExit, selectedView, selectedGameIndex, selectedConsoleIndex, selectedGenreIndex,
                  selectedPublisherIndex, selectedYearIndex, selectedCharacterIndex,
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
                               (selectedView, selectedConsoleIndex, selectedGenreIndex, selectedPublisherIndex,
                                selectedYearIndex, selectedGameIndex, selectedControlIdMainView,
                                selectedControlIdGameInfoView, selectedCharacterIndex), rcbSetting[0], True)
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



def _update_artwork_cache_for_romcollection(rom_collection, file_type_id, media_dict, gdb, config):
    Logutil.log('Begin cache_artwork_for_console', util.LOG_LEVEL_INFO)
    Logutil.log('Caching mediaPaths for Rom Collection %s' % str(rom_collection.id), util.LOG_LEVEL_INFO)

    media_paths_dict = {}
    try:
        media_paths_dict = media_dict[rom_collection.id]
    except KeyError:
        Logutil.log('No media paths dict found for rom collection %s' % rom_collection.id, util.LOG_LEVEL_WARNING)
        return

    games = GameView(gdb).getFilteredGames(rom_collection.id, 0, 0, 0, 0, '0 = 0', 0)
    for game in games:
        for media_path in rom_collection.mediaPaths:
            #check if we should handle this file type
            if str(file_type_id) != media_path.fileType.id and file_type_id != 0:
                continue

            roms = File(gdb).getRomsByGameId(game[GameView.COL_ID])
            gamename_from_file = rom_collection.getGamenameFromFilename(roms[0][0])
            #check if artwork is available for this type
            file = _find_file_in_mediadict(media_path.fileType.id, rom_collection, media_paths_dict, gamename_from_file)
            #write result to db
            # get column name from FIELDNAMES - index is the same as db column index (COL_fileTypeX)
            column = Game.FIELDNAMES[getattr(Game, "COL_fileType%s" % media_path.fileType.id)]
            Game(gdb).update((column,), (file,), game[Game.COL_ID], True)


def _cache_mediapaths_for_selection(console_id, media_dict, config):
    Logutil.log('Begin cache_mediapaths_for_selection', util.LOG_LEVEL_INFO)

    if media_dict is None:
        media_dict = {}

    #if this console is already cached there is nothing to do
    if console_id in media_dict.keys():
        Logutil.log('MediaPaths for RomCollection %s are already in cache' % console_id, util.LOG_LEVEL_INFO)
        return media_dict

    if console_id > 0:
        _cache_media_paths_for_console(str(console_id), media_dict, config)
        return media_dict
    else:
        for rcId in config.romCollections.keys():
            if rcId in media_dict.keys():
                Logutil.log('MediaPaths for RomCollection %s are already in cache' % rcId, util.LOG_LEVEL_INFO)
                continue
            _cache_media_paths_for_console(rcId, media_dict, config)

    Logutil.log('End cacheMediaPathsForSelection', util.LOG_LEVEL_INFO)
    return media_dict


def _cache_media_paths_for_console(console_id, media_dict, config):
    Logutil.log('Begin cacheMediaPathsForConsole', util.LOG_LEVEL_INFO)
    Logutil.log('Caching mediaPaths for Rom Collection %s' % console_id, util.LOG_LEVEL_INFO)

    rom_collection = config.romCollections[str(console_id)]

    media_path_dict = {}

    for media_path in rom_collection.mediaPaths:
        Logutil.log('media_path = %s' %media_path.path, util.LOG_LEVEL_INFO)
        mediadir = media_path.path
        #if foldername is gamename only get content of parent directory
        if rom_collection.useFoldernameAsGamename:
            mediadir = mediadir[0:mediadir.index('%GAME%')]

        mediafiles = []
        _walk_down_media_directories(os.path.dirname(mediadir), mediafiles)

        media_path_dict[media_path.fileType.id] = mediafiles

    media_dict[console_id] = media_path_dict
    Logutil.log('End cacheMediaPathsForConsole', util.LOG_LEVEL_INFO)


def _walk_down_media_directories(mediadir, mediafiles):
    Logutil.log('Begin walkDownMediaDirectories', util.LOG_LEVEL_INFO)
    Logutil.log('xbmcvfs.listdir', util.LOG_LEVEL_INFO)
    mediasubdirs, mediasubfiles = xbmcvfs.listdir(mediadir)
    Logutil.log('Add files', util.LOG_LEVEL_INFO)
    for mediasubfile in mediasubfiles:
        mediafiles.append(os.path.normpath(os.path.join(mediadir, mediasubfile)))

    for mediasubdir in mediasubdirs:
        _walk_down_media_directories(os.path.join(mediadir, mediasubdir), mediafiles)


def _find_file_in_mediadict(filetype_id, rom_collection, media_paths_dict, gamename_from_file):
    Logutil.log("begin getFileForControl", util.LOG_LEVEL_DEBUG)

    media_path = rom_collection.getMediaPathByTypeId(filetype_id)

    if not media_path:
        return ''

    pathname_from_file = media_path.replace("%GAME%", gamename_from_file)
    media_paths_list = media_paths_dict[str(filetype_id)]

    image_path = _find_file_with_correct_extension(pathname_from_file, media_paths_list)
    if image_path:
        return image_path

"""
def get_file_for_control(fileTypes, romCollection, mediaPathsDict, gamenameFromFile):
    Logutil.log("begin getFileForControl", util.LOG_LEVEL_DEBUG)

    for fileType in fileTypes:
        if not fileType:
            continue

        if fileType.parent != util.FILETYPEPARENT_GAME:
            continue

        mediaPath = romCollection.getMediaPathByTypeName(fileType.name)

        if not mediaPath:
            continue

        pathnameFromFile = mediaPath.replace("%GAME%", gamenameFromFile)
        mediaPathsList = mediaPathsDict[fileType.name]

        imagePath = _find_file_with_correct_extension(pathnameFromFile, mediaPathsList)
        if imagePath:
            return imagePath
"""


def _find_file_with_correct_extension(pathnameFromFile, mediaPathsList):
    pathToSearch = re.escape(os.path.normpath(pathnameFromFile.replace('.*', '')))
    pattern = re.compile('%s\..*$' % pathToSearch)
    for imagePath in mediaPathsList:
        match = pattern.search(imagePath)
        if match:
            resultFilename, resultExtension = os.path.splitext(imagePath)
            mediaPathFilename, mediaPathExtension = os.path.splitext(pathnameFromFile)
            return '%s%s' % (mediaPathFilename, resultExtension)
