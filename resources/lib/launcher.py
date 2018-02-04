import os, sys, re
import time, zipfile, glob, shutil

import dbupdate, util
from gamedatabase import *
from util import *
from util import Logutil as log
import xbmc, xbmcgui, xbmcvfs


KODI_JSONRPC_TOGGLE_FULLSCREEN = '{"jsonrpc": "2.0", "method": "Input.ExecuteAction", "params": {"action": "togglefullscreen"}, "id": "1"}'


class RCBLauncher(object):
	def __init__(self):
		pass

	def launchEmu(self, gdb, gui, gameId, config, listitem):
		log.info("Begin launcher.launchEmu")

		gameRow = Game(gdb).getObjectById(gameId)
		if gameRow is None:
			log.error("Game with id %s could not be found in database" % gameId)
			return

		romCollection = None
		try:
			romCollection = config.romCollections[str(gameRow[util.GAME_romCollectionId])]
		except KeyError:
			log.error("Cannot get rom collection with id: " + str(gameRow[util.GAME_romCollectionId]))
			gui.writeMsg(util.localize(32034))
			return

		gui.writeMsg(util.localize(32163) + " " + gameRow[util.ROW_NAME])

		# Remember viewstate
		gui.saveViewState(False)

		cmd = ""
		precmd = ""
		postcmd = ""

		# get environment OS
		env = util.getEnvironment()

		filenameRows = File(gdb).getRomsByGameId(gameRow[util.ROW_ID])
		log.info("files for current game: " + str(filenameRows))

		escapeCmd = xbmc.Addon().getSetting(util.SETTING_RCB_ESCAPECOMMAND).upper() == 'TRUE'
		cmd, precmd, postcmd, roms = self.__buildCmd(gui, filenameRows, romCollection, gameRow, escapeCmd, False)

		if not romCollection.useBuiltinEmulator:
			if cmd == '':
				log.info("No cmd created. Game will not be launched.")
				return
			if precmd.strip() == '' or precmd.strip() == 'call':
				log.info("No precmd created.")

			if postcmd.strip() == '' or postcmd.strip() == 'call':
				log.info("No postcmd created.")

			# solo mode
			if romCollection.useEmuSolo:

				self.__copyLauncherScriptsToUserdata()

				# communicate with service via settings
				xbmc.Addon().setSetting(util.SETTING_RCB_LAUNCHONSTARTUP, 'true')

				# invoke script file that kills xbmc before launching the emulator
				basePath = os.path.join(util.getAddonDataPath(), 'scriptfiles')

				if env == "win32":
					if xbmc.Addon().getSetting(util.SETTING_RCB_USEVBINSOLOMODE).lower() == 'true':
						# There is a problem with quotes passed as argument to windows command shell. This only works with "call"
						# use vb script to restart xbmc
						cmd = 'call \"' + os.path.join(basePath,
													   'applaunch-vbs.bat') + '\" ' + cmd
					else:
						# There is a problem with quotes passed as argument to windows command shell. This only works with "call"
						cmd = 'call \"' + os.path.join(basePath, 'applaunch.bat') + '\" ' + cmd
				else:
					cmd = os.path.join(basePath, 'applaunch.sh ') + cmd
			else:
				# use call to support paths with whitespaces
				if env == "win32":
					cmd = 'call ' + cmd

		# update LaunchCount
		launchCount = gameRow[util.GAME_launchCount]
		Game(gdb).update(('launchCount',), (launchCount + 1,), gameRow[util.ROW_ID], True)
		gdb.commit()

		log.info("cmd: " + cmd)
		log.info("precmd: " + precmd)
		log.info("postcmd: " + postcmd)

		try:
			self.__launchNonXbox(cmd, romCollection, gameRow, precmd, postcmd, roms, gui, listitem)

			gui.writeMsg("")

		except Exception, (exc):
			log.error("Error while launching emu: " + str(exc))
			gui.writeMsg(util.localize(32035) + ": " + str(exc))

		log.info("End launcher.launchEmu")

	def __buildCmd(self, gui, filenameRows, romCollection, gameRow, escapeCmd, calledFromSkin):
		log.info("launcher.buildCmd")

		compressedExtensions = ['7z', 'zip']

		cmd = ""
		precmd = ""
		postcmd = ""

		emuCommandLine = romCollection.emulatorCmd
		log.info("emuCommandLine: " + emuCommandLine)
		log.info("preCmdLine: " + romCollection.preCmd)
		log.info("postCmdLine: " + romCollection.postCmd)

		# handle savestates
		stateFile = self.__checkGameHasSaveStates(romCollection, gameRow, filenameRows, escapeCmd)

		if stateFile == '':
			emuParams = romCollection.emulatorParams
		else:
			emuParams = romCollection.saveStateParams
			if escapeCmd:
				stateFile = re.escape(stateFile)
			emuParams = emuParams.replace('%statefile%', stateFile)
			emuParams = emuParams.replace('%STATEFILE%', stateFile)
			emuParams = emuParams.replace('%Statefile%', stateFile)

		# params could be: {-%I% %ROM%}
		# we have to repeat the part inside the brackets and replace the %I% with the current index
		emuParams, partToRepeat = self.__prepareMultiRomCommand(emuParams)

		# ask for disc number if multidisc game
		diskName = ""
		if romCollection.diskPrefix != '' and '%I%' not in emuParams:
			log.info("Getting Multiple Disc Parameter")
			options = []
			for disk in filenameRows:
				gamename = os.path.basename(disk[0])
				match = re.search(romCollection.diskPrefix.lower(), str(gamename).lower())
				if match:
					disk = gamename[match.start():match.end()]
					options.append(disk)
			if len(options) > 1 and not calledFromSkin:
				diskNum = xbmcgui.Dialog().select(util.localize(32164) + ': ', options)
				if diskNum < 0:
					# don't launch game
					log.info("No disc was chosen. Won't launch game")
					return "", "", "", None
				else:
					diskName = options[diskNum]
					log.info("Chosen Disc: %s" % diskName)

		# insert game specific command
		gameCmd = ''
		if gameRow[util.GAME_gameCmd] is not None:
			gameCmd = str(gameRow[util.GAME_gameCmd])
		# be case insensitive with (?i)
		emuParams = re.sub('(?i)%gamecmd%', gameCmd, emuParams)

		log.info("emuParams: " + emuParams)

		fileindex = int(0)
		for fileNameRow in filenameRows:
			rom = fileNameRow[0]
			log.info("rom: " + str(rom))

			if romCollection.makeLocalCopy:
				localDir = os.path.join(util.getTempDir(), romCollection.name)
				if xbmcvfs.exists(localDir + '\\'):
					log.info("Trying to delete local rom files")
					dirs, files = xbmcvfs.listdir(localDir)
					for f in files:
						xbmcvfs.delete(os.path.join(localDir, f))
				localRom = os.path.join(localDir, os.path.basename(str(rom)))
				log.info("Creating local copy: " + str(localRom))
				if xbmcvfs.copy(rom, localRom):
					log.info("Local copy created")
				rom = localRom

			# If it's a .7z file
			# Don't extract zip files in case of savestate handling and when called From skin
			filext = rom.split('.')[-1]
			roms = [rom]
			if filext in compressedExtensions and not romCollection.doNotExtractZipFiles and stateFile == '' and not calledFromSkin:
				roms = self.__handleCompressedFile(gui, filext, rom, romCollection, emuParams)
				log.debug("roms compressed = " + str(roms))
				if len(roms) == 0:
					return "", "", "", None

			# no use for complete cmd as we just need the game name
			if romCollection.useBuiltinEmulator:
				log.debug("roms = " + str(roms))
				return "", "", "", roms

			del rom

			for rom in roms:
				precmd = ""
				postcmd = ""
				if fileindex == 0:
					emuParams = self.__replacePlaceholdersInParams(emuParams, rom, romCollection, gameRow, escapeCmd)
					if escapeCmd:
						emuCommandLine = re.escape(emuCommandLine)

					if romCollection.name in ['Linux', 'Macintosh', 'Windows']:
						cmd = self.__replacePlaceholdersInParams(emuCommandLine, rom, romCollection, gameRow, escapeCmd)
					else:
						cmd = '\"' + emuCommandLine + '\" ' + emuParams.replace('%I%', str(fileindex))
				else:
					newrepl = partToRepeat
					newrepl = self.__replacePlaceholdersInParams(newrepl, rom, romCollection, gameRow, escapeCmd)
					if escapeCmd:
						emuCommandLine = re.escape(emuCommandLine)

					newrepl = newrepl.replace('%I%', str(fileindex))
					cmd += ' ' + newrepl

				cmdprefix = ''
				env = (os.environ.get("OS", "win32"), "win32",)[os.environ.get("OS", "win32") == "xbox"]
				if env == "win32":
					cmdprefix = 'call '

				precmd = cmdprefix + self.__replacePlaceholdersInParams(romCollection.preCmd, rom, romCollection, gameRow,
																   escapeCmd)
				postcmd = cmdprefix + self.__replacePlaceholdersInParams(romCollection.postCmd, rom, romCollection, gameRow,
																	escapeCmd)

				fileindex += 1

		# A disk was chosen by the user, select it here
		if diskName:
			log.info("Choosing Disk: " + str(diskName))
			match = re.search(romCollection.diskPrefix.lower(), cmd.lower())
			replString = cmd[match.start():match.end()]
			cmd = cmd.replace(replString, diskName)

		return cmd, precmd, postcmd, roms

	def __checkGameHasSaveStates(self, romCollection, gameRow, filenameRows, escapeCmd):

		if romCollection.saveStatePath == '':
			log.debug("No save state path set")
			return ''

		rom = filenameRows[0][0]
		saveStatePath = self.__replacePlaceholdersInParams(romCollection.saveStatePath, rom, romCollection, gameRow, escapeCmd)

		saveStateFiles = glob.glob(saveStatePath)

		if len(saveStateFiles) == 0:
			log.debug("No save state files found")
			return ''

		log.info('saveStateFiles found: ' + str(saveStateFiles))

		# don't select savestatefile if ASKNUM is requested in Params
		if re.search('(?i)%ASKNUM%', romCollection.saveStateParams):
			return saveStateFiles[0]

		options = [util.localize(32165)]
		for f in saveStateFiles:
			options.append(os.path.basename(f))
		selectedFile = xbmcgui.Dialog().select(util.localize(32166), options)
		# If selections is canceled or "Don't launch statefile" option
		if selectedFile < 1:
			return ''

		return saveStateFiles[selectedFile - 1]

	def __prepareMultiRomCommand(self, emuParams):
		obIndex = emuParams.find('{')
		cbIndex = emuParams.find('}')
		partToRepeat = ''
		if obIndex > -1 and cbIndex > 1:
			partToRepeat = emuParams[obIndex+1:cbIndex]
		emuParams = emuParams.replace("{", "")
		emuParams = emuParams.replace("}", "")

		return emuParams, partToRepeat

	def __handleCompressedFile(self, gui, filext, rom, romCollection, emuParams):

		log.info("__handleCompressedFile")

		# Note: Trying to delete temporary files (from zip or 7z extraction) from last run
		# Do this before launching a new game. Otherwise game could be deleted before launch
		tempDir = os.path.join(util.getTempDir(), 'extracted', romCollection.name)
		# check if folder exists
		if not xbmcvfs.exists(tempDir +'\\'):
			log.info("Create temporary folder: " +tempDir)
			xbmcvfs.mkdir(tempDir)

		try:
			if xbmcvfs.exists(tempDir +'\\'):
				log.info("Trying to delete temporary rom files")
				#can't use xbmcvfs.listdir here as it seems to cache the file list and RetroPlayer won't find newly created files anymore
				files = os.listdir(tempDir)
				for f in files:
					#RetroPlayer places savestate files next to the roms. Don't delete these files.
					fname, ext = os.path.splitext(f)
					if(ext not in ('.sav', '.xml', '.png')):
						xbmcvfs.delete(os.path.join(tempDir, f))
		except Exception, (exc):
			log.error("Error deleting files after launch emu: " + str(exc))
			gui.writeMsg(util.localize(32036) + ": " + str(exc))

		roms = []

		log.info("Treating file as a compressed archive")
		compressed = True

		try:
			names = self.__getNames(filext, rom)
		except Exception, (exc):
			log.error("Error handling compressed file: " + str(exc))
			return []

		if names is None:
			log.error("Error handling compressed file")
			return []

		chosenROM = -1

		# check if we should handle multiple roms
		match = False
		if romCollection.diskPrefix != '':
			match = re.search(romCollection.diskPrefix.lower(), str(names).lower())

		if '%I%' in emuParams and match:
			log.info("Loading %d archives" % len(names))

			try:
				archives = self.__getArchives(filext, rom, names)
			except Exception, (exc):
				log.error("Error handling compressed file: " +str(exc))
				return []

			if archives is None:
				log.warning("Error handling compressed file")
				return []
			for archive in archives:
				newPath = os.path.join(tempDir, archive[0])
				fp = open(newPath, 'wb')
				fp.write(archive[1])
				fp.close()
				roms.append(newPath)

		elif len(names) > 1:
			log.info("The Archive has %d files" % len(names))
			chosenROM = xbmcgui.Dialog().select('Choose a ROM', names)
		elif len(names) == 1:
			log.info("Archive only has one file inside; picking that one")
			chosenROM = 0
		else:
			log.error("Archive had no files inside!")
			return []

		if chosenROM != -1:
			# Extract all files to %TMP%
			archives = self.__getArchives(filext, rom, names)
			if archives is None:
				log.warn("Error handling compressed file")
				return []
			for archive in archives:
				newPath = os.path.join(tempDir, archive[0])
				log.info("Putting extracted file in %s" % newPath)
				fo = open(str(newPath), 'wb')
				fo.write(archive[1])
				fo.close()

			# Point file name to the chosen file and continue as usual
			roms = [os.path.join(tempDir, names[chosenROM])]

		return roms

	def __replacePlaceholdersInParams(self, emuParams, rom, romCollection, gameRow, escapeCmd):

		if escapeCmd:
			rom = re.escape(rom)

		# TODO: Wanted to do this with re.sub:
		# emuParams = re.sub(r'(?i)%rom%', rom, emuParams)
		# --> but this also replaces \r \n with linefeed and newline etc.

		# full rom path ("C:\Roms\rom.zip")
		emuParams = emuParams.replace('%rom%', rom)
		emuParams = emuParams.replace('%ROM%', rom)
		emuParams = emuParams.replace('%Rom%', rom)

		# romfile ("rom.zip")
		romfile = os.path.basename(rom)
		emuParams = emuParams.replace('%romfile%', romfile)
		emuParams = emuParams.replace('%ROMFILE%', romfile)
		emuParams = emuParams.replace('%Romfile%', romfile)

		# romname ("rom")
		romname = os.path.splitext(os.path.basename(rom))[0]
		emuParams = emuParams.replace('%romname%', romname)
		emuParams = emuParams.replace('%ROMNAME%', romname)
		emuParams = emuParams.replace('%Romname%', romname)

		# gamename
		gamename = unicode(gameRow[util.ROW_NAME])
		emuParams = emuParams.replace('%game%', gamename)
		emuParams = emuParams.replace('%GAME%', gamename)
		emuParams = emuParams.replace('%Game%', gamename)

		# ask num
		if re.search('(?i)%ASKNUM%', emuParams):
			options = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
			number = unicode(xbmcgui.Dialog().select(util.localize(32167), options))
			emuParams = emuParams.replace('%asknum%', number)
			emuParams = emuParams.replace('%ASKNUM%', number)
			emuParams = emuParams.replace('%Asknum%', number)

		# ask text
		if re.search('(?i)%ASKTEXT%', emuParams):
			command = xbmcgui.Dialog().input(util.localize(32168), type=xbmcgui.INPUT_ALPHANUM)

			emuParams = emuParams.replace('%asktext%', command)
			emuParams = emuParams.replace('%ASKTEXT%', command)
			emuParams = emuParams.replace('%Asktext%', command)

		return emuParams

	def __copyLauncherScriptsToUserdata(self):
		log.info('__copyLauncherScriptsToUserdata')

		oldBasePath = os.path.join(util.getAddonInstallPath(), 'resources', 'scriptfiles')
		newBasePath = os.path.join(util.getAddonDataPath(), 'scriptfiles')

		files = []
		# Copy applaunch shell script/batch file
		if util.getEnvironment() == 'win32':
			files.append('applaunch.bat')
		else:
			files.append('applaunch.sh')

		# Copy VBS files
		if util.getEnvironment() == 'win32' and xbmc.Addon().getSetting(util.SETTING_RCB_USEVBINSOLOMODE).lower() == 'true':
			files += ['applaunch-vbs.bat', 'LaunchKodi.vbs', 'Sleep.vbs']

		for f in files:
			if not xbmcvfs.exists(os.path.join(newBasePath, f)):
				log.debug("Copying file {0} from {1} to {2}".format(f, oldBasePath, newBasePath))
				if not xbmcvfs.copy(os.path.join(oldBasePath, f), os.path.join(newBasePath, f)):
					log.warn("Error copying file")

	def __audioSuspend(self):
		if xbmcaddon.Addon().getSetting(util.SETTING_RCB_SUSPENDAUDIO).upper() == 'TRUE':
			log.debug("Suspending audio")
			xbmc.executebuiltin("PlayerControl(Stop)")
			xbmc.enableNavSounds(False)
			xbmc.audioSuspend()

	def __audioResume(self):
		if xbmcaddon.Addon().getSetting(util.SETTING_RCB_SUSPENDAUDIO).upper() == 'TRUE':
			log.debug("Resuming audio")
			xbmc.audioResume()
			xbmc.enableNavSounds(True)

	def __preDelay(self):
		preDelay = xbmcaddon.Addon().getSetting(SETTING_RCB_PRELAUNCHDELAY)
		if preDelay != '':
			log.debug("Pre delaying by {0}ms".format(preDelay))
			xbmc.sleep(int(float(preDelay)))

	def __postDelay(self):
		postDelay = xbmcaddon.Addon().getSetting(SETTING_RCB_POSTLAUNCHDELAY)
		if postDelay != '':
			log.debug("Post delaying by {0}ms".format(postDelay))
			xbmc.sleep(int(float(postDelay)))

	def __getEncoding(self):
		# HACK: sys.getfilesystemencoding() is not supported on all systems (e.g. Android)
		try:
			encoding = sys.getfilesystemencoding()
		except Exception as e:
			log.warn("Unable to get filesystem encoding, defaulting to UTF-8")
			encoding = 'utf-8'

		return encoding

	def __executePreCommand(self, precmd):
		# pre launch command
		if precmd.strip() != '' and precmd.strip() != 'call':
			log.info("Got to PRE: " + precmd.strip())
			os.system(precmd.encode(self.__getEncoding()))

	def __executeCommand(self, romCollection, cmd):
		# change working directory
		path = os.path.dirname(romCollection.emulatorCmd)
		if os.path.isdir(path):
			try:
				os.chdir(path)
			except OSError:
				log.warn("Unable to chdir to {0}".format(path))

		if romCollection.usePopen:
			import subprocess
			process = subprocess.Popen(cmd.encode(self.__getEncoding()), shell=True)
			process.wait()
		else:
			os.system(cmd.encode(self.__getEncoding()))

	def __executePostCommand(self, postcmd):
		# post launch command
		if postcmd.strip() != '' and postcmd.strip() != 'call':
			log.info("Got to POST: " + postcmd.strip())
			os.system(postcmd.encode(self.__getEncoding()))

	def __launchNonXbox(self, cmd, romCollection, gameRow, precmd, postcmd, roms, gui, listitem):
		log.info("launchEmu on non-xbox")

		screenModeToggled = False

		# use libretro core to play game
		if romCollection.useBuiltinEmulator:
			log.info("launching game with internal emulator")
			rom = roms[0]
			gameclient = romCollection.gameclient
			# HACK: use alternateGameCmd as gameclient
			if gameRow[util.GAME_alternateGameCmd] is not None and gameRow[util.GAME_alternateGameCmd] != "":
				gameclient = str(gameRow[util.GAME_alternateGameCmd])
			log.info("Preferred gameclient: " + gameclient)
			log.info("Setting platform: " + romCollection.name)

			if listitem is None:
				listitem = xbmcgui.ListItem(rom, "0", "", "")

			parameters = {"platform": romCollection.name}
			if gameclient != "":
				parameters["gameclient"] = gameclient
			listitem.setInfo(type="game", infoLabels=parameters)
			log.info("launching rom: " + rom)

			gui.player.play(rom, listitem)
			# xbmc.executebuiltin('PlayMedia(\"%s\", platform=%s, gameclient=%s)' %(rom, romCollection.name, romCollection.gameclient))
			return

		if not romCollection.useEmuSolo:
			screenMode = xbmc.getInfoLabel("System.Screenmode")
			log.info("screenMode: " + screenMode)
			isFullScreen = screenMode.endswith("Full Screen")

			toggleScreenMode = xbmc.Addon().getSetting(util.SETTING_RCB_TOGGLESCREENMODE).upper() == 'TRUE'

			if isFullScreen and toggleScreenMode:
				log.info("Toggling to windowed mode")
				# this minimizes xbmc some apps seems to need it
				xbmc.executeJSONRPC(KODI_JSONRPC_TOGGLE_FULLSCREEN)

				screenModeToggled = True

		log.info("launch emu")

		self.__executePreCommand(precmd)

		self.__preDelay()

		self.__audioSuspend()

		self.__executeCommand(romCollection, cmd)

		log.info("launch emu done")

		self.__postDelay()

		self.__audioResume()

		self.__executePostCommand(postcmd)

		if screenModeToggled:
			log.info("Toggle to Full Screen mode")
			# this brings xbmc back
			xbmc.executeJSONRPC(KODI_JSONRPC_TOGGLE_FULLSCREEN)

	# Compressed files functions
	def __getNames(self, type, filepath):
		return {'zip': self.__getNamesZip,
				'7z': self.__getNames7z}[type](filepath)

	def __getNames7z(self, filepath):

		try:
			import py7zlib
		except ImportError as e:
			xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32039), util.localize(32129))
			msg = ("You have tried to launch a .7z file but you are missing required libraries to extract the file. "
				   "You can download the latest RCB version from RCBs project page. It contains all required libraries.")
			log.error(msg)
			log.error("Error: " + str(e))
			return None

		fp = open(str(filepath), 'rb')
		archive = py7zlib.Archive7z(fp)
		names = archive.getnames()
		fp.close()
		return names

	def __getNamesZip(self, filepath):
		fp = open(str(filepath), 'rb')
		archive = zipfile.ZipFile(fp)
		names = archive.namelist()
		fp.close()
		return names

	def __getArchives(self, type, filepath, archiveList):
		return {'zip': self.__getArchivesZip,
				'7z': self.__getArchives7z}[type](filepath, archiveList)

	def __getArchives7z(self, filepath, archiveList):

		try:
			import py7zlib
		except ImportError:
			xbmcgui.Dialog().ok(util.SCRIPTNAME, util.localize(32039), util.localize(32129))
			msg = ("You have tried to launch a .7z file but you are missing required libraries to extract the file. "
				   "You can download the latest RCB version from RCBs project page. It contains all required libraries.")
			log.error(msg)
			return None

		fp = open(str(filepath), 'rb')
		archive = py7zlib.Archive7z(fp)
		archivesDecompressed = [(name, archive.getmember(name).read())for name in archiveList]
		fp.close()
		return archivesDecompressed

	def __getArchivesZip(self, filepath, archiveList):
		fp = open(str(filepath), 'rb')
		archive = zipfile.ZipFile(fp)
		archivesDecompressed = [(name, archive.read(name)) for name in archiveList]
		fp.close()
		return archivesDecompressed
