import unittest
import os, sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib', 'launcher'))

from archive_handler import ArchiveHandler


class TestArchiveHandler(unittest.TestCase):

    handler = ArchiveHandler()

    def test_check_is_archive(self):
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.smc"), False)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.zip"), True)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.7z"), True)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.rar"), True)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.tar.gz"), True)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.tar.bz2"), True)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.tar.xz"), True)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.tgz"), True)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.tbz2"), True)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.xz"), True)
        self.assertEqual(self.handler.is_archive("C:\\Test\\MyRom.cbr"), True)


    def test_get_temp_dir_path(self):
        self.assertEqual(self.handler._ArchiveHandler__get_temp_dir_path('SNES'),
                         'C:\\Users\\Malte\\AppData\\Roaming\\Kodi\\addons\\script.games.rom.collection.browser.git\\resources\\tests\\script.games.rom.collection.browser\\tmp\\extracted\\SNES')


    def test_delete_temp_files(self):
        temp_path = self.handler._ArchiveHandler__get_temp_dir_path('SNES')

        files = os.listdir(temp_path)
        if(len(files) == 0):
            open(os.path.join(temp_path, 'test'), 'a').close()

        self.handler._ArchiveHandler__delete_temp_files(temp_path)
        files = os.listdir(temp_path)
        self.assertEqual(len(files), 0)

    def test_7z(self):

        try:
            import py7zr
        except ImportError as e:
            print(e)

