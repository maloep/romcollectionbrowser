
import os, sys, re
import dbupdate, importsettings
from gamedatabase import *
import util

RCBHOME = os.getcwd()


def getFilesByControl(gdb, controlName, gameId, publisherId, developerId, romCollectionId):
		util.log("getFilesByControl controlName: " +controlName, util.LOG_LEVEL_DEBUG)
		util.log("getFilesByControl gameId: " +str(gameId), util.LOG_LEVEL_DEBUG)
		util.log("getFilesByControl publisherId: " +str(publisherId), util.LOG_LEVEL_DEBUG)
		util.log("getFilesByControl developerId: " +str(developerId), util.LOG_LEVEL_DEBUG)
		util.log("getFilesByControl romCollectionId: " +str(romCollectionId), util.LOG_LEVEL_DEBUG)
	
		fileTypeForControlRows = FileTypeForControl(gdb).getFileTypesForControlByKey(romCollectionId, controlName)
		if(fileTypeForControlRows == None):
			util.log("fileTypeForControlRows == None", util.LOG_LEVEL_WARNING)
			return
		
		mediaFiles = []
		for fileTypeForControlRow in fileTypeForControlRows:
			
			fileTypeRow = FileType(gdb).getObjectById(fileTypeForControlRow[4])
			if(fileTypeRow == None):
				util.log("fileTypeRow == None in getFilesByControl", util.LOG_LEVEL_WARNING)
				continue
				
			parentId = None
			
			#fileTypeRow[3] = parent
			if(fileTypeRow[3] == 'game'):
				parentId = gameId
			elif(fileTypeRow[3] == 'console'):
				romCollectionRow = RomCollection(gdb).getObjectById(romCollectionId)
				if(romCollectionRow == None):
					util.log("romCollectionRow == None in getFilesByControl", util.LOG_LEVEL_WARNING)
					continue
				consoleId = romCollectionRow[2]			
				parentId = consoleId
			elif(fileTypeRow[3] == 'publisher'):
				parentId = publisherId
			elif(fileTypeRow[3] == 'developer'):
				parentId = developerId
			elif(fileTypeRow[3] == 'romcollection'):
				parentId = romCollectionId
				
			files = File(gdb).getFilesByGameIdAndTypeId(parentId, fileTypeForControlRow[4])
			for file in files:				
				mediaFiles.append(file[1])
				
		return mediaFiles
		


def launchEmu(gdb, gui, gameId):
		util.log("Begin helper.launchEmu", util.LOG_LEVEL_INFO)
		
		gameRow = Game(gdb).getObjectById(gameId)
		if(gameRow == None):
			util.log("Game with id %s could not be found in database" %gameId, util.LOG_LEVEL_ERROR)
			return
			
		gui.writeMsg("Launch Game " +str(gameRow[1]))
		
		romPaths = Path(gdb).getRomPathsByRomCollectionId(gameRow[5])
		romCollectionRow = RomCollection(gdb).getObjectById(gameRow[5])
		if(romCollectionRow == None):
			util.log("Rom Collection with id %s could not be found in database" %gameRow[5], util.LOG_LEVEL_ERROR)
			return
		cmd = romCollectionRow[3]		
		
		#handle multi rom scenario
		filenameRows = File(gdb).getRomsByGameId(gameRow[0])
		fileindex = int(0)
		for fileNameRow in filenameRows:
			fileName = fileNameRow[0]
			rom = ""
			#we could have multiple rom Paths - search for the correct one
			for romPath in romPaths:
				rom = os.path.join(romPath, fileName)
				if(os.path.isfile(rom)):
					break
			if(rom == ""):
				util.log("no rom file found for game: " +str(gameRow[1]), util.LOG_LEVEL_ERROR)
				
			#cmd could be: uae {-%I% %ROM%}
			#we have to repeat the part inside the brackets and replace the %I% with the current index
			obIndex = cmd.find('{')
			cbIndex = cmd.find('}')			
			if obIndex > -1 and cbIndex > 1:
				replString = cmd[obIndex+1:cbIndex]
			cmd = cmd.replace("{", "")
			cmd = cmd.replace("}", "")
			if fileindex == 0:
				#romCollectionRow[5] = escapeCmd
				if (romCollectionRow[5] == 1):				
					cmd = cmd.replace('%ROM%', re.escape(rom))					
				else:					
					cmd = cmd.replace('%ROM%', rom)
				cmd = cmd.replace('%I%', str(fileindex))
			else:
				newrepl = replString
				if (romCollectionRow[5] == 1):
					newrepl = newrepl.replace('%ROM%', re.escape(rom))					
				else:					
					newrepl = newrepl.replace('%ROM%', rom)
				newrepl = newrepl.replace('%I%', str(fileindex))
				cmd += ' ' +newrepl			
			fileindex += 1
		#romCollectionRow[4] = useSolo
		if (romCollectionRow[4] == 'True'):
			# Backup original autoexec.py		
			autoexec = os.path.join(RCBHOME, '..', 'autoexec.py')
			doBackup(gdb, autoexec)			

			# Write new autoexec.py
			try:
				fh = open(autoexec,'w') # truncate to 0
				fh.write("#Rom Collection Browser autoexec\n")
				fh.write("import xbmc\n")
				fh.write("xbmc.executescript('"+ os.path.join(RCBHOME, 'default.py')+"')\n")
				fh.close()
			except Exception, (exc):
				util.log("Cannot write to autoexec.py: " +str(exc), util.LOG_LEVEL_ERROR)
				return

			# Remember selection
			gui.saveViewState(False)
			
			#invoke batch file that kills xbmc before launching the emulator
			env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]				
			if(env == "win32"):
				#There is a problem with quotes passed as argument to windows command shell. This only works with "call"
				cmd = 'call \"' +os.path.join(RCBHOME, 'applaunch.bat') +'\" ' +cmd						
			else:
				cmd = os.path.join(re.escape(RCBHOME), 'applaunch.sh ') +cmd
		
		#update LaunchCount
		launchCount = gameRow[19]
		Game(gdb).update(('launchCount',), (launchCount +1,) , gameRow[0])
		gdb.commit()
		
		util.log("cmd: " +cmd, util.LOG_LEVEL_INFO)
		os.system(cmd)
		
		util.log("End helper.launchEmu", util.LOG_LEVEL_INFO)
		
		
def doBackup(gdb, fName):
		util.log("Begin helper.doBackup", util.LOG_LEVEL_INFO)
	
		if os.path.isfile(fName):
			newFileName = fName+'.bak'
			
			if os.path.isfile(newFileName):
				util.log("Cannot backup autoexec.py: File exists.", util.LOG_LEVEL_ERROR)
				return
			
			try:
				os.rename(fName, newFileName)
			except Exception, (exc):
				util.log("Cannot rename autoexec.py: " +str(exc), util.LOG_LEVEL_ERROR)
				return
			
			rcbSetting = getRCBSetting()
			if (rcbSetting == None):
				util.log("rcbSetting == None in doBackup", util.LOG_LEVEL_WARNING)
				return
			
			RCBSetting(gdb).update(('autoexecBackupPath',), (newFileName,), rcbSetting[0])
			gdb.commit()
			
		util.log("End helper.doBackup", util.LOG_LEVEL_INFO)
			
			
def saveViewState(gdb, isOnExit, selectedView, selectedGameIndex, selectedConsoleIndex, selectedGenreIndex, selectedPublisherIndex, selectedYearIndex, 
	selectedControlIdMainView, selectedControlIdGameInfoView):
		
		util.log("Begin helper.saveViewState", util.LOG_LEVEL_INFO)
		
		rcbSetting = getRCBSetting(gdb)
		if(rcbSetting == None):
			util.log("rcbSetting == None in helper.saveViewState", util.LOG_LEVEL_WARNING)
			return
		
		if(isOnExit):
			#saveViewStateOnExit
			saveViewState = rcbSetting[15]
		else:
			#saveViewStateOnLaunchEmu
			saveViewState = rcbSetting[16]
			
		
		if(saveViewState == 'True'):
			RCBSetting(gdb).update(('lastSelectedView', 'lastSelectedConsoleIndex', 'lastSelectedGenreIndex', 'lastSelectedPublisherIndex', 'lastSelectedYearIndex', 'lastSelectedGameIndex', 'lastFocusedControlMainView', 'lastFocusedControlGameInfoView'),
				(selectedView, selectedConsoleIndex, selectedGenreIndex, selectedPublisherIndex, selectedYearIndex, selectedGameIndex, selectedControlIdMainView, selectedControlIdGameInfoView), rcbSetting[0])
		else:
			RCBSetting(gdb).update(('lastSelectedView', 'lastSelectedConsoleIndex', 'lastSelectedGenreIndex', 'lastSelectedPublisherIndex', 'lastSelectedYearIndex', 'lastSelectedGameIndex', 'lastFocusedControlMainView', 'lastFocusedControlGameInfoView'),
				(None, None, None, None, None, None, None, None), rcbSetting[0])
				
		gdb.commit()
		
		util.log("End helper.saveViewState", util.LOG_LEVEL_INFO)


			
def getRCBSetting(gdb):
		rcbSettingRows = RCBSetting(gdb).getAll()
		if(rcbSettingRows == None or len(rcbSettingRows) != 1):
			#TODO raise error
			return None
						
		return rcbSettingRows[0]