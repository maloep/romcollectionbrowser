from util import Logutil as log
from rcbexceptions import *


class AbstractScraper(object):
    """Parent class for all scrapers.

    This class takes care of instantiating the relevant scraper based on name

    """
    _name = ''
    _path = ''
    #store instantiated scraper to avoid instantiating new scrapers for every game
    _instantiated_scrapers = {}

    # Mapping between scraper names in the config files and the corresponding scraper classes
    scrapers = {'thegamesdb.net': 'TheGamesDB_Scraper',
                'mobygames.com': 'Mobygames_Scraper',
                'giantbomb.com': 'GiantBomb_Scraper',
                'MAME': 'MAME_Scraper',
                'Game-database-info': 'Offline_GDBI_Scraper'}

    # Mapping between scraper names in the config files and the corresponding scraper classes
    online_scrapers = {'thegamesdb.net': 'TheGamesDB_Scraper',
                       'mobygames.com': 'Mobygames_Scraper',
                       'giantbomb.com': 'GiantBomb_Scraper'}

    offline_scrapers = {'MAME': 'MAME_Scraper',
                        'Game-database-info': 'Offline_GDBI_Scraper'}

    def __init__(self):
        pass

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def get_available_scrapers(self, platform=None):
        scrapers = self.get_available_online_scrapers(platform)
        scrapers.extend(self.get_available_offline_scrapers(platform))
        return scrapers

    def get_available_online_scrapers(self, platform=None):
        #TODO check which scraper supports which platform
        return list(self.online_scrapers.keys())

    def get_available_offline_scrapers(self, platform=None):
        #MAME scraper can only be used with MAME platform
        if platform != 'MAME' and platform != None:
            return [s for s in self.offline_scrapers.keys() if s != 'MAME']
        return self.offline_scrapers.keys()

    def get_scraper_by_name(self, sname):
        """Given a scraper name, returns the scraper class

        Args:
            sname: Name of the scraper, e.g. thegamesdb.net or MAME

        Raises:
            ConfigScraperSiteDoesNotExistException: No scraper matches the name

        """
        try:
            target = self.scrapers[sname]
        except KeyError:
            raise ConfigScraperSiteDoesNotExistException("Unsupported scraper: {0}".format(sname))

        #check if we already have instantiated this scraper
        instance = None
        try:
            instance = self._instantiated_scrapers[sname]
            log.debug("Using previously instantiated scraper class {0} - {1}".format(sname, target))
        except KeyError:
            pass

        if not instance:
            log.debug("Instantiating scraper class {0} - {1}".format(sname, target))
            try:
                module = __import__(target.lower())
                class_ = getattr(module, target)
                instance = class_()
                self._instantiated_scrapers[sname] = instance
            except ImportError:
                log.error("Unable to find scraper {0}".format(sname))
                raise

        return instance

    def search(self, gamename, platform=None):
        """Search for a game using the scraper. Implementation is left to the child class scrapers.

        Args:
            gamename: The name of the game to search for
            platform: Optionally specify the platform to restrict results to

        Returns:
            A list of dicts, each representing a different search result.

            Each dict should include the following fields:
            - id
            - title
            - releaseDate
            - SearchKey (which is the same as title, and kept for backwards-compatibility)

            In most cases, the id is used for the subsequent retrieve. The other 2 fields are used for display
            when selecting between different search results.

            The previous scrapers returned a list of dicts with SearchKey, e.g.
            [{'SearchKey': ['FIFA 98']}, {'SearchKey': ['FIFA 97']}, {'SearchKey': ['FIFA 2001']}]

        """
        return []

    def retrieve(self, gameid, platform):
        """Retrieve a game using the scraper using an ID captured during the search. As per search,
        implementation is left to the child class scrapers.

        Args:
            gameid: ID of the game to retrieve
            platform: Specify the platform to restrict results to

        Returns:
            A dict containing the game details. Currently, for backwards compatibility with the existing
            parser, each key field value should be a LIST, even where only 1 value exists.

            The following keys are used:
            Game
            Description
            Publisher
            Developer
            ReleaseYear
            Players
            etc
        """
        return {}
