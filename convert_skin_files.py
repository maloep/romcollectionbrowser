from __future__ import print_function

from builtins import str
from builtins import object
import os, sys, re
from xml.etree.ElementTree import *

class SkinFileConverter(object):
    """ This object provides methods to convert skin files from Default skin to all other skins
        It will replace font names and adjusts some more skin related attributes like radiobutton sizes etc.
        Required information is read from skin specific convert.xml files that reside in each skin folder
    """

    # base skin directory
    skin_path = os.path.join(os.path.dirname(__file__), 'resources', 'skins')
    # use skin files of Default skin as source for all other skins
    source_file_dir = os.path.join(skin_path, 'Default', '720p')

    def convert_skin_files(self):

        # get list of skins to convert
        skin_dirs = [d for d in os.listdir(self.skin_path) if os.path.isdir(os.path.join(self.skin_path, d))]

        for skin_dir in skin_dirs:
            if skin_dir != 'Default':
                target_dir = os.path.join(self.skin_path, skin_dir, '720p')
                skin_files = os.listdir(self.source_file_dir)
                convert_file = os.path.join(self.skin_path, skin_dir, 'convert.xml')
                if not os.path.exists(convert_file):
                    print ('convert file does not exist: %s' %convert_file)
                    continue
                for skin_file in skin_files:
                    source_file = os.path.join(self.source_file_dir, skin_file)
                    target_file = os.path.join(target_dir, skin_file)

                    self.convert_skin_file(source_file, target_file, convert_file)

    def convert_skin_file(self, source_file, target_file, convert_file):
        tree = ElementTree()
        if sys.version_info >= (2, 7):
            parser = XMLParser(encoding='utf-8')
        else:
            parser = XMLParser()

        tree.parse(convert_file, parser)
        fonts = tree.findall('fonts/font')
        radiobutton_posx = int(tree.find('controls/radiobutton/radioposx').text)
        radiobutton_width = int(tree.find('controls/radiobutton/radiowidth').text)
        radiobutton_height = int(tree.find('controls/radiobutton/radioheight').text)
        view_50_panelcontent_posx = int(tree.find('contentpanels/view_50_panelcontent_posx').text)
        view_50_panelcontent_width = int(tree.find('contentpanels/view_50_panelcontent_width').text)
        view_50_image_focus_posy = int(tree.find('contentpanels/view_50_image_focus_posy').text)
        view_52_panellist_posx = int(tree.find('contentpanels/view_52_panellist_posx').text)
        view_52_panellist_posy = int(tree.find('contentpanels/view_52_panellist_posy').text)
        view_52_panellist_width = int(tree.find('contentpanels/view_52_panellist_width').text)
        view_52_panellist_height = int(tree.find('contentpanels/view_52_panellist_height').text)
        view_52_panelcontent_posx = int(tree.find('contentpanels/view_52_panelcontent_posx').text)
        view_52_panelcontent_posy = int(tree.find('contentpanels/view_52_panelcontent_posy').text)
        view_52_panelcontent_width = int(tree.find('contentpanels/view_52_panelcontent_width').text)
        view_52_panelcontent_height = int(tree.find('contentpanels/view_52_panelcontent_height').text)
        view_52_list_posx = int(tree.find('contentpanels/view_52_list_posx').text)
        view_52_listitem_nofocus_width = int(tree.find('contentpanels/view_52_listitem_nofocus_width').text)
        view_52_listitem_focus_width = int(tree.find('contentpanels/view_52_listitem_focus_width').text)
        view_52_labelconsole_posy = int(tree.find('contentpanels/view_52_labelconsole_posy').text)
        view_52_labeltitle_posy = int(tree.find('contentpanels/view_52_labeltitle_posy').text)
        view_52_clearlogo_posy = int(tree.find('contentpanels/view_52_clearlogo_posy').text)
        view_58_image_focus_posy = int(tree.find('contentpanels/view_58_image_focus_posy').text)
        scrollbar_h_posy = int(tree.find('controls/scrollbar/scrollbar_h_posy').text)
        scrollbar_h_height = int(tree.find('controls/scrollbar/scrollbar_h_height').text)
        scrollbar_v_posx = int(tree.find('controls/scrollbar/scrollbar_v_posx').text)
        scrollbar_v_width = int(tree.find('controls/scrollbar/scrollbar_v_width').text)
        scroll_updown_width = int(tree.find('controls/scroll_updown/scroll_updown_width').text)
        scroll_updown_height = int(tree.find('controls/scroll_updown/scroll_updown_height').text)
        scroll_updown_posx_left = int(tree.find('controls/scroll_updown/scroll_updown_posx_left').text)
        scroll_updown_posx_right = int(tree.find('controls/scroll_updown/scroll_updown_posx_right').text)
        view_50_textbox_height = int(tree.find('controls/textbox/view_50_textbox_height').text)
        view_52_textbox_height = int(tree.find('controls/textbox/view_52_textbox_height').text)
        view_53_textbox_height = int(tree.find('controls/textbox/view_53_textbox_height').text)
        view_57_textbox_height = int(tree.find('controls/textbox/view_57_textbox_height').text)
        view_58_textbox_height = int(tree.find('controls/textbox/view_58_textbox_height').text)
        view_59_textbox_height = int(tree.find('controls/textbox/view_59_textbox_height').text)
        gameinfo_textbox_height = int(tree.find('controls/textbox/gameinfo_textbox_height').text)
        bordersize = int(tree.find('controls/border/bordersize').text)
        border = int(tree.find('controls/border/border').text)
        scroll_updown_posy = int(tree.find('controls/scroll_updown/scroll_updown_posy').text)
        dialog_header_image_posy = int(tree.find('dialogs/dialog_header_image_posy').text)
        dialog_header_label_posy = int(tree.find('dialogs/dialog_header_label_posy').text)
        dialog_button_posy = int(tree.find('dialogs/dialog_button_posy').text)
        dialog_menuitem_height = int(tree.find('dialogs/dialog_menuitem_height').text)
        dialog_header_label_alignment = tree.find('dialogs/dialog_header_label_alignment').text



        with open(source_file, "rt") as fin:
            with open(target_file, "wt") as fout:
                for line in fin:
                    # Fonts
                    for font in fonts:
                        # font looks like this in convert.xml:
                        # <font name="font10">Mini</font>
                        # Estuary font names as attribute name, new skin font names as element text
                        line = line.replace(font.attrib.get('name'), font.text)

                    # Radiobuttons
                    line = self.update_radiobutton_properties(line, 'radioposx', radiobutton_posx)
                    line = self.update_radiobutton_properties(line, 'radiowidth', radiobutton_width)
                    line = self.update_radiobutton_properties(line, 'radioheight', radiobutton_height)

                    #scrollbars
                    line = self.update_numeric_properties(line, 'posy', 'scrollbar_h_posy', scrollbar_h_posy)
                    line = self.update_numeric_properties(line, 'height', 'scrollbar_h_height', scrollbar_h_height)
                    line = self.update_numeric_properties(line, 'posx', 'scrollbar_v_posx', scrollbar_v_posx)
                    line = self.update_numeric_properties(line, 'width', 'scrollbar_v_width', scrollbar_v_width)

                    #scroll-up/down
                    line = self.update_numeric_properties(line, 'width', 'scroll_updown_width', scroll_updown_width)
                    line = self.update_numeric_properties(line, 'height', 'scroll_updown_height', scroll_updown_height)
                    line = self.update_numeric_properties(line, 'posx', 'scroll_updown_posx_left', scroll_updown_posx_left)
                    line = self.update_numeric_properties(line, 'posx', 'scroll_updown_posx_right', scroll_updown_posx_right)
                    line = self.update_numeric_properties(line, 'posy', 'scroll_updown_posy', scroll_updown_posy)

                    #border
                    line = self.update_numeric_properties(line, 'bordersize', 'bordersize', bordersize)
                    line = self.update_numeric_attributes(line, 'bordertexture', 'border', border)

                    #textbox
                    line = self.update_numeric_properties(line, 'height', 'view_50_textbox_height', view_50_textbox_height)
                    line = self.update_numeric_properties(line, 'height', 'view_52_textbox_height', view_52_textbox_height)
                    line = self.update_numeric_properties(line, 'height', 'view_53_textbox_height', view_53_textbox_height)
                    line = self.update_numeric_properties(line, 'height', 'view_57_textbox_height', view_57_textbox_height)
                    line = self.update_numeric_properties(line, 'height', 'view_58_textbox_height', view_58_textbox_height)
                    line = self.update_numeric_properties(line, 'height', 'view_59_textbox_height', view_59_textbox_height)
                    line = self.update_numeric_properties(line, 'height', 'gameinfo_textbox_height', gameinfo_textbox_height)

                    # Panel adjustments
                    # View 50
                    line = self.update_numeric_properties(line, 'posx', 'view_50_panelcontent_posx', view_50_panelcontent_posx)
                    line = self.update_numeric_properties(line, 'width', 'view_50_panelcontent_width', view_50_panelcontent_width)
                    line = self.update_numeric_properties(line, 'posy', 'view_50_image_focus_posy', view_50_image_focus_posy)

                    # View 52
                    line = self.update_numeric_properties(line, 'posx', 'view_52_panellist_posx', view_52_panellist_posx)
                    line = self.update_numeric_properties(line, 'posy', 'view_52_panellist_posy', view_52_panellist_posy)
                    line = self.update_numeric_properties(line, 'width', 'view_52_panellist_width', view_52_panellist_width)
                    line = self.update_numeric_properties(line, 'height', 'view_52_panellist_height', view_52_panellist_height)

                    line = self.update_numeric_properties(line, 'posx', 'view_52_panelcontent_posx', view_52_panelcontent_posx)
                    line = self.update_numeric_properties(line, 'posy', 'view_52_panelcontent_posy', view_52_panelcontent_posy)
                    line = self.update_numeric_properties(line, 'width', 'view_52_panelcontent_width', view_52_panelcontent_width)
                    line = self.update_numeric_properties(line, 'height', 'view_52_panelcontent_height', view_52_panelcontent_height)

                    line = self.update_numeric_properties(line, 'posx', 'view_52_list_posx', view_52_list_posx)
                    line = self.update_numeric_properties(line, 'width', 'view_52_listitem_nofocus_width', view_52_listitem_nofocus_width)
                    line = self.update_numeric_properties(line, 'width', 'view_52_listitem_focus_width', view_52_listitem_focus_width)
                    line = self.update_numeric_properties(line, 'posy', 'view_52_labelconsole_posy', view_52_labelconsole_posy)
                    line = self.update_numeric_properties(line, 'posy', 'view_52_labeltitle_posy', view_52_labeltitle_posy)
                    line = self.update_numeric_properties(line, 'posy', 'view_52_clearlogo_posy', view_52_clearlogo_posy)

                    # View 58
                    line = self.update_numeric_properties(line, 'posy', 'view_58_image_focus_posy', view_58_image_focus_posy)

                    #dialogs
                    line = self.update_numeric_properties(line, 'posy', 'dialog_header_image_posy', dialog_header_image_posy)
                    line = self.update_numeric_properties(line, 'posy', 'dialog_header_label_posy', dialog_header_label_posy)
                    line = self.update_numeric_properties(line, 'posy', 'dialog_button_posy', dialog_button_posy)
                    line = self.update_numeric_properties(line, 'height', 'dialog_menuitem_height', dialog_menuitem_height)

                    line = self.update_text_properties(line, 'align', 'dialog_header_label_alignment', dialog_header_label_alignment)

                    fout.write(line)


    def update_numeric_properties(self, line, property_name, convert_comment, update_value):
        pattern = '<%s>(?P<value>[0-9]*)r?</%s><!--%s-->' %(property_name, property_name, convert_comment)
        match = re.search(pattern, line)
        if match:
            old_value = int(match.group('value'))
            new_value = old_value + update_value
            line = line.replace(str(old_value), str(new_value))

        return line

    def update_numeric_attributes(self, line, element_name, attribute_name, update_value):
        pattern = '<%s %s="(?P<value>[0-9]*)"' %(element_name, attribute_name)
        match = re.search(pattern, line)
        if match:
            old_value = int(match.group('value'))
            new_value = old_value + update_value
            line = line.replace(str(old_value), str(new_value))

        return line

    def update_text_properties(self, line, property_name, convert_comment, update_value):
        pattern = '<%s>(?P<value>.*)</%s><!--%s-->' %(property_name, property_name, convert_comment)
        match = re.search(pattern, line)
        if match:
            old_value = match.group('value')
            line = line.replace(str(old_value), str(update_value))

        return line

    def update_radiobutton_properties(self, line, property_name, update_value):
        pattern_posx = '<%s>(?P<value>[0-9]*)</%s>' %(property_name, property_name)
        match = re.search(pattern_posx, line)
        if match:
            old_value = int(match.group('value'))
            new_value = old_value + update_value
            line = line.replace(str(old_value), str(new_value))

        return line
