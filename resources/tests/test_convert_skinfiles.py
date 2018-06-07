
import unittest
from convert_skin_files import SkinFileConverter


class TestSkinFileConverter(unittest.TestCase):

    def test_convert_skin_files(self):
        SkinFileConverter().convert_skin_files()