import requests
from datetime import datetime
import time

from xbmcaddon import Addon

from scraper import AbstractScraper
from rcbexceptions import *
from util import Logutil as log
from util import __addon__


class WebScraper(AbstractScraper):
    _headers = {'User-Agent': 'RomCollectionBrowser {0}'.format(__addon__.getAddonInfo('version'))}

    """ The following attributes are overridden in child web scrapers"""
    _apikey = ''
    _search_url = ''
    _retrieve_url = ''

    # Note - this needs to map to the order of the consoleDict array.
    pmaps = ['MobyGames.com', 'thegamesdb.net', 'GiantBomb.com']

    # Mapping between the platform name in RCB and the platform identifier for the various web scrapers
    # FIXME Move to the appropriate scraper classes
    # consoleDict is the master list of all platforms that are supported by RCB. This list is also shown in configwizard to let the user select the platform
    consoleDict = {
        # name, mobygames-id, thegamesdb, giantbomb
        'Other': ['0', '', ''],
        '3DO': ['35', '3DO', '26'],
        'Acorn 32-bit': ['117', '', ''],
        'Acorn Archimedes': ['', 'Acorn Archimedes', '125'],
        'Acorn Electron': ['', 'Acorn Electron', ''],
        'Action Max': ['', 'Action Max', '148'],
        'Alice 32/90': ['194', '', ''],
        'Amiga': ['19', 'Amiga', '1'],
        'Amiga CD32': ['56', 'Amiga CD32', '39'],
        'Amstrad CPC': ['60', 'Amstrad CPC', '11'],
        'Amstrad PCW': ['136', '', ''],
        'Android': ['91', 'Android', '123'],
        'APF MP1000': ['213', 'APF MP-1000', ''],
        'Apple II': ['31', 'Apple II', '12'],
        'Atari 2600': ['28', 'Atari 2600', '40'],
        'Atari 5200': ['33', 'Atari 5200', '67'],
        'Atari 7800': ['34', 'Atari 7800', '70'],
        'Atari 8-bit': ['39', 'Atari 800', '24'],
        #'Atari Jaguar': ['17', 'Atari Jaguar', '28'],
        'Atari Jaguar CD': ['17', 'Atari Jaguar CD', '171'],
        #'Atari Lynx': ['18', 'Atari Lynx', '7'],
        'Atari ST': ['24', 'Atari ST', '13'],
        'Atari XE': ['', 'Atari XE', ''],
        'Bally Astrocade': ['160', 'Bally Astrocade', '120'],
        'BBC Micro': ['92', '', '110'],
        'BREW': ['63', '', ''],
        'Casio Loopy': ['124', '', '126'],
        'Casio PV-1000': ['125', 'Casio PV-1000', '149'],
        'CD-i': ['73', 'Philips CD-i', '27'],
        'Channel F': ['76', 'Fairchild Channel F', '66'],
        'Coleco Adam': ['156', '', ''],
        'ColecoVision': ['29', 'Colecovision', '47'],
        'Commodore 16': ['115', '', '150'],
        'Commodore 64': ['27', 'Commodore 64', '14'],
        'Commodore 128': ['61', 'Commodore 128', '58'],
        'Commodore PET/CBM': ['77', '', '62'],
        #'Commodore VIC20': ['43', 'Commodore VIC-20', '30'],
        'DoJa': ['72', '', ''],
        'DOS': ['2', '', '94'],
        'Dragon 32/64': ['79', 'Dragon 32/64', '61'],
        'Dreamcast': ['8', 'Sega Dreamcast', '37'],
        'Electron': ['93', '', '110'],
        'Entex Adventure Vision': ['210', 'Entex Adventure Vision', '93'],
        'Epoch Cassette Vision': ['137', 'Epoch Cassette Vision', '135'],
        'Epoch Super Cassette Vision': ['138', 'Epoch Super Cassette Vision', '136'],
        'ExEn': ['70', '', ''],
        'Famicom Disk System': ['', 'Famicom Disk System', '91'],
        'FM-7': ['126', 'Fujitsu FM-7', '114'],
        'FM Towns': ['102', 'FM Towns Marty', '108'],
        'Game Boy': ['10', 'Nintendo Gameboy', '3'],
        'Game Boy Advance': ['12', 'Nintendo Game Boy Advance', '4'],
        'Game Boy Color': ['11', 'Nintendo Game Boy Color', '57'],
        'Game.Com': ['50', 'Game.Com', '77'],
        'GameCube': ['14', 'Nintendo GameCube', '23'],
        'Game Gear': ['25', 'Sega Game Gear', '5'],
        'Game Wave': ['104', '', '105'],
        'Genesis': ['16', 'Sega Genesis', '6', '31'],
        'Gizmondo': ['55', '', '78'],
        'HyperScan': ['192', '', '104'],
        'Intellivision': ['30', 'Intellivision', '51'],
        'Jaguar': ['17', 'Atari Jaguar', '28'],
        'LaserActive': ['163', 'Pioneer LaserActive', '92'],
        'Leapfrog Didj': ['184', '', '144'],
        'Leapster': ['183', '', '89'],
        'Linux': ['1', '', '152'],
        'Lynx': ['18', 'Atari Lynx', '7'],
        'Macintosh': ['74', 'Mac OS', '17'],
        'MAME': ['0', 'Arcade', '84'],
        'Mega Duck': ['', 'Mega Duck', '137'],
        'Microbee': ['200', '', '168'],
        'Microvision': ['97', 'Milton Bradley Microvision', '90'],
        'Mophun': ['71', '', ''],
        'MSX': ['57', 'MSX', '15'],
        'Neo Geo': ['36', 'NeoGeo', '25'],
        'Neo Geo CD': ['54', 'Neo Geo CD', '59'],
        'Neo Geo Pocket': ['52', 'Neo Geo Pocket', '80'],
        'Neo Geo Pocket Color': ['53', 'Neo Geo Pocket Color', '81'],
        'NES': ['22', 'Nintendo Entertainment System (NES)', '21'],
        'N-Gage': ['32', 'N-Gage', '34'],
        'Nintendo 3DS': ['101', 'Nintendo 3DS', '117'],
        'Nintendo 64': ['9', 'Nintendo 64', '43'],
        'Nintendo DS': ['44', 'Nintendo DS', '52'],
        'Nintendo DSi': ['87', '', '52'],
        'Nintendo Switch': ['203', 'Nintendo Switch', '157'],
        'Nuon': ['116', 'Nuon', '85'],
        'Odyssey': ['75', 'Magnavox Odyssey 1', '74'],
        'Odyssey 2': ['78', 'Magnavox Odyssey 2', '60'],
        'Ouya': ['144', 'Ouya', '154'],
        'PC-6001': ['149', '', '115'],
        'PC-88': ['94', 'PC-88', '109'],
        'PC-98': ['95', 'PC-98', '112'],
        'PC Booter': ['4', '', '94'],
        'PC Engine SuperGrafX': ['127', '', '119'],
        'PC-FX': ['59', 'PC-FX', '75'],
        'Pippin': ['112', '', '102'],
        'PlayStation': ['6', 'Sony Playstation', '22'],
        'PlayStation 2': ['7', 'Sony Playstation 2', '19'],
        'PlayStation 3': ['81', 'Sony Playstation 3', '35'],
        'PlayStation 4': ['141', 'Sony Playstation 4', '146'],
        'Playdia': ['107', '', '127'],
        'Pokemon mini': ['152', 'Nintendo Pokemon Mini', '134'],
        'PSP': ['46', 'Sony PSP', '18'],
        'PS Vita': ['105', 'Sony Playstation Vita', '129'],
        'RCA Studio II': ['113', 'RCA Studio II', '131'],
        'SAM Coupe': ['120', 'SAM Coupe', '162'],
        'SEGA 32X': ['21', 'Sega 32X', '31'],
        'SEGA CD': ['20', 'Sega CD', '29'],
        'SEGA Master System': ['26', 'Sega Master System', '8'],
        'SEGA Pico': ['103', 'Sega Pico', '118'],
        'SEGA Saturn': ['23', 'Sega Saturn', '42'],
        'SEGA SG-1000': ['114', 'SEGA SG-1000', '141'],
        'Sharp X1': ['121', 'Sharp X1', '113'],
        'Sharp X68000': ['106', 'Sharp X68000', '95'],
        'Sharp MZ-80B/2000/2500': ['182', '', '128'],
        'Sharp MZ-80K/700/800/1500': ['181', '', '128'],
        'Socrates': ['190', '', '169'],
        'SNES': ['15', 'Super Nintendo (SNES)', '9'],
        'Spectravideo': ['85', '', ''],
        "Super A'can": ['110', '', '151'],
        'Supervision': ['109', 'Watara Supervision', '147'],
        'TI-99/4A': ['47', 'Texas Instruments TI-99/4A', '48'],
        'Tomy Tutor': ['151', 'Tomy Tutor', '165'],
        'TRS-80': ['58', '', '63'],
        'TRS-80 CoCo': ['62', 'TRS-80 Color Computer', '68'],
        'TurboGrafx-16': ['40', 'TurboGrafx 16', '55'],
        'TurboGrafx CD': ['45', 'TurboGrafx CD', '53'],
        'Vectrex': ['37', 'Vectrex', '76'],
        'VIC-20': ['43', 'Commodore VIC-20', '30'],
        'Virtual Boy': ['38', 'Nintendo Virtual Boy', '79'],
        'V.Smile': ['42', '', '82'],
        'Wii': ['82', 'Nintendo Wii', '36'],
        'Wii U': ['132', 'Nintendo Wii U', '139'],
        'Windows': ['3', 'PC', '94'],
        'Windows 3.x': ['5', '', '94'],
        'WonderSwan': ['48', 'WonderSwan', '65'],
        'WonderSwan Color': ['49', 'WonderSwan Color', '54'],
        'Xbox': ['13', 'Microsoft Xbox', '32'],
        'Xbox 360': ['69', 'Microsoft Xbox 360', '20'],
        'Xbox One': ['142', 'Microsoft Xbox One', '145'],
        'Zeebo': ['88', '', '122'],
        'Zodiac': ['68', '', '64'],
        'ZX Spectr': ['41', 'Sinclair ZX Spectrum', '16']}

    def __init__(self):
        pass

    def get_platform_for_scraper(self, platformname):
        """Get the platform identifier used on the corresponding website.

        Args:
            platformname: The RCB platform name

        Returns:
            String that is the identifier for the platform on the corresponding website.

        """
        try:
            ix = self.pmaps.index(self._name)
        except ValueError:
            # Did not find a mapping
            log.warn("Did not find a platform mapping for {0}".format(self._name))
            ix = 0

        return self.consoleDict[platformname][ix]

    def open_json_url(self, **kwargs):
        log.info('Retrieving url %s, params = %s' %(kwargs['url'], kwargs['params']))
        
        try:
            r = requests.get(kwargs['url'], headers=self._headers, params=kwargs['params'])
        except ValueError:
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
        log.info('Retrieving url %s, params = %s' %(kwargs['url'], kwargs['params']))

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
        for fmt2 in ["%Y-%m-%d", "%Y-%m", "%Y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"]:
            try:
                x = datetime.strptime(datestr, fmt2).strftime("%Y")
                break
            except ValueError as e:
                # Skip to the next format
                log.warn("ValueError in parseDate: %s" %e)
            except TypeError:
                log.warn("Unable to parse date using strptime, falling back to time function")
                try:
                    x = datetime(*(time.strptime(datestr, fmt2)[0:6])).strftime("%Y")
                    break
                except ValueError as ve:
                    log.warn("Unable to parse date %s using %s, try next format. %s" %(datestr, fmt2, ve))

        if x is not None:
            return x
        else:
            log.warn(u"Unexpected date format: {0}".format(datestr))
            return u"1970"

