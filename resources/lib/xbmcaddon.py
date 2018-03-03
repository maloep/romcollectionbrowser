# coding: utf-8
"""
A class to access addon properties
"""

import os

__author__ = 'Team Kodi <http://kodi.tv>'
__credits__ = 'Team Kodi'
__date__ = 'Fri May 01 16:22:07 BST 2015'
__platform__ = 'ALL'
__version__ = '2.20.0'


_settings = {'rcb_logLevel': 2,
             'rcb_fuzzyFactor': '3',
            'rcb_enableFullReimport': 'true',
            'rcb_createNfoWhileScraping': 'false',
            'rcb_overwriteWithNullvalues': 'false',
            'rcb_ignoreGamesWithoutDesc': 'false',
            'rcb_ignoreGamesWithoutArtwork': 'false',
            'rcb_scrapingMode': 'Automatic: Accurate',
            # Interact with cut-down MAME history dat file in the unittests
            'rcb_MAMEDescriptionFilePath': 'testdata/scraper_web_responses/history.dat'}


class Addon(object):
    """
    Addon(id=None)

    Creates a new Addon class.

    :param id: string - id of the addon (autodetected in XBMC Eden)

    Example::

        self.Addon = xbmcaddon.Addon(id='script.recentlyadded')
    """
    def __init__(self, id=None):
        """Creates a new Addon class.

        :param id: string - id of the addon (autodetected in XBMC Eden)

        Example::

            self.Addon = xbmcaddon.Addon(id='script.recentlyadded')
        """
        pass

    def getLocalizedString(self, id):
        """Returns an addon's localized 'unicode string'.

        :param id: integer - id# for string you want to localize.

        Example::

            locstr = self.Addon.getLocalizedString(id=6)
        """
        return unicode()

    def getSetting(self, id):
        """Returns the value of a setting as a unicode string.

        :param id: string - id of the setting that the module needs to access.

        Example::

            apikey = self.Addon.getSetting('apikey')
        """
        global _settings
        if _settings.has_key(id):
            return _settings[id]


    def setSetting(self, id, value):
        """Sets a script setting.

        :param id: string - id of the setting that the module needs to access.
        :param value: string or unicode - value of the setting.

        Example::

            self.Settings.setSetting(id='username', value='teamxbmc')
        """
        pass

    def openSettings(self):
        """Opens this scripts settings dialog."""
        pass

    def getAddonInfo(self, id):
        """Returns the value of an addon property as a string.

        :param id: string - id of the property that the module needs to access.

        .. note::
            Choices are (author, changelog, description, disclaimer, fanart, icon, id, name, path,
            profile, stars, summary, type, version)

        Example::

            version = self.Addon.getAddonInfo('version')
        """
        print 'getAddonInfo called with key: ' + str(id)

        if(id == 'path'):
            basepath = os.getcwd()
            path = os.path.join(basepath, "..\..")
            print 'path = ' + str(path)
            return path
        
            return 'dummy'
