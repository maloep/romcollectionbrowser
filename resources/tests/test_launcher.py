
from builtins import str
from builtins import object
import os, shutil, sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

from gamedatabase import GameDataBase, File, GameView
from launcher import RCBLauncher
from config import Config


class RCBMockGui(object):
    itemCount = 0
    def writeMsg(self, msg1, msg2, msg3, count=0):
        return True


class TestLauncher(unittest.TestCase):

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

    def test_buildcmd_placeholders(self):
        rcb_launcher = RCBLauncher()

        config_xml_file = os.path.join(os.path.dirname(__file__), 'testdata', 'config',
                                       'romcollections_launchertests.xml')
        conf = Config(config_xml_file)
        conf.readXml()

        #%ROM%
        gameid = 7
        game = GameView(self.gdb).getObjectById(gameid)
        filename_rows = File(self.gdb).getRomsByGameId(game[File.COL_ID])
        rcb_launcher.romCollection = conf.romCollections[str(game[GameView.COL_romCollectionId])]
        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)
        self.assertEquals(cmd, '"/Path/To/Atari2600/Emulator" "./testdata/roms/Atari 2600\\Adventure (1980) (Atari).a26"')

        # %ROMFILE%
        gameid = 11
        game = GameView(self.gdb).getObjectById(gameid)
        filename_rows = File(self.gdb).getRomsByGameId(game[File.COL_ID])
        rcb_launcher.romCollection = conf.romCollections[str(game[GameView.COL_romCollectionId])]
        cmd, precmd, postcmd, roms = rcb_launcher._buildCmd(RCBMockGui(), filename_rows, game, False)
        self.assertEquals(cmd, '"/Path/To/PSX/Emulator" "Bushido Blade.img"')