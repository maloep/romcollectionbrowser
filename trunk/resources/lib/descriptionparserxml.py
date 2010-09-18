
from elementtree.ElementTree import *
import urllib


class DescriptionParserXml:
	
	def __init__(self, grammarNode):
		self.grammarNode = grammarNode
		
	
	def prepareScan(self, descFile, descParseInstruction):
		pass
	
	
	def parseDescription(self, descFiles):
		
		results = None
		for descFile in descFiles:												
				
			print "descFile: " +str(descFile)
							
			if(descFile.startswith('http://')):
				print "urlopen"
				descFile = descFile.replace(" ", "%20")
				descFile = urllib.urlopen(descFile)
				print "urlopen done"					
			
			#load xmlDoc as elementtree to check with xpaths
			tree = ElementTree().parse(descFile)			
			if(tree == None):
				continue
			
			rootElementXPath = self.grammarNode.attrib.get('root')
			rootElement = tree.find(rootElementXPath)
			if(rootElement == None):
				continue
			
			tempResults = self.parseElement(rootElement)
			if tempResults != None:
				results = tempResults
		
		return results	
	
	
	def scanDescription(self, descFile, descParseInstruction):		
		
		if(descFile.startswith('http://')):
			descFile = urllib.urlopen(descFile)
		
		#load xmlDoc as elementtree to check with xpaths
		tree = ElementTree().parse(descFile)
		
		#single result as dictionary
		result = {}
					
		rootElement = self.grammarNode.attrib.get('root')		
		
		#TODO get game node xpath from config
		for node in tree.findall(rootElement):
			
			result = self.parseElement(node)
						
			yield result
			

			
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
		
		
		