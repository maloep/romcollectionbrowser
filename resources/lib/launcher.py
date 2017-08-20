import xbmc, xbmcgui
import os, sys, re
import dbupdate, util, helper
from gamedatabase import *
from util import *
from util import Logutil as log
import time, zipfile, glob, shutil
import struct, io
from collections import namedtuple

KODI_JSONRPC_TOGGLE_FULLSCREEN = '{"jsonrpc": "2.0", "method": "Input.ExecuteAction", "params": {"action": "togglefullscreen"}, "id": "1"}'

PKZIP_EOCD = namedtuple('PKZIP_EOCD', ['signature', 'disk_cnt', 'cdir_disk', 'cdir_cnt_disk', 'cdir_cnt', 'cdir_sz', 'cdir_pos', 'cmmt_sz', 'cmmt'])
PKZIP_CDIR = namedtuple('PKZIP_CDIR', ['signature', 'ver_crt', 'ver_min', 'gen_flg', 'cmpr_typ', 'mod_tim', 'mod_dte', 'crc32', 'cmpr_sz', 'real_sz', 'fname_sz', 'extra_sz', 'cmmt_sz', 'start_disk', 'int_attr', 'ext_attr', 'rel_pos', 'fname', 'extra', 'cmmt'])
			
def launchEmu(gdb, gui, gameId, config, settings, listitem):
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

	escapeCmd = settings.getSetting(util.SETTING_RCB_ESCAPECOMMAND).upper() == 'TRUE'
	cmd, precmd, postcmd, roms = __buildCmd(filenameRows, romCollection, gameRow, escapeCmd, False)
	
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
			
			__copyLauncherScriptsToUserdata(settings)

			# communicate with service via settings
			settings.setSetting(util.SETTING_RCB_LAUNCHONSTARTUP, 'true')
			
			# invoke script file that kills xbmc before launching the emulator
			basePath = os.path.join(util.getAddonDataPath(), 'scriptfiles')
			# xbmc needs other script files than kodi
			xbmcFilenameSuffix = "_xbmc"
			if KodiVersions().getKodiVersion() >= KodiVersions.HELIX:
				xbmcFilenameSuffix = ""
						
			if env == "win32":
				if settings.getSetting(util.SETTING_RCB_USEVBINSOLOMODE).lower() == 'true':
					# There is a problem with quotes passed as argument to windows command shell. This only works with "call"
					# use vb script to restart xbmc
					cmd = 'call \"' + os.path.join(basePath, 'applaunch-vbs%s.bat' % xbmcFilenameSuffix) + '\" ' + cmd
				else:					
					# There is a problem with quotes passed as argument to windows command shell. This only works with "call"
					cmd = 'call \"' + os.path.join(basePath, 'applaunch%s.bat' % xbmcFilenameSuffix) + '\" ' + cmd
			else:
				cmd = os.path.join(basePath, 'applaunch%s.sh ' % xbmcFilenameSuffix) + cmd
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
		__launchNonXbox(cmd, romCollection, gameRow, settings, precmd, postcmd, roms, gui, listitem)
	
		gui.writeMsg("")
					
	except Exception, (exc):
		log.error("Error while launching emu: " + str(exc))
		gui.writeMsg(util.localize(32035) + ": " + str(exc))

	log.info("End launcher.launchEmu")


##################

# HELPER METHODS #

##################
		
		
def __buildCmd(filenameRows, romCollection, gameRow, escapeCmd, calledFromSkin):
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
	stateFile = __checkGameHasSaveStates(romCollection, gameRow, filenameRows, escapeCmd)
		
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
	emuParams, partToRepeat = __prepareMultiRomCommand(emuParams)

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
			if os.path.exists(localDir):
				log.info("Trying to delete local rom files")
				files = os.listdir(localDir)
				for f in files:
					os.remove(os.path.join(localDir, f))
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
			roms = __handleCompressedFile(filext, rom, romCollection, emuParams)
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
				emuParams = __replacePlaceholdersInParams(emuParams, rom, romCollection, gameRow, escapeCmd)
				if escapeCmd:
					emuCommandLine = re.escape(emuCommandLine)
				
				if romCollection.name in ['Linux', 'Macintosh', 'Windows']:
					cmd = __replacePlaceholdersInParams(emuCommandLine, rom, romCollection, gameRow, escapeCmd)
				else:
					cmd = '\"' + emuCommandLine + '\" ' + emuParams.replace('%I%', str(fileindex))
			else:
				newrepl = partToRepeat
				newrepl = __replacePlaceholdersInParams(newrepl, rom, romCollection, gameRow, escapeCmd)
				if escapeCmd:
					emuCommandLine = re.escape(emuCommandLine)

				newrepl = newrepl.replace('%I%', str(fileindex))
				cmd += ' ' + newrepl
				
			cmdprefix = ''
			env = (os.environ.get("OS", "win32"), "win32", )[os.environ.get("OS", "win32") == "xbox"]
			if env == "win32":
				cmdprefix = 'call '
				
			precmd = cmdprefix + __replacePlaceholdersInParams(romCollection.preCmd, rom, romCollection, gameRow, escapeCmd)
			postcmd = cmdprefix + __replacePlaceholdersInParams(romCollection.postCmd, rom, romCollection, gameRow, escapeCmd)
						
			fileindex += 1

	# A disk was chosen by the user, select it here
	if diskName:
		log.info("Choosing Disk: " + str(diskName))
		match = re.search(romCollection.diskPrefix.lower(), cmd.lower())
		replString = cmd[match.start():match.end()]
		cmd = cmd.replace(replString, diskName)
			
	return cmd, precmd, postcmd, roms


def __checkGameHasSaveStates(romCollection, gameRow, filenameRows, escapeCmd):
	
	if romCollection.saveStatePath == '':
		log.debug("No save state path set")
		return ''
		
	rom = filenameRows[0][0]
	saveStatePath = __replacePlaceholdersInParams(romCollection.saveStatePath, rom, romCollection, gameRow, escapeCmd)
		
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


def __prepareMultiRomCommand(emuParams):
	obIndex = emuParams.find('{')
	cbIndex = emuParams.find('}')			
	partToRepeat = ''
	if obIndex > -1 and cbIndex > 1:
		partToRepeat = emuParams[obIndex+1:cbIndex]
	emuParams = emuParams.replace("{", "")
	emuParams = emuParams.replace("}", "")
	
	return emuParams, partToRepeat


def __handleCompressedFile(filext, rom, romCollection, emuParams):
	
	# Note: Trying to delete temporary files (from zip or 7z extraction) from last run
	# Do this before launching a new game. Otherwise game could be deleted before launch
	tempDir = os.path.join(util.getTempDir(), 'extracted')
	# check if folder exists
	if not os.path.isdir(tempDir):
		os.mkdir(tempDir)
	
	try:		
		if os.path.exists(tempDir):
			log.info("Trying to delete temporary rom files")
			files = os.listdir(tempDir)
			for f in files:
				os.remove(os.path.join(tempDir, f))
	except Exception, (exc):
		log.error("Error deleting files after launch emu: " + str(exc))
		gui.writeMsg(util.localize(32036) + ": " + str(exc))
	
	roms = []
	
	pze = romCollection.progressiveZipExtraction
	
	log.info("Treating file as a compressed archive")
	compressed = True						

	try:
		names = __getNames(filext, rom, pze)
	except Exception, (exc):
		log.error("Error handling compressed file: " + str(exc))
		return []
	
	if names is None:
		log.error("Error handling compressed file")
		return []
	
	cdirs = []	
	if pze:
		cdirs = names
		names = []
		for cdir in cdirs:
			names.append(cdir.fname)
	
	chosenROM = -1
	
	# check if we should handle multiple roms
	match = False
	if romCollection.diskPrefix != '':
		match = re.search(romCollection.diskPrefix.lower(), str(names).lower())
	
	if '%I%' in emuParams and match:
		log.info("Loading %d archives" % len(names))

		try:
			archives = __getArchives(filext, rom, names if not pze else cdirs, pze)
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
	log.info(names[chosenROM])
	if chosenROM != -1:
		# Extract all files to %TMP%
		# ... or just the chosen one, in case progressiveZipExtraction is being used
		archives = __getArchives(filext, rom, names if not pze else [cdirs[chosenROM]], pze)
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


def __replacePlaceholdersInParams(emuParams, rom, romCollection, gameRow, escapeCmd):
		
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
		
		keyboard = xbmc.Keyboard()
		keyboard.setHeading(util.localize(32168))
		keyboard.doModal()
		command = ''
		if keyboard.isConfirmed():
			command = keyboard.getText()
		
		emuParams = emuParams.replace('%asktext%', command)
		emuParams = emuParams.replace('%ASKTEXT%', command)
		emuParams = emuParams.replace('%Asktext%', command)
	
	return emuParams

def __copyLauncherScriptsToUserdata(settings):
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
	if util.getEnvironment() == 'win32' and settings.getSetting(util.SETTING_RCB_USEVBINSOLOMODE).lower() == 'true':
		files += ['applaunch-vbs.bat', 'LaunchXBMC.vbs', 'Sleep.vbs']

	for f in files:
		log.debug("Copying file {0} from {1} to {2}".format(f, oldBasePath, newBasePath))
		if not xbmcvfs.copy(os.path.join(oldBasePath, f), os.path.join(newBasePath, f)):
			log.warn("Error copying file")
	
def __launchNonXbox(cmd, romCollection, gameRow, settings, precmd, postcmd, roms, gui, listitem):
	log.info("launchEmu on non-xbox")

	screenModeToggled = False
		
	encoding = 'utf-8'
	# HACK: sys.getfilesystemencoding() is not supported on all systems (e.g. Android)
	try:
		encoding = sys.getfilesystemencoding()
	except:
		pass
	
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
		
		toggleScreenMode = settings.getSetting(util.SETTING_RCB_TOGGLESCREENMODE).upper() == 'TRUE'
		
		if isFullScreen and toggleScreenMode:
			log.info("Toggling to windowed mode")
			# this minimizes xbmc some apps seems to need it
			xbmc.executeJSONRPC(KODI_JSONRPC_TOGGLE_FULLSCREEN)
			
			screenModeToggled = True

	log.info("launch emu")

	# pre launch command
	if precmd.strip() != '' and precmd.strip() != 'call':
		log.info("Got to PRE: " + precmd.strip())
		os.system(precmd.encode(encoding))
	
	preDelay = settings.getSetting(SETTING_RCB_PRELAUNCHDELAY)
	if preDelay != '':
		preDelay = int(float(preDelay))
		xbmc.sleep(preDelay)
	
	# change working directory
	path = os.path.dirname(romCollection.emulatorCmd)
	if os.path.isdir(path):
		try:
			os.chdir(path)
		except OSError:
			pass

	# pause audio
	suspendAudio = settings.getSetting(util.SETTING_RCB_SUSPENDAUDIO).upper() == 'TRUE'
	if suspendAudio:
		xbmc.executebuiltin("PlayerControl(Stop)")
		xbmc.enableNavSounds(False)
		xbmc.audioSuspend()
	
	if romCollection.usePopen:
		import subprocess
		process = subprocess.Popen(cmd.encode(encoding), shell=True)
		process.wait()
	else:
		try:
			os.system(cmd.encode(encoding))
		except:
			os.system(cmd.encode('utf-8'))

	log.info("launch emu done")

	postDelay = settings.getSetting(SETTING_RCB_POSTLAUNCHDELAY)
	if postDelay != '':
		postDelay = int(float(postDelay))
		xbmc.sleep(postDelay)
	
	# resume audio
	if suspendAudio:
		xbmc.audioResume()
		xbmc.enableNavSounds(True)
	
	# post launch command
	if postcmd.strip() != '' and postcmd.strip() != 'call':
		log.info("Got to POST: " + postcmd.strip())
		os.system(postcmd.encode(encoding))
	
	if screenModeToggled:
		log.info("Toggle to Full Screen mode")
		# this brings xbmc back
		xbmc.executeJSONRPC(KODI_JSONRPC_TOGGLE_FULLSCREEN)

	
# Compressed files functions

def __getNames(type, filepath, pze):
	return {'zip': __getNamesZip,
			'7z': __getNames7z}[type](filepath, pze)


def __getNames7z(filepath, pze):
	
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

	
def __getNamesZip(filepath, pze):
	if not pze:
		fp = open(str(filepath), 'rb')
		archive = zipfile.ZipFile(fp)
		names = archive.namelist()
		fp.close()
		return names
	else:
		log.info('Reading files in compressed file in pze: ' + filepath)
		names = []
		fp = xbmcvfs.File(filepath, 'r')
		if not fp:
			log.error('Error while opening compressed file in pze: ' + filepath)
		else:
			file_sz = fp.size()
			eocd_sz = 256 # should be enough if there is no extensive comment in the eocd.
			if not fp.seek(-eocd_sz, 2):
				log.error('Error while seeking compressed file in pze: ' + filepath)
			else:
				eocd_bin = fp.readBytes(eocd_sz)
				if not eocd_bin:
					log.error('Error while reading compressed file in pze: ' + filepath)
				else:
					eocd_pos = eocd_bin.rfind(b'\x50\x4b\x05\x06')
					if not eocd_pos >= 0:
						log.error('No EOCD block found at the end on compressed file in pze: ' + filepath)
					else:							
						eocd = PKZIP_EOCD._make(struct.unpack('<LHHHHLLH0s', eocd_bin[eocd_pos:eocd_pos + 34]))
						eocd = PKZIP_EOCD._make(struct.unpack('<LHHHHLLH' + str(eocd.cmmt_sz) + 's', eocd_bin[eocd_pos:eocd_pos + 34 + eocd.cmmt_sz]))
						#-- End Of Central Dictionary record found. 
						log.info('{:08X}'.format(eocd.signature))
						log.info(eocd)
						if not(eocd.cdir_cnt > 0 and eocd.cdir_cnt == eocd.cdir_cnt_disk):
							log.error('Compressed file is empty or multidisk in pze: ' + filepath)
						else:	
							if not fp.seek(eocd.cdir_pos, 0):
								log.error('Error while seeking compressed file in pze: ' + filepath)
							else:
								cdir_bin = fp.readBytes(eocd.cdir_sz);
								if not cdir_bin:
									log.error('Error while reading compressed file in pze: ' + filepath)
								else:
									for cdir_i in xrange(0, eocd.cdir_cnt):
										cdir = PKZIP_CDIR._make(struct.unpack('<LHHHHHHLLLHHHHHLL0s0s0s', cdir_bin[:46]))
										cdir_sz = 46 + cdir.fname_sz + cdir.extra_sz + cdir.cmmt_sz
										cdir = PKZIP_CDIR._make(struct.unpack('<LHHHHHHLLLHHHHHLL' + str(cdir.fname_sz) + 's' + str(cdir.extra_sz) + 's' + str(cdir.cmmt_sz) + 's', cdir_bin[:cdir_sz]))
										if not(cdir.signature == 0x02014b50 and cdir.start_disk == 0):
											log.error('Not a valid CDIR block in compressed file in pze: ' + filepath)
											break
										else:
											log.info('Found CDIR block in compressed file: ' + cdir.fname)
											#-- Central Dictionary record found.
											#~ log.info('{:02X} {:08X}'.format(cdir_i, cdir.signature))
											#~ log.info(cdir)
											names.append(cdir)							
										cdir_bin = cdir_bin[cdir_sz:]					
			fp.close();
		return names

	
def __getArchives(type, filepath, archiveList, pze):
	return {'zip': __getArchivesZip,
			'7z': __getArchives7z}[type](filepath, archiveList, pze)
			
				
def __getArchives7z(filepath, archiveList, pze):
	
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


def __getArchivesZip(filepath, archiveList, pze):
	if not pze:
		fp = open(str(filepath), 'rb')
		archive = zipfile.ZipFile(fp)
		archivesDecompressed = [(name, archive.read(name)) for name in archiveList]
		fp.close()
		return archivesDecompressed
	else:
		log.info('Extracting files from compressed file in pze: ' + filepath)
		archivesDecompressed = []
		fp = xbmcvfs.File(filepath, 'r')
		
		if not fp:
			log.error('Error while opening compressed file in pze: ' + filepath)
		else:
			cdir_i = 0
			for cdir in archiveList:
				cdir_i = cdir_i + 1
				file_sz = cdir.cmpr_sz + 30 + cdir.fname_sz
				fp.seek(cdir.rel_pos, 0)
				dialog  = xbmcgui.DialogProgress()
				one_mb  = float(1024 * 1024)
				prog_sz = (1024 * 1024) / 10
				file_bin = bytearray();
				dialog.create(util.localize(32204) % (cdir_i, len(archiveList)), cdir.fname, '', util.localize(32205) % (0, file_sz / one_mb))
				for x in xrange(0, file_sz, prog_sz):
					if dialog.iscanceled():
						return []
					dialog.update((x / file_sz) * 100, cdir.fname, '', util.localize(32205) % (x / one_mb, file_sz / one_mb))
					file_bin.extend(fp.readBytes(prog_sz))
				dialog.close()
				if not file_bin:
					log.error('Error while opening compressed file in pze: ' + filepath)
				else:
					cdir_bin = struct.pack('<LHHHHHHLLLHHHHHLL' + str(cdir.fname_sz) + 's' + str(cdir.extra_sz) + 's' + str(cdir.cmmt_sz) + 's', cdir.signature, cdir.ver_crt, cdir.ver_min, cdir.gen_flg, cdir.cmpr_typ, cdir.mod_tim, cdir.mod_dte, cdir.crc32, cdir.cmpr_sz, cdir.real_sz, cdir.fname_sz, cdir.extra_sz, cdir.cmmt_sz, cdir.start_disk, cdir.int_attr, cdir.ext_attr, 0, cdir.fname, cdir.extra, cdir.cmmt)
					eocd_bin = struct.pack('<LHHHHLLH0s', 0x06054b50, 0, 0, 1, 1, len(cdir_bin), len(file_bin), 0, '')
					file_bin.extend(cdir_bin)
					file_bin.extend(eocd_bin)
					file_io = io.BytesIO(file_bin)
					zf = zipfile.ZipFile(file_io)
					uncmpr_bin = zf.read(cdir.fname)
					archivesDecompressed.append([cdir.fname, uncmpr_bin])
					#~ log.info(' '.join('{:02X}'.format(x) for x in uncmpr_bin[:64]))
					#~ log.info(''.join(chr(x) if x > 0x20 and x < 0x80 else '.' for x in uncmpr_bin[:64]))	
			fp.close()
		return archivesDecompressed
		
