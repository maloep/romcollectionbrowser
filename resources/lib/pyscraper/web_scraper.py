import re
import requests
from datetime import datetime
import time

from xbmcaddon import Addon

from scraper import AbstractScraper
from rcbexceptions import *
from util import Logutil as log


class WebScraper(AbstractScraper):
    _headers = {'User-Agent': 'RomCollectionBrowser {0}'.format(Addon().getAddonInfo('version'))}

    """ The following attributes are overridden in child web scrapers"""
    _apikey = ''
    _search_url = ''
    _retrieve_url = ''

    # Note - this needs to map to the order of the consoleDict array.
    pmaps = ['MobyGames.com', 'TheGamesDB.com', 'archive.vg', 'GiantBomb.com']

    # Mapping between the platform name in RCB and the platform identifier for the various web scrapers
    # FIXME Move to the appropriate scraper classes
    # consoleDict is the master list of all platforms that are supported by RCB. This list is also shown in configwizard to let the user select the platform
    consoleDict = {
        # name, mobygames-id, thegamesdb, archive vg, giantbomb
        'Other': ['0', '', '', ''],
        '3DO': ['35', '3DO', '3do', '26'],
        'Amiga': ['19', 'Amiga', 'amiga', '1'],
        'Amiga CD32': ['56', '', 'cd32'],
        'Amstrad CPC': ['60', 'Amstrad CPC', 'cpc'],
        'Apple II': ['31', '', 'appleii'],
        'Atari 2600': ['28', 'Atari 2600', 'atari2600', '40'],
        'Atari 5200': ['33', 'Atari 5200', 'atari5200'],
        'Atari 7800': ['34', 'Atari 7800', 'atari7800'],
        'Atari 8-bit': ['39', '', 'atari8bit'],
        'Atari ST': ['24', '', 'ast'],
        'BBC Micro': ['92', '', 'bbc', '110'],
        'BREW': ['63', '', ''],
        'CD-i': ['73', '', 'cdi'],
        'Channel F': ['76', '', 'channelf'],
        'ColecoVision': ['29', 'Colecovision', 'colecovision'],
        'Commodore 128': ['61', '', '', '58'],
        'Commodore 64': ['27', 'Commodore 64', 'c64', '14'],
        'Commodore PET/CBM': ['77', '', 'pet'],
        'DoJa': ['72', '', ''],
        'DOS': ['2', '', '', '94'],
        'Dragon 32/64': ['79', '', '', '61'],
        'Dreamcast': ['8', 'Sega Dreamcast', 'dreamcast', '37'],
        'Electron': ['93', '', '', '110'],
        'ExEn': ['70', '', ''],
        'Game Boy': ['10', 'Nintendo Gameboy', 'gameboy', '3'],
        'Game Boy Advance': ['12', 'Nintendo Game Boy Advance', 'gba', '4'],
        'Game Boy Color': ['11', 'Nintendo Game Boy Color', 'gbc', '57'],
        'GameCube': ['14', 'Nintendo GameCube', 'gamecube', '23'],
        'Game Gear': ['25', 'Sega Game Gear', 'gamegear', '5'],
        'Genesis': ['16', 'Sega Genesis', 'genesis', '6', '31'],
        'Gizmondo': ['55', '', 'gizmondo'],
        'Intellivision': ['30', 'Intellivision', 'intellivision'],
        'Jaguar': ['17', 'Atari Jaguar', 'jaguar', '28'],
        'Linux': ['1', '', ''],
        'Lynx': ['18', '', 'lynx', '7'],
        'Macintosh': ['74', 'Mac OS', '', '17'],
        'MAME': ['0', 'Arcade', ''],
        'Mophun': ['71', '', ''],
        'MSX': ['57', '', 'msx'],
        'Neo Geo': ['36', 'NeoGeo', 'neo'],
        'Neo Geo CD': ['54', '', 'neogeocd'],
        'Neo Geo Pocket': ['52', '', ''],
        'Neo Geo Pocket Color': ['53', '', 'ngpc'],
        'NES': ['22', 'Nintendo Entertainment System (NES)', 'nes', '21'],
        'N-Gage': ['32', '', 'ngage', '34'],
        'Nintendo 64': ['9', 'Nintendo 64', 'n64', '43'],
        'Nintendo DS': ['44', 'Nintendo DS', '', '52'],
        'Nintendo DSi': ['87', '', '', '52'],
        'Odyssey': ['75', '', 'odyssey', '74'],
        'Odyssey 2': ['78', '', 'odyssey2'],
        'PC-88': ['94', '', 'pc88'],
        'PC-98': ['95', '', 'pc98', '112'],
        'PC Booter': ['4', '', '', '94'],
        'PC-FX': ['59', '', 'pcfx'],
        'PlayStation': ['6', 'Sony Playstation', 'ps', '22'],
        'PlayStation 2': ['7', 'Sony Playstation 2', 'ps2', '19'],
        'PlayStation 3': ['81', 'Sony Playstation 3', '35'],
        'PSP': ['46', 'Sony PSP', '', '18'],
        'SEGA 32X': ['21', 'Sega 32X', 'sega32x'],
        'SEGA CD': ['20', 'Sega CD', 'segacd'],
        'SEGA Master System': ['26', 'Sega Master System', 'sms'],
        'SEGA Saturn': ['23', 'Sega Saturn', 'saturn', '42'],
        'SNES': ['15', 'Super Nintendo (SNES)', 'snes', '9'],
        'Spectravideo': ['85', '', ''],
        'TI-99/4A': ['47', '', 'ti99'],
        'TRS-80': ['58', '', ''],
        'TRS-80 CoCo': ['62', '', '', '68'],
        'TurboGrafx-16': ['40', 'TurboGrafx 16', 'tg16'],
        'TurboGrafx CD': ['45', '', ''],
        'Vectrex': ['37', '', 'vectrex'],
        'VIC-20': ['43', '', 'vic20', '30'],
        'Virtual Boy': ['38', 'Nintendo Virtual Boy', 'virtualboy'],
        'V.Smile': ['42', '', ''],
        'Wii': ['82', 'Nintendo Wii', '', '36'],
        'Windows': ['3', 'PC', '', '94'],
        'Windows 3.x': ['5', '', '', '94'],
        'WonderSwan': ['48', '', 'wonderswan'],
        'WonderSwan Color': ['49', '', ''],
        'Xbox': ['13', 'Microsoft Xbox', 'xbox'],
        'Xbox 360': ['69', 'Microsoft Xbox 360', ''],
        'Zeebo': ['88', '', ''],
        'Zodiac': ['68', '', 'zod'],
        'ZX Spectr': ['41', 'Sinclair ZX Spectrum', '']}

    def __init__(self):
        pass

    def prepare_gamename_for_request(self, gamename):
        """Some websites (giantbomb and MobyGames) don't handle special characters in game search requests very well. Strip
        out anything after a special character

        Args:
        	gamename: e.g. My Game Name (1984) [cr TCS]

        Returns:
        	Game name without any suffix, e.g. My Game Name
        """
        pattern = r"[^:,\-[(]*"     # Match anything until : , - [ or (
        return re.search(pattern, gamename).group(0).strip().replace("'", "")

    def get_platform_for_scraper(self, platformname):
        """Get the platform identifier used on the corresponding website.

        Args:
        	platformname: The RCB platform name

        Returns:
        	String that is the identifier for the platform on the corresponding website.

        """
        try:
            ix = self.pmaps.index(self._name)
        except ValueError as e:
            # Did not find a mapping
            log.warn("Did not find a platform mapping for {0}".format(self._name))
            ix = 0

        return self.consoleDict[platformname][ix]

    def open_json_url(self, **kwargs):
        try:
            r = requests.get(kwargs['url'], headers=self._headers, params=kwargs['params'])
        except ValueError as e:
            # Typically non-JSON response
            raise ScraperUnexpectedContentException("Non-JSON response received")

        log.debug(u"Retrieving {0} as JSON - HTTP{1}".format(r.url, r.status_code))

        if r.status_code == 401:
            # Mobygames and GiantBomb send a 401 if the API key is invalid
            raise ScraperUnauthorisedException("Invalid API key sent")

        if r.status_code == 429:
            raise ScraperExceededAPIQuoteException("Scraper exceeded API key limits")

        if r.status_code == 500:
            raise ScraperWebsiteUnavailableException("Website unavailable")

        return r.json()

    def open_xml_url(self, **kwargs):
        print 'Retrieving url ' + kwargs['url']

        r = requests.get(kwargs['url'], headers=self._headers, params=kwargs['params'])

        log.debug(u"Retrieving {0} as XML - HTTP{1}".format(r.url, r.status_code))

        # Need to ensure we are sending back Unicode text
        return r.text.encode('utf-8')

    def _parse_date(self, datestr):
        """Extract the year from a given date string using a given format. This function is used to cater for
        an edge case identified in https://forum.kodi.tv/showthread.php?tid=112916&pid=1214507#pid1214507.

        Args:
        	datestr: Input date

        Returns:
            Year as a %Y format string
        """
        if datestr is None:
            return '1970'

        x = None
        for fmt2 in ["%Y-%m-%d", "%Y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"]:
            try:
                x = datetime.strptime(datestr, fmt2).strftime("%Y")
            except ValueError as e:
                # Skip to the next format
                pass
            except TypeError as e:
                log.warn("Unable to parse date using strptime, falling back to time function")
                try:
                    x = datetime(*(time.strptime(datestr, fmt2)[0:6]))
                except ValueError as ve:
                    log.warn("Unable to parse date using %s, try next format." %fmt2)
        if x is not None:
            return x
        else:
            log.warn(u"Unexpected date format: {0}".format(datestr))
            return u"1970"

