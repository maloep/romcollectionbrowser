#  -*- coding: utf-8 -*-

"""
python -m unittest discover -v resources/tests/ "test_db_upgrade.py"
"""

import os
import sys
import shutil
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

from xbmcaddon import Addon
import util, gamedatabase
from gamedatabase import GameDataBase, Game, RCBSetting

# Shared resources
addon = Addon(id='script.games.rom.collection.browser')
addonPath = addon.getAddonInfo('path')


class TestDBUpgrade(unittest.TestCase):
    def get_testdata_path(self):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata')

    def test_DBUpgrade_074_075(self):
        db_path = os.path.join (self.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames-0.7.4.db')), "Expected to find 0.7.4 DB")
        shutil.copyfile(os.path.join(db_path, 'MyGames-0.7.4.db'), os.path.join(db_path, 'MyGames.db'))

        gdb = GameDataBase(db_path)
        gdb.connect()

        util.CURRENT_DB_VERSION = '0.7.5'
        # Create db if not existent and maybe update to new version
        gdb.checkDBStructure()

        # Check backup files were created
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames.db.backup 0.7.4')), "No backup database created")

        rcbSettingRows = RCBSetting(gdb).getAll()
        self.assertEquals('0.7.5', rcbSettingRows[0][RCBSetting.COL_dbVersion])
        self.assertEquals(117, Game(gdb).getCount())

        # Cleanup
        gdb.close()
        os.remove(os.path.join(db_path, 'MyGames.db'))
        os.remove(os.path.join(db_path, 'MyGames.db.backup 0.7.4'))

    def test_DBUpgrade_074_220(self):
        db_path = os.path.join (self.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames-0.7.4.db')), "Expected to find 0.7.4 DB")
        shutil.copyfile(os.path.join(db_path, 'MyGames-0.7.4.db'), os.path.join(db_path, 'MyGames.db'))

        gdb = GameDataBase(db_path)
        gdb.connect()

        util.CURRENT_DB_VERSION = '2.2.0'
        # Create db if not existent and maybe update to new version
        gdb.checkDBStructure()

        # Check backup files were created
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames.db.backup 0.7.4')), "No backup database created")

        rcbSettingRows = RCBSetting(gdb).getAll()
        self.assertEquals('2.2.0', rcbSettingRows[0][RCBSetting.COL_dbVersion])
        self.assertEquals(117, Game(gdb).getCount())

        # Cleanup
        gdb.close()
        os.remove(os.path.join(db_path, 'MyGames.db'))
        os.remove(os.path.join(db_path, 'MyGames.db.backup 0.7.4'))

    def test_DBUpgrade_074_221(self):
        db_path = os.path.join (self.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames-0.7.4.db')), "Expected to find 0.7.4 DB")
        shutil.copyfile(os.path.join(db_path, 'MyGames-0.7.4.db'), os.path.join(db_path, 'MyGames.db'))

        gdb = GameDataBase(db_path)
        gdb.connect()

        util.CURRENT_DB_VERSION = '2.2.1'
        # Create db if not existent and maybe update to new version
        gdb.checkDBStructure()

        # Check backup files were created
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames.db.backup 0.7.4')), "No backup database created")

        rcbSettingRows = RCBSetting(gdb).getAll()
        self.assertEquals('2.2.1', rcbSettingRows[0][RCBSetting.COL_dbVersion])
        self.assertEquals(117, Game(gdb).getCount())

        # Cleanup
        gdb.close()
        os.remove(os.path.join(db_path, 'MyGames.db'))
        os.remove(os.path.join(db_path, 'MyGames.db.backup 0.7.4'))

    def test_DBUpgrade_075_220(self):
        db_path = os.path.join (self.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames-0.7.5.db')), "Expected to find 0.7.5 DB")
        shutil.copyfile(os.path.join(db_path, 'MyGames-0.7.5.db'), os.path.join(db_path, 'MyGames.db'))

        gdb = GameDataBase(db_path)
        gdb.connect()

        util.CURRENT_DB_VERSION = '2.2.0'
        # Create db if not existent and maybe update to new version
        gdb.checkDBStructure()

        # Check backup files were created
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames.db.backup 0.7.5')), "No backup database created")

        rcbSettingRows = RCBSetting(gdb).getAll()
        self.assertEquals('2.2.0', rcbSettingRows[0][RCBSetting.COL_dbVersion])
        self.assertEquals(117, Game(gdb).getCount())

        # Cleanup
        gdb.close()
        os.remove(os.path.join(db_path, 'MyGames.db'))
        os.remove(os.path.join(db_path, 'MyGames.db.backup 0.7.5'))

    def test_DBUpgrade_075_221(self):
        db_path = os.path.join (self.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames-0.7.5.db')), "Expected to find 0.7.5 DB")
        shutil.copyfile(os.path.join(db_path, 'MyGames-0.7.5.db'), os.path.join(db_path, 'MyGames.db'))

        gdb = GameDataBase(db_path)
        gdb.connect()

        util.CURRENT_DB_VERSION = '2.2.1'
        # Create db if not existent and maybe update to new version
        gdb.checkDBStructure()

        # Check backup files were created
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames.db.backup 0.7.5')), "No backup database created")

        rcbSettingRows = RCBSetting(gdb).getAll()
        self.assertEquals('2.2.1', rcbSettingRows[0][RCBSetting.COL_dbVersion])
        self.assertEquals(117, Game(gdb).getCount())

        # Cleanup
        gdb.close()
        os.remove(os.path.join(db_path, 'MyGames.db'))
        os.remove(os.path.join(db_path, 'MyGames.db.backup 0.7.5'))

    def test_DBUpgrade_220_221(self):
        db_path = os.path.join (self.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames-2.2.0.db')), "Expected to find 2.2.0 DB")
        shutil.copyfile(os.path.join(db_path, 'MyGames-2.2.0.db'), os.path.join(db_path, 'MyGames.db'))

        gdb = GameDataBase(db_path)
        gdb.connect()

        util.CURRENT_DB_VERSION = '2.2.1'
        # Create db if not existent and maybe update to new version
        gdb.checkDBStructure()

        # Check backup files were created
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames.db.backup 2.2.0')), "No backup database created")

        rcbSettingRows = RCBSetting(gdb).getAll()
        self.assertEquals('2.2.1', rcbSettingRows[0][RCBSetting.COL_dbVersion])
        self.assertEquals(117, Game(gdb).getCount())

        # Cleanup
        gdb.close()
        os.remove(os.path.join(db_path, 'MyGames.db'))
        os.remove(os.path.join(db_path, 'MyGames.db.backup 2.2.0'))

    def test_DBUpgrade_221_222(self):
        db_path = os.path.join (self.get_testdata_path(), 'database')

        # Setup data - MyGames.db is the hard-coded expected DB name
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames-2.2.1.db')), "Expected to find 2.2.1 DB")
        shutil.copyfile(os.path.join(db_path, 'MyGames-2.2.1.db'), os.path.join(db_path, 'MyGames.db'))

        gdb = GameDataBase(db_path)
        gdb.connect()

        util.CURRENT_DB_VERSION = '2.2.2'
        # Create db if not existent and maybe update to new version
        gdb.checkDBStructure()

        # Check backup files were created
        self.assertTrue(os.path.isfile(os.path.join(db_path, 'MyGames.db.backup 2.2.1')), "No backup database created")

        rcbSettingRows = RCBSetting(gdb).getAll()
        self.assertEquals('2.2.2', rcbSettingRows[0][RCBSetting.COL_dbVersion])
        self.assertEquals(117, Game(gdb).getCount())

        # Cleanup
        gdb.close()
        os.remove(os.path.join(db_path, 'MyGames.db'))
        os.remove(os.path.join(db_path, 'MyGames.db.backup 2.2.1'))

if __name__ == "__main__":
    unittest.main()