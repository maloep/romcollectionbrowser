
from xml.dom.minidom import parseString, Node, Document
from elementtree.ElementTree import *

class DescriptionParserXml:
	
	def __init__(self, grammarNode):
		self.grammarNode = grammarNode
	
	def parseDescription(self, descFile):
		
		print "load xml"
		
		#load xmlDoc as elementtree to check with xpaths
		tree = ElementTree().parse(descFile)		
		
		for node in self.grammarNode.childNodes:
			if (node.nodeType != Node.ELEMENT_NODE):
				continue
			
			if (node.hasChildNodes()):
				nodeValue = node.firstChild.nodeValue
				print nodeValue
				print node.nodeName
				
				elements = tree.findall(nodeValue)						
				for element in elements:
					print element.text										
					
				"""
				def asDict( self ):        		
          			return dict( self.items() )
          		"""
		
		return None
	
	
	def prepareScan(self, descFile, descParseInstruction):
		pass
	
	
	def scanDescription(self, descFile, descParseInstruction):		
		pass