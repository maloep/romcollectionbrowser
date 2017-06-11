
import config
from config import *
from gamedatabase import *
from descriptionparserfactory import *
import util
from util import *

import difflib

import xbmcgui
import HTMLParser


class PyScraper:
	digits = ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']
	romes = ['X', 'IX', 'VIII', 'VII', 'VI', 'V', 'IV', 'III', 'II', 'I']

	def __init__(self):
		pass

	def log_results(self, resultslist):
		for item in resultslist:
			Logutil.log(' - ' + str(item), util.LOG_LEVEL_DEBUG)

	def scrapeResults(self, results, scraper, urlsFromPreviousScrapers, gamenameFromFile, foldername, filecrc, romFile, fuzzyFactor, updateOption, romCollection, settings):		
		Logutil.log("using parser file: " +scraper.parseInstruction, util.LOG_LEVEL_DEBUG)		
		Logutil.log("using game description: " +scraper.source, util.LOG_LEVEL_DEBUG)
		
		scraperSource = scraper.source.decode('utf-8')

		Logutil.log('Expected platform: {0}'.format(romCollection.name), util.LOG_LEVEL_DEBUG)
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
				Logutil.log("Configuration error: scraper source is numeric and there is no previous scraper that returned an url to scrape.", util.LOG_LEVEL_ERROR)
				return results, urlsFromPreviousScrapers, True			

			try:
				url = urlsFromPreviousScrapers[int(scraper.source) -1]
				Logutil.log("using url from previous scraper: " +str(url), util.LOG_LEVEL_INFO)
			except Exception as e:
				# FIXME TODO - out of bounds exception
				Logutil.log("Configuration error: no url found at index " + str(scraper.source), util.LOG_LEVEL_ERROR)
				return results, urlsFromPreviousScrapers, True
			
			if scraper.sourceAppend is not None and scraper.sourceAppend != "":
				url = url + '/' + scraper.sourceAppend
				Logutil.log("sourceAppend = '%s'. New url = '%s'" % (scraper.sourceAppend, url), util.LOG_LEVEL_INFO)
			
			scraperSource = url
			
		if scraper.source == 'nfo':
			scraperSource = self.getNfoFile(settings, romCollection, gamenameFromFile)
				
		tempResults = self.parseDescriptionFile(scraper, scraperSource, gamenameFromFile)
		try:
			Logutil.log("Found {0} results for {1} from URL {2}".format(len(tempResults), gamenameFromFile, scraperSource), util.LOG_LEVEL_DEBUG)
			self.log_results(tempResults)
		except:
			# Ignore if an exception since it will be where tempResults is None
			pass

		tempResults = self.getBestResults(tempResults, gamenameFromFile)
		
		if tempResults is None:
			# try again without (*) and [*]
			altname = re.sub('\s\(.*\)|\s\[.*\]|\(.*\)|\[.*\]', '', gamenameFromFile)
			Logutil.log("Did not find any matches for {0}, trying again with {1}".format(gamenameFromFile, altname),
						util.LOG_LEVEL_DEBUG)
			tempResults = self.parseDescriptionFile(scraper, scraperSource, altname)
			tempResults = self.getBestResults(tempResults, altname)
				
			if tempResults is None:
				Logutil.log("Still no matches after modifying game name", util.LOG_LEVEL_DEBUG)
				if scraper.returnUrl:
					urlsFromPreviousScrapers.append('')
				return results, urlsFromPreviousScrapers, True

			Logutil.log("After modifying game name, found {0} best results for {1}".format(len(tempResults), altname), util.LOG_LEVEL_DEBUG)
		
		if scraper.returnUrl:
			try:								
				tempUrl = self.resolveParseResult(tempResults, 'url')
				urlsFromPreviousScrapers.append(tempUrl)
				Logutil.log("pass url to next scraper: " + str(tempUrl), util.LOG_LEVEL_INFO)
			except:
				Logutil.log("Should pass url to next scraper, but url is empty.", util.LOG_LEVEL_WARNING)
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
					Logutil.log("No existing value for key {0}, replacing with new value [{1}]".format(resultKey, ','.join(str(x) for x in resultValueNew)), util.LOG_LEVEL_DEBUG)
					results[resultKey] = resultValueNew
					resultValue = resultValueNew
				else:
					Logutil.log("Retaining existing value for key {0} ([{1}])".format(resultKey, ','.join(str(x) for x in resultValueOld)), util.LOG_LEVEL_DEBUG)
					resultValue = resultValueOld
			del tempResults
					
		return results, urlsFromPreviousScrapers, False
	
	def getNfoFile(self, settings, romCollection, gamenameFromFile):
		Logutil.log("getNfoFile", util.LOG_LEVEL_INFO)
		nfoFile = ''
		nfoFolder = settings.getSetting(util.SETTING_RCB_NFOFOLDER)
		splittedname = os.path.splitext(os.path.basename(self.romFile))
		filename = ''
		if len(splittedname) == 1:
			filename = splittedname[0]
		elif len(splittedname) == 2:
			filename = splittedname[1]
			
		if(nfoFolder != '' and nfoFolder != None):
			nfoFolder = os.path.join(nfoFolder, romCollection.name)
			nfoFile = os.path.join(nfoFolder, gamenameFromFile + '.nfo')
			
			#check for exact rom name (no friendly name)	
			if not xbmcvfs.exists(nfoFile):
				nfoFile = os.path.join(nfoFolder, filename + '.nfo')
				
		if not xbmcvfs.exists(nfoFile):
			romDir = os.path.dirname(self.romFile)
			Logutil.log('Romdir: ' + str(romDir), util.LOG_LEVEL_INFO)
			nfoFile = os.path.join(romDir, gamenameFromFile + '.nfo')
			
			# check for exact rom name (no friendly name)
			if (not xbmcvfs.exists(nfoFile)):
				nfoFile = os.path.join(romDir, filename + '.nfo')
			
		Logutil.log('Using nfoFile: ' + str(nfoFile), util.LOG_LEVEL_INFO)
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
		Logutil.log("parseDescriptionFile", util.LOG_LEVEL_INFO)
		scraperSource = self.prepareScraperSource(scraper, scraperSource, gamenameFromFile)
		if scraperSource == "":
			Logutil.log("Scraper source for scraper {0} is empty".format(scraper.parseInstruction), util.LOG_LEVEL_DEBUG)
			return None
			
		try:
			parser = DescriptionParserFactory.getParser(str(scraper.parseInstruction))
			results = parser.parseDescription(scraperSource, scraper.encoding)
			del parser
		except Exception, (exc):
			Logutil.log("an error occured while parsing game description: " + scraperSource, util.LOG_LEVEL_WARNING)
			Logutil.log("Parser complains about: " + str(exc), util.LOG_LEVEL_WARNING)
			return None
				
		return results
	
	def prepareScraperSource(self, scraper, scraperSourceOrig, romFilename):
		# replace configurable tokens
		replaceKeys = scraper.replaceKeyString.split(',')
		Logutil.log("replaceKeys: " + str(replaceKeys), util.LOG_LEVEL_DEBUG)
		replaceValues = scraper.replaceValueString.split(',')
		Logutil.log("replaceValues: " + str(replaceValues), util.LOG_LEVEL_DEBUG)
		
		if len(replaceKeys) != len(replaceValues):
			Logutil.log("Configuration error: replaceKeyString (%s) and replaceValueString(%s) does not have the same number of ','-separated items." % (scraper.replaceKeyString, scraper.replaceValueString), util.LOG_LEVEL_ERROR)
			return None
		
		for i in range(0, len(replaceKeys)):
			scraperSource = scraperSourceOrig.replace(replaceKeys[i], replaceValues[i])
			# also replace in gamename for later result matching
			gamenameFromFile = romFilename.replace(replaceKeys[i], replaceValues[i])
			
		if scraperSource.startswith('http://'):
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
		
		if not scraperSource.startswith('http://') and not os.path.exists(scraperSource):
			# try again with original rom filename
			scraperSource = scraperSourceOrig.replace("%GAME%", romFilename)
			if not os.path.exists(scraperSource):				
				Logutil.log("description file for game " + gamenameFromFile + " could not be found. "\
						"Check if this path exists: " + scraperSource, util.LOG_LEVEL_WARNING)
				return ""
		
		Logutil.log("description file (tokens replaced): " + scraperSource, util.LOG_LEVEL_INFO)
		Logutil.log("Encoding: %s" % scraper.encoding, util.LOG_LEVEL_WARNING)
		return scraperSource

	def ask_user_for_result(self, gamename, results):
		options = ['Skip Game']
		for result in results:
			options.append(self.resolveParseResult(result, 'SearchKey'))

		resultIndex = xbmcgui.Dialog().select('Search for: ' + gamename, options)
		return resultIndex
	
	def getBestResults(self, results, gamenameFromFile):
		Logutil.log("getBestResults", util.LOG_LEVEL_INFO)

		if results is None or len(results) == 0:
			Logutil.log('No results found with current scraper', util.LOG_LEVEL_INFO)
			return None

		Logutil.log('Searching for game: ' + gamenameFromFile, util.LOG_LEVEL_INFO)
		Logutil.log('%s results found. Try to find best match.' % str(len(results)), util.LOG_LEVEL_INFO)

		result, highestRatio = self.matchGamename(results, gamenameFromFile, False)
		bestMatchingGame = self.resolveParseResult(result, 'SearchKey')

		if highestRatio != 1.0:

			# stop searching in accurate mode
			if self.update_option == util.SCRAPING_OPTION_AUTO_ACCURATE:
				Logutil.log('Ratio != 1.0 and scraping option is set to "Accurate". Result will be skipped', LOG_LEVEL_WARNING)
				return None

			# Ask for correct result in Interactive mode
			if self.update_option == util.SCRAPING_OPTION_INTERACTIVE:
				res = self.ask_user_for_result(gamenameFromFile, results)
				if res == 0:    # Skip Game
					Logutil.log('No result chosen by user', util.LOG_LEVEL_INFO)
					return None
				else:
					selectedGame = self.resolveParseResult(results[res - 1], 'Game')
					Logutil.log('Result chosen by user: ' + str(selectedGame), util.LOG_LEVEL_INFO)
					return results[res - 1]

			# check seq no in guess names mode
			seqNoIsEqual = self.checkSequelNoIsEqual(gamenameFromFile, bestMatchingGame)
			if not seqNoIsEqual:
				highestRatio = 0.0

		if highestRatio < self.fuzzy_factor:
			Logutil.log('No result found with a ratio better than %s. Try again with subtitle search.' % (str(self.fuzzy_factor),), LOG_LEVEL_WARNING)
			result, highestRatio = self.matchGamename(results, gamenameFromFile, True)
			# check for sequel numbers because it could be misinteroreted as subtitle
			bestMatchingGame = self.resolveParseResult(result, 'SearchKey')
			seqNoIsEqual = self.checkSequelNoIsEqual(gamenameFromFile, bestMatchingGame)
			if not seqNoIsEqual:
				return None

		if highestRatio < self.fuzzy_factor:
			Logutil.log('No result found with a ratio better than %s. Result will be skipped.' % (str(self.fuzzy_factor),), LOG_LEVEL_WARNING)
			return None

		# get name of found result
		bestMatchingGame = self.resolveParseResult(result, 'SearchKey')

		Logutil.log('Using result %s' %bestMatchingGame, util.LOG_LEVEL_INFO)
		return result

	def matchGamename(self, results, gamenameFromFile, checkSubtitle):
		
		highestRatio = 0.0
		bestIndex = 0
		for idx, result in enumerate(results):
			try:
				# Check if the result has the correct platform (if needed)
				found_platform = self.resolveParseResult(result, 'PlatformSearchKey')
				if found_platform != '' and self.expected_platform != found_platform:
					Logutil.log('Platform mismatch. %s != %s. Result will be skipped.' % (self.expected_platform, found_platform), util.LOG_LEVEL_INFO)
					continue
				
				searchKey = self.resolveParseResult(result, 'SearchKey')
				# keep it for later reference
				origSearchKey = searchKey
				gamenameToCheck = gamenameFromFile
				
				# searchKey is specified in parserConfig - if no one is specified first result is valid (1 file per game scenario)
				if searchKey == '':
					Logutil.log('No searchKey found. Using first result', util.LOG_LEVEL_INFO)
					return result, 1.0
				
				Logutil.log('Comparing %s with %s' % (gamenameToCheck, searchKey), util.LOG_LEVEL_INFO)
				if self.compareNames(gamenameToCheck, searchKey, checkSubtitle):
					# perfect match
					return result, 1.0
						
				# try again with normalized names
				gamenameToCheck = self.normalizeName(gamenameToCheck)
				searchKey = self.normalizeName(searchKey)
				Logutil.log('Try normalized names. Comparing %s with %s' % (gamenameToCheck, searchKey), util.LOG_LEVEL_INFO)
				if self.compareNames(gamenameToCheck, searchKey, checkSubtitle):
					# perfect match
					return result, 1.0
							
				# try again with replaced sequel numbers
				sequelGamename = gamenameToCheck
				sequelSearchKey = searchKey
				for j in range(0, len(self.digits)):
					sequelGamename = sequelGamename.replace(self.digits[j], self.romes[j])
					sequelSearchKey = sequelSearchKey.replace(self.digits[j], self.romes[j])
				
				Logutil.log('Try with replaced sequel numbers. Comparing %s with %s' % (sequelGamename, sequelSearchKey), util.LOG_LEVEL_INFO)
				if self.compareNames(sequelGamename, sequelSearchKey, checkSubtitle):
					# perfect match
					return result, 1.0
				
				# remove last char for sequel number 1 from gamename
				if gamenameFromFile.endswith(' 1') or gamenameFromFile.endswith(' I'):
					gamenameRemovedSequel = sequelGamename[:len(sequelGamename) - 1]
					Logutil.log('Try with removed sequel numbers. Comparing %s with %s' % (gamenameRemovedSequel, sequelSearchKey), util.LOG_LEVEL_INFO)
					if self.compareNames(gamenameRemovedSequel, sequelSearchKey, checkSubtitle):
						# perfect match
						return result, 1.0
				
				# remove last char for sequel number 1 from result (check with gamenameFromFile because we need the ' ' again)
				if origSearchKey.endswith(' 1') or origSearchKey.endswith(' I'):
					searchKeyRemovedSequels = sequelSearchKey[:len(sequelSearchKey) - 1]
					Logutil.log('Try with removed sequel numbers. Comparing %s with %s' % (sequelGamename, searchKeyRemovedSequels), util.LOG_LEVEL_INFO)
					if self.compareNames(sequelGamename, searchKeyRemovedSequels, checkSubtitle):
						# perfect match
						return result, 1.0
				
				
				ratio = difflib.SequenceMatcher(None, sequelGamename.upper(), sequelSearchKey.upper()).ratio()
				Logutil.log('No result found. Try to find game by ratio. Comparing %s with %s, ratio: %s' % (sequelGamename, sequelSearchKey, str(ratio)), util.LOG_LEVEL_INFO)
				
				if ratio > highestRatio:
					highestRatio = ratio
					bestIndex = idx
					
			except Exception, (exc):
				Logutil.log("An error occured while matching the best result: " + str(exc), util.LOG_LEVEL_WARNING)
		
		return results[bestIndex], highestRatio

	def compareNames(self, gamename, searchkey, checkSubtitle):
		if checkSubtitle:
			if searchkey.find(gamename) > -1:
				Logutil.log('%s is a subtitle of %s. Using result %s' % (gamename, searchkey, searchkey), util.LOG_LEVEL_INFO)
				return True
		else:
			if gamename == searchkey:
				Logutil.log('Perfect match. Using result %s' % searchkey, util.LOG_LEVEL_INFO)
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
		Logutil.log('Check sequel numbers for "%s" and "%s".' % (gamenameFromFile, searchKey), util.LOG_LEVEL_INFO)
		
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
			Logutil.log('"%s" and "%s" both don\'t contain a sequel number. Skip checking sequel number match.' % (gamenameFromFile, searchKey), util.LOG_LEVEL_INFO)
			return True
		
		if (indexGamename == -1 or indexSearchKey == -1) and (indexGamename == 9 or indexSearchKey == 9):
			Logutil.log('"%s" and "%s" seem to be sequel number 1. Skip checking sequel number match.' % (gamenameFromFile, searchKey), util.LOG_LEVEL_INFO)
			return True
		
		if indexGamename != indexSearchKey:
			Logutil.log('Sequel number index for "%s" : "%s"' % (gamenameFromFile, str(indexGamename)), util.LOG_LEVEL_INFO)
			Logutil.log('Sequel number index for "%s" : "%s"' % (searchKey, str(indexSearchKey)), util.LOG_LEVEL_INFO)
			Logutil.log('Sequel numbers don\'t match. Result will be skipped.', util.LOG_LEVEL_INFO)
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
									
		except Exception, (exc):
			Logutil.log("Error while resolving item: " + itemName + " : " + str(exc), util.LOG_LEVEL_WARNING)
						
		try:
			Logutil.log("Result " + itemName + " = " + resultValue, util.LOG_LEVEL_DEBUG)
		except:
			pass
				
		return resultValue
