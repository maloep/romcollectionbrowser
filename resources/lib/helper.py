import xbmc, xbmcgui
import os, sys, re
import json


import dbupdate
from gamedatabase import *
import util
from util import *
import config


def cacheFiles(fileRows):
		
	Logutil.log("Begin cacheFiles" , util.LOG_LEVEL_DEBUG)
	
	fileDict = {}
	for fileRow in fileRows:
		key = '%i;%i' % (fileRow[util.FILE_parentId] , fileRow[util.FILE_fileTypeId])
		item = None
		try:
			item = fileDict[key]
		except:
			pass
		if(item == None):
			fileRowList = []
			fileRowList.append(fileRow)
			fileDict[key] = fileRowList
		else:				
			fileRowList = fileDict[key]
			fileRowList.append(fileRow)
			fileDict[key] = fileRowList
			
	Logutil.log("End cacheFiles" , util.LOG_LEVEL_DEBUG)
	return fileDict


def cacheYears(gdb):
	Logutil.log("Begin cacheYears" , util.LOG_LEVEL_DEBUG)
	yearRows = Year(gdb).getAll()
	if(yearRows == None):
		Logutil.log("yearRows == None in cacheYears", util.LOG_LEVEL_WARNING)
		return
	yearDict = {}
	for yearRow in yearRows:
		yearDict[yearRow[util.ROW_ID]] = yearRow
		
	Logutil.log("End cacheYears" , util.LOG_LEVEL_DEBUG)
	return yearDict
	
	
def cacheReviewers(gdb):
	Logutil.log("Begin cacheReviewers" , util.LOG_LEVEL_DEBUG)
	reviewerRows = Reviewer(gdb).getAll()
	if(reviewerRows == None):
		Logutil.log("reviewerRows == None in cacheReviewers", util.LOG_LEVEL_WARNING)
		return
	reviewerDict = {}
	for reviewerRow in reviewerRows:
		reviewerDict[reviewerRow[util.ROW_ID]] = reviewerRow
		
	Logutil.log("End cacheReviewers" , util.LOG_LEVEL_DEBUG)
	return reviewerDict
	

def cachePublishers(gdb):
	Logutil.log("Begin cachePublishers" , util.LOG_LEVEL_DEBUG)
	publisherRows = Publisher(gdb).getAll()
	if(publisherRows == None):
		Logutil.log("publisherRows == None in cachePublishers", util.LOG_LEVEL_WARNING)
		return
	publisherDict = {}
	for publisherRow in publisherRows:
		publisherDict[publisherRow[util.ROW_ID]] = publisherRow
		
	Logutil.log("End cachePublishers" , util.LOG_LEVEL_DEBUG)
	return publisherDict
	
	
def cacheDevelopers(gdb):
	Logutil.log("Begin cacheDevelopers" , util.LOG_LEVEL_DEBUG)
	developerRows = Developer(gdb).getAll()
	if(developerRows == None):
		Logutil.log("developerRows == None in cacheDevelopers", util.LOG_LEVEL_WARNING)
		return
	developerDict = {}
	for developerRow in developerRows:
		developerDict[developerRow[util.ROW_ID]] = developerRow
		
	Logutil.log("End cacheDevelopers" , util.LOG_LEVEL_DEBUG)
	return developerDict
	

def cacheGenres(gdb):
	
	Logutil.log("Begin cacheGenres" , util.LOG_LEVEL_DEBUG)
			
	genreGameRows = GenreGame(gdb).getAll()
	if(genreGameRows == None):
		Logutil.log("genreRows == None in cacheGenres", util.LOG_LEVEL_WARNING)
		return
	genreDict = {}
	for genreGameRow in genreGameRows:
		key = genreGameRow[util.GENREGAME_gameId]
		item = None
		try:
			item = genreDict[key]
			continue
		except:
			pass
			
		genreRows = Genre(gdb).getGenresByGameId(genreGameRow[util.GENREGAME_gameId])
		for i in range(0, len(genreRows)):
			if(i == 0):
				genres = genreRows[i][util.ROW_NAME]	
				genreDict[key] = genres
			else:				
				genres = genreDict[key]					
				genres = genres + ', ' + genreRows[i][util.ROW_NAME]					
				genreDict[key] = genres
			
	Logutil.log("End cacheGenres" , util.LOG_LEVEL_DEBUG)
	return genreDict


def saveReadString(property):
						
		try:
			result = unicode(property)
		except:
			result = u''
			
		return result


def getPropertyFromCache(dataRow, dict, key, index):
		
	result = ""
	try:
		itemRow = dict[dataRow[key]]
		result = itemRow[index]
	except:
		pass
		
	return result


def getFilenameForGame(gameid, filetypeid, fileDict):
	"""
	Returns a Row object from the cache based on a key comprising the game ID and the filetype ID
	"""
	key = '%i;%i' % (int(gameid), int(filetypeid))
	Logutil.log("Searching file cache for file type {0}, game {1} using key {2}".format(filetypeid, gameid, key), util.LOG_LEVEL_DEBUG)
	try:
		# Get the Row object from the cache dict
		files = fileDict[key]
		Logutil.log("Found in cache: {0}".format(files), util.LOG_LEVEL_DEBUG)
	except KeyError:
		Logutil.log("Not found in file cache", util.LOG_LEVEL_DEBUG)
		return ''

	return files[0][ROW_NAME]


def getFilesByControl_Cached(gdb, fileTypes, gameId, publisherId, developerId, romCollectionId, fileDict):
					
	Logutil.log("getFilesByControl gameId: " +str(gameId), util.LOG_LEVEL_DEBUG)
	Logutil.log("getFilesByControl publisherId: " +str(publisherId), util.LOG_LEVEL_DEBUG)
	Logutil.log("getFilesByControl developerId: " +str(developerId), util.LOG_LEVEL_DEBUG)
	Logutil.log("getFilesByControl romCollectionId: " +str(romCollectionId), util.LOG_LEVEL_DEBUG)
	
	mediaFiles = []
	for fileType in fileTypes:
		Logutil.log("fileType: " +str(fileType.name), util.LOG_LEVEL_DEBUG)
		
		parentId = None
					
		if(fileType.parent == util.FILETYPEPARENT_GAME):
			parentId = gameId			
		elif(fileType.parent == util.FILETYPEPARENT_PUBLISHER):
			parentId = publisherId
		elif(fileType.parent == util.FILETYPEPARENT_DEVELOPER):
			parentId = developerId
		elif(fileType.parent == util.FILETYPEPARENT_ROMCOLLECTION):
			parentId = romCollectionId
			
		Logutil.log("parentId: " +str(parentId), util.LOG_LEVEL_DEBUG)
			
		if(parentId != None):
			key = '%i;%i' %(parentId, int(fileType.id))
			try:								
				files = fileDict[key]				
			except:
				files = None
		else:
			files = None
		
		if(files == None):
			Logutil.log("files == None in getFilesByControl", util.LOG_LEVEL_DEBUG)
			continue
			
		for file in files:
			mediaFiles.append(file[1])
	
	return mediaFiles
		
		
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
