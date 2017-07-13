
import time
import urllib2

class DescriptionParser(object):
	def __init__(self):
		pass

	def downloadDescription(self):
		pass

	def openFile(self):
		pass

	def getDescriptionContents(self, descFile):
		if(descFile.startswith('http://')):
			req = urllib2.Request(descFile)
			req.add_unredirected_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31')
			fileAsString = urllib2.urlopen(req).read()
			del req
		else:
			fh = open(str(descFile), 'r')
			fileAsString = fh.read()
			del fh

		return fileAsString

	def replaceResultTokens(self, resultAsDict):
		"""
		Process the description dict according to the GameGrammar for this scraper
		Args:
			resultAsDict: A dictionary containing a key for each field returned by the scraper (e.g. Game,
				ReleaseYear, Description) and a value list

		Returns:
			A dictionary with each element processed according to the GrammarNode
		"""
		# resultAsDict
		# Each GameGrammar node will have a key e.g. Game, ReleaseYear, Description and a list with the value(s)
		log.debug("replaceResultTokens: {0}".format(resultAsDict))
		for key in resultAsDict.keys():
			grammarElement = self.grammarNode.find(key)
			if grammarElement is None:
				log.warn("Could not find grammar element to describe result field {0}".format(key))
				continue

			itemList = resultAsDict[key]
			for i in range(0, len(itemList)):
				try:
					item = itemList[i]
					newValue = item
					del item

					# Add prefix and suffix - appends/prepends empty string if not found in dict
					newValue = "{0}{1}{2}".format(grammarElement.attrib.get('appendResultTo', ''),
						newValue,
						grammarElement.attrib.get('appendResultWith', ''))

					# Parse ReleaseYear (for some parsers)
					if 'dateFormat' in grammarElement.attrib:
						if grammarElement.attrib.get('dateFormat') == 'epoch':
							# Used only for archive.vg
							try:
								newValue = time.gmtime(int(newValue))
							except Exception as e:
								print 'error converting timestamp: ' + str(newValue) + ': ' + str(e)
						else:
							# Parse according to the datetime format
							newValue = time.strptime(newValue, grammarElement.attrib.get('dateFormat'))

					itemList[i] = newValue
				except Exception as e:
					print "Error while parsing result with GrammarNode: " + str(e)

			resultAsDict[key] = itemList

			# This is only used in archive.vg
			replaceKeyString = grammarElement.attrib.get('replaceInResultKey')
			replaceValueString = grammarElement.attrib.get('replaceInResultValue')
			if replaceKeyString is not None and replaceValueString is not None:
				replaceKeys = replaceKeyString.split(',')
				replaceValues = replaceValueString.split(',')

				if len(replaceKeys) != len(replaceValues):
					log.warn("Configuration error: replaceKeys must be the same number as replaceValues")

				itemList = resultAsDict[key]
				for i in range(0, len(itemList)):
					try:
						tokens = zip(replaceKeyString.split(','), replaceValueString.split(','))
						for (k, v) in tokens:
							itemList[i] = itemList[i].replace(k, v)

					except Exception as e:
						log.warn("Error while handling appendResultTo: " + str(e))

				resultAsDict[key] = itemList
				del itemList

		return resultAsDict
