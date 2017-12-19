
import config
from config import *
from gamedatabase import *
from descriptionparserfactory import *
import util
from util import *
from util import Logutil as log
from matcher import Matcher

import xbmcvfs
import HTMLParser
import urllib
import re
import os


class PyScraper(object):
	def __init__(self):
		self.scraper = None
		self.crc = ''
		self.foldername = ''
		self.romfile = ''

	def searchAndMatchResults(self, scraper, source, gamename):
		""" Using the scraper, search for a gamename, and get the best match. Returns None if no match found """
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
			if match:
				log.debug("After modifying game name, found {0} best results for {1}".format(len(match), altname))

		return match

	def getUrlFromPreviousRequest(self, scraper, urlsFromPreviousScrapers):
		# Check that the previous scraper has returned a URL
		if len(urlsFromPreviousScrapers) == 0:
			log.error("Configuration error: we expected a URL to have been provided by a previous scrape")
			return None

		try:
			# Get the URL returned from source
			url = urlsFromPreviousScrapers[int(scraper.source) - 1]
			log.info("Scraper with parse instruction {0} using url from previous scraper: {1}".format(scraper.parseInstruction, url))
		except IndexError:
			log.error("Configuration error: parse instruction {0} did not find a URL from source {1}".format(scraper.parseInstruction, str(scraper.source)))
			return None

		if scraper.sourceAppend is not None and scraper.sourceAppend != "":
			url = url + '/' + scraper.sourceAppend
			log.info("sourceAppend = '%s'. New url = '%s'" % (scraper.sourceAppend, url))

		return url

	def scrapeResults(self, results, scraper, urlsFromPreviousScrapers, gamenameFromFile, foldername, filecrc, romFile, romCollection, settings):
		log.debug("Using parser file {0} and game description {1}".format(scraper.parseInstruction, scraper.source))

		scraperSource = scraper.source.decode('utf-8')

		log.debug("Expected platform: {0}".format(romCollection.name))
		self.expected_platform = config.getPlatformByRomCollection(scraperSource, romCollection.name)
		self.scraper = scraper

		# Information about the current game
		self.crc = filecrc
		self.foldername = foldername
		self.romfile = romFile

		# url to scrape may be passed from the previous scraper
		if scraper.source.isdigit():
			scraperSource = self.getUrlFromPreviousRequest(scraper, urlsFromPreviousScrapers)
			if scraperSource is None:
				return results, urlsFromPreviousScrapers, True
			
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

		# Add the fields from the scrape to any existing results
		results = self.addNewElements(results, tempResults)

		return results, urlsFromPreviousScrapers, False

	def addNewElements(self, results, tempResults):
		""" Add fields from the results to the existing set of results, adding if new, replacing if empty. This allows
			us to add fields from subsequent site scrapes that were missing or not available in previous sites.

		Args:
			results: Existing results dict from previous scrapes
			tempResults: Result dict from most recent scrape

		Returns:
			Updated dict of result fields
		"""
		if tempResults is None:
			log.warn("No results found, not adding to existing results")
			return

		for resultKey in tempResults.keys():
			try:
				resultValueOld = results.get(resultKey, [])
				resultValueNew = tempResults.get(resultKey, [])

				# Unescaping ugly html encoding from websites
				if len(resultValueNew) > 0:
					resultValueNew[0] = HTMLParser.HTMLParser().unescape(resultValueNew[0])

				if resultKey not in results:
					log.debug(u"No existing value for key {0}, replacing with new value [{1}]".format(resultKey, ','.join(x for x in resultValueNew)))

					results[resultKey] = resultValueNew
				else:
					# FIXME TODO Check if the previous value is empty, and overwrite if so
					if resultValueOld == []:
						log.debug(u"Previous value empty for key {0}, replacing with new value [{1}]".format(resultKey, ','.join(x for x in resultValueNew)))
						results[resultKey] = resultValueNew
					else:
						log.debug(u"Retaining existing value for key {0} ([{1}])".format(resultKey, ','.join(x for x in resultValueOld)))
			except Exception as e:
				log.warn("There was an error adding key {0} to existing result set: {1}".format(resultKey, str(e)))

		return results
	
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
	
	def getBestResults(self, results, gamenameFromFile):
		# FIXME TODO Kept for meantime to transition to matcher class
		m = Matcher()
		return m.getBestResults(results, gamenameFromFile)

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
