
import os, sys


#
# CONSTANTS #
#

LOG_LEVEL_ERROR = 0
LOG_LEVEL_WARNING = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_DEBUG = 3

CURRENT_LOG_LEVEL = LOG_LEVEL_DEBUG

SETTING_RCB_VIEW_MODE = 'rcb_view_mode'

ROW_ID = 0
ROW_NAME = 1

RCBSETTING_lastSelectedView = 1
RCBSETTING_lastSelectedConsoleIndex = 2
RCBSETTING_lastSelectedGenreIndex = 3
RCBSETTING_lastSelectedPublisherIndex = 4
RCBSETTING_lastSelectedYearIndex = 5
RCBSETTING_lastSelectedGameIndex = 6
RCBSETTING_favoriteConsoleId = 7
RCBSETTING_favoriteGenreId = 8
RCBSETTING_autoexecBackupPath = 9
RCBSETTING_dbVersion = 10
RCBSETTING_showEntryAllConsoles = 11
RCBSETTING_showEntryAllGenres = 12
RCBSETTING_showEntryAllYears = 13
RCBSETTING_showEntryAllPublisher = 14
RCBSETTING_saveViewStateOnExit = 15
RCBSETTING_saveViewStateOnLaunchEmu = 16
RCBSETTING_lastFocusedControlMainView = 17
RCBSETTING_lastFocusedControlGameInfoView = 18

GAME_description = 2
GAME_romCollectionId = 5
GAME_publisherId = 6
GAME_developerId = 7

VIEW_MAINVIEW = 'mainView'
VIEW_GAMEINFOVIEW = 'gameInfoView'

IMAGE_CONTROL_MV_BACKGROUND = 'mainviewbackground'
IMAGE_CONTROL_MV_GAMELIST = 'gamelist'
IMAGE_CONTROL_MV_GAMELISTSELECTED = 'gamelistselected'
IMAGE_CONTROL_MV_GAMEINFO = 'mainviewgameinfo'

TEXT_CONTROL_MV_GAMEDESC = 'gamedesc'



#
# METHODS #
#

def log(message, logLevel):
		
		if(logLevel > CURRENT_LOG_LEVEL):
			return
			
		prefix = ''
		if(logLevel == LOG_LEVEL_DEBUG):
			prefix = 'RCB_DEBUG: '
		elif(logLevel == LOG_LEVEL_INFO):
			prefix = 'RCB_INFO: '
		elif(logLevel == LOG_LEVEL_WARNING):
			prefix = 'RCB_WARNING: '
		elif(logLevel == LOG_LEVEL_ERROR):
			prefix = 'RCB_ERROR: '

		print prefix + message