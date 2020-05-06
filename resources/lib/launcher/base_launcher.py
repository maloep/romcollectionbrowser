
import os, re, glob
import traceback
import zipfile

import util
from util import Logutil as log
from util import __addon__
from gamedatabase import *

import xbmc, xbmcgui, xbmcvfs

class AbstractLauncher(object):
    """Parent class for all launchers.

        This class takes care of instantiating the relevant launcher based on romCollection.useBuiltinEmulator
    """

    # store instantiated launcher to avoid instantiating new launcher for every game launch
    _instantiated_launcher = {}

    gdb = None
    config = None
    gui = None
    romcollection = None
    gameRow = None
    calledFromSkin = False
    compressedExtensions = ['7z', 'zip']


    CMD_LAUNCHER = "Cmd_Launcher"
    RETROPLAYER_LAUNCHER = "RetroPlayer_Launcher"

    def __init__(self, gdb, config, gui):
        self.gdb = gdb
        self.config = config
        self.gui = gui

        # Do we need to escape commands before executing?
        self.escapeCmd = __addon__.getSetting(util.SETTING_RCB_ESCAPECOMMAND).upper() == 'TRUE'
        self.env = (os.environ.get("OS", "win32"), "win32",)[os.environ.get("OS", "win32") == "xbox"]

    def launch_game(self, gameid, listitem):
        log.info("AbstractLauncher.launch_game()")
        try:
            launcher = self.get_launcher_by_gameid(gameid)
            if(launcher is None):
                log.error("Launcher could not be created.")
                return

            precmd, postcmd, cmd, roms = launcher.prepare(self.romCollection, self.gameRow)
            launcher.pre_launch(self.romCollection, self.gameRow, precmd)
            launcher.launch(self.romCollection, self.gameRow, cmd, roms, listitem)
            launcher.post_launch(self.romCollection, self.gameRow, postcmd)
        except Exception as exc:
            error = "%s: %s" %(util.localize(32035), str(exc))
            traceback.print_exc()
            self.gui.writeMsg(error)

    def get_launcher_by_gameid(self, gameid):
        """Returns the launcher class based on romCollection.useBuiltinEmulator

        Args:
            gameid: the id of the game we want to launch
        """
        log.info("AbstractLauncher.get_launcher_by_gameid()")
        self.gameRow = GameView(self.gdb).getObjectById(gameid)
        if self.gameRow is None:
            log.error("Game with id %s could not be found in database" % gameid)
            return None

        try:
            self.romCollection = self.config.romCollections[str(self.gameRow[GameView.COL_romCollectionId])]
        except KeyError:
            log.error("Cannot get rom collection with id: " + str(self.gameRow[GameView.COL_romCollectionId]))
            self.gui.writeMsg(util.localize(32034))
            return

        self.gui.writeMsg(util.localize(32163) + " " + self.gameRow[DataBaseObject.COL_NAME])

        launchername = self.CMD_LAUNCHER
        if(self.romCollection.useBuiltinEmulator):
            launchername = self.RETROPLAYER_LAUNCHER

        #check if we already have instantiated this scraper
        instance = None
        try:
            instance = self._instantiated_launcher[launchername]
            log.debug("Using previously instantiated launcher class {0}".format(launchername))
        except KeyError:
            pass

        if not instance:
            log.debug("Instantiating launcher class {0}".format(launchername))
            try:
                module = __import__(launchername.lower())
                class_ = getattr(module, launchername)
                instance = class_()
                self._instantiated_launcher[launchername] = instance
            except ImportError:
                log.error("Unable to find launcher {0}".format(launchername))
                raise

        instance.gdb = self.gdb
        instance.gui = self.gui
        instance.config = self.config
        return instance

    def prepare(self, romCollection, gameRow):
        log.info("AbstractLauncher.prepare()")

        # Remember viewstate
        self.gui.saveViewState(False)

        filenameRows = File(self.gdb).getRomsByGameId(gameRow[DataBaseObject.COL_ID])
        log.info("files for current game: " + str(filenameRows))

        # handle savestates
        saveStateParams = self.checkGameHasSaveStates(romCollection, gameRow, filenameRows)

        # ask for disc number if multidisc game
        diskName = self._selectdisc(romCollection, filenameRows, self.calledFromSkin)

        # params could be: {-%I% %ROM%}
        # we have to repeat the part inside the brackets and replace the %I% with the current index
        emuParams, part_to_repeat_in_emuparams = self.prepareMultiRomCommand(romCollection.emulatorParams)

        # insert game specific command
        emuParams = self.replace_gamecmd(gameRow, emuParams)

        #iterate rom files
        fileindex = int(0)
        roms = []
        for fileNameRow in filenameRows:
            rom = fileNameRow[0]
            log.info("rom: " + rom)

            rom = self._copylocal(romCollection, rom)

            extracted_roms = self.__extract_archive(romCollection, rom, saveStateParams, emuParams)
            roms.extend(extracted_roms)

        precmd, postcmd, cmd = self.build_cmd(romCollection, gameRow, roms, emuParams, part_to_repeat_in_emuparams)

        cmd = self.replace_diskname(romCollection, cmd, diskName)

        cmd = self.prepare_solomode(romCollection, cmd)

        self.__update_launchcount(gameRow)

        log.info("cmd: " + cmd)
        log.info("precmd: " + precmd)
        log.info("postcmd: " + postcmd)
        return precmd, postcmd, cmd, roms

    def pre_launch(self, romCollection, gameRow, precmd):
        log.info("AbstractLauncher.pre_launch()")
        pass

    def launch(self, romCollection, gameRow, cmd, roms, listitem):
        log.info("AbstractLauncher.launch()")
        pass

    def post_launch(self, romCollection, gameRow, postcmd):
        log.info("AbstractLauncher.post_launch()")
        pass

    def prepareMultiRomCommand(self, emuParams):
        log.info("AbstractLauncher.prepareMultiRomCommand()")
        return "", ""

    def replace_gamecmd(self, gameRow, emuParams):
        log.info("AbstractLauncher.replace_gamecmd()")
        return ""

    def replace_diskname(self, romCollection, cmd, diskName):
        log.info("AbstractLauncher.replace_disk_name()")
        return cmd

    def build_cmd(self, romCollection, gameRow, roms, emuParams, part_to_repeat_in_emuparams):
        log.info("AbstractLauncher.build_cmd()")
        return "", "", ""

    def prepare_solomode(self, romCollection, cmd):
        log.info("AbstractLauncher.prepare_solomode()")
        return cmd

    def checkGameHasSaveStates(self, romCollection, gameRow, filenameRows):
        log.info("AbstractLauncher.checkGameHasSaveStates()")
        stateFile = ''
        saveStateParams = ''

        if romCollection.saveStatePath == '':
            log.debug("No save state path set")
            return ''

        rom = filenameRows[0][0]
        saveStatePath = self.replacePlaceholdersInParams(romCollection.saveStatePath, rom, gameRow)

        saveStateFiles = glob.glob(saveStatePath)

        if len(saveStateFiles) == 0:
            log.debug("No save state files found")
            return ''

        log.info('saveStateFiles found: ' + str(saveStateFiles))

        # don't select savestatefile if ASKNUM is requested in Params
        if re.search('(?i)%ASKNUM%', romCollection.saveStateParams):
            stateFile = saveStateFiles[0]
        else:
            options = [util.localize(32165)]
            for f in saveStateFiles:
                options.append(os.path.basename(f))
            selectedFile = xbmcgui.Dialog().select(util.localize(32166), options)
            # If selections is canceled or "Don't launch statefile" option
            if selectedFile < 1:
                stateFile = ''
            else:
                stateFile = saveStateFiles[selectedFile - 1]

        if stateFile != '':
            saveStateParams = romCollection.saveStateParams
            if self.escapeCmd:
                stateFile = re.escape(stateFile)

            pattern = re.compile('%statefile%', re.IGNORECASE)
            saveStateParams = pattern.sub(stateFile, saveStateParams)

        return saveStateParams

    def replacePlaceholdersInParams(self, emuParams, rom, gameRow):

        #escape \ in rom file names
        rom = rom.replace('\\', r'\\')

        # full rom path ("C:\Roms\rom.zip")
        pattern = re.compile('%rom%', re.IGNORECASE)
        emuParams = pattern.sub(rom, emuParams)

        # romfile ("rom.zip")
        romfile = os.path.basename(rom)
        pattern = re.compile('%romfile%', re.IGNORECASE)
        emuParams = pattern.sub(romfile, emuParams)

        # romname ("rom")
        romname = os.path.splitext(os.path.basename(rom))[0]
        pattern = re.compile('%romname%', re.IGNORECASE)
        emuParams = pattern.sub(romname, emuParams)

        # gamename
        gamename = str(gameRow[DataBaseObject.COL_NAME])
        pattern = re.compile('%game%', re.IGNORECASE)
        emuParams = pattern.sub(gamename, emuParams)

        # ask num
        if re.search('(?i)%ASKNUM%', emuParams):
            options = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            number = str(xbmcgui.Dialog().select(util.localize(32167), options))
            pattern = re.compile('%asknum%', re.IGNORECASE)
            emuParams = pattern.sub(number, emuParams)

        # ask text
        if re.search('(?i)%ASKTEXT%', emuParams):
            command = xbmcgui.Dialog().input(util.localize(32168), type=xbmcgui.INPUT_ALPHANUM)
            pattern = re.compile('%asktext%', re.IGNORECASE)
            emuParams = pattern.sub(command, emuParams)

        return emuParams

    def _selectdisc(self, romCollection, filenameRows, calledFromSkin):
        diskName = ''
        if romCollection.diskPrefix != '' and '%I%' not in romCollection.emulatorParams:
            log.info("Getting Multiple Disc Parameter")
            options = []
            for disk in filenameRows:
                gamename = os.path.basename(disk[0])
                match = re.search(romCollection.diskPrefix, gamename, re.IGNORECASE)
                if match:
                    disk = gamename[match.start():match.end()]
                    options.append(disk)
            if len(options) > 1 and not calledFromSkin:
                diskNum = xbmcgui.Dialog().select(util.localize(32164) + ': ', options)
                if diskNum < 0:
                    # don't launch game
                    log.info("No disc was chosen. Won't launch game")
                else:
                    diskName = options[diskNum]
                    log.info("Chosen Disc: %s" % diskName)
        return diskName

    def _copylocal(self, romCollection, rom):
        if romCollection.makeLocalCopy:
            localDir = os.path.join(util.getTempDir(), romCollection.name)
            if xbmcvfs.exists(localDir + '\\'):
                log.info("Trying to delete local rom files")
                dirs, files = xbmcvfs.listdir(localDir)
                for f in files:
                    xbmcvfs.delete(os.path.join(localDir, f))
            else:
                log.info("Create temporary folder: " + localDir)
                xbmcvfs.mkdir(localDir)
            localRom = os.path.join(localDir, os.path.basename(str(rom)))
            log.info("Creating local copy: " + str(localRom))
            if xbmcvfs.copy(rom, localRom):
                log.info("Local copy created")
            rom = localRom

        return rom

    def __extract_archive(self, romCollection, rom, saveStateParams, emuParams):
        # If it's a .7z file
        # Don't extract zip files in case of savestate handling and when called From skin
        filext = rom.split('.')[-1]
        roms = [rom]
        if filext in self.compressedExtensions and not romCollection.doNotExtractZipFiles and saveStateParams == '' and not self.calledFromSkin:
            roms = self.__handleCompressedFile(romCollection, filext, rom, emuParams)
            log.debug("roms compressed = " + str(roms))
            if len(roms) == 0:
                return None

        return roms

    def __handleCompressedFile(self, romCollection, filext, rom, emuParams):

        log.info("__handleCompressedFile")

        # Note: Trying to delete temporary files (from zip or 7z extraction) from last run
        # Do this before launching a new game. Otherwise game could be deleted before launch
        tempDir = os.path.join(util.getTempDir(), 'extracted', romCollection.name)
        # check if folder exists
        if not xbmcvfs.exists(tempDir + '\\'):
            log.info("Create temporary folder: " + tempDir)
            xbmcvfs.mkdir(tempDir)

        try:
            if xbmcvfs.exists(tempDir + '\\'):
                log.info("Trying to delete temporary rom files")
                #can't use xbmcvfs.listdir here as it seems to cache the file list and RetroPlayer won't find newly created files anymore
                files = os.listdir(tempDir)
                for f in files:
                    #RetroPlayer places savestate files next to the roms. Don't delete these files.
                    fname, ext = os.path.splitext(f)
                    if ext not in ('.sav', '.xml', '.png'):
                        xbmcvfs.delete(os.path.join(tempDir, f))
        except Exception as exc:
            log.error("Error deleting files after launch emu: " + str(exc))
            self.gui.writeMsg(util.localize(32036) + ": " + str(exc))

        roms = []

        log.info("Treating file as a compressed archive")

        try:
            names = self.__getNames(filext, rom)
        except Exception as exc:
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
            except Exception as exc:
                log.error("Error handling compressed file: " + str(exc))
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

    # Compressed files functions
    def __getNames(self, compression_type, filepath):
        return {'zip': self.__getNamesZip,
                '7z': self.__getNames7z}[compression_type](filepath)

    def __getNames7z(self, filepath):

        try:
            import py7zlib
        except ImportError as e:
            # 32039 = Error launching .7z file.
            # 32129 = Please check kodi.log for details.
            message = "%s[CR]%s" % (util.localize(32039), util.localize(32129))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            msg = (
                "You have tried to launch a .7z file but you are missing required libraries to extract the file. "
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

    def __getArchives(self, compression_type, filepath, archiveList):
        return {'zip': self.__getArchivesZip,
                '7z': self.__getArchives7z}[compression_type](filepath, archiveList)

    def __getArchives7z(self, filepath, archiveList):

        try:
            import py7zlib
        except ImportError:
            # 32039 = Error launching .7z file.
            # 32129 = Please check kodi.log for details.
            message = "%s[CR]%s" % (util.localize(32039), util.localize(32129))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            msg = (
                "You have tried to launch a .7z file but you are missing required libraries to extract the file. "
                "You can download the latest RCB version from RCBs project page. It contains all required libraries.")
            log.error(msg)
            return None

        fp = open(str(filepath), 'rb')
        archive = py7zlib.Archive7z(fp)
        archivesDecompressed = [(name, archive.getmember(name).read()) for name in archiveList]
        fp.close()
        return archivesDecompressed

    def __getArchivesZip(self, filepath, archiveList):
        fp = open(str(filepath), 'rb')
        archive = zipfile.ZipFile(fp)
        archivesDecompressed = [(name, archive.read(name)) for name in archiveList]
        fp.close()
        return archivesDecompressed

    def __update_launchcount(self, gameRow):
        # update LaunchCount
        launchCount = gameRow[GameView.COL_launchCount]
        if launchCount is None:
            launchCount = 0
        Game(self.gdb).update(('launchCount',), (launchCount + 1,), gameRow[Game.COL_ID], True)
        self.gdb.commit()