# coding: utf-8
"""
Classes and functions to work with Kodi GUI
"""

import xbmc as _xbmc

ACTION_ANALOG_FORWARD = 113
ACTION_ANALOG_MOVE = 49
ACTION_ANALOG_MOVE_X = 601
ACTION_ANALOG_MOVE_Y = 602
ACTION_ANALOG_REWIND = 114
ACTION_ANALOG_SEEK_BACK = 125
ACTION_ANALOG_SEEK_FORWARD = 124
ACTION_ASPECT_RATIO = 19
ACTION_AUDIO_DELAY = 161
ACTION_AUDIO_DELAY_MIN = 54
ACTION_AUDIO_DELAY_PLUS = 55
ACTION_AUDIO_NEXT_LANGUAGE = 56
ACTION_BACKSPACE = 110
ACTION_BIG_STEP_BACK = 23
ACTION_BIG_STEP_FORWARD = 22
ACTION_BUILT_IN_FUNCTION = 122
ACTION_CALIBRATE_RESET = 48
ACTION_CALIBRATE_SWAP_ARROWS = 47
ACTION_CHANGE_RESOLUTION = 57
ACTION_CHANNEL_DOWN = 185
ACTION_CHANNEL_SWITCH = 183
ACTION_CHANNEL_UP = 184
ACTION_CHAPTER_OR_BIG_STEP_BACK = 98
ACTION_CHAPTER_OR_BIG_STEP_FORWARD = 97
ACTION_CONTEXT_MENU = 117
ACTION_COPY_ITEM = 81
ACTION_CREATE_BOOKMARK = 96
ACTION_CREATE_EPISODE_BOOKMARK = 95
ACTION_CURSOR_LEFT = 120
ACTION_CURSOR_RIGHT = 121
ACTION_CYCLE_SUBTITLE = 99
ACTION_DECREASE_PAR = 220
ACTION_DECREASE_RATING = 137
ACTION_DELETE_ITEM = 80
ACTION_ENTER = 135
ACTION_ERROR = 998
ACTION_FILTER = 233
ACTION_FILTER_CLEAR = 150
ACTION_FILTER_SMS2 = 151
ACTION_FILTER_SMS3 = 152
ACTION_FILTER_SMS4 = 153
ACTION_FILTER_SMS5 = 154
ACTION_FILTER_SMS6 = 155
ACTION_FILTER_SMS7 = 156
ACTION_FILTER_SMS8 = 157
ACTION_FILTER_SMS9 = 158
ACTION_FIRST_PAGE = 159
ACTION_FORWARD = 16
ACTION_GESTURE_BEGIN = 501
ACTION_GESTURE_END = 599
ACTION_GESTURE_NOTIFY = 500
ACTION_GESTURE_PAN = 504
ACTION_GESTURE_ROTATE = 503
ACTION_GESTURE_SWIPE_DOWN = 541
ACTION_GESTURE_SWIPE_DOWN_TEN = 550
ACTION_GESTURE_SWIPE_LEFT = 511
ACTION_GESTURE_SWIPE_LEFT_TEN = 520
ACTION_GESTURE_SWIPE_RIGHT = 521
ACTION_GESTURE_SWIPE_RIGHT_TEN = 530
ACTION_GESTURE_SWIPE_UP = 531
ACTION_GESTURE_SWIPE_UP_TEN = 540
ACTION_GESTURE_ZOOM = 502
ACTION_GUIPROFILE_BEGIN = 204
ACTION_HIGHLIGHT_ITEM = 8
ACTION_INCREASE_PAR = 219
ACTION_INCREASE_RATING = 136
ACTION_INPUT_TEXT = 244
ACTION_JUMP_SMS2 = 142
ACTION_JUMP_SMS3 = 143
ACTION_JUMP_SMS4 = 144
ACTION_JUMP_SMS5 = 145
ACTION_JUMP_SMS6 = 146
ACTION_JUMP_SMS7 = 147
ACTION_JUMP_SMS8 = 148
ACTION_JUMP_SMS9 = 149
ACTION_LAST_PAGE = 160
ACTION_MOUSE_DOUBLE_CLICK = 103
ACTION_MOUSE_DRAG = 106
ACTION_MOUSE_END = 109
ACTION_MOUSE_LEFT_CLICK = 100
ACTION_MOUSE_LONG_CLICK = 108
ACTION_MOUSE_MIDDLE_CLICK = 102
ACTION_MOUSE_MOVE = 107
ACTION_MOUSE_RIGHT_CLICK = 101
ACTION_MOUSE_START = 100
ACTION_MOUSE_WHEEL_DOWN = 105
ACTION_MOUSE_WHEEL_UP = 104
ACTION_MOVE_DOWN = 4
ACTION_MOVE_ITEM = 82
ACTION_MOVE_ITEM_DOWN = 116
ACTION_MOVE_ITEM_UP = 115
ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MUTE = 91
ACTION_NAV_BACK = 92
ACTION_NEXT_CHANNELGROUP = 186
ACTION_NEXT_CONTROL = 181
ACTION_NEXT_ITEM = 14
ACTION_NEXT_LETTER = 140
ACTION_NEXT_PICTURE = 28
ACTION_NEXT_SCENE = 138
ACTION_NEXT_SUBTITLE = 26
ACTION_NONE = 0
ACTION_NOOP = 999
ACTION_OSD_HIDESUBMENU = 84
ACTION_OSD_SHOW_DOWN = 72
ACTION_OSD_SHOW_LEFT = 69
ACTION_OSD_SHOW_RIGHT = 70
ACTION_OSD_SHOW_SELECT = 73
ACTION_OSD_SHOW_UP = 71
ACTION_OSD_SHOW_VALUE_MIN = 75
ACTION_OSD_SHOW_VALUE_PLUS = 74
ACTION_PAGE_DOWN = 6
ACTION_PAGE_UP = 5
ACTION_PARENT_DIR = 9
ACTION_PASTE = 180
ACTION_PAUSE = 12
ACTION_PLAY = 68
ACTION_PLAYER_FORWARD = 77
ACTION_PLAYER_PLAY = 79
ACTION_PLAYER_PLAYPAUSE = 229
ACTION_PLAYER_REWIND = 78
ACTION_PREVIOUS_CHANNELGROUP = 187
ACTION_PREVIOUS_MENU = 10
ACTION_PREV_CONTROL = 182
ACTION_PREV_ITEM = 15
ACTION_PREV_LETTER = 141
ACTION_PREV_PICTURE = 29
ACTION_PREV_SCENE = 139
ACTION_PVR_PLAY = 188
ACTION_PVR_PLAY_RADIO = 190
ACTION_PVR_PLAY_TV = 189
ACTION_QUEUE_ITEM = 34
ACTION_RECORD = 170
ACTION_RELOAD_KEYMAPS = 203
ACTION_REMOVE_ITEM = 35
ACTION_RENAME_ITEM = 87
ACTION_REWIND = 17
ACTION_ROTATE_PICTURE_CCW = 51
ACTION_ROTATE_PICTURE_CW = 50
ACTION_SCAN_ITEM = 201
ACTION_SCROLL_DOWN = 112
ACTION_SCROLL_UP = 111
ACTION_SELECT_ITEM = 7
ACTION_SETTINGS_LEVEL_CHANGE = 242
ACTION_SETTINGS_RESET = 241
ACTION_SHIFT = 118
ACTION_SHOW_CODEC = 27
ACTION_SHOW_FULLSCREEN = 36
ACTION_SHOW_GUI = 18
ACTION_SHOW_INFO = 11
ACTION_SHOW_MPLAYER_OSD = 83
ACTION_SHOW_OSD = 24
ACTION_SHOW_OSD_TIME = 123
ACTION_SHOW_PLAYLIST = 33
ACTION_SHOW_SUBTITLES = 25
ACTION_SHOW_VIDEOMENU = 134
ACTION_SMALL_STEP_BACK = 76
ACTION_STEP_BACK = 21
ACTION_STEP_FORWARD = 20
ACTION_STEREOMODE_NEXT = 235
ACTION_STEREOMODE_PREVIOUS = 236
ACTION_STEREOMODE_SELECT = 238
ACTION_STEREOMODE_SET = 240
ACTION_STEREOMODE_TOGGLE = 237
ACTION_STEREOMODE_TOMONO = 239
ACTION_STOP = 13
ACTION_SUBTITLE_ALIGN = 232
ACTION_SUBTITLE_DELAY = 162
ACTION_SUBTITLE_DELAY_MIN = 52
ACTION_SUBTITLE_DELAY_PLUS = 53
ACTION_SUBTITLE_VSHIFT_DOWN = 231
ACTION_SUBTITLE_VSHIFT_UP = 230
ACTION_SWITCH_PLAYER = 234
ACTION_SYMBOLS = 119
ACTION_TAKE_SCREENSHOT = 85
ACTION_TELETEXT_BLUE = 218
ACTION_TELETEXT_GREEN = 216
ACTION_TELETEXT_RED = 215
ACTION_TELETEXT_YELLOW = 217
ACTION_TOGGLE_DIGITAL_ANALOG = 202
ACTION_TOGGLE_FULLSCREEN = 199
ACTION_TOGGLE_SOURCE_DEST = 32
ACTION_TOGGLE_WATCHED = 200
ACTION_TOUCH_LONGPRESS = 411
ACTION_TOUCH_LONGPRESS_TEN = 420
ACTION_TOUCH_TAP = 401
ACTION_TOUCH_TAP_TEN = 410
ACTION_TRIGGER_OSD = 243
ACTION_VIS_PRESET_LOCK = 130
ACTION_VIS_PRESET_NEXT = 128
ACTION_VIS_PRESET_PREV = 129
ACTION_VIS_PRESET_RANDOM = 131
ACTION_VIS_PRESET_SHOW = 126
ACTION_VIS_RATE_PRESET_MINUS = 133
ACTION_VIS_RATE_PRESET_PLUS = 132
ACTION_VOLAMP = 90
ACTION_VOLAMP_DOWN = 94
ACTION_VOLAMP_UP = 93
ACTION_VOLUME_DOWN = 89
ACTION_VOLUME_SET = 245
ACTION_VOLUME_UP = 88
ACTION_VSHIFT_DOWN = 228
ACTION_VSHIFT_UP = 227
ACTION_ZOOM_IN = 31
ACTION_ZOOM_LEVEL_1 = 38
ACTION_ZOOM_LEVEL_2 = 39
ACTION_ZOOM_LEVEL_3 = 40
ACTION_ZOOM_LEVEL_4 = 41
ACTION_ZOOM_LEVEL_5 = 42
ACTION_ZOOM_LEVEL_6 = 43
ACTION_ZOOM_LEVEL_7 = 44
ACTION_ZOOM_LEVEL_8 = 45
ACTION_ZOOM_LEVEL_9 = 46
ACTION_ZOOM_LEVEL_NORMAL = 37
ACTION_ZOOM_OUT = 30
ALPHANUM_HIDE_INPUT = 2
CONTROL_TEXT_OFFSET_X = 10
CONTROL_TEXT_OFFSET_Y = 2
ICON_OVERLAY_HD = 6
ICON_OVERLAY_LOCKED = 3
ICON_OVERLAY_NONE = 0
ICON_OVERLAY_RAR = 1
ICON_OVERLAY_UNWATCHED = 4
ICON_OVERLAY_WATCHED = 5
ICON_OVERLAY_ZIP = 2
ICON_TYPE_FILES = 106
ICON_TYPE_MUSIC = 103
ICON_TYPE_NONE = 101
ICON_TYPE_PICTURES = 104
ICON_TYPE_PROGRAMS = 102
ICON_TYPE_SETTINGS = 109
ICON_TYPE_VIDEOS = 105
ICON_TYPE_WEATHER = 107
INPUT_ALPHANUM = 0
INPUT_DATE = 2
INPUT_IPADDRESS = 4
INPUT_NUMERIC = 1
INPUT_PASSWORD = 5
INPUT_TIME = 3
KEY_APPCOMMAND = 53248
KEY_ASCII = 61696
KEY_BUTTON_A = 256
KEY_BUTTON_B = 257
KEY_BUTTON_BACK = 275
KEY_BUTTON_BLACK = 260
KEY_BUTTON_DPAD_DOWN = 271
KEY_BUTTON_DPAD_LEFT = 272
KEY_BUTTON_DPAD_RIGHT = 273
KEY_BUTTON_DPAD_UP = 270
KEY_BUTTON_LEFT_ANALOG_TRIGGER = 278
KEY_BUTTON_LEFT_THUMB_BUTTON = 276
KEY_BUTTON_LEFT_THUMB_STICK = 264
KEY_BUTTON_LEFT_THUMB_STICK_DOWN = 281
KEY_BUTTON_LEFT_THUMB_STICK_LEFT = 282
KEY_BUTTON_LEFT_THUMB_STICK_RIGHT = 283
KEY_BUTTON_LEFT_THUMB_STICK_UP = 280
KEY_BUTTON_LEFT_TRIGGER = 262
KEY_BUTTON_RIGHT_ANALOG_TRIGGER = 279
KEY_BUTTON_RIGHT_THUMB_BUTTON = 277
KEY_BUTTON_RIGHT_THUMB_STICK = 265
KEY_BUTTON_RIGHT_THUMB_STICK_DOWN = 267
KEY_BUTTON_RIGHT_THUMB_STICK_LEFT = 268
KEY_BUTTON_RIGHT_THUMB_STICK_RIGHT = 269
KEY_BUTTON_RIGHT_THUMB_STICK_UP = 266
KEY_BUTTON_RIGHT_TRIGGER = 263
KEY_BUTTON_START = 274
KEY_BUTTON_WHITE = 261
KEY_BUTTON_X = 258
KEY_BUTTON_Y = 259
KEY_INVALID = 65535
KEY_MOUSE_CLICK = 57344
KEY_MOUSE_DOUBLE_CLICK = 57360
KEY_MOUSE_DRAG = 57604
KEY_MOUSE_DRAG_END = 57606
KEY_MOUSE_DRAG_START = 57605
KEY_MOUSE_END = 61439
KEY_MOUSE_LONG_CLICK = 57376
KEY_MOUSE_MIDDLECLICK = 57346
KEY_MOUSE_MOVE = 57603
KEY_MOUSE_NOOP = 61439
KEY_MOUSE_RDRAG = 57607
KEY_MOUSE_RDRAG_END = 57609
KEY_MOUSE_RDRAG_START = 57608
KEY_MOUSE_RIGHTCLICK = 57345
KEY_MOUSE_START = 57344
KEY_MOUSE_WHEEL_DOWN = 57602
KEY_MOUSE_WHEEL_UP = 57601
KEY_TOUCH = 61440
KEY_UNICODE = 61952
KEY_VKEY = 61440
KEY_VMOUSE = 61439
NOTIFICATION_ERROR = 'error'
NOTIFICATION_INFO = 'info'
NOTIFICATION_WARNING = 'warning'
PASSWORD_VERIFY = 1
REMOTE_0 = 58
REMOTE_1 = 59
REMOTE_2 = 60
REMOTE_3 = 61
REMOTE_4 = 62
REMOTE_5 = 63
REMOTE_6 = 64
REMOTE_7 = 65
REMOTE_8 = 66
REMOTE_9 = 67
HORIZONTAL = 0
VERTICAL = 1

__author__ = 'Team Kodi <http://kodi.tv>'
__credits__ = 'Team Kodi'
__date__ = 'Fri May 01 16:22:15 BST 2015'
__platform__ = 'ALL'
__version__ = '2.20.0'


class Window(object):
    """
    Window(existingWindowId=-1)

    Create a new Window to draw on.

    Specify an id to use an existing window.

    :raises ValueError: If supplied window Id does not exist.
    :raises Exception: If more then 200 windows are created.

    Deleting this window will activate the old window that was active
    and resets (not delete) all controls that are associated with this window.
    """

    def __init__(self, existingWindowId=-1):
        """
        Create a new Window to draw on.

        Specify an id to use an existing window.

        :raises ValueError: If supplied window Id does not exist.
        :raises Exception: If more then 200 windows are created.

        Deleting this window will activate the old window that was active
        and resets (not delete) all controls that are associated with this window.
        """
        pass

    def show(self):
        """Show this window.

        Shows this window by activating it, calling close() after it wil activate the current window again.

        .. note:: If your script ends this window will be closed to. To show it forever,
            make a loop at the end of your script and use ``doModal()`` instead.
        """
        pass

    def close(self):
        """Closes this window.

        Closes this window by activating the old window.
        The window is not deleted with this method.
        """
        pass

    def onAction(self, action):
        """onAction method.

        This method will recieve all actions that the main program will send to this window.
        By default, only the ``PREVIOUS_MENU`` action is handled.
        Overwrite this method to let your script handle all actions.

        Don't forget to capture ``ACTION_PREVIOUS_MENU``, else the user can't close this window.
        """
        pass

    def onClick(self, controlId):
        """onClick method.

        This method will recieve all click events that the main program will send to this window.
        """
        pass

    def onDoubleClick(self, controlId):
        """
        onClick method.

        This method will recieve all double click events that the main program will send
        to this window.
        """
        pass

    def onControl(self, control):
        """
        onControl method.

        This method will recieve all control events that the main program will send to this window.
        'control' is an instance of a Control object.
        """
        pass

    def onFocus(self, control):
        """onFocus method.

        This method will recieve all focus events that the main program will send to this window.
        """
        pass

    def onInit(self):
        """onInit method.

        This method will be called to initialize the window.
        """
        pass

    def doModal(self):
        """Display this window until ``close()`` is called."""
        pass

    def addControl(self, pControl):
        """Add a Control to this window.

        :raises TypeError: If supplied argument is not a Control type.
        :raises ReferenceError: If control is already used in another window.
        :raises RuntimeError: Should not happen :-)

        The next controls can be added to a window atm:

            * ``ControlLabel``
            * ``ControlFadeLabel``
            * ``ControlTextBox``
            * ``ControlButton``
            * ``ControlCheckMark``
            * ``ControlList``
            * ``ControlGroup``
            * ``ControlImage``
            * ``ControlRadioButton``
            * ``ControlProgress``
        """
        pass

    def addControls(self, pControls):
        """
        Add a list of Controls to this window.

        :raises TypeError, if supplied argument is not ofList type, or a control is not ofControl type
        :raises ReferenceError, if control is already used in another window
        :raises RuntimeError, should not happen :-)
        """
        pass

    def getControl(self, iControlId):
        """Get's the control from this window.

        :raises Exception: If Control doesn't exist

        controlId doesn't have to be a python control, it can be a control id
        from a xbmc window too (you can find id's in the xml files).

        .. note:: Non-Python controls are not completely usable yet.
            You can only use the ``Control`` functions.
        """
        return Control()

    def setFocus(self, pControl):
        """Give the supplied control focus.

        :raises TypeError: If supplied argument is not a Control type.
        :raises SystemError: On Internal error.
        :raises RuntimeError: If control is not added to a window.
        """
        pass

    def setFocusId(self, iControlId):
        """Gives the control with the supplied focus.

        :raises SystemError: On Internal error.
        :raises RuntimeError: If control is not added to a window.
        """
        pass

    def getFocus(self):
        """Returns the control which is focused.

        :raises SystemError: On Internal error.
        :raises RuntimeError: If no control has focus.
        """
        return Control

    def getFocusId(self):
        """Returns the id of the control which is focused.

        :raises SystemError: On Internal error.
        :raises RuntimeError: If no control has focus.
        """
        return long()

    def removeControl(self, pControl):
        """Removes the control from this window.

        :raises TypeError: If supplied argument is not a Control type.
        :raises RuntimeError: If control is not added to this window.

        This will not delete the control. It is only removed from the window.
        """
        pass

    def removeControls(self, pControls):
        """
        removeControls(self, List)--Removes a list of controls from this window.

        :raises TypeError: if supplied argument is not aControl type
        :raises RuntimeError: if control is not added to this window

        This will not delete the controls. They are only removed from the window.
        """
        pass

    def getHeight(self):
        """Returns the height of this screen."""
        return long()

    def getWidth(self):
        """Returns the width of this screen."""
        return long()

    def getResolution(self):
        """Returns the resolution of the screen.

        The returned value is one of the following:

        * RES_INVALID        = -1,
        * RES_HDTV_1080i     =  0,
        * RES_HDTV_720pSBS   =  1,
        * RES_HDTV_720pTB    =  2,
        * RES_HDTV_1080pSBS  =  3,
        * RES_HDTV_1080pTB   =  4,
        * RES_HDTV_720p      =  5,
        * RES_HDTV_480p_4x3  =  6,
        * RES_HDTV_480p_16x9 =  7,
        * RES_NTSC_4x3       =  8,
        * RES_NTSC_16x9      =  9,
        * RES_PAL_4x3        = 10,
        * RES_PAL_16x9       = 11,
        * RES_PAL60_4x3      = 12,
        * RES_PAL60_16x9     = 13,
        * RES_AUTORES        = 14,
        * RES_WINDOW         = 15,
        * RES_DESKTOP        = 16,  Desktop resolution for primary screen
        * RES_CUSTOM         = 16 + 1

        See: https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Resolution.h
        """
        return long()

    def setCoordinateResolution(self, res):
        """Sets the resolution that the coordinates of all controls are defined in.

        Allows XBMC to scale control positions and width/heights to whatever resolution
        XBMC is currently using.

        resolution is one of the following:

        * RES_INVALID        = -1,
        * RES_HDTV_1080i     =  0,
        * RES_HDTV_720pSBS   =  1,
        * RES_HDTV_720pTB    =  2,
        * RES_HDTV_1080pSBS  =  3,
        * RES_HDTV_1080pTB   =  4,
        * RES_HDTV_720p      =  5,
        * RES_HDTV_480p_4x3  =  6,
        * RES_HDTV_480p_16x9 =  7,
        * RES_NTSC_4x3       =  8,
        * RES_NTSC_16x9      =  9,
        * RES_PAL_4x3        = 10,
        * RES_PAL_16x9       = 11,
        * RES_PAL60_4x3      = 12,
        * RES_PAL60_16x9     = 13,
        * RES_AUTORES        = 14,
        * RES_WINDOW         = 15,
        * RES_DESKTOP        = 16,  Desktop resolution for primary screen
        * RES_CUSTOM         = 16 + 1

        See: https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/Resolution.h
        """
        pass

    def setProperty(self, key, value):
        """Sets a window property, similar to an infolabel.

        :param key: string - property name.
        :param value: string or unicode - value of property.

        .. note:: key is NOT case sensitive. Setting value to an empty string is equivalent to clearProperty(key).

        Example::

            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            win.setProperty('Category', 'Newest')
        """
        pass

    def getProperty(self, key):
        """Returns a window property as a string, similar to an infolabel.

        :param key: string - property name.

        .. note:: key is NOT case sensitive.

        Example::

            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            category = win.getProperty('Category')
        """
        return str()

    def clearProperty(self, key):
        """Clears the specific window property.

        :param key: string - property name.

        .. note:: key is NOT case sensitive. Equivalent to setProperty(key,'').

        Example::

            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            win.clearProperty('Category')
        """
        pass

    def clearProperties(self):
        """Clears all window properties.

        Example::

            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            win.clearProperties()
        """
        pass


class WindowDialog(Window):
    """
    WindowDialog()

    Create a new WindowDialog with transparent background.

    Unlike Window, WindowDialog always stays on top of XBMC UI.
    """
    pass


class WindowXML(Window):
    """
    WindowXML(xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p', isMedia=False)

    WindowXML class.

    :param xmlFilename: the name of the xml file to look for.
    :type xmlFilename: str
    :param scriptPath: path to script. used to fallback to if the xml doesn't exist in the current skin.
        (eg ``os.getcwd()``)
    :type scriptPath: str
    :param defaultSkin: name of the folder in the skins path to look in for the xml.
    :type defaultSkin: str
    :param defaultRes: default skins resolution.
    :type defaultRes: str
    :param isMedia: if False, create a regular window. if True,
        create a mediawindow. (default=False)
    :type isMedia: bool
    :raises Exception: if more then 200 windows are created.

    .. note:: Skin folder structure is eg (resources/skins/Default/720p).

    Example::

        ui = WindowXML('script-Lyrics-main.xml', os.getcwd(), 'LCARS', 'PAL')
        ui.doModal()
        del ui
    """

    def __init__(self, xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p', isMedia=False):
        """
        Class constructor

        :param xmlFilename: the name of the xml file to look for.
        :type xmlFilename: str
        :param scriptPath: path to script. used to fallback to if the xml doesn't exist in the current skin.
            (eg ``os.getcwd()``)
        :type scriptPath: str
        :param defaultSkin: name of the folder in the skins path to look in for the xml.
        :type defaultSkin: str
        :param defaultRes: default skins resolution.
        :type defaultRes: str
        :param isMedia: if False, create a regular window. if True,
            create a mediawindow. (default=False)
        :type isMedia: bool
        :raises Exception: if more then 200 windows are created.

        .. note:: Skin folder structure is eg (resources/skins/Default/720p).

        Example::

            ui = WindowXML('script-Lyrics-main.xml', os.getcwd(), 'LCARS', 'PAL')
            ui.doModal()
            del ui
        """
        pass

    def removeItem(self, position):
        """Removes a specified item based on position, from the Window List.

        :param position: integer - position of item to remove.
        """
        pass

    def addItem(self, item, position=32767):
        """Add a new item to this Window List.

        :param item: string, unicode or ListItem - item to add.
        :param position: integer - position of item to add.
            (NO Int = Adds to bottom,0 adds to top, 1 adds to one below from top,-1 adds to one above from bottom etc etc)
            If integer positions are greater than list size, negative positions will add to top of list,
            positive positions will add to bottom of list.

        Example::

            self.addItem('Reboot XBMC', 0)
        """
        pass

    def addItems(self, items):
        """
        Add a list of items to to the window list.

        :param items: list of strings, unicode objects or ListItems to add.
        :type items: list
        """
        pass

    def clearList(self):
        """Clear the Window List."""
        pass

    def setCurrentListPosition(self, position):
        """Set the current position in the Window List.

        :param position: integer - position of item to set.
        """
        pass

    def getCurrentListPosition(self):
        """Gets the current position in the Window List."""
        return int()

    def getListItem(self, position):
        """Returns a given ListItem in this Window List.

        :param position: integer - position of item to return.
        """
        return ListItem()

    def getListSize(self):
        """Returns the number of items in this Window List."""
        return int()

    def setContainerProperty(self, key, value):
        """
        Sets a container property, similar to an infolabel.

        :param key: string - property name.
        :param value: string or unicode - value of property.

        .. note:: ``key`` is NOT case sensitive.

        Example::

            self.setProperty('Category', 'Newest')
        """
        pass

    def getCurrentContainerId(self):
        """
        Returns the id of the currently visible container.

        Example::

            container_id = self.getCurrentContainerId()
        """
        return int()

    def setContent(self, value):
        """
        Sets the content type of the container.

        :param value: string or unicode -- content value.

        Available content types:

        =========== =========================================
        Name        Media
        ----------- -----------------------------------------
        actors      Videos
        addons      Addons, Music, Pictures, Programs, Videos
        albums      Music, Videos
        artists     Music, Videos
        countries   Music, Videos
        directors   Videos
        files       Music, Videos
        games       Games
        genres      Music, Videos
        images      Pictures
        mixed       Music, Videos
        movies      Videos
        Musicvideos Music, Videos
        playlists   Music, Videos
        seasons     Videos
        sets        Videos
        songs       Music
        studios     Music, Videos
        tags        Music, Videos
        tvshows     Videos
        videos      Videos
        years       Music, Videos
        =========== =========================================

        v18 Python API changes: Added new function.

        Example::

            self.setContent('movies')
        """
        pass


class WindowXMLDialog(WindowXML):
    """
    WindowXMLDialog(xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p')

    WindowXMLDialog class.

    :param xmlFilename: string - the name of the xml file to look for.
    :param: scriptPath: string - path to script. used to fallback to if the xml doesn't exist in the current skin.
        (eg ``os.getcwd()``)
    :param defaultSkin: string - name of the folder in the skins path to look in for the xml.
    :param defaultRes: string - default skins resolution.

    .. note:: Skin folder structure is eg (resources/skins/Default/720p).

    Example::

        ui = WindowXMLDialog('script-Lyrics-main.xml', os.getcwd(), 'LCARS', 'PAL')
        ui.doModal()
        del ui
    """
    pass


class Control(object):
    """
    Parent for control classes.

    The problem here is that Python uses references to this class in a dynamic typing way.
    For example, you will find this type of python code frequently::

        window.getControl( 100 ).setLabel( "Stupid Dynamic Type")

    Notice that the 'getControl' call returns a 'Control ' object.

    In a dynamically typed language, the subsequent call to setLabel works if the specific type of control has the method.
    The script writer is often in a position to know more than the code about the specificControl type
    (in the example, that control id 100 is a 'ControlLabel ') where the C++ code is not.

    SWIG doesn't support this type of dynamic typing. The 'Control ' wrapper that's returned will wrap aControlLabel
    but will not have the 'setLabel' method on it. The only way to handle this is to add all possible subclass methods
    to the parent class. This is ugly but the alternative is nearly as ugly.
    It's particularly ugly here because the majority of the methods are unique to the particular subclass.

    If anyone thinks they have a solution then let me know. The alternative would be to have a set of 'getContol'
    methods, each one coresponding to a type so that the downcast can be done in the native code.

    IOW rather than a simple 'getControl' there would be a 'getControlLabel', 'getControlRadioButton',
    'getControlButton', etc.

    TODO: This later solution should be implemented for future scripting languages
    while the former will remain as deprecated functionality for Python.
    """
    def addItem(self):
        pass

    def addItems(self):
        pass

    def canAcceptMessages(self):
        pass

    def controlDown(self, control):
        """
        Set's the controls down navigation.

        :param control: control object - control to navigate to on down.

        .. note:: You can also usesetNavigation() . Set to self to disable navigation.

        :raises TypeError: if one of the supplied arguments is not a control type.
        :raises: ReferenceError if one of the controls is not added to a window.

        example::

            self.button.controlDown(self.button1)
        """
        pass

    def controlLeft(self, control):
        """
        Set's the controls left navigation.

        :param control: control object - control to navigate to on left.

        .. note:: You can also usesetNavigation(). Set to self to disable navigation.

        :raises TypeError: if one of the supplied arguments is not a control type.
        :raises ReferenceError: if one of the controls is not added to a window.

        example::

            self.button.controlLeft(self.button1)
        """
        pass

    def controlRight(self, control):
        """
        Set's the controls right navigation.

        :param control: control object - control to navigate to on right.

        .. note:: You can also usesetNavigation(). Set to self to disable navigation.

        :raises TypeError: if one of the supplied arguments is not a control type.
        :raises ReferenceError: if one of the controls is not added to a window.

        example::

            self.button.controlRight(self.button1)
        """
        pass

    def controlUp(self, control):
        """
        Set's the controls up navigation.

        :param control: control object - control to navigate to on up.

        .. note:: You can also usesetNavigation() . Set to self to disable navigation.

        :raises TypeError: if one of the supplied arguments is not a control type.
        :raises ReferenceError: if one of the controls is not added to a window.

        example::

            self.button.controlUp(self.button1)
         """
        pass

    def getHeight(self):
        """
        Returns the control's current height as an integer.

        example::

            height = self.button.getHeight()
        """
        return long()

    def getId(self):
        """
        Returns the control's current id as an integer.

        example::

            id = self.button.getId()
        """
        return long()

    def getPosition(self):
        """
        Returns the control's current position as a x,y integer tuple.

        example::

            pos = self.button.getPosition()
        """
        return long(), long()

    def getWidth(self):
        """
        Returns the control's current width as an integer.

        example::

            width = self.button.getWidth()
        """
        return long()

    def getX(self):
        """
        Get X coordinate of a control as an integer.
        """
        return long()

    def getY(self):
        """
        Get Y coordinate of a control as an integer.
        """
        return long()

    def setAnimations(self, eventAttr):
        """
        Set's the control's animations.

        :param eventAttr: list -- A list of tuples [(event,attr,)*] consisting of event and attributes pairs.

        ``event`` : string - The event to animate.
        ``attr`` : string - The whole attribute string separated by spaces.

        Animating your skin -http://wiki.xbmc.org/?title=Animating_Your_Skin

        example::

            self.button.setAnimations([('focus', 'effect=zoom end=90,247,220,56 time=0',)])
        """
        pass

    def setEnableCondition(self, enable):
        """
        Set's the control's enabled condition.

        Allows XBMC to control the enabled status of the control.

        :param enable: string - Enable condition.

        List of Conditions: http://wiki.xbmc.org/index.php?title=List_of_Boolean_Conditions

        example::

            self.button.setEnableCondition('System.InternetState')
        """
        pass

    def setEnabled(self, enabled):
        """
        Set's the control's enabled/disabled state.

        :param enabled: bool - True=enabled / False=disabled.

        example::

            self.button.setEnabled(False)
        """
        pass

    def setHeight(self, height):
        """
        Set's the controls height.

        :param height: integer - height of control.

        example::

            self.image.setHeight(100)
        """
        pass

    def setNavigation(self, up, down, left, right):
        """
        Set's the controls navigation.

        :param up: control object - control to navigate to on up.
        :param down: control object - control to navigate to on down.
        :param left: control object - control to navigate to on left.
        :param right: control object - control to navigate to on right.

        .. note:: Same ascontrolUp() ,controlDown() ,controlLeft() ,controlRight().
            Set to self to disable navigation for that direction.

        :raises TypeError: if one of the supplied arguments is not a control type.
        :raises ReferenceError: if one of the controls is not added to a window.

        example::

            self.button.setNavigation(self.button1, self.button2, self.button3, self.button4)
        """
        pass

    def setPosition(self, x, y):
        """
        Set's the controls position.

        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.

        .. note:: You may use negative integers. (e.g sliding a control into view)

        example::

            self.button.setPosition(100, 250)
        """
        pass

    def setVisible(self, visible):
        """
        Set's the control's visible/hidden state.

        :param visible: bool - True=visible / False=hidden.

        example::

            self.button.setVisible(False)
        """
        pass

    def setVisibleCondition(self, condition, allowHiddenFocus=False):
        """
        Set's the control's visible condition.

        Allows XBMC to control the visible status of the control.

        :param condition: string - Visible condition.
        :param: allowHiddenFocus: bool - True=gains focus even if hidden.

        List of Conditions: http://wiki.xbmc.org/index.php?title=List_of_Boolean_Conditions

        example::

            self.button.setVisibleCondition('[Control.IsVisible(41) + !Control.IsVisible(12)]', True)
        """
        pass

    def setWidth(self, width):
        """
        Set's the controls width.

        :param width: integer - width of control.

        example::

            self.image.setWidth(100)
        """
        pass


class ListItem(object):
    """
    ListItem(self, label='', label2='', iconImage=None, thumbnailImage=None, path=None, offscreen=False)

    Creates a new ListItem.

    :param label: string or unicode -- label1 text.
    :param label2: string or unicode -- label2 text.
    :param iconImage: string -- icon filename.
    :param thumbnailImage: string -- thumbnail filename.
    :param path: string or unicode -- listitem's path.
    :param offscreen: bool

    .. warning:: Starting from 16.0 (Jarvis) all image-related parameters and methods will be deprecated,
        and :func:`setArt` will become the only method for setting ListItem's images.

    Example::

        listitem = xbmcgui.ListItem('Casino Royale', '[PG-13]',
                    'blank-poster.tbn', 'poster.tbn',
                    path='f:\\movies\\casino_royale.mov')
    """

    def __init__(self, label='', label2='', iconImage=None, thumbnailImage=None, path=None, offscreen=False):
        """
        :param label: string or unicode -- label1 text.
        :param label2: string or unicode -- label2 text.
        :param iconImage: string -- icon filename.
        :param thumbnailImage: string -- thumbnail filename.
        :param path: string or unicode -- listitem's path.
        :param offscreen: bool -- do not lock UI (for scrapers and subtitle addons).

        Example::

            listitem = xbmcgui.ListItem('Casino Royale', '[PG-13]',
                        'blank-poster.tbn', 'poster.tbn',
                        path='f:\\movies\\casino_royale.mov')
        """
        pass

    def addStreamInfo(self, cType, dictionary):
        """
        addStreamInfo(type, values) -- Add a stream with details.

        :param cType: string - type of stream(video/audio/subtitle).
        :param dictionary: dictionary - pairs of { label: value }.

        Video Values::

            codec         : string (h264)
            aspect        : float (1.78)
            width         : integer (1280)
            height        : integer (720)
            duration      : integer (seconds)

        Audio Values::

            codec         : string (dts)
            language      : string (en)
            channels      : integer (2)

        Subtitle Values::

            language      : string (en)

        example::

            self.list.getSelectedItem().addStreamInfo('video', { 'Codec': 'h264', 'Width' : 1280 })
        """
        pass

    def getdescription(self):
        """
        Returns the description of this PlayListItem.
        """
        return str()

    def getduration(self):
        """
        Returns the duration of this PlayListItem
        """
        return str()

    def getfilename(self):
        """
        Returns the filename of this PlayListItem.
        """
        return str()

    def getLabel(self):
        """Returns the listitem label."""
        return str()

    def getLabel2(self):
        """Returns the listitem's second label."""
        return str()

    def setLabel(self, label):
        """Sets the listitem's label.

        :param label: string or unicode - text string.
        """
        pass

    def setLabel2(self, label2):
        """Sets the listitem's second label.

        :param label2: string or unicode - text string.
        """
        pass

    def setIconImage(self, iconImage):
        """Sets the listitem's icon image.

        :param iconImage: string or unicode - image filename.
        """
        pass

    def setThumbnailImage(self, thumbFilename):
        """Sets the listitem's thumbnail image.

        :param thumbFilename: string or unicode - image filename.
        """
        pass

    def select(self, selected):
        """Sets the listitem's selected status.

        :param selected: bool - True=selected/False=not selected.
        """
        pass

    def isSelected(self):
        """Returns the listitem's selected status."""
        return bool(1)

    def setInfo(self, type, infoLabels):
        """Sets the listitem's infoLabels.

        :param type: string - type of media(video/music/pictures).
        :param infoLabels: dictionary - pairs of { label: value }.

        .. note::
            To set pictures exif info, prepend 'exif:' to the label. Exif values must be passed
            as strings, separate value pairs with a comma. (eg. {'exif:resolution': '720,480'}
            See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings.

        General Values that apply to all types:

            * count : integer (12) - can be used to store an id for later, or for sorting purposes
            * size  : long (1024) - size in bytes
            * date  : string (%d.%m.%Y / 01.01.2009) - file date

        Video Values::

            genre         : string (Comedy)
            year          : integer (2009)
            episode       : integer (4)
            season        : integer (1)
            top250        : integer (192)
            tracknumber   : integer (3)
            rating        : float (6.4) - range is 0..10
            watched       : deprecated - use playcount instead
            playcount     : integer (2) - number of times this item has been played
            overlay       : integer (2) - range is 0..8.  See GUIListItem.h for values
            cast          : list (Michal C. Hall)
            castandrole   : list (Michael C. Hall|Dexter)
            director      : string (Dagur Kari)
            mpaa          : string (PG-13)
            plot          : string (Long Description)
            plotoutline   : string (Short Description)
            title         : string (Big Fan)
            originaltitle : string (Big Fan)
            duration      : string - duration in minutes (95)
            studio        : string (Warner Bros.)
            tagline       : string (An awesome movie) - short description of movie
            writer        : string (Robert D. Siegel)
            tvshowtitle   : string (Heroes)
            premiered     : string (2005-03-04)
            status        : string (Continuing) - status of a TVshow
            code          : string (tt0110293) - IMDb code
            aired         : string (2008-12-07)
            credits       : string (Andy Kaufman) - writing credits
            lastplayed    : string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)
            album         : string (The Joshua Tree)
            votes         : string (12345 votes)
            trailer       : string (/home/user/trailer.avi)
            imdbnumber    : string (tt0110293) - IMDb code
            set           : string (Batman Collection) - name of the collection
            setid         : integer (14) - ID of the collection
            mediatype     : string "video", "movie", "tvshow", "season", "episode" or "musicvideo" 

        Music Values::

            tracknumber : integer (8)
            duration    : integer (245) - duration in seconds
            year        : integer (1998)
            genre       : string (Rock)
            album       : string (Pulse)
            artist      : string (Muse)
            title       : string (American Pie)
            rating      : string (3) - single character between 0 and 5
            lyrics      : string (On a dark desert highway...)
            playcount   : integer (2) - number of times this item has been played
            lastplayed  : string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)

        Picture Values::

            title       : string (In the last summer-1)
            picturepath : string (/home/username/pictures/img001.jpg)
            exif        : string (See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings)

        Example::

            self.list.getSelectedItem().setInfo('video', { 'Genre': 'Comedy' })
        """
        pass

    def setCast(self, actors):
        """ Sets the cast parameters, including artwork and the ability to specify the order of occurrence

        :param actors: list of dictionaries (see below for relevant keys)

        Keys::

            name          : string (Michael C. Hall)
            role          : string (Dexter)
            thumbnail     : string (http://www.someurl.com/someimage.png)
            order         : integer (1)

        Example::

            actors = [{"name": "Actor 1", "role": "role 1"}, {"name": "Actor 2", "role": "role 2"}]
            listitem.setCast(actors)
        """
        pass

    def setProperty(self, key, value):
        """Sets a listitem property, similar to an infolabel.

        :param key: string - property name.
        :param value: string or unicode - value of property.

        .. note::
            Key is NOT case sensitive.

        Some of these are treated internally by XBMC, such as the 'StartOffset' property, which is
        the offset in seconds at which to start playback of an item.  Others may be used in the skin
        to add extra information, such as 'WatchedCount' for tvshow items

        Example::

            self.list.getSelectedItem().setProperty('AspectRatio', '1.85 : 1')
            self.list.getSelectedItem().setProperty('StartOffset', '256.4')
        """
        pass

    def getProperty(self, key):
        """Returns a listitem property as a string, similar to an infolabel.

        :param key: string - property name.

        .. note::
            Key is NOT case sensitive.
        """
        return str()

    def addContextMenuItems(self, items):
        """Adds item(s) to the context menu for media lists.

        :param items: list - [(label, action)] A list of tuples consisting of label and action pairs.
            label: string or unicode - item's label.
            action: string or unicode - any built-in function to perform.

        List of functions: http://wiki.xbmc.org/?title=List_of_Built_In_Functions

        Example::

            listitem.addContextMenuItems([('Theater Showtimes',
                    'XBMC.RunScript(special://home/scripts/showtimes/default.py,Iron Man)')])
        """
        pass

    def setPath(self, path):
        """
        Sets the listitem's path.

        :param path: string or unicode - path, activated when item is clicked.

        .. note:: You can use the above as keywords for arguments.

        example::

            self.list.getSelectedItem().setPath(path='ActivateWindow(Weather)')
        """
        pass

    def getPath(self):
        """
        Returns the path of this listitem.

        v17 Python API changes: New function added.
        """
        return str()

    def setArt(self, dictionary):
        """
        Sets the listitem's art

        :param dictionary: dict - pairs of { label: value }.

        Some default art values (any string possible):

        * thumb     : string - image filename
        * poster    : string - image filename
        * banner    : string - image filename
        * fanart    : string - image filename
        * clearart  : string - image filename
        * clearlogo : string - image filename
        * landscape : string - image filename

        .. warning:: Starting from 16.0 (Jarvis) all image-related parameters and methods will be deprecated,
            and ``setArt`` will become the only method for setting ListItem's images.

        example::

            self.list.getSelectedItem().setArt({ 'poster': 'poster.png', 'banner' : 'banner.png' })
        """
        pass

    def getMusicInfoTag(self):
        """
        returns the MusicInfoTag for this item.
        """
        return _xbmc.InfoTagMusic()

    def getVideoInfoTag(self):
        """
        returns the VideoInfoTag for this item.
        """
        return _xbmc.InfoTagVideo()

    def setMimeType(self, mimetype):
        """
        Sets the listitem's mimetype if known.

        :param mimetype : string or unicode - mimetype.

        If known prehand, this can avoid xbmc doing ``HEAD`` requests to http servers to figure out file type.
        """
        pass

    def setSubtitles(self, subtitleFiles):
        """
        Sets subtitles for this listitem.

        :param subtitleFiles: - list of subtitle paths

        example::

            listitem.setSubtitles(['special://temp/example.srt', 'http://example.com/example.srt' ])
        """
        pass

    def getArt(self, key):
        """
        Returns a listitem art path as a string, similar to an infolabel

        :param key: art name
        :return: path to art image

        Some default art values (any string possible)::

            - thumb         : string - image path
            - poster        : string - image path
            - banner        : string - image path
            - fanart        : string - image path
            - clearart      : string - image path
            - clearlogo     : string - image path
            - landscape     : string - image path
            - icon          : string - image path

        Example::

            poster = self.list.getSelectedItem().getArt('poster')

        """
        return str()

    def setUniqueIDs(self, values, defaultrating=''):
        """
        Sets the listitem's uniqueID 
        
        Some example values (any string possible):
        
        =========  ======================
        **Label**  **Type**
        ---------  ----------------------
        imdb       string - uniqueid name
        tvdb       string - uniqueid name
        tmdb       string - uniqueid name
        anidb      string - uniqueid name
        =========  ======================
        
        :param values: pairs of ``{label: value}``
        :type values: dict
        :param defaultrating: [opt] the name of default rating
        :type defaultrating: str
        
        Example::
        
            # setUniqueIDs(values, defaultrating)
            listitem.setUniqueIDs({ 'imdb': 'tt8938399', 'tmdb' : '9837493' }, "imdb")
        """
        pass

    def getUniqueID(self, key):
        """
        Returns a listitem uniqueID as a string, similar to an infolabel.

        Parameters:

        - key: string - uniqueID name.

        Some example values (any string possible):

        =========  ======================
        **Label**  **Type**
        ---------  ----------------------
        imdb       string - uniqueid name
        tvdb       string - uniqueid name
        tmdb       string - uniqueid name
        anidb      string - uniqueid name
        =========  ======================

        Example::

            uniqueID = listitem.getUniqueID('imdb')

        """
        return str()

    def addAvailableThumb(self, images):
        """
        Add a thumb to available thumbs (needed for scrapers)

        Parameters:

        - url: string (image path url)
        - aspect: [opt] string (image type)
        - referrer: [opt] string (referr url)
        - cache: [opt] string (filename in cache)
        - post: [opt] bool (use post to retrieve the image, default false)
        - isgz: [opt] bool (use gzip to retrieve the image, default false)
        - season: [opt] integer (number of season in case of season thumb)

        v18 Python API changes: New function added.

        Example::

            listitem.addAvailableThumb(path_to_image_1, "1.77")

        """
        pass

    def addSeason(self, number, name=''):
        """
        Add a season with name to a listitem. It needs at least the season number

        Parameters:

        - number: int -- the number of the season.
        - name: string -- the name of the season. Default "".

        v18 Python API changes: New function added.

        Example::

            listitem.addSeason(1, 'Murder House-)

        """
        pass

    def getRating(self, key):
        """
        Returns a listitem rating as a float.

        Parameters:

        - key: string -- rating type.

        Some default key values (any string possible):

        =====  ==================
        Label  Type
        -----  ------------------
        imdb   string - type name
        tvdb   string - type name
        tmdb   string - type name
        anidb  string - type name
        =====  ==================
        """
        return float()

    def setRating(self, type, rating, votes=0, defaultt=False):
        """
        Sets a listitem's rating. It needs at least type and rating param

        Parameters:

        - type: string - the type of the rating. Any string.
        - rating: float - the value of the rating.
        - votes: int - the number of votes. Default 0.
        - defaultt: bool - is the default rating? Default: ``False``.

        Some default key values (any string possible):

        =====  ==================
        Label  Type
        -----  ------------------
        imdb   string - type name
        tvdb   string - type name
        tmdb   string - type name
        anidb  string - type name
        =====  ==================
        """

    def getVotes(self, key):
        """
        Returns a listitem votes as a integer.

        Parameters:

        - key: string - rating type.

        Some default key values (any string possible):

        =====  ==================
        Label  Type
        -----  ------------------
        imdb   string - type name
        tvdb   string - type name
        tmdb   string - type name
        anidb  string - type name
        =====  ==================

        Example::

            votes = listitem.getVotes('imdb')

        """
        return int()

    def setAvailableFanart(self, images):
        """
        Set available images (needed for scrapers)

        Parameters:

        - images: list of dictionaries (see below for relevant keys)

        Keys:

        ==========  ============================================================
        Label       Description
        ----------  ------------------------------------------------------------
        image       string (http://www.someurl.com/someimage.png)
        preview     [opt] string (http://www.someurl.com/somepreviewimage.png)
        colors      [opt] string (either comma separated Kodi hex values ("``FFFFFFFF,DDDDDDDD``")
                    or TVDB RGB Int Triplets ("``|68,69,59|69,70,58|78,78,68|``"))
        ==========  ============================================================

        v18 Python API changes: New function added.

        Example::

            fanart = [
                {"image": path_to_image_1, "preview": path_to_preview_1},
                {"image": path_to_image_2, "preview": path_to_preview_2}
                ]
            listitem.setAvailableFanart(fanart)

        """
        pass

    def setContentLookup(self, enable):
        """
        Enable or disable content lookup for item.

        If disabled, HEAD requests to e.g determine mime type will not be sent.

        :param enable:
        :type enable: bool

        v16 Python API changes: New function added.
        """
        pass


class ControlLabel(Control):

    """
    ControlLabel(x, y, width, height, label, font=None, textColor=None, disabledColor=None, alignment=0, hasPath=False, angle=0)

    ControlLabel class.

    Creates a text label.

    :param x: integer -- x coordinate of control.
    :param y: integer -- y coordinate of control.
    :param width: integer -- width of control.
    :param height: integer -- height of control.
    :param label: string or unicode -- text string.
    :param font: string -- font used for label text. (e.g. 'font13')
    :param textColor: hexstring -- color of enabled label's label. (e.g. '0xFFFFFFFF')
    :param disabledColor: hexstring -- color of disabled label's label. (e.g. '0xFFFF3300')
    :param alignment: integer -- alignment of label -- \*Note, see xbfont.h
    :param hasPath: bool -- True=stores a path / False=no path.
    :param angle: integer -- angle of control. (+ rotates CCW, - rotates CW)

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.label = xbmcgui.ControlLabel(100, 250, 125, 75, 'Status', angle=45)
    """

    def __init__(self, x, y, width, height, label,
                 font=None, textColor=None, disabledColor=None, alignment=0,
                 hasPath=False, angle=0):
        """
        :param x: integer -- x coordinate of control.
        :param y: integer -- y coordinate of control.
        :param width: integer -- width of control.
        :param height: integer -- height of control.
        :param label: string or unicode -- text string.
        :param font: string -- font used for label text. (e.g. 'font13')
        :param textColor: hexstring -- color of enabled label's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: hexstring -- color of disabled label's label. (e.g. '0xFFFF3300')
        :param alignment: integer -- alignment of label -- *Note, see xbfont.h
        :param hasPath: bool -- True=stores a path / False=no path.
        :param angle: integer -- angle of control. (+ rotates CCW, - rotates CW)

        .. note::
            After you create the control, you need to add it to the window with addControl().

        Example::

            self.label = xbmcgui.ControlLabel(100, 250, 125, 75, 'Status', angle=45)
        """
        pass

    def setLabel(self, label='', font=None, textColor=None, disabledColor=None, shadowColor=None,
                 focusedColor=None, label2=''):
        """Set's text for this label.

        :param label: string or unicode - text string.
        """
        pass

    def getLabel(self):
        """Returns the text value for this label."""
        return unicode()


class ControlFadeLabel(Control):

    """
    ControlFadeLabel(x, y, width, height, font=None, textColor=None, _alignment=0)

    Control which scrolls long label text.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param font: string - font used for label text. (e.g. 'font13')
    :param textColor: hexstring - color of fadelabel's labels. (e.g. '0xFFFFFFFF')
    :param _alignment: integer - alignment of label - \*Note, see xbfont.h

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.fadelabel = xbmcgui.ControlFadeLabel(100, 250, 200, 50, textColor='0xFFFFFFFF')
    """

    def __init__(self, x, y, width, height, font=None, textColor=None, _alignment=0):
        """
        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.
        :param width: integer - width of control.
        :param height: integer - height of control.
        :param font: string - font used for label text. (e.g. 'font13')
        :param textColor: hexstring - color of fadelabel's labels. (e.g. '0xFFFFFFFF')
        :param _alignment: integer - alignment of label - *Note, see xbfont.h

        .. note::
            After you create the control, you need to add it to the window with addControl().

        Example::

            self.fadelabel = xbmcgui.ControlFadeLabel(100, 250, 200, 50, textColor='0xFFFFFFFF')
        """
        pass

    def addLabel(self, label):
        """Add a label to this control for scrolling.

        :param label: string or unicode - text string.
        """
        pass

    def reset(self):
        """Clears this fadelabel."""
        pass


class ControlTextBox(Control):

    """
    ControlTextBox(x, y, width, height, font=None, textColor=None)

    ControlTextBox class.

    Creates a box for multi-line text.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param font: string - font used for text. (e.g. 'font13')
    :param textColor: hexstring - color of textbox's text. (e.g. '0xFFFFFFFF')

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.textbox = xbmcgui.ControlTextBox(100, 250, 300, 300, textColor='0xFFFFFFFF')
    """

    def __init__(self, x, y, width, height, font=None, textColor=None):
        """
        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.
        :param width: integer - width of control.
        :param height: integer - height of control.
        :param font: string - font used for text. (e.g. 'font13')
        :param textColor: hexstring - color of textbox's text. (e.g. '0xFFFFFFFF')

        .. note::
            After you create the control, you need to add it to the window with addControl().

        Example::

            self.textbox = xbmcgui.ControlTextBox(100, 250, 300, 300, textColor='0xFFFFFFFF')
        """
        pass

    def autoScroll(self, delay, time, repeat):
        """
        Set autoscrolling times.

        :param delay: integer - Scroll delay (in ms)
        :param time: integer - Scroll time (in ms)
        :param repeat: integer - Repeat time

        example::

            self.textbox.autoScroll(1, 2, 1)
        """
        pass

    def getText(self):
        """
        Returns the text value for this textbox.

        example::

            text = self.text.getText()
        """
        return unicode()

    def setText(self, text):
        """Set's the text for this textbox.

        :param text: string or unicode - text string.
        """
        pass

    def scroll(self, id):
        """Scrolls to the given position.

        :param id: integer - position to scroll to.
        """
        pass

    def reset(self):
        """Clear's this textbox."""
        pass


class ControlButton(Control):

    """
    ControlButton(x, y, width, height, label, focusTexture=None, noFocusTexture=None, textOffsetX=CONTROL_TEXT_OFFSET_X, textOffsetY=CONTROL_TEXT_OFFSET_Y, alignment=4, font=None, textColor=None, disabledColor=None, angle=0, shadowColor=None, focusedColor=None)

    ControlButton class.

    Creates a clickable button.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param label: string or unicode - text string.
    :param focusTexture: string - filename for focus texture.
    :param noFocusTexture: string - filename for no focus texture.
    :param textOffsetX: integer - x offset of label.
    :param textOffsetY: integer - y offset of label.
    :param alignment: integer - alignment of label - \*Note, see xbfont.h
    :param font: string - font used for label text. (e.g. 'font13')
    :param textColor: hexstring - color of enabled button's label. (e.g. '0xFFFFFFFF')
    :param disabledColor: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
    :param angle: integer - angle of control. (+ rotates CCW, - rotates CW)
    :param shadowColor: hexstring - color of button's label's shadow. (e.g. '0xFF000000')
    :param focusedColor: hexstring - color of focused button's label. (e.g. '0xFF00FFFF')

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.button = xbmcgui.ControlButton(100, 250, 200, 50, 'Status', font='font14')
    """

    def __init__(self, x, y, width, height, label, focusTexture=None, noFocusTexture=None,
                 textOffsetX=CONTROL_TEXT_OFFSET_X,
                 textOffsetY=CONTROL_TEXT_OFFSET_Y,
                 alignment=4,
                 font=None, textColor=None, disabledColor=None, angle=0,
                 shadowColor=None, focusedColor=None):
        """
        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.
        :param width: integer - width of control.
        :param height: integer - height of control.
        :param label: string or unicode - text string.
        :param focusTexture: string - filename for focus texture.
        :param noFocusTexture: string - filename for no focus texture.
        :param textOffsetX: integer - x offset of label.
        :param textOffsetY: integer - y offset of label.
        :param alignment: integer - alignment of label - *Note, see xbfont.h
        :param font: string - font used for label text. (e.g. 'font13')
        :param textColor: hexstring - color of enabled button's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
        :param angle: integer - angle of control. (+ rotates CCW, - rotates CW)
        :param shadowColor: hexstring - color of button's label's shadow. (e.g. '0xFF000000')
        :param focusedColor: hexstring - color of focused button's label. (e.g. '0xFF00FFFF')

        .. note::
            After you create the control, you need to add it to the window with addControl().

        Example::

            self.button = xbmcgui.ControlButton(100, 250, 200, 50, 'Status', font='font14')
        """
        pass

    def setDisabledColor(self, color):
        """Set's this buttons disabled color.

        :param color: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
        """
        pass

    def setLabel(self, label='', font=None, textColor=None, disabledColor=None, shadowColor=None,
                 focusedColor=None, label2=''):
        """Set's this buttons text attributes.

        :param label: string or unicode - text string.
        :param font: string - font used for label text. (e.g. 'font13')
        :param textColor: hexstring - color of enabled button's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
        :param shadowColor: hexstring - color of button's label's shadow. (e.g. '0xFF000000')
        :param focusedColor: hexstring - color of focused button's label. (e.g. '0xFFFFFF00')
        :param label2: string or unicode - text string.

        Example::

            self.button.setLabel('Status', 'font14', '0xFFFFFFFF', '0xFFFF3300', '0xFF000000')
        """
        pass

    def getLabel(self):
        """Returns the buttons label as a unicode string."""
        return unicode()

    def getLabel2(self):
        """Returns the buttons label2 as a unicode string."""
        return unicode()


class ControlList(Control):

    """
    ControlList(x, y, width, height, font=None, textColor=None, buttonTexture=None, buttonFocusTexture=None, selectedColor=None, _imageWidth=10, _imageHeight=10, _itemTextXOffset=10, _itemTextYOffset=2, _itemHeight=27, _space=2, _alignmentY=4)

    ControlList class.

    Creates a list of items.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param font: string - font used for items label. (e.g. 'font13')
    :param textColor: hexstring - color of items label. (e.g. '0xFFFFFFFF')
    :param buttonTexture: string - filename for no focus texture.
    :param buttonFocusTexture: string - filename for focus texture.
    :param selectedColor: integer - x offset of label.
    :param _imageWidth: integer - width of items icon or thumbnail.
    :param _imageHeight: integer - height of items icon or thumbnail.
    :param _itemTextXOffset: integer - x offset of items label.
    :param _itemTextYOffset: integer - y offset of items label.
    :param _itemHeight: integer - height of items.
    :param _space: integer - space between items.
    :param _alignmentY: integer - Y-axis alignment of items label - \*Note, see xbfont.h

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.cList = xbmcgui.ControlList(100, 250, 200, 250, 'font14', _space=5)
    """

    def __init__(self, x, y, width, height, font=None, textColor=None, buttonTexture=None,
                 buttonFocusTexture=None, selectedColor=None, _imageWidth=10, _imageHeight=10,
                 _itemTextXOffset=10, _itemTextYOffset=2,
                 _itemHeight=27, _space=2, _alignmentY=4):
        """
        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.
        :param width: integer - width of control.
        :param height: integer - height of control.
        :param font: string - font used for items label. (e.g. 'font13')
        :param textColor: hexstring - color of items label. (e.g. '0xFFFFFFFF')
        :param buttonTexture: string - filename for no focus texture.
        :param buttonFocusTexture: string - filename for focus texture.
        :param selectedColor: integer - x offset of label.
        :param _imageWidth: integer - width of items icon or thumbnail.
        :param _imageHeight: integer - height of items icon or thumbnail.
        :param _itemTextXOffset: integer - x offset of items label.
        :param _itemTextYOffset: integer - y offset of items label.
        :param _itemHeight: integer - height of items.
        :param _space: integer - space between items.
        :param _alignmentY: integer - Y-axis alignment of items label - *Note, see xbfont.h

        .. note::
            After you create the control, you need to add it to the window with addControl().

        Example::

            self.cList = xbmcgui.ControlList(100, 250, 200, 250, 'font14', _space=5)
        """
        pass

    def addItem(self, item, sendMessage=True):
        """Add a new item to this list control.

        :param item: string, unicode or ListItem - item to add.
        """
        pass

    def addItems(self, items):
        """Adds a list of listitems or strings to this list control.

        :param items: List - list of strings, unicode objects or ListItems to add.
        """
        pass

    def selectItem(self, item):
        """Select an item by index number.

        :param item: integer - index number of the item to select.
        """
        pass

    def reset(self):
        """Clear all ListItems in this control list."""
        pass

    def getSpinControl(self):
        """Returns the associated ControlSpin object.

        .. warning:: Not working completely yet.
            After adding this control list to a window it is not possible to change
            the settings of this spin control.
        """
        return ControlSpin()

    def setImageDimensions(self, imageWidth, imageHeight):
        """Sets the width/height of items icon or thumbnail.

        :param imageWidth: integer - width of items icon or thumbnail.
        :param imageHeight: integer - height of items icon or thumbnail.
        """
        pass

    def setItemHeight(self, itemHeight):
        """Sets the height of items.

        :param itemHeight: integer - height of items.
        """
        pass

    def setPageControlVisible(self, visible):
        """Sets the spin control's visible/hidden state.

        :param visible: boolean - True=visible / False=hidden.
        """
        pass

    def setSpace(self, space):
        """Set's the space between items.

        :param space: integer - space between items.
        """
        pass

    def getSelectedPosition(self):
        """Returns the position of the selected item as an integer.

        .. note:: Returns ``-1`` for empty lists.
        """
        return long()

    def getSelectedItem(self):
        """Returns the selected item as a ListItem object.

       .. note:: Same as ``getSelectedPosition()``, but instead of an integer a ``ListItem`` object is returned.
            Returns ``None`` for empty lists.
        """
        return ListItem()

    def size(self):
        """Returns the total number of items in this list control as an integer."""
        return long()

    def getListItem(self, index):
        """Returns a given ListItem in this List.

        :param index: integer - index number of item to return.

        :raises ValueError: If index is out of range.
        """
        return ListItem()

    def getItemHeight(self):
        """Returns the control's current item height as an integer."""
        return long()

    def getSpace(self):
        """Returns the control's space between items as an integer."""
        return long()

    def setStaticContent(self, items):
        """Fills a static list with a list of listitems.

        :param items: List - list of listitems to add.
        """
        pass

    def removeItem(self, index):
        """
        Remove an item by index number.

        :param index: integer - index number of the item to remove.

        example::

            my_list.removeItem(12)
        """
        pass


class ControlImage(Control):
    """
    ControlImage(x, y, width, height, filename, aspectRatio=0, colorDiffuse=None)

    ControlImage class.

    Displays an image from a file.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param filename: string - image filename.
    :param colorKey: hexString - (example, '0xFFFF3300')
    :param aspectRatio: integer - (values 0 = stretch (default), 1 = scale up (crops), 2 = scale down (black bars)
    :param colorDiffuse: hexString - (example, '0xC0FF0000' (red tint)).

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.image = xbmcgui.ControlImage(100, 250, 125, 75, aspectRatio=2)
    """

    def __init__(self, x, y, width, height, filename, aspectRatio=0, colorDiffuse=None):
        """
        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.
        :param width: integer - width of control.
        :param height: integer - height of control.
        :param filename: string - image filename.
        :param colorKey: hexString - (example, '0xFFFF3300')
        :param aspectRatio: integer - (values 0 = stretch (default), 1 = scale up (crops), 2 = scale down (black bars)
        :param colorDiffuse: hexString - (example, '0xC0FF0000' (red tint)).

        .. note::
            After you create the control, you need to add it to the window with addControl().

        Example::

            self.image = xbmcgui.ControlImage(100, 250, 125, 75, aspectRatio=2)
        """
        pass

    def setImage(self, imageFilename, useCache=True):
        """Changes the image.

        :param imageFilename: string - image filename.
        """
        pass

    def setColorDiffuse(self, hexString):
        """Changes the images color.

        :param hexString: - example -- '0xC0FF0000' (red tint).
        """
        pass


class ControlProgress(Control):

    """
    ControlProgress(self, x, y, width, height, texturebg=None, textureleft=None, texturemid=None, textureright=None, textureoverlay=None)

    ControlProgress class.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param texturebg: string - image filename.
    :param textureleft: string - image filename.
    :param texturemid: string - image filename.
    :param textureright: string - image filename.
    :param textureoverlay: string - image filename.

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.progress = xbmcgui.ControlProgress(100, 250, 125, 75)

    .. warning::
        This control seems to be broken. At least I couldn't make it work (Roman V.M.).
    """

    def __init__(self, x, y, width, height,
                 texturebg=None, textureleft=None,
                 texturemid=None, textureright=None,
                 textureoverlay=None):
        """
        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.
        :param width: integer - width of control.
        :param height: integer - height of control.
        :param texturebg: string - image filename.
        :param textureleft: string - image filename.
        :param texturemid: string - image filename.
        :param textureright: string - image filename.
        :param textureoverlay: string - image filename.

        .. note::
            After you create the control, you need to add it to the window with addControl().

        Example::

            self.progress = xbmcgui.ControlProgress(100, 250, 125, 75)
        """
        pass

    def setPercent(self, pct):
        """Sets the percentage of the progressbar to show.

        :param pct: float - percentage of the bar to show.

        .. note::
            Valid range for percent is 0-100.
        """
        pass

    def getPercent(self):
        """Returns a float of the percent of the progress."""
        return float()


class ControlSlider(Control):

    """
    ControlSlider(x, y, width, height, textureback=None, texture=None, texturefocus=None, orientation=VERTICAL)

    ControlSlider class.

    Creates a slider.

    :param x: integer -- x coordinate of control.
    :param y: integer -- y coordinate of control.
    :param width: integer -- width of control.
    :param height: integer -- height of control.
    :param textureback: string -- image filename.
    :param texture: string -- image filename.
    :param texturefocus: string -- image filename.
    :param orientation: int -- orientation of the slider

    .. note::
        By default a ControlSlider has vertical orientation.

    .. note::
        After you create the control, you need to add it to the window with addControl().

    Example::

        self.slider = xbmcgui.ControlSlider(100, 250, 350, 40)
    """

    def __init__(self, x, y, width, height, textureback=None, texture=None, texturefocus=None, orientation=VERTICAL):
        """
        :param x: integer -- x coordinate of control.
        :param y: integer -- y coordinate of control.
        :param width: integer -- width of control.
        :param height: integer -- height of control.
        :param textureback: string -- image filename.
        :param texture: string -- image filename.
        :param texturefocus: string -- image filename.
        :param orientation: int -- orientation of the slider

        .. note::
            After you create the control, you need to add it to the window with addControl().

        Example::

            self.slider = xbmcgui.ControlSlider(100, 250, 350, 40, orientation=xbmcgui.HORIZONTAL)
        """
        pass

    def getPercent(self):
        """Returns a float of the percent of the slider."""
        return float()

    def setPercent(self, percent):
        """Sets the percent of the slider.

        :param percent: float -- slider % value
        """
        pass


class ControlGroup(Control):

    """
    ControlGroup(x, y, width, height)

    ControlGroup class.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.

    Example::

        self.group = xbmcgui.ControlGroup(100, 250, 125, 75)
    """

    def __init__(self, x, y, width, height):
        """
        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.
        :param width: integer - width of control.
        :param height: integer - height of control.

        Example::

            self.group = xbmcgui.ControlGroup(100, 250, 125, 75)
        """
        pass


class ControlEdit(Control):

    """
    ControlEdit(self, x, y, width, height, label, font=None, textColor=None, disabledColor=None, _alignment=0, focusTexture=None, noFocusTexture=None, isPassword=False)

    ControlEdit class.

    :param x: integer - x coordinate of control.
    :param y: integer - y coordinate of control.
    :param width: integer - width of control.
    :param height: integer - height of control.
    :param label: string or unicode - text string.
    :param font: [opt] string - font used for label text. (e.g. 'font13')
    :param textColor: [opt] hexstring - color of enabled label's label. (e.g. '0xFFFFFFFF')
    :param disabledColor: [opt] hexstring - color of disabled label's label. (e.g. '0xFFFF3300')
    :param _alignment: [opt] integer - alignment of label - \*Note, see xbfont.h
    :param focusTexture: [opt] string - filename for focus texture.
    :param noFocusTexture: [opt] string - filename for no focus texture.
    :param isPassword: [opt] bool - if true, mask text value.

    .. note::
        You can use the above as keywords for arguments and skip certain optional arguments.
        Once you use a keyword, all following arguments require the keyword.
        After you create the control, you need to add it to the window with ``addControl()``.

    Example::

        self.edit = xbmcgui.ControlEdit(100, 250, 125, 75, 'Status')
    """

    def __init__(self, x, y, width, height, label, font=None, textColor=None,
                 disabledColor=None, _alignment=0,
                 focusTexture=None, noFocusTexture=None, isPassword=False):
        """
        :param x: integer - x coordinate of control.
        :param y: integer - y coordinate of control.
        :param width: integer - width of control.
        :param height: integer - height of control.
        :param label: string or unicode - text string.
        :param font: [opt] string - font used for label text. (e.g. 'font13')
        :param textColor: [opt] hexstring - color of enabled label's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: [opt] hexstring - color of disabled label's label. (e.g. '0xFFFF3300')
        :param _alignment: [opt] integer - alignment of label - *Note, see xbfont.h
        :param focusTexture: [opt] string - filename for focus texture.
        :param noFocusTexture: [opt] string - filename for no focus texture.
        :param isPassword: [opt] bool - if true, mask text value.

        .. note::
            You can use the above as keywords for arguments and skip certain optional arguments.
            Once you use a keyword, all following arguments require the keyword.
            After you create the control, you need to add it to the window with ``addControl()``.

        Example::

            self.edit = xbmcgui.ControlEdit(100, 250, 125, 75, 'Status')
        """
        pass

    def getLabel(self):
        """Returns the text heading for this edit control.

        example::

            label = self.edit.getLabel()
        """
        return unicode()

    def getText(self):
        """
        Returns the text value for this edit control.

        example::

            value = self.edit.getText()
        """
        return unicode()

    def setLabel(self, label='', font=None, textColor=None, disabledColor=None, shadowColor=None,
                 focusedColor=None, label2=''):
        """
        Set's text heading for this edit control.

        :param label: string or unicode - text string.

        example::

            self.edit.setLabel('Status')
        """
        pass

    def setText(self, text):
        """
        Set's text value for this edit control.

        :param text: - string or unicode - text string.

        example::

            self.edit.setText('online')
        """
        pass


class ControlRadioButton(Control):

    """
    ControlRadioButton class.
    Creates a radio-button with 2 states.
    """

    def __init__(self, x, y, width, height, label, focusTexture=None, noFocusTexture=None, textOffsetX=None,
                 textOffsetY=None, _alignment=None, font=None, textColor=None, disabledColor=None, angle=None,
                 shadowColor=None, focusedColor=None, focusOnTexture=None, noFocusOnTexture=None,
                 focusOffTexture=None, noFocusOffTexture=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        label: string or unicode - text string.
        focusTexture: string - filename for focus texture.
        noFocusTexture: string - filename for no focus texture.
        textOffsetX: integer - x offset of label.
        textOffsetY: integer - y offset of label.
        _alignment: integer - alignment of label - *Note, see xbfont.h
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of enabled radio button's label. (e.g. '0xFFFFFFFF')
        disabledColor: hexstring - color of disabled radio button's label. (e.g. '0xFFFF3300')
        angle: integer - angle of control. (+ rotates CCW, - rotates CW)
        shadowColor: hexstring - color of radio button's label's shadow. (e.g. '0xFF000000')
        focusedColor: hexstring - color of focused radio button's label. (e.g. '0xFF00FFFF')
        focusOnTexture: string - filename for radio focused/checked texture.
        noFocusOnTexture: string - filename for radio not focused/checked texture.
        focusOffTexture: string - filename for radio focused/unchecked texture.
        noFocusOffTexture: string - filename for radio not focused/unchecked texture.
        Note: To customize RadioButton all 4 abovementioned textures need to be provided.
        focus and noFocus textures can be the same.

        Note::
            After you create the control, you need to add it to the window with addControl().

        Example::
            self.radiobutton = xbmcgui.ControlRadioButton(100, 250, 200, 50, 'Status', font='font14')
        """
        pass

    def setSelected(self, selected):
        """Sets the radio buttons's selected status.

        :param selected: bool - True=selected (on) / False=not selected (off)
        """
        pass

    def isSelected(self):
        """Returns the radio buttons's selected status."""
        return bool(1)

    def setLabel(self, label, font=None, textColor=None, disabledColor=None, shadowColor=None, focusedColor=None):
        """Set's the radio buttons text attributes.

        :param label: string or unicode - text string.
        :param font: string - font used for label text. (e.g. 'font13')
        :param textColor: hexstring - color of enabled radio button's label. (e.g. '0xFFFFFFFF')
        :param disabledColor: hexstring - color of disabled radio button's label. (e.g. '0xFFFF3300')
        :param shadowColor: hexstring - color of radio button's label's shadow. (e.g. '0xFF000000')
        :param focusedColor: hexstring - color of focused radio button's label. (e.g. '0xFFFFFF00')

        Example::

            self.radiobutton.setLabel('Status', 'font14', '0xFFFFFFFF', '0xFFFF3300', '0xFF000000')
        """
        pass

    def setRadioDimension(self, x, y, width, height):
        """Sets the radio buttons's radio texture's position and size.

        :param x: integer - x coordinate of radio texture.
        :param y: integer - y coordinate of radio texture.
        :param width: integer - width of radio texture.
        :param height: integer - height of radio texture.

        Example::

            radiobutton.setRadioDimension(x=100, y=5, width=20, height=20)
        """
        pass


class ControlSpin(Control):
    """
    ControlSpin class.

    .. warning:: Not working yet.

    you can't create this object, it is returned by objects likeControlTextBox andControlList.
    """

    def setTextures(self, up, down, upFocus, downFocus):
        """
        setTextures(up, down, upFocus, downFocus)--Set's textures for this control.

        texture are image files that are used for example in the skin
        """
        pass


class Dialog(object):
    """
    Initializes Dialog instance.

    Then you need to call a method to open the respective dialog.
    """
    def browse(self, type, heading, s_shares, mask='', useThumbs=False, treatAsFolder=False, defaultt='',
               enableMultiple=False):
        """Show a 'Browse' dialog.

        :param type: integer - the type of browse dialog.
        :param heading: string or unicode - dialog heading.
        :param s_shares: string or unicode - from sources.xml. (i.e. 'myprograms')
        :param mask: string or unicode - '|' separated file mask. (i.e. '.jpg|.png')
        :param useThumbs: boolean - if True autoswitch to Thumb view if files exist.
        :param treatAsFolder: boolean - if True playlists and archives act as folders.
        :param defaultt: string - default path or file. Note the spelling of the argument name.
        :param enableMultiple: boolean - if True multiple file selection is enabled.

        Types::

            0: ShowAndGetDirectory
            1: ShowAndGetFile
            2: ShowAndGetImage
            3: ShowAndGetWriteableDirectory

        .. note::
            If enableMultiple is False (default): returns filename and/or path as a string
            to the location of the highlighted item, if user pressed 'Ok' or a masked item
            was selected. Returns the default value if dialog was canceled.

            If enableMultiple is True: returns tuple of marked filenames as a string,
            if user pressed 'Ok' or a masked item was selected. Returns empty tuple if dialog was canceled.

            If type is 0 or 3 the enableMultiple parameter is ignored.

        Example::

            dialog = xbmcgui.Dialog()
            fn = dialog.browse(3, 'XBMC', 'files', '', False, False, False, 'special://masterprofile/script_data/XBMC Lyrics')
        """
        return str()

    def browseMultiple(self, type, heading, shares, mask='', useThumbs=None, treatAsFolder=None, defaultt=''):
        """
        Show a 'Browse' dialog.

        :param type: integer - the type of browse dialog.
        :param heading: string or unicode - dialog heading.
        :param shares: string or unicode - from sources.xml. (i.e. 'myprograms')
        :param mask: [opt] string or unicode - '|' separated file mask. (i.e. '.jpg|.png')
        :param useThumbs: [opt] boolean - if True autoswitch to Thumb view if files exist (default=false).
        :param treatAsFolder: [opt] boolean - if True playlists and archives act as folders (default=false).
        :param defaultt: [opt] string - default path or file. Note the spelling of the argument name.

        Types::

            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage


        .. note::
            Returns tuple of marked filenames as a string,
            if user pressed 'Ok' or a masked item was selected. Returns empty tuple if dialog was canceled.

        Example::

            dialog = xbmcgui.Dialog()
            fn = dialog.browseMultiple(2, 'XBMC', 'files', '', False, False, 'special://masterprofile/script_data/XBMC Lyrics')
        """
        return tuple()

    def browseSingle(self, type, heading, shares, mask='', useThumbs=None, treatAsFolder=None, defaultt=''):
        """
        Show a 'Browse' dialog.

        :param type: integer - the type of browse dialog.
        :param heading: string or unicode - dialog heading.
        :param shares: string or unicode - from sources.xml. (i.e. 'myprograms')
        :param mask: [opt] string or unicode - '|' separated file mask. (i.e. '.jpg|.png')
        :param useThumbs: [opt] boolean - if True autoswitch to Thumb view if files exist (default=false).
        :param treatAsFolder: [opt] boolean - if True playlists and archives act as folders (default=false).
        :param defaultt: [opt] string - default path or file. Note the spelling of the argument name.

        Types::

            - 0 : ShowAndGetDirectory
            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage
            - 3 : ShowAndGetWriteableDirectory

        .. note:: Returns filename and/or path as a string to the location of the highlighted item,
            if user pressed 'Ok' or a masked item was selected.
            Returns the default value if dialog was canceled.

        Example::

            dialog = xbmcgui.Dialog()
            fn = dialog.browse(3, 'XBMC', 'files', '', False, False, 'special://masterprofile/script_data/XBMC Lyrics')
        """
        return str()

    def input(self, heading, defaultt='', type=INPUT_ALPHANUM, option=0, autoclose=0):
        """
        Show an Input dialog.

        :param heading: string -- dialog heading.
        :param defaultt: [opt] string -- default value. (default=empty string)
        :param type: [opt] integer -- the type of keyboard dialog. (default=xbmcgui.INPUT_ALPHANUM)
        :param option: [opt] integer -- option for the dialog. (see Options below)
        :param autoclose: [opt] integer -- milliseconds to autoclose dialog. (default=do not autoclose)

        Types:

        - xbmcgui.INPUT_ALPHANUM (standard keyboard)
        - xbmcgui.INPUT_NUMERIC (format: #)
        - xbmcgui.INPUT_DATE (format: DD/MM/YYYY)
        - xbmcgui.INPUT_TIME (format: HH:MM)
        - xbmcgui.INPUT_IPADDRESS (format: #.#.#.#)
        - xbmcgui.INPUT_PASSWORD (return md5 hash of input, input is masked)


        Options PasswordDialog: xbmcgui.PASSWORD_VERIFY (verifies an existing (default) md5 hashed password)
        Options AlphanumDialog: xbmcgui.ALPHANUM_HIDE_INPUT (masks input)


        .. note::
            Returns the entered data as a string.
            Returns an empty string if dialog was canceled.

        .. note::
            available since Gotham

        Example::

            dialog = xbmcgui.Dialog()
            d = dialog.input('Enter secret code', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        """
        return str()

    def numeric(self, type, heading, defaultt=''):
        """Show a 'Numeric' dialog.

        :param type: integer -- the type of numeric dialog.
        :param heading: string or unicode -- dialog heading.
        :param defaultt: string -- default value.

        Types::

            0: ShowAndGetNumber    (default format: #)
            1: ShowAndGetDate      (default format: DD/MM/YYYY)
            2: ShowAndGetTime      (default format: HH:MM)
            3: ShowAndGetIPAddress (default format: #.#.#.#)

        .. note::
            Returns the entered data as a string.
            Returns the default value if dialog was canceled.

        Example::

            dialog = xbmcgui.Dialog()
            d = dialog.numeric(1, 'Enter date of birth')
        """
        return str()

    def notification(self, heading, message, icon='', time=0, sound=True):
        """
        Show a Notification alert.

        :param heading: string -- dialog heading.
        :param message: string -- dialog message.
        :param icon: [opt] string -- icon to use. (default xbmcgui.NOTIFICATION_INFO)
        :param time: [opt] integer -- time in milliseconds (default 5000)
        :param sound: [opt] bool -- play notification sound (default True)

        Builtin Icons:

        - xbmcgui.NOTIFICATION_INFO
        - xbmcgui.NOTIFICATION_WARNING
        - xbmcgui.NOTIFICATION_ERROR

        example::

            dialog = xbmcgui.Dialog()
            dialog.notification('Movie Trailers', 'Finding Nemo download finished.', xbmcgui.NOTIFICATION_INFO, 5000)
        """
        pass

    def yesno(self, heading, line1, line2='', line3='', nolabel='', yeslabel='', autoclose=0):
        """Show a confirmation dialog 'YES/NO'.

        :param heading: string or unicode -- dialog heading.
        :param line1: string or unicode -- line #1 text.
        :param line2: string or unicode -- line #2 text.
        :param line3: string or unicode -- line #3 text.
        :param nolabel: label to put on the no button.
        :param yeslabel: label to put on the yes button.
        :param autoclose: [opt] integer -- milliseconds to autoclose dialog. (default=do not autoclose)

        .. note::
            Returns ``True`` if 'Yes' was pressed, else ``False``.

        Example::

            dialog = xbmcgui.Dialog()
            ret = dialog.yesno('XBMC', 'Do you want to exit this script?')
        """
        return bool(1)

    def ok(self, heading, line1, line2='', line3=''):
        """Show a dialog 'OK'.

        :param heading: string or unicode -- dialog heading.
        :param line1: string or unicode -- line #1 text.
        :param line2: string or unicode -- line #2 text.
        :param line3: string or unicode -- line #3 text.

        .. note::
            Returns ``True`` if 'Ok' was pressed, else ``False``.

        Example::

            dialog = xbmcgui.Dialog()
            ok = dialog.ok('XBMC', 'There was an error.')
        """
        return bool(1)

    def select(self, heading, list_, autoclose=0, preselect=-1):
        """Show a select dialog.

        :param heading: string or unicode -- dialog heading.
        :param list_: string list -- list of items.
        :param autoclose: integer -- milliseconds to autoclose dialog (optional).
        :param preselect: integer -- pre-selected item's index (optional)

        .. note::
            autoclose = 0 - This disables autoclose.
            Returns the position of the highlighted item as an integer.

        Example::

            dialog = xbmcgui.Dialog()
            ret = dialog.select('Choose a playlist', ['Playlist #1', 'Playlist #2, 'Playlist #3'])
        """
        return int()

    def contextmenu(self, list_):
        """
        Shows a context menu dialog

        :param list_: a :class:`list` of menu item labels
        :return: the index of a selected item or ``-1`` if nothing is selected

        Example::

            res = xbmcgui.Dialog().contextmenu(list=['option1', 'option2'])
        """
        return int()

    def textviewer(self, heading, text):
        """
        Show a dialog for viewing some text

        :param heading: dialog heading
        :param text: text to display.

        Example::

            dialog = xbmcgui.Dialog()
            dialog.textviewer('Plot', 'Some movie plot.')
        """
        pass

    def multiselect(self, heading, options, autoclose=0, preselect=None):
        """
        Show a multi-select dialog

        :param heading: dialog heading.
        :param options: options to choose from.
        :param autoclose: milliseconds to autoclose dialog. (default=do not autoclose)
        :param preselect: the list of pre-selected items' indices (optional)
        :return: the selected items as a list of indices, or ``None`` if cancelled.

        Example::

            dialog = xbmcgui.Dialog()
            ret = dialog.multiselect('Choose something', ['Foo', 'Bar', 'Baz'])
        """
        return list()

    def info(self, item):
        """
        Show the corresponding info dialog for a given listItem

        The type of a dialog is based on the ListItem InfoTag.

        :param item: ListItem instance
        :type item: ListItem
        :return: ``True`` if the info dialog is opened successfully
        :rtype: bool
        """
        return bool(1)


class DialogProgress(object):
    """
    Implements a modal progress dialog
    """
    def create(self, heading, line1='', line2='', line3=''):
        """Create and show a progress dialog.

        :param heading: string or unicode - dialog heading.
        :param line1: string or unicode - line #1 text.
        :param line2: string or unicode - line #2 text.
        :param line3: string or unicode - line #3 text.

        .. note::
            Use update() to update lines and progressbar.

        Example::

            pDialog = xbmcgui.DialogProgress()
            ret = pDialog.create('XBMC', 'Initializing script...')
        """
        pass

    def update(self, percent, line1='', line2='', line3=''):
        """Update's the progress dialog.

        :param percent: integer - percent complete. (0:100)
        :param line1: string or unicode - line #1 text.
        :param line2: string or unicode - line #2 text.
        :param line3: string or unicode - line #3 text.

        .. note::
            If percent == 0, the progressbar will be hidden.

        Example::

            pDialog.update(25, 'Importing modules...')
        """
        pass

    def iscanceled(self):
        """Returns ``True`` if the user pressed cancel."""
        return False

    def close(self):
        """Close the progress dialog."""
        pass


class DialogProgressBG(object):
    """
    Displays a small progress dialog in the corner of the screen.

    The dialog is not modal and does not block Kodi UI.
    """

    def close(self):
        """
        Close the background progress dialog

        example::

            pDialog.close()
        """
        pass

    def create(self, heading, message=''):
        """
        Create and show a background progress dialog.n

        :param heading: string or unicode - dialog heading
        :param message: [opt] string or unicode - message text

        .. note:: 'heading' is used for the dialog's id. Use a unique heading.
            Use update() to update heading, message and progressbar.

        example::

            pDialog = xbmcgui.DialogProgressBG()
            pDialog.create('Movie Trailers', 'Downloading Monsters Inc. ...')
        """
        pass

    def isFinished(self):
        """
        Returns ``True`` if the background dialog is active.

        example::

            if (pDialog.isFinished()):
                break
        """
        return bool(1)

    def update(self, percent=0, heading='', message=''):
        """
        Updates the background progress dialog.

        :param percent: [opt] integer - percent complete. (0:100)
        :param heading: [opt] string or unicode - dialog heading
        :param message: [opt] string or unicode - message text

        .. note:: To clear heading or message, you must pass a blank character.

        example::

            pDialog.update(25, message='Downloading Finding Nemo ...')
        """
        pass


class DialogBusy(object):
    """
    Provides "Busy" dialog for long running actions.

    .. note:: Added on Kodi v.17 (Krypton)
    """
    def create(self):
        """
        Create and show a busy dialog.

        .. note:: Use :meth:`DialogBusy.update` to update the progressbar.

        Example::

            dialog = xbmcgui.DialogBusy()
            dialog.create()
        """
        pass

    def update(self, percent):
        """
        Updates the busy dialog.

        :param percent: percent complete. (-1:100).
        :type percent: int

        .. note:: If percent == -1 (default), the progressbar will be hidden.
        """
        pass

    def close(self):
        """
        Close the progress dialog.
        """
        pass

    def iscanceled(self):
        """
        Checks if busy dialog is canceled.

        :return: ``True`` if the user pressed cancel.
        :rtype: bool
        """
        return bool(0)


class Action(object):
    """Action class.

    For backwards compatibility reasons the == operator is extended so that it
    can compare an action with other actions and action.GetID() with numbers.

    Example::

        if action == ACTION_MOVE_LEFT:
            do.something()
    """

    def getId(self):
        """Returns the action's current id as a long or 0 if no action is mapped in the xml's."""
        return long()

    def getButtonCode(self):
        """Returns the button code for this action."""
        return long()

    def getAmount1(self):
        """Returns the first amount of force applied to the thumbstick."""
        return float()

    def getAmount2(self):
        """Returns the second amount of force applied to the thumbstick."""
        return float()


def getCurrentWindowId():
    """
    Returns the id for the current 'active' window as an integer.

    example::

        wid = xbmcgui.getCurrentWindowId()
    """
    return long()


def getCurrentWindowDialogId():
    """
    Returns the id for the current 'active' dialog as an integer.

    example::

        wid = xbmcgui.getCurrentWindowDialogId()
    """
    return long()