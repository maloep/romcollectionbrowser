
import os, sys, re
import json

from base_launcher import AbstractLauncher
import util
from util import Logutil as log
from util import __addon__
from gamedatabase import *

import xbmc

KODI_JSONRPC_TOGGLE_FULLSCREEN = '{"jsonrpc": "2.0", "method": "Input.ExecuteAction", "params": {"action": "togglefullscreen"}, "id": "1"}'

class Cmd_Launcher(AbstractLauncher):

    def __init__(self):
        # Do we need to escape commands before executing?
        self.escapeCmd = __addon__.getSetting(util.SETTING_RCB_ESCAPECOMMAND).upper() == 'TRUE'
        self.env = (os.environ.get("OS", "win32"), "win32",)[os.environ.get("OS", "win32") == "xbox"]
        self.screenModeToggled = False

    def pre_launch(self, romCollection, gameRow, precmd):
        log.info("Cmd_Launcher.pre_launch()")

        if not romCollection.useEmuSolo:
            self.__toggle_screenmode()

        self.__executePreCommand(precmd)
        self.__preDelay()
        self.__audioSuspend()
        self.__disableScreensaver()

    def launch(self, romCollection, gameRow, cmd, roms, listitem):
        log.info("Cmd_Launcher.launch()")

        self.__executeCommand(romCollection, cmd)

    def post_launch(self, romCollection, gameRow, postcmd):
        log.info("Cmd_Launcher.post_launch()")

        self.__postDelay()
        self.__audioResume()
        self.__executePostCommand(postcmd)
        self.__enableScreensaver()

        if self.screenModeToggled:
            log.info("Toggle to Full Screen mode")
            # this brings xbmc back
            xbmc.executeJSONRPC(KODI_JSONRPC_TOGGLE_FULLSCREEN)

    def prepareMultiRomCommand(self, emuParams):
        obIndex = emuParams.find('{')
        cbIndex = emuParams.find('}')
        partToRepeat = ''
        if obIndex > -1 and cbIndex > 1:
            partToRepeat = emuParams[obIndex + 1:cbIndex]
        emuParams = emuParams.replace("{", "")
        emuParams = emuParams.replace("}", "")

        return emuParams, partToRepeat

    def replace_gamecmd(self, gameRow, emuParams):
        gameCmd = ''
        if gameRow[GameView.COL_gameCmd] is not None:
            gameCmd = str(gameRow[GameView.COL_gameCmd])
        # be case insensitive with (?i)
        emuParams = re.sub('(?i)%gamecmd%', gameCmd, emuParams)
        return emuParams

    def replace_diskname(self, romCollection, cmd, diskName):
        # A disk was chosen by the user, select it here
        if diskName:
            log.info("Choosing Disk: " + str(diskName))
            match = re.search(romCollection.diskPrefix.lower(), cmd.lower())
            replString = cmd[match.start():match.end()]
            cmd = cmd.replace(replString, diskName)
        return cmd

    def build_cmd(self, romCollection, gameRow, roms, emuParams, part_to_repeat_in_emuparams):

        emuCommandLine = romCollection.emulatorCmd
        cmd = ''
        romindex = 0
        for rom in roms:
            if romindex == 0:
                emuParams = super().replacePlaceholdersInParams(emuParams, rom, gameRow)
                if self.escapeCmd:
                    emuCommandLine = re.escape(emuCommandLine)

                if romCollection.name in ['Linux', 'Macintosh', 'Windows']:
                    cmd = super().replacePlaceholdersInParams(emuCommandLine, rom, gameRow)
                else:
                    cmd = '\"' + emuCommandLine + '\" ' + emuParams.replace('%I%', str(romindex))
            else:
                newrepl = part_to_repeat_in_emuparams
                newrepl = super().replacePlaceholdersInParams(newrepl, rom, gameRow)
                if self.escapeCmd:
                    emuCommandLine = re.escape(emuCommandLine)

                newrepl = newrepl.replace('%I%', str(romindex))
                if newrepl:
                    cmd += ' ' + newrepl

            cmdprefix = ''

            if self.env == "win32":
                cmdprefix = 'call '

            precmd = cmdprefix + super().replacePlaceholdersInParams(romCollection.preCmd, rom, gameRow)
            postcmd = cmdprefix + super().replacePlaceholdersInParams(romCollection.postCmd, rom, gameRow)

            romindex += 1

        return  precmd, postcmd, cmd

    def prepare_solomode(self, romCollection, cmd):
        # solo mode
        if romCollection.useEmuSolo:

            self.__copyLauncherScriptsToUserdata()

            # communicate with service via settings
            __addon__.setSetting(util.SETTING_RCB_LAUNCHONSTARTUP, 'true')

            # invoke script file that kills xbmc before launching the emulator
            basePath = os.path.join(util.getAddonDataPath(), 'scriptfiles')

            if self.env == "win32":
                if __addon__.getSetting(util.SETTING_RCB_USEVBINSOLOMODE).lower() == 'true':
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
            if self.env == "win32":
                cmd = 'call ' + cmd

        return cmd

    def __copyLauncherScriptsToUserdata(self):
        log.info('__copyLauncherScriptsToUserdata')

        oldBasePath = os.path.join(util.getAddonInstallPath(), 'resources', 'scriptfiles')
        newBasePath = os.path.join(util.getAddonDataPath(), 'scriptfiles')

        files = []
        # Copy applaunch shell script/batch file
        if self.env == 'win32':
            files.append('applaunch.bat')
        else:
            files.append('applaunch.sh')

        # Copy VBS files
        if self.env == 'win32' and __addon__.getSetting(util.SETTING_RCB_USEVBINSOLOMODE).lower() == 'true':
            files += ['applaunch-vbs.bat', 'LaunchKodi.vbs', 'Sleep.vbs']

        for f in files:
            if not xbmcvfs.exists(os.path.join(newBasePath, f)):
                log.debug("Copying file {0} from {1} to {2}".format(f, oldBasePath, newBasePath))
                if not xbmcvfs.copy(os.path.join(oldBasePath, f), os.path.join(newBasePath, f)):
                    log.warn("Error copying file")

    def __toggle_screenmode(self):
        screenMode = xbmc.getInfoLabel("System.Screenmode")
        log.info("screenMode: " + screenMode)
        isFullScreen = screenMode.endswith("Full Screen")

        toggleScreenMode = __addon__.getSetting(util.SETTING_RCB_TOGGLESCREENMODE).upper() == 'TRUE'

        if isFullScreen and toggleScreenMode:
            log.info("Toggling to windowed mode")
            # this minimizes xbmc some apps seems to need it
            xbmc.executeJSONRPC(KODI_JSONRPC_TOGGLE_FULLSCREEN)

            self.screenModeToggled = True

    def __executePreCommand(self, precmd):
        # pre launch command
        if precmd.strip() != '' and precmd.strip() != 'call':
            log.info("Got to PRE: " + precmd.strip())
            os.system(precmd)

    def __preDelay(self):
        preDelay = __addon__.getSetting(util.SETTING_RCB_PRELAUNCHDELAY)
        if preDelay != '':
            log.debug("Pre delaying by {0}ms".format(preDelay))
            xbmc.sleep(int(float(preDelay)))

    def __postDelay(self):
        postDelay = __addon__.getSetting(util.SETTING_RCB_POSTLAUNCHDELAY)
        if postDelay != '':
            log.debug("Post delaying by {0}ms".format(postDelay))
            xbmc.sleep(int(float(postDelay)))

    def __audioSuspend(self):
        if __addon__.getSetting(util.SETTING_RCB_SUSPENDAUDIO).upper() == 'TRUE':
            log.debug("Suspending audio")
            xbmc.executebuiltin("PlayerControl(Stop)")
            xbmc.enableNavSounds(False)
            xbmc.audioSuspend()

    def __audioResume(self):
        if __addon__.getSetting(util.SETTING_RCB_SUSPENDAUDIO).upper() == 'TRUE':
            log.debug("Resuming audio")
            xbmc.audioResume()
            xbmc.enableNavSounds(True)

    def __disableScreensaver(self):
        if __addon__.getSetting(util.SETTING_RCB_DISABLESCREENSAVER).upper() == 'TRUE':
            log.debug("Disable Screensaver")
            response = xbmc.executeJSONRPC(
                '{ "jsonrpc": "2.0", "id": 0, "method": "Settings.getSettingValue", "params": {"setting":"screensaver.mode" } }')

            jsonresult = json.loads(response)
            screensaver = jsonresult['result']['value']
            log.debug("Current Screensaver: {0}".format(screensaver))

            __addon__.setSetting(util.SETTING_RCB_CURRENTSCREENSAVER, screensaver)

            log.debug("Set Screensaver to empty value")
            xbmc.executeJSONRPC(
                '{ "jsonrpc": "2.0", "id": 0, "method":"Settings.setSettingValue", "params": {"setting":"screensaver.mode", "value":""} } ')

    def __enableScreensaver(self):
        if __addon__.getSetting(util.SETTING_RCB_DISABLESCREENSAVER).upper() == 'TRUE':
            log.debug("Enable Screensaver")

            screensaver = __addon__.getSetting(util.SETTING_RCB_CURRENTSCREENSAVER)

            log.debug("Set Screensaver back to: {0}".format(screensaver))

            jsonobj = { "jsonrpc": "2.0", "id": 0, "method":"Settings.setSettingValue", "params": {"setting":"screensaver.mode", "value": screensaver} }
            xbmc.executeJSONRPC(json.dumps(jsonobj))

            xbmc.sleep(2000)

            response = xbmc.executeJSONRPC(
                '{"jsonrpc": "2.0", "method": "XBMC.GetInfoBooleans", "params": {"booleans": ["System.ScreenSaverActive"]}, "id": 1}')

            log.debug('Screensaver is active: {0}'.format(response))
            jsonresult = json.loads(response)
            screensaver_active = jsonresult['result']['System.ScreenSaverActive']

            log.debug('Screensaver is active: {0}'.format(screensaver_active))

            if(screensaver_active):
                xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Input.Select", "id": 1}')

    def __executeCommand(self, romCollection, cmd):
        log.info('__executeCommand')
        # change working directory
        path = os.path.dirname(romCollection.emulatorCmd)
        if os.path.isdir(path):
            try:
                os.chdir(path)
            except OSError:
                log.warn("Unable to chdir to {0}".format(path))

        if romCollection.usePopen:
            log.info('execute command with popen')
            import subprocess
            process = subprocess.Popen(cmd, shell=True)
            process.wait()
        else:
            log.info('execute command with os.system')
            os.system(cmd)

    def __executePostCommand(self, postcmd):
        # post launch command
        if postcmd.strip() != '' and postcmd.strip() != 'call':
            log.info("Got to POST: " + postcmd.strip())
            os.system(postcmd)