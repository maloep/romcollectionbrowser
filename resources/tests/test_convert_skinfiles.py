
from builtins import str
import os, re, sys
from xml.etree.ElementTree import *
import unittest
from convert_skin_files import SkinFileConverter


class TestSkinFileConverter(unittest.TestCase):

    @unittest.skip("only used manually to convert skin files")
    def test_convert_skin_files(self):
        SkinFileConverter().convert_skin_files()

    @unittest.skip("manual test")
    def test_re(self):
        line = '<bordertexture border="2" colordiffuse="$INFO[Skin.String(rcb_button_focus)]">rcb-thumbnail-border.png</bordertexture>'

        pattern = '<bordertexture border="(?P<value>[0-9]*)"'
        #pattern = '<radioposx>(?P<value>[0-9]*)</radioposx>'
        match = re.search(pattern, line)
        old_value = int(match.group('value'))
        new_value = old_value +20
        print (old_value)
        print (new_value)
        print (line.replace(str(old_value), str(new_value)))

    @unittest.skip("manual test")
    def test_read_xml(self):
        tree = ElementTree()
        if sys.version_info >= (2, 7):
            parser = XMLParser(encoding='utf-8')
        else:
            parser = XMLParser()

        skin_path = os.path.join(os.path.dirname(__file__), '..', 'skins')
        # use skin files of Default skin as source for all other skins
        convert_file = os.path.join(skin_path, 'Arctic.Zephyr', 'convert.xml')
        tree.parse(convert_file, parser)

        fonts = tree.findall('fonts/font')
        for font in fonts:
            print (font.attrib.get('name'))



