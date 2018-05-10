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


def cacheMediaPathsForSelection(consoleId, mediaDict, config):
    Logutil.log('Begin cacheMediaPathsForSelection', util.LOG_LEVEL_INFO)

    if mediaDict is None:
        mediaDict = {}

    #if this console is already cached there is nothing to do
    if str(consoleId) in mediaDict.keys():
        Logutil.log('MediaPaths for RomCollection %s are already in cache' % str(consoleId), util.LOG_LEVEL_INFO)
        return mediaDict

    if consoleId > 0:
        cacheMediaPathsForConsole(consoleId, mediaDict, config)
        return mediaDict
    else:
        for rcId in config.romCollections.keys():
            if str(rcId) in mediaDict.keys():
                Logutil.log('MediaPaths for RomCollection %s are already in cache' % str(rcId), util.LOG_LEVEL_INFO)
                continue
            cacheMediaPathsForConsole(rcId, mediaDict, config)

    Logutil.log('End cacheMediaPathsForSelection', util.LOG_LEVEL_INFO)
    return mediaDict


def cacheMediaPathsForConsole(consoleId, mediaDict, config):
    Logutil.log('Begin cacheMediaPathsForConsole', util.LOG_LEVEL_INFO)
    Logutil.log('Caching mediaPaths for Rom Collection %s' % str(consoleId), util.LOG_LEVEL_INFO)

    romCollection = config.romCollections[str(consoleId)]
    # only cache images for gamelist and clearlogo
    gamelist_types = []
    if util.getSettings().getSetting(util.SETTING_RCB_LOADGAMELISTARTWORK).upper() == 'TRUE':
        gamelist_types.extend(romCollection.imagePlacingMain.fileTypesForGameList)
    if util.getSettings().getSetting(util.SETTING_RCB_USECLEARLOGOASTITLE).upper() == 'TRUE':
        gamelist_types.append(FileType(name='clearlogo'))

    mediaPathDict = {}

    for filetype in gamelist_types:
        is_gamelist_type = False
        for mediaPath in romCollection.mediaPaths:
            if mediaPath.fileType.name == filetype.name:
                is_gamelist_type = True
                break
        if not is_gamelist_type:
            Logutil.log('%s is no gamelist type. Skip type.' %mediaPath.fileType.name, util.LOG_LEVEL_INFO)
            continue

        Logutil.log('mediaPath = %s' %mediaPath.path, util.LOG_LEVEL_INFO)
        mediadir = mediaPath.path
        #if foldername is gamename only get content of parent directory
        if romCollection.useFoldernameAsGamename:
            mediadir = mediadir[0:mediadir.index('%GAME%')]

        mediafiles = []
        walkDownMediaDirectories(os.path.dirname(mediadir), mediafiles)

        mediaPathDict[mediaPath.fileType.name] = mediafiles

    mediaDict[str(consoleId)] = mediaPathDict
    Logutil.log('End cacheMediaPathsForConsole', util.LOG_LEVEL_INFO)


def walkDownMediaDirectories(mediadir, mediafiles):
    Logutil.log('Begin walkDownMediaDirectories', util.LOG_LEVEL_INFO)
    Logutil.log('xbmcvfs.listdir', util.LOG_LEVEL_INFO)
    mediasubdirs, mediasubfiles = xbmcvfs.listdir(mediadir)
    Logutil.log('Add files', util.LOG_LEVEL_INFO)
    for mediasubfile in mediasubfiles:
        mediafiles.append(os.path.normpath(os.path.join(mediadir, mediasubfile)))

    for mediasubdir in mediasubdirs:
        walkDownMediaDirectories(os.path.join(mediadir, mediasubdir), mediafiles)


def getFileForControl(fileTypes, romCollection, mediaPathsDict, gamenameFromFile):
    Logutil.log("begin getFileForControl", util.LOG_LEVEL_DEBUG)

    for fileType in fileTypes:
        if not fileType:
            continue

        if fileType.parent != util.FILETYPEPARENT_GAME:
            continue

        mediaPath = romCollection.getMediaPathByType(fileType.name)

        if not mediaPath:
            continue

        pathnameFromFile = mediaPath.replace("%GAME%", gamenameFromFile)
        mediaPathsList = mediaPathsDict[fileType.name]

        imagePath = _findFileWithCorrectExtensionRegex(pathnameFromFile, mediaPathsList)
        if imagePath:
            return imagePath


def getFileForControl_NoCache(fileTypes, romCollection, gamenameFromFile, isVideo):
    Logutil.log("begin getFileForControl_NoCache_xbmcvfs", util.LOG_LEVEL_INFO)

    for fileType in fileTypes:
        if not fileType:
            continue

        if fileType.parent != util.FILETYPEPARENT_GAME:
            continue

        mediaPath = romCollection.getMediaPathByType(fileType.name)
        if not mediaPath:
            continue

        pathnameFromFileOrig = mediaPath.replace("%GAME%", gamenameFromFile)
        Logutil.log("pathnameFromFileOrig: %s" %pathnameFromFileOrig, util.LOG_LEVEL_INFO)
        if pathnameFromFileOrig.endswith('.*'):
            if not isVideo:
                extensions = ['png', 'jpg', 'gif', 'bmp', 'jpeg']
            else:
                extensions = ['mp4', 'wmv', 'avi', 'flv']
            for extension in extensions:
                filename = pathnameFromFileOrig.replace('*', extension)
                if xbmcvfs.exists(filename):
                    return  filename
        else:
            if xbmcvfs.exists(pathnameFromFileOrig):
                return pathnameFromFileOrig

    Logutil.log("end getFileForControl_NoCache_xbmcvfs - nothing found", util.LOG_LEVEL_INFO)
    return ""


def getFileForControl_NoCache_glob(fileTypes, romCollection, mediaPathsDict, gamenameFromFile):
    """
    Just kept as reference. glob does not seem to work with network shares in libreelec.
    """
    Logutil.log("begin getFileForControl_NoCache", util.LOG_LEVEL_INFO)

    for fileType in fileTypes:
        if not fileType:
            continue

        if fileType.parent != util.FILETYPEPARENT_GAME:
            continue

        mediaPath = romCollection.getMediaPathByType(fileType.name)
        if not mediaPath:
            continue

        pathnameFromFileOrig = mediaPath.replace("%GAME%", gamenameFromFile)
        Logutil.log("pathnameFromFileOrig: %s" %pathnameFromFileOrig, util.LOG_LEVEL_INFO)
        #HACK: glob can't handle smb paths, so we need to use unc path syntax
        if pathnameFromFileOrig.startswith('smb://'):
            pathnameFromFile = pathnameFromFileOrig.replace('smb://', '\\\\')
            pathnameFromFile = pathnameFromFile.replace('/', '\\')
        else:
            pathnameFromFile = pathnameFromFileOrig
        Logutil.log("pathnameFromFile: %s" % pathnameFromFile, util.LOG_LEVEL_INFO)
        files = glob.glob(pathnameFromFile)
        Logutil.log("files found by glob: %s" % files, util.LOG_LEVEL_INFO)

        if len(files) > 0:
            filename = pathnameFromFileOrig.replace('.*', os.path.splitext(files[0])[1])
            Logutil.log("end getFileForControl_NoCache: %s" %filename, util.LOG_LEVEL_INFO)
            return filename

    Logutil.log("end getFileForControl_NoCache - nothing found", util.LOG_LEVEL_INFO)
    return ""


def _findFileWithCorrectExtensionRegex(pathnameFromFile, mediaPathsList):
    pathToSearch = re.escape(os.path.normpath(pathnameFromFile.replace('.*', '')))
    pattern = re.compile('%s\..*$' % pathToSearch)
    for imagePath in mediaPathsList:
        match = pattern.search(imagePath)
        if match:
            resultFilename, resultExtension = os.path.splitext(imagePath)
            mediaPathFilename, mediaPathExtension = os.path.splitext(pathnameFromFile)
            return '%s%s' % (mediaPathFilename, resultExtension)


def get_file_for_control_from_db(file_types, game):
    """
    Read media files from db entry. Media files are stored as fileType1, fileType2, ... in db with the filetype id at the end of the name
    :param file_types:
    :param listitem:
    :return:
    """
    Logutil.log("begin get_file_for_control_from_db", util.LOG_LEVEL_DEBUG)

    for file_type in file_types:
        prop = 'fileType%s' %file_type.id
        file = getattr(game, prop)
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
                               (None, None, None, None, None, None, None, None, None), rcbSetting[util.ROW_ID], True)

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

    return rcbSettingRows[util.ROW_ID]


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
