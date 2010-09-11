# -*- coding: iso-8859-15 -*-

from elementtree.ElementTree import Element
from descriptionparserflatfile import *
from descriptionparserxml import *


class DescriptionParserFactory:

	@classmethod
	def getParser(self, descParseInstruction):		
				
		fh=open(descParseInstruction,"r")		
		xmlDoc = fh.read()		
		fh.close()
		
		tree = ElementTree().parse(descParseInstruction)		
		
		grammarNode = tree.find('GameGrammar')
		if(grammarNode == None):
			return "";
					
		attributes = grammarNode.attrib
		
		parserType = attributes.get('type')					
		if(parserType == 'multiline'):
			return DescriptionParserFlatFile(grammarNode)			
		elif(parserType == 'xml'):
			return DescriptionParserXml(grammarNode)
		else:
			print "Unknown parser: " +parserType
			return None		
		
		
	
