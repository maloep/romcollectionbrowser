import HTMLParser
import re

import xbmcgui
from xbmcaddon import Addon

import difflib
import util
from util import *
from util import Logutil as log



"""
This object performs the comparison of a game name against the result set
"""
class Matcher(object):
	""" Initial defaults """
	update_option = 0  # Automatic: Accurate
	fuzzy_factor = 0.8

	""" Used for comparing sequel numbers in roman vs arabic """
	digits = ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
	romes = ['X', 'IX', 'VIII', 'VII', 'VI', 'V', 'IV', 'III', 'II', 'I']

	def __init__(self):
		self.fuzzy_factor = self.getFuzzyFactor()
		self.update_option = self.getScrapingMode()

	def getFuzzyFactor(self):
		# Set the fuzzy factor before scraping
		matchingRatioIndex = Addon().getSetting(util.SETTING_RCB_FUZZYFACTOR)

		if matchingRatioIndex == '':
			matchingRatioIndex = 2
		log.info("matchingRatioIndex: {0}".format(matchingRatioIndex))

		self.fuzzyFactor = util.FUZZY_FACTOR_ENUM[int(matchingRatioIndex)]
		log.info("fuzzyFactor: {0}".format(self.fuzzyFactor))

	def getScrapingMode(self):
		mode = 0
		scrape_options = {'Automatic: Accurate': 0,
						  'Automatic: Guess Matches': 1,
						  'Interactive: Select Matches': 2}
		try:
			mode = scrape_options[Addon().getSetting(SETTING_RCB_SCRAPINGMODE)]
		except KeyError:
			pass

		log.info("Scraping mode: " + mode)

		return mode

	def getBestResults(self, results, gamenameFromFile):

		"""
		Compare a game name against each item in a result set to work out which is the likely match
		Args:
			results: A list of dicts with the SearchKey key being the game title in the result set
			gamenameFromFile: The title of the game we are trying to match

		Returns:
			Either None if no match was found, or the title of the matching game (SearchKey key in the dict)
		"""

		log.info("getBestResults")

		if results is None or len(results) == 0:
			log.info("No results found with current scraper")
			return None

		log.info("Searching for game: " + gamenameFromFile)
		log.info("%s results found. Try to find best match." % str(len(results)))

		result, highestRatio = self.matchGamename(results, gamenameFromFile, False)
		bestMatchingGame = self.resolveParseResult(result, 'SearchKey')

		if highestRatio != 1.0:

			# stop searching in accurate mode
			if self.update_option == util.SCRAPING_OPTION_AUTO_ACCURATE:
				log.warn("Ratio != 1.0 and scraping option is set to 'Accurate'. Result will be skipped")
				return None

			# Ask for correct result in Interactive mode
			if self.update_option == util.SCRAPING_OPTION_INTERACTIVE:
				res = self.ask_user_for_result(gamenameFromFile, results)
				if res == 0:  # Skip Game
					log.info("No result chosen by user")
					return None
				else:
					selectedGame = self.resolveParseResult(results[res - 1], 'Game')
					log.info("Result chosen by user: " + str(selectedGame))
					return results[res - 1]

			# check seq no in guess names mode
			seqNoIsEqual = self.checkSequelNoIsEqual(gamenameFromFile, bestMatchingGame)
			if not seqNoIsEqual:
				highestRatio = 0.0

		if highestRatio < self.fuzzy_factor:
			log.warn("No result found with a ratio better than %s. Try again with subtitle search." % (
			str(self.fuzzy_factor),))
			result, highestRatio = self.matchGamename(results, gamenameFromFile, True)
			# check for sequel numbers because it could be misinteroreted as subtitle
			bestMatchingGame = self.resolveParseResult(result, 'SearchKey')
			seqNoIsEqual = self.checkSequelNoIsEqual(gamenameFromFile, bestMatchingGame)
			if not seqNoIsEqual:
				return None

		if highestRatio < self.fuzzy_factor:
			log.warn("No result found with a ratio better than %s. Result will be skipped." % (str(self.fuzzy_factor),))
			return None

		# get name of found result
		bestMatchingGame = self.resolveParseResult(result, 'SearchKey')

		log.info("Using best result %s" % bestMatchingGame)
		return result

	def ask_user_for_result(self, gamename, results):
		options = ['Skip Game']
		for result in results:
			options.append(self.resolveParseResult(result, 'SearchKey'))

		resultIndex = xbmcgui.Dialog().select('Search for: ' + gamename, options)
		return resultIndex

	def matchGamename(self, results, gamenameFromFile, checkSubtitle):

		highestRatio = 0.0
		bestIndex = 0
		for idx, result in enumerate(results):
			try:
				# Check if the result has the correct platform (if needed)
				found_platform = self.resolveParseResult(result, 'PlatformSearchKey')
				if found_platform != '' and self.expected_platform != found_platform:
					log.info("Platform mismatch. %s != %s. Result will be skipped." % (
					self.expected_platform, found_platform))
					continue

				searchKey = self.resolveParseResult(result, 'SearchKey')
				# keep it for later reference
				origSearchKey = searchKey
				gamenameToCheck = gamenameFromFile

				# searchKey is specified in parserConfig - if no one is specified first result is valid (1 file per game scenario)
				if searchKey == '':
					log.info("No searchKey found. Using first result")
					return result, 1.0

				log.info("Comparing %s with %s" % (gamenameToCheck, searchKey))
				if self.compareNames(gamenameToCheck, searchKey, checkSubtitle):
					# perfect match
					return result, 1.0

				# try again with normalized names
				gamenameToCheck = self.normalizeName(gamenameToCheck)
				searchKey = self.normalizeName(searchKey)
				log.info("Try normalized names. Comparing %s with %s" % (gamenameToCheck, searchKey))
				if self.compareNames(gamenameToCheck, searchKey, checkSubtitle):
					# perfect match
					return result, 1.0

				# try again with replaced sequel numbers
				sequelGamename = self.replaceSequelNumbers(gamenameToCheck)
				sequelSearchKey = self.replaceSequelNumbers(searchKey)

				log.info("Try with replaced sequel numbers. Comparing %s with %s" % (sequelGamename, sequelSearchKey))
				if self.compareNames(sequelGamename, sequelSearchKey, checkSubtitle):
					# perfect match
					return result, 1.0

				# remove last char for sequel number 1 from gamename
				if gamenameFromFile.endswith(' 1') or gamenameFromFile.endswith(' I'):
					gamenameRemovedSequel = sequelGamename[:len(sequelGamename) - 1]
					log.info("Try with removed sequel numbers. Comparing %s with %s" % (
					gamenameRemovedSequel, sequelSearchKey))
					if self.compareNames(gamenameRemovedSequel, sequelSearchKey, checkSubtitle):
						# perfect match
						return result, 1.0

				# remove last char for sequel number 1 from result (check with gamenameFromFile because we need the ' ' again)
				if origSearchKey.endswith(' 1') or origSearchKey.endswith(' I'):
					searchKeyRemovedSequels = sequelSearchKey[:len(sequelSearchKey) - 1]
					log.info("Try with removed sequel numbers. Comparing %s with %s" % (
					sequelGamename, searchKeyRemovedSequels))
					if self.compareNames(sequelGamename, searchKeyRemovedSequels, checkSubtitle):
						# perfect match
						return result, 1.0

				ratio = difflib.SequenceMatcher(None, sequelGamename.upper(), sequelSearchKey.upper()).ratio()
				log.info("No result found. Try to find game by ratio. Comparing %s with %s, ratio: %s" % (
				sequelGamename, sequelSearchKey, str(ratio)))

				if ratio > highestRatio:
					highestRatio = ratio
					bestIndex = idx

			except Exception, (exc):
				log.warn("An error occured while matching the best result: " + str(exc))

		return results[bestIndex], highestRatio

	def compareNames(self, gamename, searchkey, checkSubtitle):
		if checkSubtitle:
			if searchkey.find(gamename) > -1:
				log.info("%s is a subtitle of %s. Using result %s" % (gamename, searchkey, searchkey))
				return True
		else:
			if gamename == searchkey:
				log.info("Perfect match. Using result %s" % searchkey)
				return True

		return False

	def normalizeName(self, name):

		removeChars = [', A', 'THE', ' ', '&', '-', '_', ':', '!', "'", '"', '.', ',', '#']

		name = name.upper()

		for char in removeChars:
			name = name.replace(char, '')

		return name

	def checkSequelNoIsEqual(self, gamenameFromFile, searchKey):
		""" Given a gamename and a possible matching gamegame, check whether they
		share a sequel number

		Args:
			gamenameFromFile: Existing filename that we are matching
			searchKey: Found gamename from parser

		Returns:
			True if there is a number (either roman or decimal) that the games share
			False otherwise

		"""
		log.info("Check sequel numbers for '%s' and '%s'." % (gamenameFromFile, searchKey))

		# first check equality of last number (also works for year sequels like Fifa 98)
		numbers = re.findall(r"\d+", gamenameFromFile)
		if len(numbers) > 0:
			numberGamename = numbers[len(numbers) - 1]
		else:
			numberGamename = '1'

		numbers = re.findall(r"\d+", searchKey)
		if len(numbers) > 0:
			numberSearchkey = numbers[len(numbers) - 1]
		else:
			numberSearchkey = '2'

		if numberGamename == numberSearchkey:
			return True

		indexGamename = self.getSequelNoIndex(gamenameFromFile)
		indexSearchKey = self.getSequelNoIndex(searchKey)

		if indexGamename == -1 and indexSearchKey == -1:
			log.info("'%s' and '%s' both don't contain a sequel number. Skip checking sequel number match." % (
			gamenameFromFile, searchKey))
			return True

		if (indexGamename == -1 or indexSearchKey == -1) and (indexGamename == 9 or indexSearchKey == 9):
			log.info("'%s' and '%s' seem to be sequel number 1. Skip checking sequel number match." % (
			gamenameFromFile, searchKey))
			return True

		if indexGamename != indexSearchKey:
			log.info("Sequel number index for '%s' : '%s'" % (gamenameFromFile, str(indexGamename)))
			log.info("Sequel number index for '%s' : '%s'" % (searchKey, str(indexSearchKey)))
			log.info("Sequel numbers don\'t match. Result will be skipped.")
			return False

		return True

	def getSequelNoIndex(self, gamename):
		""" Returns the index in the list that matches the first number found, either number or roman numeral.
			This is used to compare a game that has a sequel number with a result that has a sequel number in a
			different format (e.g. Final Fantasy VIII vs. Final Fantasy 8).
			Note we currently only support matching up to X (10), so Final Fantasy XIII won't work
			In addition, because of the way this iterates, we won't match IX properly since X is found first
		"""
		indexGamename = -1

		for i in range(0, len(self.digits)):
			if gamename.find(' ' + self.digits[i]) != -1:
				indexGamename = i
				break
			if gamename.find(' ' + self.romes[i]) != -1:
				indexGamename = i
				break

		return indexGamename

	def replaceSequelNumbers(self, name):
		""" Replace any sequel-style digits in the game name with the roman numeral equivalent, and return the
			string with the replaced digits
			FIXME TODO This only matches on single digits """
		for i in range(0, len(self.digits)):
			name = name.replace(self.digits[i], self.romes[i])
		return name

	""" This method is due to the fact that our result set is a list of dicts """
	def resolveParseResult(self, result, itemName):

		resultValue = ""

		try:
			resultValue = result[itemName][0]
			resultValue = util.html_unescape(resultValue)
			resultValue = resultValue.strip()
			# unescape ugly html encoding from websites
			resultValue = HTMLParser.HTMLParser().unescape(resultValue)

		except Exception as e:
			# log.warn("Error while resolving item: " + itemName + " : " + str(exc))
			log.warn("Error while resolving item: {0} : {1} {2}".format(itemName, type(e), str(e)))

		try:
			log.debug("Result " + itemName + " = " + resultValue)
		except:
			pass

		return resultValue