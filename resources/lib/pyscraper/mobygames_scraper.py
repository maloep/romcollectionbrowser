from web_scraper import WebScraper
from rcbexceptions import *
from util import Logutil as log
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
		print 'returning ' + kwargs['gamename']
		return {'title': '{0}'.format(self.prepare_gamename_for_request(kwargs['gamename'])),
				'api_key': self._apikey,
				'platform': self.consoleDict[kwargs['platform']][0],
				'format': 'brief'}

	def _get_retrieve_url(self, gameid):
		return self._retrieve_url.format(gameid)

	def _get_retrieve_params(self, **kwargs):
		return {'api_key': self._apikey}

	def search(self, gamename, platform=None):
		time.sleep(1.2)
		response = self.open_json_url(url=self._get_search_url(), params=self._get_search_params(gamename=gamename, platform=platform))

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

		""" response is expected to be a JSON object """
		log.debug("Parsing response for search results: {0}".format(response))
		print "Parsing response for search results: {0}".format(response)

		if len(response["games"]) == 0:
			log.warn("No results found")
			return results

		for result in response['games']:
			print result
			results.append({'id': result['game_id'],
							'title': result['title'],
							'releaseDate': "",    # MobyGames search doesn't return a year in brief mode
							'SearchKey': [result['title']]})

		log.debug("Found {0} results using requests JSON parser: {1}".format(len(results), results))

		return results

	def retrieve(self, gameid):
		time.sleep(1.2)
		response = self.open_json_url(url=self._get_retrieve_url(gameid), params=self._get_retrieve_params())

		# Handle API status code
		if 'error' in response:
			self._check_status_code(response['code'])

		results = self._parse_game_result(response)
		print results
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
			except KeyError as k:
				log.warn("Unable to find key: {0}".format(k))
			except Exception as e:
				log.warn("Unable to extract data from key {0}".format(e))

		# Custom fields (i.e. ones that require special handling)
		result['Genre'] = self._parse_genres(response['genres'])
		try:
			result['ReleaseYear'] = [self._parse_date(response['platforms'][0]['first_release_date'], "%Y")]
		except ValueError:
			result['ReleaseYear'] = [self._parse_date(response['platforms'][0]['first_release_date'], "%Y-%m-%d")]
		# FIXME TODO If this raises an exception, set to u"1970"

		# FIXME TODO Publisher is in releases.companies.@role="Published by"?

		return result

	def _parse_genres(self, genres):
		gens = []
		for gen in genres:
			if gen["genre_category"] == "Basic Genres":
				gens.append(gen['genre_name'])
		return gens

