# -*- coding: utf-8 -*-

"""
python -m unittest discover -v resources/tests/ "test_dbupdate.py"
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'pyscraper'))

from config import FileType
from dbupdate import DBUpdate


class TestDbUpdate(unittest.TestCase):
    def get_scraper_xml_path(self, xml_filename):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'scraper', xml_filename)

    def test_getFoldernameFromRomFilename(self):
        dbu = DBUpdate()
        # POSIX
        fname = dbu.getFoldernameFromRomFilename("/Users/User/Games/Emulation/SNES/Chrono Trigger (USA).zip")
        self.assertEqual(fname, "SNES")

        # Windows
        #fname = dbu.getFoldernameFromRomFilename("c:\\Users\\user.name\\Games\\Emulation\\SNES\\Chrono Trigger (USA).zip")
        #self.assertEqual(fname, "SNES")

        fname = dbu.getFoldernameFromRomFilename("Chrono Trigger (USA).zip")
        self.assertEqual(fname, "")

    def test_AddNewElements(self):
        ps = DBUpdate()
        existingResults = {"SearchKey": ["Tekken 2"], "Publisher": []}
        newResults = {"SearchKey": ["Tekken 3"], "Description": ["Tekken 2 description & history"],
                      "Publisher": ["Namco"]}
        existingResults = ps.addNewElements(existingResults, newResults)

        self.assertIn("Description", existingResults, "Expected to add Description")
        self.assertEqual(existingResults.get("SearchKey")[0], "Tekken 2",
                         "Expected existing field SearchKey to not be overwritten (now {0})".format(
                             existingResults.get("SearchKey")[0]))
        self.assertEqual(existingResults.get("Publisher")[0], "Namco",
                         "Expected existing but empty field Publisher to be overwritten")

    def test_AddNewElementsUnicode(self):
        ps = DBUpdate()
        existingResults = {"SearchKey": ["Random Game"]}
        newResults = {"Description": [u"'Super Keirin (スーパー競輪, Super Keirin) is a Japan-exclusive video game"]}
        existingResults = ps.addNewElements(existingResults, newResults)

        self.assertEqual(existingResults.get("Description")[0],
                         u"'Super Keirin (スーパー競輪, Super Keirin) is a Japan-exclusive video game",
                         "Expected Unicode string to be handled when adding new search result element")

    @unittest.skip("Not yet implemented")
    def test_getFilesByWildcard(self):
        dbu = DBUpdate()
        # FIXME TODO Not sure what this function is meant to do
        fname = dbu.getFilesByWildcard("/Users/andrew/Games/Emulation/SNES/Chrono Trigger (USA).zip")
        print("fname is {0}".format(fname))

        a = FileType()
        a.id, a.name, a.parent = 0, "rcb_rom", "game"
        print(a)
        # fileType.id = 0
        # fileType.name = "rcb_rom"
        # fileType.parent = "game"

    @unittest.skip("Not yet implemented")
    def test_getFilesByGameNameIgnoreCase(self):
        """
        /Users/andrew/Games/Emulation/SNES/Artwork/fanart/Madden NFL 97.*
        /Users/andrew/Games/Emulation/SNES/Artwork/fanart/SNES.*
        /Users/andrew/Games/Emulation/SNES/Artwork/fanart/Madden NFL '97 (USA).*
        Returns:

        """

        dbu = DBUpdate()
        fname = dbu.getFilesByWildcard("/Users/user/Games/Emulation/SNES/Chrono Trigger (USA).*")
        print ("test_getFilesByGameNameIgnoreCase")
        print (fname)


if __name__ == "__main__":
    unittest.main()
