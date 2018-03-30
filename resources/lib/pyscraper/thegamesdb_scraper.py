import sys
import xml.etree.ElementTree as ET
from web_scraper import WebScraper
from util import Logutil as log

# FIXME TODO Exception handling (i.e. no games found)


class TheGamesDB_Scraper(WebScraper):
	"""TheGamesDB.net has its API described at http://wiki.thegamesdb.net/index.php/API_Introduction

	It only supports XML response. This is parsed using either BeautifulSoup or the Python xml.etree.ElementTree
	library. Kodi does not distribute the XML parser required for BeautifulSoup to parse XML files, so the parsing
	defaults to ElementTree with BeautifulSoup provided as a possible future implementation.
	"""
	_name = 'thegamesdb.net'
	_search_url = 'http://thegamesdb.net/api/GetGamesList.php'
	_retrieve_url = 'http://thegamesdb.net/api/GetGame.php'

	# Mapping between the dict keys and the XML fields in the response
	_game_mapping = {
		'Game': 'GameTitle',
		'Description': 'Overview',
		'Publisher': 'Publisher',
		'Developer': 'Developer',
		'Players': 'Players',
		'Rating': 'Rating',
		'Filetypefanart': 'Images/fanart/original',
		'Filetypeboxfront': "Images/boxart[@side='front']",
		'Filetypeboxback': "Images/boxart[@side='back']",
		'Filetypescreenshot': "Images/screenshot/original",
		'Filetypeclearlogo': "Images/clearlogo"
	}

	def __init__(self):
		pass

	def _get_search_url(self):
		return self._search_url

	def _get_search_params(self, **kwargs):
		return {'name': kwargs['gamename'], 'platform': self.get_platform_for_scraper(kwargs['platform']),}

	def _get_retrieve_url(self):
		return self._retrieve_url

	def _get_retrieve_params(self, **kwargs):
		return {'id': kwargs['gameid']}

	def search(self, gamename, platform=None):
		""" Ref http://wiki.thegamesdb.net/index.php/GetGamesList """
		response = self.open_xml_url(url=self._get_search_url(), params=self._get_search_params(gamename=gamename, platform=platform))

		result = self._parseSearchResults(response)
		return result

	def retrieve(self, gameid, platform):
		""" Ref http://wiki.thegamesdb.net/index.php/GetGame """
		response = self.open_xml_url(url=self._get_retrieve_url(), params=self._get_retrieve_params(gameid=gameid))

		results = self._parseGameResult(response)
		return results

	"""
	def _parseGameResultBS(self, response):
		print 'parseGameResultBS'

		result = {}

		#soup = BeautifulSoup(response, 'xml')
		soup = BeautifulSoup(response, 'html.parser')    # This converts all tags to lowercase but is more lenient

		sr = soup.find('game')

		# Standard fields
		for k, v in self._game_mapping.items():
			result[k] = sr.find(v.lower()).string

		result['Genres'] = self._parse_genres(sr.find("Genres"))

		# Date
		result['ReleaseYear'] = self._parse_date(sr.find("releasedate").string)

		# Artwork
		# FIXME TODO http://wiki.thegamesdb.net/index.php/GetArt
		try:
			result['fanart'] = "http://thegamesdb.net/banners/" + sr.find("fanart").find("original").string
			result['screenshot'] = "http://thegamesdb.net/banners/" + sr.find("screenshot").find("original").string
			result['boxfront'] = "http://thegamesdb.net/banners/" + sr.find("boxart", side="front").string
			result['boxback'] = "http://thegamesdb.net/banners/" + sr.find("boxart", side="back").string
		except AttributeError as e:
			print "Unable to find attribute: " + str(e)

		print "Found game using BeautifulSoup parser: {0}".format(result)
		return result
	"""

	def _parseGameResult(self, response):
		# FIXME TODO This currently is not fully implemented
		result = {}

		if sys.version_info >= (2, 7):
			parser = ET.XMLParser(encoding='utf-8')
		else:
			parser = ET.XMLParser()

		tree = ET.fromstring(response, parser)

		game = tree.find('Game')
		# FIXME TODO others

		# Standard fields
		for k, v in self._game_mapping.items():
			# HACK - This is only used to retain backwards compatibility with existing scraper, where each key value was a
			# list, even if only one value is in that list
			try:
				result[k] = [game.find(v).text]
				# FIXME TODO When we remove the hack, this will be the code to use:
				# result[k] = game.find(v).text
			except Exception as e:
				# Typically this result doesn't have this field
				log.debug("Unable to extract data from key {0}".format(k))

		# Custom fields
		result['Genre'] = self._parse_genres(game.find("Genres"))

		# Adjust the date
		releaseDate = game.find("ReleaseDate")
		if releaseDate is not None:
			result['ReleaseYear'] = [self._parse_date(releaseDate.text)]

		# Prefix images with base url
		for image in ['fanart', 'boxfront', 'boxback', 'screenshot', 'clearlogo']:
			try:
				result['Filetype' + image] = ["http://thegamesdb.net/banners/" + result['Filetype' + image][0]]
			except KeyError:
				log.warn("Image type {0} not present in retrieve results".format(image))

		print u"Found game using ElementTree parser: {0}".format(result)
		return result

	"""
	def _parseSearchResultsBS(self, response):
		results = []
		soup = BeautifulSoup(response, 'xml')
		for sr in soup.find_all('Game'):
			results.append({'id': sr.id.string,
							'title': sr.GameTitle.string,
							'releaseDate': sr.ReleaseDate.string,
							'SearchKey': sr.GameTitle.string})

		print u"Found {0} results using BeautifulSoup parser: {1}".format(len(results), results)
		return results
	"""

	def _parseSearchResults(self, response):
		"""
		Parse the response from the GetGamesList API call using ElementTree XML parser
		Returns a list of dicts with id, title and releaseDate
		"""
		if sys.version_info >= (2, 7):
			parser = ET.XMLParser(encoding='utf-8')
		else:
			parser = ET.XMLParser()
		# FIXME TODO throws ParseError

		tree = ET.fromstring(response, parser)

		# ET.iterparse()
		results = []
		for game in tree.findall('Game'):
			#print "{0} - {1} - {2}".format(game.find('id').text, game.find('GameTitle').text, game.find('ReleaseDate').text)
			try:
				results.append({'id': game.find('id').text,
								'title': game.find('GameTitle').text,
								'releaseDate': game.find('ReleaseDate').text,
								'SearchKey': [game.find('GameTitle').text]})
			except AttributeError as e:
				# If we have an attribute error, typically there is no ReleaseDate for this game. Skip.
				pass

		print u"Found {0} results using ElementTree parser: {1}".format(len(results), results)

		return results

	# FIXME TODO Do we add genres to a list? Or concat the string with a /? e.g. Fighting / Racing
	def _parse_genres(self, sr):
		# Genres - <Genres><genre>...</><genre><genre>...</genre></></Genres>
		genres = []

		if sr is None:
			return genres

		for genre in sr.findall("genre"):
			genres.append(genre.text)

		return genres
