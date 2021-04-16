import os, shutil, sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'launcher'))

from gamedatabase import GameDataBase, File, GameView, DataBaseObject
from config import Config
from cmd_launcher import Cmd_Launcher

class TestLauncher_Cmd(unittest.TestCase):

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

    def test_prepareMultiRomCommand(self):

        emuParams = '-foo {-%I% %ROM%} -bar'
        emuParams, part_to_repeat = Cmd_Launcher().prepareMultiRomCommand(emuParams)

        self.assertEqual('-foo -%I% %ROM% -bar', emuParams)
        self.assertEqual('-%I% %ROM%', part_to_repeat)

    def test_replace_gamecmd(self):
        # 9 = Asteroids, Atari 2600
        gameRow = GameView(self.gdb).getObjectById(9)
        emuParams = '%ROM% %GAMECMD%'

        emuParams = Cmd_Launcher().replace_gamecmd(gameRow, emuParams)

        self.assertEqual('%ROM% My Game Cmd', emuParams)

    def test_replace_diskname(self):
        conf = self._get_config()
        romCollection = conf.romCollections['4']
        cmd = '/path/to/emu "My Game (Disc 1 of 2)"'
        diskName = '(Disc 2 of 2)'

        emuParams = Cmd_Launcher().replace_diskname(romCollection, cmd, diskName)
        self.assertEqual('/path/to/emu "My Game (Disc 2 of 2)"', emuParams)

    def test_buildcmd(self):
        conf = self._get_config()
        # 1 = Chrono Trigger, SNES
        gameRow = GameView(self.gdb).getObjectById(1)
        romCollection = conf.romCollections[str(gameRow[GameView.COL_romCollectionId])]
        filenameRows = File(self.gdb).getRomsByGameId(gameRow[DataBaseObject.COL_ID])
        roms = [filenameRows[0][0]]
        fileindex = 0
        emuParams = '-v -L /Applications/RetroArch.app/Contents/Resources/cores/bnes_libretro.lib "%rom%"'
        part_to_repeat_in_emuparams = ''

        precmd, postcmd, cmd = Cmd_Launcher().build_cmd(romCollection, gameRow, roms, emuParams, part_to_repeat_in_emuparams)

        self.assertEqual("", precmd)
        self.assertEqual("", postcmd)
        self.assertEqual('"/Path/To/SNES/Emulator" -v -L /Applications/RetroArch.app/Contents/Resources/cores/bnes_libretro.lib "./testdata/roms/SNES\Chrono Trigger\game.sfc"', cmd)

    def test_buildCmd_multidisc_Amiga(self):
        conf = self._get_config()

        gameid = 6
        gameRow = GameView(self.gdb).getObjectById(gameid)
        filename_rows = File(self.gdb).getRomsByGameId(gameRow[File.COL_ID])
        roms = [f[0] for f in filename_rows]
        romCollection = conf.romCollections[str(gameRow[GameView.COL_romCollectionId])]
        emuParams = '-%I% "%ROM%"'
        part_to_repeat_in_emuparams = '-%I% "%ROM%"'
        launcher = Cmd_Launcher()

        precmd, postcmd, cmd = launcher.build_cmd(romCollection, gameRow, roms, emuParams, part_to_repeat_in_emuparams)
        print (cmd)
        self.assertEqual(cmd,'"/Path/To/Amiga/Emulator" -0 "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 1.adf" -1 "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 2.adf" -2 "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 3.adf" -3 "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 4.adf"')


        """
        # select disk 2
        Dialog.select_result = 1
        precmd, postcmd, cmd = launcher.build_cmd(romCollection, gameRow, roms, fileindex, emuParams, part_to_repeat_in_emuparams)
        self.assertEqual(cmd,
                          '"/Path/To/Amiga/Emulator" "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 2.adf"')
        # select disk 3
        Dialog.select_result = 2
        precmd, postcmd, cmd = launcher.build_cmd(romCollection, gameRow, roms, fileindex, emuParams, part_to_repeat_in_emuparams)
        self.assertEqual(cmd,
                          '"/Path/To/Amiga/Emulator" "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 3.adf"')
        # select disk 4
        Dialog.select_result = 3
        precmd, postcmd, cmd = launcher.build_cmd(romCollection, gameRow, roms, fileindex, emuParams, part_to_repeat_in_emuparams)
        self.assertEqual(cmd,
                          '"/Path/To/Amiga/Emulator" "./testdata/roms/Amiga\MicroProse Formula One Grand Prix_Disk 4.adf"')
        """
