
from elementtree.ElementTree import *

class DescriptionParserXml:
	
	def __init__(self, grammarNode):
		self.grammarNode = grammarNode
	
	def parseDescription(self, descFile):
		
		#results as list
		results = []
		
		#load xmlDoc as elementtree to check with xpaths
		tree = ElementTree().parse(descFile)
		
		rootElementXPath = self.grammarNode.attrib.get('root')
		rootElement = tree.find(rootElementXPath)
		
		result = self.parseElement(rootElement)
		
		return result
	
	
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
				
			elements = tree.findall(nodeValue)
			resultValues = []
			for element in elements:
				resultValues.append(element.text)					
				#print "found result: " +element.text
				
			try:
				resultEntry = result[resultKey]
				resultEntry.append(resultValues)
				result[resultKey] = resultEntry
			except:
				result[resultKey] = resultValues
									
		return result
	
	
	def prepareScan(self, descFile, descParseInstruction):
		pass
	
	
	def scanDescription(self, descFile, descParseInstruction):		
		#load xmlDoc as elementtree to check with xpaths
		tree = ElementTree().parse(descFile)
		
		#single result as dictionary
		result = {}
					
		rootElement = self.grammarNode.attrib.get('root')		
		
		#TODO get game node xpath from config
		for node in tree.findall(rootElement):
			
			result = self.parseElement(node)
						
			yield result
		
		
		