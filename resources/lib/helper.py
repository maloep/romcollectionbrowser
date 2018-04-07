import json
import os, re

from gamedatabase import *
from util import *
import util
import xbmc, xbmcgui


def saveReadString(property):
						
		try:
			result = unicode(property)
		except:
			result = u''
			
		return result


def cacheMediaPathsForSelection(consoleId, mediaDict, config):
	Logutil.log('Begin cacheMediaPathsForSelection', util.LOG_LEVEL_INFO)
	
	if mediaDict is None:
		mediaDict = {}
		
	#if this console is already cached there is nothing to do
	if str(consoleId) in mediaDict.keys():
		Logutil.log('MediaPaths for RomCollection %s are already in cache' %str(consoleId), util.LOG_LEVEL_INFO)
		return mediaDict
	
	if(consoleId > 0):
		cacheMediaPathsForConsole(consoleId, mediaDict, config)
		return mediaDict
	else:
		for rcId in config.romCollections.keys():
			if str(rcId) in mediaDict.keys():
				Logutil.log('MediaPaths for RomCollection %s are already in cache' %str(rcId), util.LOG_LEVEL_INFO)
				continue
			cacheMediaPathsForConsole(rcId, mediaDict, config)
			
	return mediaDict
		

def cacheMediaPathsForConsole(consoleId, mediaDict, config):
	Logutil.log('Begin cacheMediaPathsForConsole', util.LOG_LEVEL_INFO)
	Logutil.log('Caching mediaPaths for Rom Collection %s' %str(consoleId), util.LOG_LEVEL_INFO)
	
	romCollection = config.romCollections[str(consoleId)]
			
	mediaPathDict = {}
	
	for mediaPath in romCollection.mediaPaths:
		mediadir = mediaPath.path
		#if foldername is gamename only get content of parent directory
		if romCollection.useFoldernameAsGamename:
			mediadir = mediadir[0:mediadir.index('%GAME%')]
		
		mediafiles = []
		walkDownMediaDirectories(os.path.dirname(mediadir), mediafiles)
		
		mediaPathDict[mediaPath.fileType.name] = mediafiles
		
	mediaDict[str(consoleId)] = mediaPathDict
				
	
def walkDownMediaDirectories(mediadir, mediafiles):
	
	mediasubdirs, mediasubfiles = xbmcvfs.listdir(mediadir)
	for mediasubfile in mediasubfiles:
		mediafiles.append(os.path.normpath(os.path.join(mediadir, mediasubfile)))
	
	for mediasubdir in mediasubdirs:
		walkDownMediaDirectories(os.path.join(mediadir, mediasubdir), mediafiles)


def getFileForControl(fileTypes, romCollection, mediaPathsDict, gamenameFromFile, isVideo=False):
		
	Logutil.log("begin getFileForControl", util.LOG_LEVEL_DEBUG)

	for fileType in fileTypes:
		if not fileType:
			continue

		if(fileType.parent != util.FILETYPEPARENT_GAME):
			continue
		
		mediaPath = romCollection.getMediaPathByType(fileType.name)
		
		if(not mediaPath):
			continue
		
		pathnameFromFile = mediaPath.replace("%GAME%", gamenameFromFile)
		mediaPathsList = mediaPathsDict[fileType.name]
				
		imagePath = _findFileWithCorrectExtensionRegex(pathnameFromFile, mediaPathsList, isVideo)
		if imagePath:
			return imagePath


def _findFileWithCorrectExtensionRegex(pathnameFromFile, mediaPathsList, isVideo):
	pathToSearch = re.escape(os.path.normpath(pathnameFromFile.replace('.*', '')))
	pattern = re.compile('%s\..*$' %pathToSearch)
	for imagePath in mediaPathsList:
		match = pattern.search(imagePath)
		if match:
			resultFilename, resultExtension = os.path.splitext(imagePath)
			mediaPathFilename, mediaPathExtension = os.path.splitext(pathnameFromFile)
			return '%s%s' %(mediaPathFilename, resultExtension)
		

def _findFileWithCorrectExtensionRegexFilter(pathnameFromFile, mediaPathsList, isVideo):
	pathToSearch = re.escape(os.path.normpath(pathnameFromFile.replace('.*', '')))
	pattern = re.compile('%s\..*$' %pathToSearch)
	result = filter(pattern.match, mediaPathsList)
	if len(result) > 0:
		resultFilename, resultExtension = os.path.splitext(result[0])
		mediaPathFilename, mediaPathExtension = os.path.splitext(pathnameFromFile)
		return '%s%s' %(mediaPathFilename, resultExtension)
		
		
def _findFileWithCorrectExtension(pathnameFromFile, mediaPathsList, isVideo):
	extensionlist = ['jpg', 'gif', 'jpeg', 'bmp', 'png']
	if isVideo:
		extensionlist = ['wmv', 'mp4', 'avi', 'flv']
	for extension in extensionlist:
		path = pathnameFromFile.replace('*', extension)
		#HACK: os.path.normpath creates smb paths like smb:\\foo. Only use this path for searching the image in mediadict
		pathToSearch = os.path.normpath(path)
		Logutil.log("Looking for image: %s" %path, util.LOG_LEVEL_DEBUG)
		if pathToSearch in mediaPathsList:
			Logutil.log("image found", util.LOG_LEVEL_DEBUG)
			Logutil.log("end getFileForControl", util.LOG_LEVEL_DEBUG)
			return path
					
	Logutil.log("end getFileForControl", util.LOG_LEVEL_DEBUG)
	return ""
		
		
def saveViewState(gdb, isOnExit, selectedView, selectedGameIndex, selectedConsoleIndex, selectedGenreIndex, selectedPublisherIndex, selectedYearIndex, selectedCharacterIndex,
	selectedControlIdMainView, selectedControlIdGameInfoView, settings):
		
	Logutil.log("Begin helper.saveViewState", util.LOG_LEVEL_INFO)				
	
	if(isOnExit):
		#saveViewStateOnExit
		saveViewState = settings.getSetting(util.SETTING_RCB_SAVEVIEWSTATEONEXIT).upper() == 'TRUE'
	else:
		#saveViewStateOnLaunchEmu
		saveViewState = settings.getSetting(util.SETTING_RCB_SAVEVIEWSTATEONLAUNCHEMU).upper() == 'TRUE'
		
	rcbSetting = getRCBSetting(gdb)
	if(rcbSetting == None):
		Logutil.log("rcbSetting == None in helper.saveViewState", util.LOG_LEVEL_WARNING)
		return
	
	if(saveViewState):
		RCBSetting(gdb).update(('lastSelectedView', 'lastSelectedConsoleIndex', 'lastSelectedGenreIndex', 'lastSelectedPublisherIndex', 'lastSelectedYearIndex', 'lastSelectedGameIndex', 'lastFocusedControlMainView', 'lastFocusedControlGameInfoView', 'lastSelectedCharacterIndex'),
			(selectedView, selectedConsoleIndex, selectedGenreIndex, selectedPublisherIndex, selectedYearIndex, selectedGameIndex, selectedControlIdMainView, selectedControlIdGameInfoView, selectedCharacterIndex), rcbSetting[0], True)
	else:
		RCBSetting(gdb).update(('lastSelectedView', 'lastSelectedConsoleIndex', 'lastSelectedGenreIndex', 'lastSelectedPublisherIndex', 'lastSelectedYearIndex', 'lastSelectedGameIndex', 'lastFocusedControlMainView', 'lastFocusedControlGameInfoView', 'lastSelectedCharacterIndex'),
			(None, None, None, None, None, None, None, None, None), rcbSetting[util.ROW_ID], True)
			
	gdb.commit()
	
	Logutil.log("End helper.saveViewState", util.LOG_LEVEL_INFO)


def createArtworkDirectories(romCollections):
	Logutil.log('Begin createArtworkDirectories', util.LOG_LEVEL_INFO)

	for romCollection in romCollections.values():
		for mediaPath in romCollection.mediaPaths:
			# Add the trailing slash that xbmcvfs.exists expects
			dirname = os.path.join(os.path.dirname(mediaPath.path), '')
			Logutil.log('Check if directory exists: %s' %dirname, util.LOG_LEVEL_INFO)
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
	if(rcbSettingRows == None or len(rcbSettingRows) != 1):
		#TODO raise error
		return None
					
	return rcbSettingRows[util.ROW_ID]


def isRetroPlayerSupported():
	
	Logutil.log("Begin isRetroPlayerSupported", util.LOG_LEVEL_INFO)
	
	kodiVersion = KodiVersions.getKodiVersion()
	Logutil.log("Kodi Version = " +str(kodiVersion), util.LOG_LEVEL_INFO)
	
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
	addonsJson = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddons", "params": { "type": "kodi.gameclient" } }')
	jsonResult = json.loads(addonsJson)
	
	Logutil.log("selectlibretrocore: jsonresult = " +str(jsonResult), util.LOG_LEVEL_INFO)	
	if (str(jsonResult.keys()).find('error') >= 0):
		Logutil.log("Error while reading gameclient addons via json. Assume that we are not in RetroPlayer branch.", util.LOG_LEVEL_WARNING)
		return False, None
	
	try:
		for addonObj in jsonResult[u'result'][u'addons']:
			id = addonObj[u'addonid']
			addonDetails = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": { "addonid": "%s", "properties" : ["name", "thumbnail"] } }' %id)
			jsonResultDetails = json.loads(addonDetails)
			Logutil.log("selectlibretrocore: jsonResultDetails = " +str(jsonResultDetails), util.LOG_LEVEL_INFO)
			
			name = jsonResultDetails[u'result'][u'addon'][u'name']			
			thumbnail = jsonResultDetails[u'result'][u'addon'][u'thumbnail']
			item = xbmcgui.ListItem(name, id, thumbnail)
			items.append(item)
	except KeyError:
		#no addons installed or found
		return True, addons
		
	index = xbmcgui.Dialog().select('Select core', items, useDetails=True)
	
	if(index == -1):
		return False, ""
	elif(index == 0):
		return True, ""
	else:
		selectedCore = items[index].getLabel2()
		return True, selectedCore


def readLibretroCores():
	
	Logutil.log("readLibretroCores", util.LOG_LEVEL_INFO)
		
	addons = []
	addonsJson = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddons", "params": { "type": "kodi.gameclient" } }')
	jsonResult = json.loads(addonsJson)
	Logutil.log("readLibretroCores: jsonresult = " +str(jsonResult), util.LOG_LEVEL_INFO)	
	if (str(jsonResult.keys()).find('error') >= 0):
		Logutil.log("Error while reading gameclient addons via json. Assume that we are not in RetroPlayer branch.", util.LOG_LEVEL_WARNING)
		return False, None
			
	try:
		for addonObj in jsonResult[u'result'][u'addons']:
			id = addonObj[u'addonid']
			addons.append(id)
	except KeyError:
		#no addons installed or found
		return True, addons
	Logutil.log("addons: %s" %str(addons), util.LOG_LEVEL_INFO)
	return True, addons
