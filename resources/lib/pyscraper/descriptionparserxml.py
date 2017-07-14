
from descriptionparser import DescriptionParser
from xml.etree import ElementTree as ET

import util
from util import Logutil


class DescriptionParserXml(DescriptionParser):
	
	def __init__(self, grammarNode):
		self.grammarNode = grammarNode
		
	
	def prepareScan(self, descFile, descParseInstruction):
		pass

	def applyGrammerToDescription(self, description):
		"""
		Using the GameGrammar node for this scraper, parse the description
		Args:
			description:

		Returns:
			List containing the search result dicts
		"""
		tree = ET.fromstring(description)

		rootElementXPath = self.grammarNode.attrib.get('root', '.')
		rootElements = tree.findall(rootElementXPath)

		if rootElements is None:
			log.warn("Unable to find root element {0} in description".format(rootElementXPath))
			return []

		resultList = []

		for rootElement in rootElements:
			tempResults = self.parseElement(rootElement)
			if tempResults is None:
				continue

			resultList.append(self.replaceResultTokens(tempResults))

		return resultList

	def parseDescription(self, descFile, encoding):
		"""
		Get a "description" (i.e. a search result) and process it according to the GrammarNode for the site we are
		using.

		Args:
			descFile: Either a URL or a file path to the source of the "description"
			encoding:

		Returns:
			A list of dicts with keys matching the GameGrammar elements, or None if there was an error parsing.

			Each dict in the list is a matching search result.
		"""

		Logutil.log('parseDescription: %s' % descFile, util.LOG_LEVEL_INFO)

		# Parse the description
		descFile = self.getDescriptionContents(descFile)

		# Apply the GrammarNode rules to find the data
		return self.applyGrammerToDescription(descFile)
	
	
	def scanDescription(self, descFile, descParseInstruction, encoding):
		
		Logutil.log('scanDescription: %s' % descFile, util.LOG_LEVEL_INFO)

		descFile = self.getDescriptionContents(descFile)
		
		#load xmlDoc as elementtree to check with xpaths
		tree = ET.fromstring(descFile)
		del descFile
		
		#single result as dictionary
		result = {}
					
		rootElement = self.grammarNode.attrib.get('root')
				
		for node in tree.findall(rootElement):
			result = self.parseElement(node)
			result = self.replaceResultTokens(result)
			yield result

			
	def parseElement(self, sourceTree):
		#single result as dictionary
		result = {}
		
		for parserNode in self.grammarNode:
					
			resultKey = parserNode.tag
			xpath = parserNode.text
			sourceRoot = sourceTree
				
			if(xpath == None):
				continue
			
			#check if xpath uses attributes for searching
			parts = xpath.split('[@')
			
			if(len(parts) == 2):
				xpathRest = str(parts[1])
				attribnameIndex = xpathRest.find('="')
				searchedattribname = xpathRest[0:attribnameIndex]
				searchedvalue = xpathRest[attribnameIndex +2: xpathRest.find('"', attribnameIndex +2)]
				
				resultValues = []
				sourceElements = sourceRoot.findall(parts[0])
				for sourceElement in sourceElements:
					attribute = sourceElement.attrib.get(searchedattribname)
					if(attribute != searchedvalue):
						continue
										
					if xpath.find(']/') != -1:
						parts = xpath.split(']/')
						attribute = sourceElement.attrib.get(parts[1])
						resultValues.append(attribute)
					else:
						resultValues.append(sourceElement.text)
			else:
				#check if xpath targets an attribute 
				parts = xpath.split('/@')
				if(len(parts) > 2):
					print("Usage error: wrong xpath! Only 1 attribute allowed")
					continue
				
				resultValues = []
				
				#check only the first part without attribute (elementtree does not support attributes as target)			
				elements = sourceRoot.findall(parts[0])
								
				for element in elements:
					#if search for attribute
					if(len(parts) > 1):
						attribute = element.attrib.get(parts[1])
						resultValues.append(attribute)
						#print "found attribute: " +attribute
					else:
						if(element.text != None):
							resultValues.append(element.text.encode('utf-8'))					
						#print "found result: " +element.text
			
			try:
				resultEntry = result[resultKey]
				resultEntry.append(resultValues)
				result[resultKey] = resultEntry
			except:
				result[resultKey] = resultValues
									
		return result
		
		
		