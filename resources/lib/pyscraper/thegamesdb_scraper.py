from __future__ import absolute_import
import sys
import xml.etree.ElementTree as ET
from web_scraper import WebScraper
from util import Logutil as log
from gamename_utils import GameNameUtil


# FIXME TODO Exception handling (i.e. no games found)


class TheGamesDB_Scraper(WebScraper):
    """TheGamesDB.net has its API described at https://api.thegamesdb.net/
    """
    _name = 'thegamesdb.net'
    _search_url = 'https://api.thegamesdb.net/v1/Games/ByGameName'
    _genres_url = 'https://api.thegamesdb.net/v1/Genres'
    _developers_url = 'https://api.thegamesdb.net/v1/Developers'
    _publishers_url = 'https://api.thegamesdb.net/v1/Publishers'
    _images_url = 'https://api.thegamesdb.net/v1/Games/Images'
    #_retrieve_url = 'http://thegamesdb.net/api/GetGame.php'
    _api_key = '1e821bf1bab06854840650d77e7e2248f49583821ff9191f2cced47e43bf0a73'
    _fields = 'id,game_title,release_date,developers,publishers,players,genres,overview,rating'
    _include = 'boxart'

    # Mapping between the dict keys and the json fields in the response
    _game_mapping = {
        'Game': 'game_title',
        'Description': 'overview',
        'Players': 'players'
    }

    # This is only used to persist data between the search and retrieve as the search request already returns
    # a complete game with all details
    resultdata = {}

    # store genres, developers and publishers during the scrape process
    genres = {}
    developers = {}
    publishers = {}

    def __init__(self):
        pass

    def _get_search_url(self):
        return self._search_url

    def _get_search_params(self, **kwargs):
        return {'name': GameNameUtil().prepare_gamename_for_searchrequest(kwargs['gamename']),
                'filter[platform]': self.get_platform_for_scraper(kwargs['platform']),
                'apikey': self._api_key,
                'fields': self._fields,
                'include': self._include}

    def _get_apikey_param(self):
        return {'apikey': self._api_key}

    def _get_images_params(self, gameid):
        return {'games_id': gameid,
            'apikey': self._api_key}

    def _get_retrieve_url(self):
        return ''

    def _get_retrieve_params(self, **kwargs):
        return {}

    def search(self, gamename, platform=None):
        """ https://api.thegamesdb.net/ """
        response = self.open_json_url(url=self._get_search_url(),
                                     params=self._get_search_params(gamename=gamename, platform=platform))

        result = self._parseSearchResults(response)
        return result

    def retrieve(self, gameid, platform):

        if len(self.genres) == 0:
            self.genres = self.open_json_url(url=self._genres_url, params=self._get_apikey_param())
        if len(self.developers) == 0:
            self.developers = self.open_json_url(url=self._developers_url, params=self._get_apikey_param())
        if len(self.publishers) == 0:
            self.publishers = self.open_json_url(url=self._publishers_url, params=self._get_apikey_param())

        results = self._parseGameResult(self.resultdata[int(gameid)])

        images = self.open_json_url(url=self._images_url, params=self._get_images_params(gameid))
        image_results = self._parse_image_result(images, gameid)

        results.update(image_results)

        return results

    def _parseSearchResults(self, response):
        """
        Parse the json response from the Games/ByGameName API call
        Returns a list of dicts with id, title and releaseDate
        """
        results = []

        code = response['code']
        status = response['status']

        if code != 200 or status != "Success":
            log.error("thegamesdb returned an error. Code = %s, Status = %s" %(code, status))
            return results

        data = response['data']
        self.resultdata = {}

        for result in data['games']:
            results.append({'id': result['id'],
                            'title': result['game_title'],
                            'releaseDate': result['release_date'],
                            'SearchKey': [result['game_title']]})
            #store result for later use in retrieve method
            self.resultdata[result['id']] = result

        log.info(u"Found {0} results using json response: {1}".format(len(results), results))

        return results

    def _parseGameResult(self, game):
        result = {}

        # Standard fields
        for k, v in self._game_mapping.items():
            # HACK - This is only used to retain backwards compatibility with existing scraper, where each key value was a
            # list, even if only one value is in that list
            try:
                result[k] = [game[v]]
            except Exception:
                # Typically this result doesn't have this field
                log.debug("Unable to extract data from key {0}".format(k))

        # Custom fields
        # Adjust the date
        releaseDate = game['release_date']
        if releaseDate is not None:
            result['ReleaseYear'] = [self._parse_date(releaseDate)]

        result['Genre'] = self._parse_lookup_data(game['genres'], self.genres['data']['genres'])
        result['Developer'] = self._parse_lookup_data(game['developers'], self.developers['data']['developers'])
        result['Publisher'] = self._parse_lookup_data(game['publishers'], self.publishers['data']['publishers'])



        """
        # Prefix images with base url
        for image in ['fanart', 'boxfront', 'boxback', 'screenshot', 'clearlogo']:
            try:
                result['Filetype' + image] = ["http://thegamesdb.net/banners/" + result['Filetype' + image][0]]
            except KeyError:
                log.warn("Image type {0} not present in retrieve results".format(image))
        """
        return result

    def _parse_image_result(self, images, gameid):

        result = {}
        base_url = ''
        for image_size in ['large', 'medium', 'original']:
            try:
                base_url = images['data']['base_url'][image_size]
                break
            except KeyError:
                pass

        game_images = images['data']['images'][str(gameid)]
        for image in game_images:
            if image['type'] == 'clearlogo':
                result['Filetypeclearlogo'] = [base_url + image['filename']]
            elif image['type'] == 'screenshot':
                result['Filetypescreenshot'] = [base_url + image['filename']]
            elif image['type'] == 'fanart':
                result['Filetypefanart'] = [base_url + image['filename']]
            elif image['type'] == 'boxart':
                if (image['side']) == 'front':
                    result['Filetypeboxfront'] = [base_url + image['filename']]
                elif (image['side']) == 'back':
                    result['Filetypeboxback'] = [base_url + image['filename']]

        return result

    def _parse_lookup_data(self, ids, dict):
        results = []

        if ids is None or len(ids) == 0:
            return results

        for id in ids:
            try:
                results.append(dict[str(id)]['name'])
            except KeyError:
                pass

        return results
