from __future__ import print_function
from __future__ import absolute_import
from web_scraper import WebScraper
from rcbexceptions import *
from util import Logutil as log
from gamename_utils import GameNameUtil
import time


class Mobygames_Scraper(WebScraper):
    """Mobygames.com has its API described at https://www.mobygames.com/info/api

    NOTE API requests are a maximum of 1 per second, and no more than 360 for the hour. We cater for this by adding
    a deliberate sleep delay into each request
    """
    _name = 'MobyGames.com'
    _apikey = 'FH9VxTkB6BGAEsF3qlnnxQ=='
    _search_url = 'https://api.mobygames.com/v1/games'
    _retrieve_url = 'https://api.mobygames.com/v1/games/{0}'  # game ID is substituted
    _retrieve_release_url = 'https://api.mobygames.com/v1/games/{0}/platforms/{1}'  # game ID and platform ID will be substituted
    _retrieve_covers_url = 'https://api.mobygames.com/v1/games/{0}/platforms/{1}/covers'  # game ID and platform ID will be substituted
    _retrieve_screenshots_url = 'https://api.mobygames.com/v1/games/{0}/platforms/{1}/screenshots'  # game ID and platform ID will be substituted

    # Mapping between the dict keys and the JSON fields in the response
    _game_mapping = {
        'Game': 'title',
        'Description': 'description',  # Short description
    }

    def __init__(self):
        pass

    def _get_search_url(self):
        return self._search_url

    def _get_search_params(self, **kwargs):
        print ('returning ' + kwargs['gamename'])
        return {'title': '%s' % GameNameUtil().prepare_gamename_for_searchrequest(kwargs['gamename']),
                'api_key': self._apikey,
                'platform': self.get_platform_for_scraper(kwargs['platform']),
                'format': 'brief'}

    def _get_retrieve_url(self, gameid):
        return self._retrieve_url.format(gameid)

    def _get_retrieve_release_url(self, gameid, platformid):
        return self._retrieve_release_url.format(gameid, platformid)

    def _get_retrieve_covers_url(self, gameid, platformid):
        return self._retrieve_covers_url.format(gameid, platformid)

    def _get_retrieve_screenshots_url(self, gameid, platformid):
        return self._retrieve_screenshots_url.format(gameid, platformid)

    def _get_retrieve_params(self, **kwargs):
        return {'api_key': self._apikey}

    def search(self, gamename, platform=None):
        time.sleep(1.2)
        response = self.open_json_url(url=self._get_search_url(),
                                      params=self._get_search_params(gamename=gamename, platform=platform))

        # Handle API status code
        if 'error' in response:
            self._check_status_code(response['code'])

        result = self._parse_search_results(response)
        return result

    def _check_status_code(self, sc):
        if sc == 429:
            raise ScraperExceededAPIQuoteException("API quota exceeded for MobyGames")
        elif sc == 401:
            raise ScraperUnauthorisedException("API key unauthorised for MobyGames")
        else:
            raise ScraperUnexpectedError("Unexpected error when scraping MobyGames")

    def _parse_search_results(self, response):
        results = []

        #response is expected to be a JSON object
        log.debug("Parsing response for search results: {0}".format(response))

        if len(response["games"]) == 0:
            log.warn("No results found")
            return results

        for result in response['games']:
            results.append({'id': result['game_id'],
                            'title': result['title'],
                            'releaseDate': "",  # MobyGames search doesn't return a year in brief mode
                            'SearchKey': [result['title']]})

        log.debug("Found {0} results using requests JSON parser: {1}".format(len(results), results))

        return results

    def retrieve(self, gameid, platform):
        time.sleep(1.2)
        response = self.open_json_url(url=self._get_retrieve_url(gameid), params=self._get_retrieve_params())

        # Handle API status code
        if 'error' in response:
            self._check_status_code(response['code'])

        results = self._parse_game_result(response)

        platformid = self.get_platform_for_scraper(platform)

        #get release specific information for this game
        results.update(self.retrieve_release(gameid, platformid))

        #TODO check if we should invoke this from dbupdate after we searched for local artwork
        results.update(self.retrieve_images(gameid, platformid))

        return results

    def _parse_game_result(self, response):
        """ response is expected to be a JSON object """
        result = {}

        # Standard fields
        for k, v in self._game_mapping.items():
            try:
                # HACK - for compatibility we need to put each result in an array
                # result[k] = response[v]
                result[k] = [response[v]]
            except KeyError:
                log.warn("Unable to find key: {0}".format(k))
            except Exception as e:
                log.warn("Unable to extract data from key {0}".format(e))

        # Custom fields (i.e. ones that require special handling)
        result['Genre'] = self._parse_genres(response['genres'])

        # FIXME TODO Publisher is in releases.companies.@role="Published by"?

        return result

    def retrieve_release(self, gameid, platformid):
        time.sleep(1.2)
        response = self.open_json_url(url=self._get_retrieve_release_url(gameid, platformid),
                                      params=self._get_retrieve_params())

        # Handle API status code
        if 'error' in response:
            self._check_status_code(response['code'])

        result = self._parse_release_result(response)

        return result

    def _parse_release_result(self, response):
        """ response is expected to be a JSON object """
        result = {}

        # Release year can be either %Y-%m-%d
        result['ReleaseYear'] = [self._parse_date(response['first_release_date'])]

        for company in response['releases'][0]['companies']:
            if company['role'] == 'Published by':
                result['Publisher'] = [company['company_name']]
            elif company['role'] == 'Developed by':
                result['Developer'] = [company['company_name']]

        for attribute in response['attributes']:
            if attribute['attribute_category_name'] == 'Input Devices Supported':
                result['Controller'] = [attribute['attribute_name']]
            elif attribute['attribute_category_name'] == 'Number of Players Supported':
                result['Players'] = [attribute['attribute_name']]

        return result

    def retrieve_images(self, gameid, platformid):

        result = self.retrieve_covers(gameid, platformid)

        result.update(self.retrieve_screenshots(gameid, platformid))

        return result

    def retrieve_covers(self, gameid, platformid):
        time.sleep(1.2)
        response = self.open_json_url(url=self._get_retrieve_covers_url(gameid, platformid),
                                      params=self._get_retrieve_params())

        # Handle API status code
        if 'error' in response:
            self._check_status_code(response['code'])

        results = self._parse_covers_result(response)

        return results

    def _parse_covers_result(self, response):

        result = {}

        covergroups = response['cover_groups']

        if len(covergroups) == 0:
            log.warn("No covers found in mobygames response")
            return result

        #HACK: always use the first covergroup. We could add an option to search for specific region covers
        covergroup = covergroups[0]
        for cover in covergroup['covers']:
            if cover['scan_of'] == 'Front Cover':
                result['Filetypeboxfront'] = [cover['image']]
            elif cover['scan_of'] == 'Back Cover':
                result['Filetypeboxback'] = [cover['image']]
            elif cover['scan_of'] == 'Media':
                result['Filetypecartridge'] = [cover['image']]

        return result

    def retrieve_screenshots(self, gameid, platformid):
        time.sleep(1.2)
        response = self.open_json_url(url=self._get_retrieve_screenshots_url(gameid, platformid),
                                      params=self._get_retrieve_params())

        # Handle API status code
        if 'error' in response:
            self._check_status_code(response['code'])

        results = self._parse_screenshots_result(response)

        return results

    def _parse_screenshots_result(self, response):

        result = {}

        screenshots = response['screenshots']

        if len(screenshots) == 0:
            log.warn("No screenshots found in mobygames response")
            return result

        #HACK: always return the first screenshot. We could add support for multiple screenshots or screenshot selection.
        screenshot = screenshots[0]
        result['Filetypescreenshot'] = [screenshot['image']]
        return result

    def _parse_genres(self, genres):
        gens = []
        for gen in genres:
            if gen["genre_category"] == "Basic Genres":
                gens.append(gen['genre_name'])
        return gens
