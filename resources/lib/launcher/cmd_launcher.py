
import os, sys, re

from base_launcher import AbstractLauncher
import util
from util import Logutil as log
from util import __addon__
from gamedatabase import *

class Cmd_Launcher(AbstractLauncher):

    def __init__(self):

        # Do we need to escape commands before executing?
        self.escapeCmd = __addon__.getSetting(util.SETTING_RCB_ESCAPECOMMAND).upper() == 'TRUE'
        self.env = (os.environ.get("OS", "win32"), "win32",)[os.environ.get("OS", "win32") == "xbox"]

    def pre_launch(self, romCollection, gameRow):
        log.info("Cmd_Launcher.pre_launch()")
        pass

    def launch(self, romCollection, gameRow):
        log.info("Cmd_Launcher.launch()")
        pass

    def post_launch(self, romCollection, gameRow):
        log.info("Cmd_Launcher.post_launch()")
        pass

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

    def replace_diskname(self, cmd, diskName):
        # A disk was chosen by the user, select it here
        if diskName:
            log.info("Choosing Disk: " + str(diskName))
            match = re.search(self.romCollection.diskPrefix.lower(), cmd.lower())
            replString = cmd[match.start():match.end()]
            cmd = cmd.replace(replString, diskName)
        return cmd

    def build_cmd(self, romCollection, gameRow, roms, fileindex, emuParams, part_to_repeat_in_emuparams):

        emuCommandLine = romCollection.emulatorCmd
        cmd = ''
        for rom in roms:
            if fileindex == 0:
                emuParams = super().replacePlaceholdersInParams(emuParams, rom, gameRow)
                if self.escapeCmd:
                    emuCommandLine = re.escape(emuCommandLine)

                if romCollection.name in ['Linux', 'Macintosh', 'Windows']:
                    cmd = super().replacePlaceholdersInParams(emuCommandLine, rom, gameRow)
                else:
                    cmd = '\"' + emuCommandLine + '\" ' + emuParams.replace('%I%', str(fileindex))
            else:
                newrepl = part_to_repeat_in_emuparams
                newrepl = super().replacePlaceholdersInParams(newrepl, rom, gameRow)
                if self.escapeCmd:
                    emuCommandLine = re.escape(emuCommandLine)

                newrepl = newrepl.replace('%I%', str(fileindex))
                if newrepl:
                    cmd += ' ' + newrepl

            cmdprefix = ''

            if self.env == "win32":
                cmdprefix = 'call '

            precmd = cmdprefix + super().replacePlaceholdersInParams(romCollection.preCmd, rom, gameRow)
            postcmd = cmdprefix + super().replacePlaceholdersInParams(romCollection.postCmd, rom, gameRow)

        return  precmd, postcmd, cmd