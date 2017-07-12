
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

			appendResultTo = grammarElement.attrib.get('appendResultTo')
			appendResultWith = grammarElement.attrib.get('appendResultWith')
			replaceKeyString = grammarElement.attrib.get('replaceInResultKey')
			replaceValueString = grammarElement.attrib.get('replaceInResultValue')
			dateFormat = grammarElement.attrib.get('dateFormat')
			del grammarElement

			#TODO: avoid multiple loops
			if(appendResultTo != None or appendResultWith != None or dateFormat != None):
				itemList = resultAsDict[key]
				for i in range(0, len(itemList)):
					try:
						item = itemList[i]
						newValue = item
						del item
						if(appendResultTo != None):
							newValue = appendResultTo +newValue
						if(appendResultWith != None):
							newValue = newValue + appendResultWith
						if(dateFormat != None):
							if(dateFormat == 'epoch'):
								try:
									newValue = time.gmtime(int(newValue))
								except:
									print 'error converting timestamp: ' +str(newValue)
							else:
								newValue = time.strptime(newValue, dateFormat)
						itemList[i] = newValue
					except Exception, (exc):
						print "Error while handling appendResultTo: " +str(exc)

				resultAsDict[key] = itemList
				del itemList

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
