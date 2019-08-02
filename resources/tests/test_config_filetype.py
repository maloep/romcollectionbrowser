import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'lib'))

from config import Config, FileType


class TestFileType(unittest.TestCase):
    """
    This unittest class is used for testing the FileType object
    """
    def test_ParseValidFileIsSuccessful(self):
        # Load the default config_template.xml distributed with RCB
        configxmlfile = os.path.join(os.path.dirname(__file__), '..', 'database', 'config_template.xml')
        conf = Config(configxmlfile)
        conf.initXml()

        ft, msg = conf.get_filetype_by_name('gameplay', conf.tree)
        self.assertIsInstance(ft, FileType, u'Expected FileType object')

        self.assertTrue(ft.type == 'video')
        self.assertTrue(ft.parent == 'game')
        self.assertTrue(ft.id == '12')


if __name__ == "__main__":
    unittest.main()
