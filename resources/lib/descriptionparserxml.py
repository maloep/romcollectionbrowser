
from elementtree.ElementTree import *
import urllib
import time


class DescriptionParserXml:
	
	def __init__(self, grammarNode):
		self.grammarNode = grammarNode
		
	
	def prepareScan(self, descFile, descParseInstruction):
		pass
	
	
	def parseDescription(self, descFile):
		
		results = None						
						
		if(descFile.startswith('http://')):			
			descFile = descFile.replace(" ", "%20")
			descFile = urllib.urlopen(descFile)				
		
		#load xmlDoc as elementtree to check with xpaths
		tree = ElementTree().parse(descFile)			
		if(tree == None):
			return None				
		
		rootElementXPath = self.grammarNode.attrib.get('root')
		rootElements = tree.findall(rootElementXPath)
		if(rootElements == None):
			return None
		
		resultList = []
		
		for rootElement in rootElements:
			tempResults = self.parseElement(rootElement)
			if tempResults != None:
				results = tempResults
				results = self.replaceResultTokens(results)
				resultList.append(results)
		
		return resultList
	
	
	def scanDescription(self, descFile, descParseInstruction):		
		
		if(descFile.startswith('http://')):
			descFile = descFile.replace(' ', '%20')
			descFile = urllib.urlopen(descFile)
		
		#load xmlDoc as elementtree to check with xpaths
		tree = ElementTree().parse(descFile)
		
		#single result as dictionary
		result = {}
					
		rootElement = self.grammarNode.attrib.get('root')		
				
		for node in tree.findall(rootElement):
			result = self.parseElement(node)
			result = self.replaceResultTokens(result)
			yield result
	
	
	#TODO: make a base class and make this a base method
	def replaceResultTokens(self, resultAsDict):
		for key in resultAsDict.keys():			
			grammarElement = self.grammarNode.find(key)
			if(grammarElement != None):
				appendResultTo = grammarElement.attrib.get('appendResultTo')
				replaceKeyString = grammarElement.attrib.get('replaceInResultKey')
				replaceValueString = grammarElement.attrib.get('replaceInResultValue')
				dateFormat = grammarElement.attrib.get('dateFormat')
														
				#TODO: avoid multiple loops
				if(appendResultTo != None or dateFormat != None):									
					itemList = resultAsDict[key]
					for i in range(0, len(itemList)):
						try:							
							item = itemList[i]
							if(appendResultTo != None):								
								newValue = appendResultTo +item
							elif(dateFormat != None):
								newValue = time.strptime(item, dateFormat)
							itemList[i] = newValue
						except:
							print "Error while handling appendResultTo"
							
					resultAsDict[key] = itemList
					
				if(replaceKeyString != None and replaceValueString != None):												
					replaceKeys = replaceKeyString.split(',')
					replaceValues = replaceValueString.split(',')
					
					if(len(replaceKeys) != len(replaceValues)):
						print "Configuration error: replaceKeys must be the same number as replaceValues"
					
					itemList = resultAsDict[key]
					for i in range(0, len(itemList)):
						try:							
							item = itemList[i]
							
							for j in range(len(replaceKeys)):
								replaceKey = replaceKeys[j]
								replaceValue = replaceValues[j]
															
								newValue = item.replace(replaceKey, replaceValue)							
								itemList[i] = newValue
						except:
							print "Error while handling appendResultTo"
							
					resultAsDict[key] = itemList
				
		return resultAsDict			

			
	def parseElement(self, tree):
		#single result as dictionary
		result = {}					
		
		for node in self.grammarNode:
			
			resultKey = node.tag
			nodeValue = node.text				
			#print "Looking for: " +str(resultKey)
			#print "using xpath: " +str(nodeValue)
				
			if(nodeValue == None):
				continue
			
			#check if xpath targets an attribute 
			parts = nodeValue.split('/@')
			if(len(parts) > 2):
				print("Usage error: wrong xpath! Only 1 attribute allowed")
							
			#check only the first part without attribute (elementtree does not support attributes as target)			
			elements = tree.findall(parts[0])					
			
			resultValues = []
			for element in elements:
				#if search for attribute
				if(len(parts) > 1):
					attribute = element.attrib.get(parts[1])
					resultValues.append(attribute)
					#print "found attribute: " +attribute
				else:
					resultValues.append(element.text)					
					#print "found result: " +element.text
				
			try:
				resultEntry = result[resultKey]
				resultEntry.append(resultValues)
				result[resultKey] = resultEntry
			except:
				result[resultKey] = resultValues
									
		return result
		
		
		