
import config
from config import *
from gamedatabase import *
from descriptionparserfactory import *
import util
from util import *
from util import Logutil as log

import difflib

import xbmcgui
import xbmcvfs
import HTMLParser
import urllib
import re
import os


class PyScraper(object):
	digits = ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
	romes = ['X', 'IX', 'VIII', 'VII', 'VI', 'V', 'IV', 'III', 'II', 'I']

	def __init__(self):
		self.scraper = None
		self.crc = ''
		self.foldername = ''
		self.romfile = ''

		self.update_option = 0		# Automatic: Accurate
		self.fuzzy_factor = 0.8

	def searchAndMatchResults(self, scraper, source, gamename):
		""" Using the scraper, search for a gamename, and get the best match """
		resultset = self.parseDescriptionFile(scraper, source, gamename)
		try:
			log.debug("Found {0} results for {1} from URL {2}".format(len(resultset), gamename, source))
			for item in resultset:
				log.debug(" - " + str(item))
		except Exception as e:
			# Ignore if an exception since it will be where tempResults is None
			pass

		match = self.getBestResults(resultset, gamename)
		if match is None:
			# try again without (*) and [*]
			altname = re.sub('\s\(.*\)|\s\[.*\]|\(.*\)|\[.*\]', '', gamename)
			log.debug("Did not find any matches for {0}, trying again with {1}".format(gamename, altname))
			match = self.getBestResults(resultset, altname)
			log.debug("After modifying game name, found {0} best results for {1}".format(len(match), altname))

		return match


	def scrapeResults(self, results, scraper, urlsFromPreviousScrapers, gamenameFromFile, foldername, filecrc, romFile, fuzzyFactor, updateOption, romCollection, settings):
		log.debug("Using parser file {0} and game description {1}".format(scraper.parseInstruction, scraper.source))

		scraperSource = scraper.source.decode('utf-8')

		log.debug("Expected platform: {0}".format(romCollection.name))
		self.expected_platform = config.getPlatformByRomCollection(scraperSource, romCollection.name)

		self.fuzzy_factor = fuzzyFactor
		self.update_option = updateOption
		self.scraper = scraper

		# Information about the current game
		self.crc = filecrc
		self.foldername = foldername
		self.romfile = romFile

		# url to scrape may be passed from the previous scraper
		if scraper.source.isdigit():
			if len(urlsFromPreviousScrapers) == 0:
				log.error("Configuration error: scraper source is numeric and there is no previous scraper that returned an url to scrape.")
				return results, urlsFromPreviousScrapers, True

			try:
				url = urlsFromPreviousScrapers[int(scraper.source) - 1]
				log.info("using url from previous scraper: " + str(url))
			except IndexError:
				log.error("Configuration error: no url found at index " + str(scraper.source))
				return results, urlsFromPreviousScrapers, True
			
			if scraper.sourceAppend is not None and scraper.sourceAppend != "":
				url = url + '/' + scraper.sourceAppend
				log.info("sourceAppend = '%s'. New url = '%s'" % (scraper.sourceAppend, url))

			scraperSource = url
			
		if scraper.source == 'nfo':
			scraperSource = self.getNfoFile(settings, romCollection, gamenameFromFile)

		tempResults = self.searchAndMatchResults(scraper, scraperSource, gamenameFromFile)
		if tempResults is None:
			log.debug("No matches found in result set")
			if scraper.returnUrl:
				urlsFromPreviousScrapers.append('')
			return results, urlsFromPreviousScrapers, True

		if scraper.returnUrl:
			try:								
				tempUrl = self.resolveParseResult(tempResults, 'url')
				urlsFromPreviousScrapers.append(tempUrl)
				log.info("pass url to next scraper: " + str(tempUrl))
			except Exception as e:
				log.warn("Should pass url to next scraper, but url is empty.")
				log.debug("{0} - {1}".format(type(e), str(e)))
			return results, urlsFromPreviousScrapers, True

		# For each result, compare against already existing results. If the old key value doesn't exist and the new
		# one does, then use the new value, otherwise retain the value
		if tempResults is not None:
			for resultKey in tempResults.keys():
				resultValue = []
				
				resultValueOld = results.get(resultKey, [])
				# unescaping ugly html encoding from websites
				if len(resultValueOld) > 0:
					resultValueOld[0] = HTMLParser.HTMLParser().unescape(resultValueOld[0])
				
				resultValueNew = tempResults.get(resultKey, [])
				# unescaping ugly html encoding from websites
				if len(resultValueNew) > 0:
					resultValueNew[0] = HTMLParser.HTMLParser().unescape(resultValueNew[0])

				if len(resultValueOld) == 0 and (len(resultValueNew) != 0 and resultValueNew != [None, ] and resultValueNew != None and resultValueNew != ''):
					log.debug("No existing value for key {0}, replacing with new value [{1}]".format(resultKey, ','.join(str(x) for x in resultValueNew)))
					results[resultKey] = resultValueNew
					resultValue = resultValueNew
				else:
					log.debug("Retaining existing value for key {0} ([{1}])".format(resultKey, ','.join(str(x) for x in resultValueOld)))
					resultValue = resultValueOld
			del tempResults
					
		return results, urlsFromPreviousScrapers, False
	
	def getNfoFile(self, settings, romCollection, gamenameFromFile):
		log.info("getNfoFile")
		nfoFile = ''
		nfoFolder = settings.getSetting(util.SETTING_RCB_NFOFOLDER)
		splittedname = os.path.splitext(os.path.basename(self.romFile))
		filename = ''
		if len(splittedname) == 1:
			filename = splittedname[0]
		elif len(splittedname) == 2:
			filename = splittedname[1]
			
		if nfoFolder != '' and nfoFolder != None:
			nfoFolder = os.path.join(nfoFolder, romCollection.name)
			nfoFile = os.path.join(nfoFolder, gamenameFromFile + '.nfo')
			
			# check for exact rom name (no friendly name)
			if not xbmcvfs.exists(nfoFile):
				nfoFile = os.path.join(nfoFolder, filename + '.nfo')
				
		if not xbmcvfs.exists(nfoFile):
			romDir = os.path.dirname(self.romFile)
			log.info("Romdir: " + str(romDir))
			nfoFile = os.path.join(romDir, gamenameFromFile + '.nfo')
			
			# check for exact rom name (no friendly name)
			if not xbmcvfs.exists(nfoFile):
				nfoFile = os.path.join(romDir, filename + '.nfo')
			
		log.info("Using nfoFile: " + str(nfoFile))
		return nfoFile
	
	def parseDescriptionFile(self, scraper, scraperSource, gamenameFromFile):
		"""
		Given a scraper, source (URL or file) and a gamename, retrieve a list
		of possible matches.
		Args:
			scraper: scraper object to use to retrieve the results
			scraperSource: either a URL or a file
			gamenameFromFile: game to search for
		Returns:
			A list of dicts for each result, where each dict value is itself a list, or None if an error occurred
		"""
		log.info("parseDescriptionFile")
		scraperSource = self.prepareScraperSource(scraper, scraperSource, gamenameFromFile)
		if scraperSource == "":
			log.warn("Scraper source for scraper {0} is empty".format(scraper.parseInstruction))
			return None
			
		try:
			parser = DescriptionParserFactory.getParser(str(scraper.parseInstruction))
			results = parser.parseDescription(scraperSource, scraper.encoding)
			del parser
		except Exception as e:
			log.warn("an error occured while parsing game description: " + scraperSource)
			log.warn("Parser complains about: {0} {1}".format(type(e), str(e)))
			return None
				
		return results
	
	def prepareScraperSource(self, scraper, scraperSourceOrig, romFilename):
		# replace configurable tokens
		replaceKeys = scraper.replaceKeyString.split(',')
		log.debug("replaceKeys: " + str(replaceKeys))
		replaceValues = scraper.replaceValueString.split(',')
		log.debug("replaceValues: " + str(replaceValues))
		
		if len(replaceKeys) != len(replaceValues):
			log.debug("Configuration error: replaceKeyString (%s) and replaceValueString(%s) does not have the same number of ','-separated items." % (scraper.replaceKeyString, scraper.replaceValueString))
			return None
		
		for i in range(0, len(replaceKeys)):
			scraperSource = scraperSourceOrig.replace(replaceKeys[i], replaceValues[i])
			# also replace in gamename for later result matching
			gamenameFromFile = romFilename.replace(replaceKeys[i], replaceValues[i])
			
		if scraperSource.startswith('http'):
			gamenameToParse = urllib.quote(gamenameFromFile, safe='')
		else:
			gamenameToParse = gamenameFromFile
			
		scraperSource = scraperSource.replace(u'%GAME%', gamenameToParse)
		
		replaceTokens = [u'%FILENAME%', u'%FOLDERNAME%', u'%CRC%']
		replaceValues = [gamenameFromFile, self.foldername, self.crc]
		for key, value in util.API_KEYS.iteritems():
			replaceTokens.append(key)
			replaceValues.append(value)
			
		for i in range(0, len(replaceTokens)):
			scraperSource = scraperSource.replace(replaceTokens[i], replaceValues[i])
		
		if not scraperSource.startswith('http') and not os.path.exists(scraperSource):
			# try again with original rom filename
			scraperSource = scraperSourceOrig.replace("%GAME%", romFilename)
			if not os.path.exists(scraperSource):
				log.warn("description file for game {0} could not be found. Check if this path exists: {1}".format(gamenameFromFile, scraperSource))
				return ""

		log.info("description file (tokens replaced): " + scraperSource)
		log.warn("Encoding: %s" % scraper.encoding)
		return scraperSource

	def ask_user_for_result(self, gamename, results):
		options = ['Skip Game']
		for result in results:
			options.append(self.resolveParseResult(result, 'SearchKey'))

		resultIndex = xbmcgui.Dialog().select('Search for: ' + gamename, options)
		return resultIndex
	
	def getBestResults(self, results, gamenameFromFile):
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
				if res == 0:    # Skip Game
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
			log.warn("No result found with a ratio better than %s. Try again with subtitle search." % (str(self.fuzzy_factor),))
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

	def matchGamename(self, results, gamenameFromFile, checkSubtitle):
		
		highestRatio = 0.0
		bestIndex = 0
		for idx, result in enumerate(results):
			try:
				# Check if the result has the correct platform (if needed)
				found_platform = self.resolveParseResult(result, 'PlatformSearchKey')
				if found_platform != '' and self.expected_platform != found_platform:
					log.info("Platform mismatch. %s != %s. Result will be skipped." % (self.expected_platform, found_platform))
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
				sequelGamename = gamenameToCheck
				sequelSearchKey = searchKey
				for j in range(0, len(self.digits)):
					sequelGamename = sequelGamename.replace(self.digits[j], self.romes[j])
					sequelSearchKey = sequelSearchKey.replace(self.digits[j], self.romes[j])
				
				log.info("Try with replaced sequel numbers. Comparing %s with %s" % (sequelGamename, sequelSearchKey))
				if self.compareNames(sequelGamename, sequelSearchKey, checkSubtitle):
					# perfect match
					return result, 1.0
				
				# remove last char for sequel number 1 from gamename
				if gamenameFromFile.endswith(' 1') or gamenameFromFile.endswith(' I'):
					gamenameRemovedSequel = sequelGamename[:len(sequelGamename) - 1]
					log.info("Try with removed sequel numbers. Comparing %s with %s" % (gamenameRemovedSequel, sequelSearchKey))
					if self.compareNames(gamenameRemovedSequel, sequelSearchKey, checkSubtitle):
						# perfect match
						return result, 1.0
				
				# remove last char for sequel number 1 from result (check with gamenameFromFile because we need the ' ' again)
				if origSearchKey.endswith(' 1') or origSearchKey.endswith(' I'):
					searchKeyRemovedSequels = sequelSearchKey[:len(sequelSearchKey) - 1]
					log.info("Try with removed sequel numbers. Comparing %s with %s" % (sequelGamename, searchKeyRemovedSequels))
					if self.compareNames(sequelGamename, searchKeyRemovedSequels, checkSubtitle):
						# perfect match
						return result, 1.0
				
				ratio = difflib.SequenceMatcher(None, sequelGamename.upper(), sequelSearchKey.upper()).ratio()
				log.info("No result found. Try to find game by ratio. Comparing %s with %s, ratio: %s" % (sequelGamename, sequelSearchKey, str(ratio)))

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
			log.info("'%s' and '%s' both don't contain a sequel number. Skip checking sequel number match." % (gamenameFromFile, searchKey))
			return True
		
		if (indexGamename == -1 or indexSearchKey == -1) and (indexGamename == 9 or indexSearchKey == 9):
			log.info("'%s' and '%s' seem to be sequel number 1. Skip checking sequel number match." % (gamenameFromFile, searchKey))
			return True
		
		if indexGamename != indexSearchKey:
			log.info("Sequel number index for '%s' : '%s'" % (gamenameFromFile, str(indexGamename)))
			log.info("Sequel number index for '%s' : '%s'" % (searchKey, str(indexSearchKey)))
			log.info("Sequel numbers don\'t match. Result will be skipped.")
			return False
		
		return True
		
	def getSequelNoIndex(self, gamename):
		indexGamename = -1
		
		for i in range(0, len(self.digits)):
			if gamename.find(self.digits[i]) != -1:
				indexGamename = i
				break
			if gamename.find(self.romes[i]) != -1:
				indexGamename = i
				break
				
		return indexGamename
				
	# TODO merge with method from dbupdate.py
	def resolveParseResult(self, result, itemName):
		
		resultValue = ""
		
		try:			
			resultValue = result[itemName][0]
			resultValue = util.html_unescape(resultValue)
			resultValue = resultValue.strip()
			# unescape ugly html encoding from websites
			resultValue = HTMLParser.HTMLParser().unescape(resultValue)
									
		except Exception as e:
			#log.warn("Error while resolving item: " + itemName + " : " + str(exc))
			log.warn("Error while resolving item: {0} : {1} {2}".format(itemName, type(e), str(e)))

		try:
			log.debug("Result " + itemName + " = " + resultValue)
		except:
			pass
				
		return resultValue
