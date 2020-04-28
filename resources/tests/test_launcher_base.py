
from builtins import str
from builtins import object
import os, shutil, sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'launcher'))

from gamedatabase import GameDataBase, File, GameView, DataBaseObject
from old_launcher import RCBLauncher
from base_launcher import AbstractLauncher
from retroplayer_launcher import RetroPlayer_Launcher
from cmd_launcher import Cmd_Launcher
from config import Config
import xbmc


class RCBMockGui(object):
    itemCount = 0
    player = xbmc.Player()
    def writeMsg(self, msg1):
        return True

    def saveViewState(self, isOnExit):
        pass


class TestLauncher_Base(unittest.TestCase):

    @classmethod
    def get_testdata_path(cls):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata')

    @classmethod
    def setUpClass(cls):
        # Open the DB
        db_path = os.path.join(cls.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        shutil.copyfile(os.path.join(db_path, 'MyGames_current_12_games.db'), os.path.join(db_path, 'MyGames.db'))

        cls.gdb = GameDataBase(db_path)
        cls.gdb.connect()

    @classmethod
    def tearDownClass(cls):
        # Cleanup
        cls.gdb.close()
        os.remove(os.path.join(os.path.join(cls.get_testdata_path(), 'database'), 'MyGames.db'))

    def _get_config(self):
        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_launchertests.xml')
        config_file = Config(config_xml_file)
        config_file.readXml()
        return config_file

    @unittest.skip("manual test")
    def test_launch_game(self):
        conf = self._get_config()
        gameid = 10
        AbstractLauncher(self.gdb, conf, RCBMockGui()).launch_game(gameid, None)

    def test_get_launcher_by_gameid(self):
        conf = self._get_config()

        abs_launcher = AbstractLauncher(self.gdb, conf, RCBMockGui())

        # 10 = 1080 Snowboarding, N64
        launcher = abs_launcher.get_launcher_by_gameid(10)
        self.assertTrue(isinstance(launcher, RetroPlayer_Launcher))

        # 3 = Airborn Ranger, Amiga
        launcher = abs_launcher.get_launcher_by_gameid(3)
        self.assertTrue(isinstance(launcher, Cmd_Launcher))

    def test_checkGameHasSaveStates(self):
        conf = self._get_config()
        # 1 = Chrono Trigger, SNES
        gameRow = GameView(self.gdb).getObjectById(1)
        romCollection = conf.romCollections[str(gameRow[GameView.COL_romCollectionId])]
        filenameRows = File(self.gdb).getRomsByGameId(gameRow[DataBaseObject.COL_ID])

        from xbmcgui import Dialog
        Dialog.select_result = 1

        abs_launcher = AbstractLauncher(self.gdb, conf, RCBMockGui())
        savestateparams = abs_launcher.checkGameHasSaveStates(romCollection, gameRow, filenameRows)

        self.assertEqual("./testdata/savestates/SNES/Chrono Trigger.state", savestateparams)

    def test_replacePlaceholdersInParams(self):
        conf = self._get_config()

        gameRow = GameView(self.gdb).getObjectById(1)
        filenameRows = File(self.gdb).getRomsByGameId(gameRow[DataBaseObject.COL_ID])
        rom = filenameRows[0][0]

        abs_launcher = AbstractLauncher(self.gdb, conf, RCBMockGui())

        emulatorParams = '-v -L /Applications/RetroArch.app/Contents/Resources/cores/bnes_libretro.dylib "%rom%"'
        emuparams = abs_launcher.replacePlaceholdersInParams(emulatorParams, rom, gameRow)
        self.assertEqual('-v -L /Applications/RetroArch.app/Contents/Resources/cores/bnes_libretro.dylib "./testdata/roms/SNES\Chrono Trigger\game.sfc"', emuparams)

        emulatorParams = '%ROM%'
        emuparams = abs_launcher.replacePlaceholdersInParams(emulatorParams, rom, gameRow)
        self.assertEqual('./testdata/roms/SNES\Chrono Trigger\game.sfc', emuparams)

        emulatorParams = '%Rom%'
        emuparams = abs_launcher.replacePlaceholdersInParams(emulatorParams, rom, gameRow)
        self.assertEqual('./testdata/roms/SNES\Chrono Trigger\game.sfc', emuparams)

        emulatorParams = '%romfile%'
        emuparams = abs_launcher.replacePlaceholdersInParams(emulatorParams, rom, gameRow)
        self.assertEqual('game.sfc', emuparams)

        emulatorParams = '%romname%'
        emuparams = abs_launcher.replacePlaceholdersInParams(emulatorParams, rom, gameRow)
        self.assertEqual('game', emuparams)

        emulatorParams = '%game%'
        emuparams = abs_launcher.replacePlaceholdersInParams(emulatorParams, rom, gameRow)
        self.assertEqual('Chrono Trigger', emuparams)

        emulatorParams = '%asknum%'
        from xbmcgui import Dialog
        Dialog.select_result = 0
        emuparams = abs_launcher.replacePlaceholdersInParams(emulatorParams, rom, gameRow)
        self.assertEqual('0', emuparams)

        emulatorParams = '%asktext%'
        emuparams = abs_launcher.replacePlaceholdersInParams(emulatorParams, rom, gameRow)
        #xbmcgui.Dialog.input() returns "Text"
        self.assertEqual('Text', emuparams)

    def test_selectdisc(self):
        conf = self._get_config()

        #Formula One, Amiga
        gameRow = GameView(self.gdb).getObjectById(6)
        filenameRows = File(self.gdb).getRomsByGameId(gameRow[DataBaseObject.COL_ID])
        romCollection = conf.romCollections[str(gameRow[GameView.COL_romCollectionId])]

        abs_launcher = AbstractLauncher(self.gdb, conf, RCBMockGui())
        discname = abs_launcher._selectdisc(romCollection, filenameRows, False)
        # EmuParams contains %I%, so we expect no disc selection
        self.assertEqual('', discname)

        # Silent Hill, PSX
        gameRow = GameView(self.gdb).getObjectById(12)
        filenameRows = File(self.gdb).getRomsByGameId(gameRow[DataBaseObject.COL_ID])
        romCollection = conf.romCollections[str(gameRow[GameView.COL_romCollectionId])]

        abs_launcher = AbstractLauncher(self.gdb, conf, RCBMockGui())
        discname = abs_launcher._selectdisc(romCollection, filenameRows, False)
        self.assertEqual('(Disc 1 of 2)', discname)

    def test_make_local_copy(self):
        conf = self._get_config()

        # Silent Hill, PSX
        gameRow = GameView(self.gdb).getObjectById(12)
        filenameRows = File(self.gdb).getRomsByGameId(gameRow[DataBaseObject.COL_ID])
        romCollection = conf.romCollections[str(gameRow[GameView.COL_romCollectionId])]
        rom = filenameRows[0][0]

        abs_launcher = AbstractLauncher(self.gdb, conf, RCBMockGui())
        rom = abs_launcher._copylocal(romCollection, rom)

        expected_rom = os.path.join(os.getcwd(), 'script.games.rom.collection.browser', 'tmp', 'Playstation', 'Silent Hill (Disc 1 of 2).bin')
        self.assertEqual(expected_rom, rom)


    """
    def test_buildCmd_multidisc(self):
        rcb_launcher = RCBLauncher()

        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        gameid = 6
        game = GameView(self.gdb).getObjectById(gameid)
        filename_rows = File(self.gdb).getRomsByGameId(game[File.COL_ID])
        rcb_launcher.romCollection = conf.romCollections[str(game[GameView.COL_romCollectionId])]

        from xbmcgui import Dialog

        #select disk 1
        Dialog.select_result = 0
        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)
        self.assertEquals(cmd, '"/Path/To/Amiga/Emulator" "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 1.adf"')
        #select disk 2
        Dialog.select_result = 1
        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)
        self.assertEquals(cmd, '"/Path/To/Amiga/Emulator" "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 2.adf"')
        #select disk 3
        Dialog.select_result = 2
        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)
        self.assertEquals(cmd, '"/Path/To/Amiga/Emulator" "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 3.adf"')
        #select disk 4
        Dialog.select_result = 3
        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)
        self.assertEquals(cmd,'"/Path/To/Amiga/Emulator" "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 4.adf"')

    def test_buildCmd_multidisc_psx(self):
        rcb_launcher = RCBLauncher()

        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        gameid = 12
        game = GameView(self.gdb).getObjectById(gameid)
        filename_rows = File(self.gdb).getRomsByGameId(game[File.COL_ID])
        rcb_launcher.romCollection = conf.romCollections[str(game[GameView.COL_romCollectionId])]

        from xbmcgui import Dialog

        #select disk 1
        Dialog.select_result = 0
        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)
        self.assertEquals(cmd, '"/Path/To/PSX/Emulator" "./testdata/roms/PSX\\Silent Hill (Disc 1 of 2).bin"')
        #select disk 2
        Dialog.select_result = 1
        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)
        self.assertEquals(cmd, '"/Path/To/PSX/Emulator" "./testdata/roms/PSX\\Silent Hill (Disc 2 of 2).bin"')

    def test_buildCmd_foldername_as_gamename(self):
        rcb_launcher = RCBLauncher()

        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_imageloading.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        gameid = 1
        game = GameView(self.gdb).getObjectById(gameid)
        filename_rows = File(self.gdb).getRomsByGameId(game[File.COL_ID])
        rcb_launcher.romCollection = conf.romCollections[str(game[GameView.COL_romCollectionId])]

        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)

        self.assertEquals(cmd, '"/Path/To/SNES/Emulator" -v -L /Applications/RetroArch.app/Contents/Resources/cores/bnes_libretro.dylib "./testdata/roms/SNES\Chrono Trigger\game.sfc"')

    def test_buildcmd_amiga_multidisk(self):
        rcb_launcher = RCBLauncher()

        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_launchertests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        gameid = 6
        game = GameView(self.gdb).getObjectById(gameid)
        filename_rows = File(self.gdb).getRomsByGameId(game[File.COL_ID])
        rcb_launcher.romCollection = conf.romCollections[str(game[GameView.COL_romCollectionId])]

        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)

        self.assertEquals(cmd, '"/Path/To/Amiga/Emulator" -0 "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 1.adf" -1 "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 2.adf" -2 "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 3.adf" -3 "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 4.adf"')
    """