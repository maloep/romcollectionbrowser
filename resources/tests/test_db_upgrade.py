#  -*- coding: utf-8 -*-

"""
python -m unittest discover -v resources/tests/ "test_db_upgrade.py"
"""

import sys
import os
import shutil
import unittest
import datetime
from pprint import pprint
from resources.lib.xbmcaddon import Addon

# Shared resources
addon = Addon(id='script.games.rom.collection.browser')
addonPath = addon.getAddonInfo('path')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append (os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

class TestDBUpgrade(unittest.TestCase):
    def get_testdata_path(self):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'tests', 'testdata')

    def test_DBUpgrade(self):
        from resources.lib.gamedatabase import GameDataBase

        db_path = os.path.join (self.get_testdata_path(), 'dbupgrade')

        # Setup data - MyGames.db is the hard-coded expected DB name
        self.assertTrue(os.path.isfile(os.path.join (db_path, 'MyGames-0.7.4.db')), "Expected to find 0.7.4 DB")
        shutil.copyfile(os.path.join (db_path, 'MyGames-0.7.4.db'), os.path.join (db_path, 'MyGames.db'))

        gdb = GameDataBase(db_path)
        gdb.connect()

        #create db if not existent and maybe update to new version
        gdb.checkDBStructure()
        gdb.close()

        # Check backup files were created
        self.assertTrue(os.path.isfile(os.path.join (db_path, 'MyGames.db.backup 0.7.4')), "No backup database created")

        # FIXME TODO Assert version is 0.7.5
        # FIXME TODO Assert no data lost (num of rows for games, publishers, etc, is correct)

        # Cleanup
        os.remove(os.path.join (db_path, 'MyGames.db'))
        os.remove(os.path.join (db_path, 'MyGames.db.backup 0.7.4'))

if __name__ == "__main__":
    unittest.main()