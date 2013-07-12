import xbmc
import os, sys, re
from resources.lib.rcb.datamodel.gamedatabase import GameDataBase, Reviewer, GenreGame
from resources.lib.rcb.datamodel.year import Year
from resources.lib.rcb.datamodel.publisher import Publisher
from resources.lib.rcb.datamodel.developer import Developer
from resources.lib.rcb.datamodel.genre import Genre
from resources.lib.rcb.datamodel.rcbsetting import RCBSetting
import util
from util import *
from resources.lib.rcb.configuration import config


def cacheFiles(files):
		
	Logutil.log("Begin cacheFiles" , util.LOG_LEVEL_DEBUG)
	
	fileDict = {}
	for file in files:
		key = '%i;%i' % (file.parentId , file.fileTypeId)
		item = None
		try:
			item = fileDict[key]
		except:
			pass
		if(item == None):
			fileRowList = []
			fileRowList.append(file)
			fileDict[key] = fileRowList
		else:				
			fileRowList = fileDict[key]
			fileRowList.append(file)
			fileDict[key] = fileRowList
			
	Logutil.log("End cacheFiles" , util.LOG_LEVEL_DEBUG)
	return fileDict


def cacheYears(gdb):
	Logutil.log("Begin cacheYears" , util.LOG_LEVEL_DEBUG)
	years = Year(gdb).getAll()
	if(years == None):
		Logutil.log("yearRows == None in cacheYears", util.LOG_LEVEL_WARNING)
		return
	yearDict = {}
	for year in years:
		yearDict[year.id] = year
		
	Logutil.log("End cacheYears" , util.LOG_LEVEL_DEBUG)
	return yearDict
	
	
def cacheReviewers(gdb):
	Logutil.log("Begin cacheReviewers" , util.LOG_LEVEL_DEBUG)
	reviewers = Reviewer(gdb).getAll()
	if(reviewers == None):
		Logutil.log("reviewerRows == None in cacheReviewers", util.LOG_LEVEL_WARNING)
		return
	reviewerDict = {}
	for reviewer in reviewers:
		reviewerDict[reviewer.id] = reviewer
		
	Logutil.log("End cacheReviewers" , util.LOG_LEVEL_DEBUG)
	return reviewerDict
	

def cachePublishers(gdb):
	Logutil.log("Begin cachePublishers" , util.LOG_LEVEL_DEBUG)
	publishers = Publisher(gdb).getAll()
	if(publishers == None):
		Logutil.log("publisherRows == None in cachePublishers", util.LOG_LEVEL_WARNING)
		return
	publisherDict = {}
	for publisher in publishers:
		publisherDict[publisher.id] = publisher
		
	Logutil.log("End cachePublishers" , util.LOG_LEVEL_DEBUG)
	return publisherDict
	
	
def cacheDevelopers(gdb):
	Logutil.log("Begin cacheDevelopers" , util.LOG_LEVEL_DEBUG)
	developers = Developer(gdb).getAll()
	if(developers == None):
		Logutil.log("developerRows == None in cacheDevelopers", util.LOG_LEVEL_WARNING)
		return
	developerDict = {}
	for developer in developers:
		developerDict[developer.id] = developer
		
	Logutil.log("End cacheDevelopers" , util.LOG_LEVEL_DEBUG)
	return developerDict
	

def cacheGenres(gdb):
	
	Logutil.log("Begin cacheGenres" , util.LOG_LEVEL_DEBUG)
			
	genreGames = GenreGame(gdb).getAll()
	if(genreGames == None):
		Logutil.log("genreRows == None in cacheGenres", util.LOG_LEVEL_WARNING)
		return
	genreDict = {}
	for genreGame in genreGames:
		key = genreGame.gameId
		item = None
		try:
			item = genreDict[key]
			continue
		except:
			pass
			
		genres = Genre(gdb).getGenresByGameId(genreGame.gameId)
		for i in range(0, len(genres)):
			if(i == 0):
				newgenres = genres[i].name
				genreDict[key] = newgenres
			else:				
				newgenres = genreDict[key]					
				newgenres = newgenres + ', ' + genres[i].name					
				genreDict[key] = newgenres
			
	Logutil.log("End cacheGenres" , util.LOG_LEVEL_DEBUG)
	return genreDict


def saveReadString(property):
						
		try:
			result = str(property)
		except:
			result = ""
			
		return result


def getPropertyFromCache(key, dict, index):
		
	result = ""
	try:
		itemRow = dict[key]
		result = itemRow[index]
	except:
		pass
		
	return result


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
			mediaFiles.append(file.name)
	
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
		rcbSetting.lastSelectedView = selectedView
		rcbSetting.lastSelectedConsoleIndex = selectedConsoleIndex 
		rcbSetting.lastSelectedGenreIndex = selectedGenreIndex
		rcbSetting.lastSelectedPublisherIndex = selectedPublisherIndex
		rcbSetting.lastSelectedYearIndex = selectedYearIndex
		rcbSetting.lastSelectedGameIndex = selectedGameIndex
		rcbSetting.lastFocusedControlMainView = selectedControlIdMainView
		rcbSetting.lastFocusedControlGameInfoView = selectedControlIdGameInfoView
		rcbSetting.lastSelectedCharacterIndex = selectedCharacterIndex
	else:
		rcbSetting.lastSelectedView = None
		rcbSetting.lastSelectedConsoleIndex = None 
		rcbSetting.lastSelectedGenreIndex = None
		rcbSetting.lastSelectedPublisherIndex = None
		rcbSetting.lastSelectedYearIndex = None
		rcbSetting.lastSelectedGameIndex = None
		rcbSetting.lastFocusedControlMainView = None
		rcbSetting.lastFocusedControlGameInfoView = None
		rcbSetting.lastSelectedCharacterIndex = None
		
	RCBSetting(gdb).updateAllColumns(rcbSetting, True)
			
	gdb.commit()
	
	Logutil.log("End helper.saveViewState", util.LOG_LEVEL_INFO)


			
def getRCBSetting(gdb):
	rcbSettingRows = RCBSetting(gdb).getAll()
	if(rcbSettingRows == None or len(rcbSettingRows) != 1):
		#TODO raise error
		return None
					
	return rcbSettingRows[util.ROW_ID]
		
		

def buildLikeStatement(selectedCharacter, searchTerm):
	Logutil.log("helper.buildLikeStatement", util.LOG_LEVEL_INFO)
	
	likeStatement = ''
	
	if (selectedCharacter == util.localize(40020)):
		likeStatement = "0 = 0"
	elif (selectedCharacter == '0-9'):
		
		likeStatement = '('
		for i in range (0, 10):				
			likeStatement += "name LIKE '%s'" %(str(i) +'%')
			if(i != 9):
				likeStatement += ' or '
		
		likeStatement += ')'
	else:		
		likeStatement = "name LIKE '%s'" %(selectedCharacter +'%')
	
	if(searchTerm != ''):
		likeStatement += " AND name LIKE '%s'" %('%' +searchTerm +'%')
	
	return likeStatement


def builMissingFilterStatement(config):

	if(config.showHideOption.lower() == util.localize(40057)):
		return ''
		
	statement = ''
	
	andStatementInfo = buildInfoStatement(config.missingFilterInfo.andGroup, ' AND ')
	if(andStatementInfo != ''):
		statement = andStatementInfo
		
	orStatementInfo =  buildInfoStatement(config.missingFilterInfo.orGroup, ' OR ')
	if(orStatementInfo != ''):
		if (statement != ''):
			statement = statement +' OR '
		statement = statement + orStatementInfo
		
	andStatementArtwork = buildArtworkStatement(config, config.missingFilterArtwork.andGroup, ' AND ')
	if(andStatementArtwork != ''):
		if (statement != ''):
			statement = statement +' OR '
		statement = statement + andStatementArtwork
	
	orStatementArtwork =  buildArtworkStatement(config, config.missingFilterArtwork.orGroup, ' OR ')
	if(orStatementArtwork != ''):
		if (statement != ''):
			statement = statement +' OR '
		statement = statement + orStatementArtwork
	
	if(statement != ''):
		statement = '(%s)' %(statement)
		if(config.showHideOption.lower() == util.localize(40061)):
			statement = 'NOT ' +statement
	
	return statement


def buildInfoStatement(group, operator):
	statement = ''
	for item in group:
		if statement == '':
			statement = '('
		else:
			statement = statement + operator
		statement = statement + config.gameproperties[item][1]
	if(statement != ''):
		statement = statement + ')'
	
	return statement


def buildArtworkStatement(config, group, operator):
	statement = ''
	for item in group:
		if statement == '':
			statement = '('
		else:
			statement = statement + operator
			
		typeId = ''
						
		fileTypeRows = config.tree.findall('FileTypes/FileType')
		for element in fileTypeRows:
			if(element.attrib.get('name') == item):
				typeId = element.attrib.get('id')
				break
		statement = statement + 'Id NOT IN (SELECT ParentId from File Where fileTypeId = %s)' %str(typeId) 
	
	if(statement != ''):
		statement = statement + ')'
	
	return statement
