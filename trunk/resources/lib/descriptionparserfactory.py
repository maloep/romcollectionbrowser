# -*- coding: iso-8859-15 -*-

from xml.dom.minidom import parseString, Node, Document
from descriptionparserflatfile import *
from descriptionparserxml import *


class DescriptionParserFactory:

	@classmethod
	def getParser(self, descParseInstruction):
		
		#configFile = os.path.join(databaseDir, 'parserConfig.xml')
		fh=open(descParseInstruction,"r")
		xmlDoc = fh.read()
		fh.close()
		
		xmlDoc = parseString(xmlDoc)
		
		gameGrammar = xmlDoc.getElementsByTagName('GameGrammar')
		if(gameGrammar == None):
			return "";
			
		grammarNode = gameGrammar[0]
		attributes = grammarNode.attributes
		
		attrNode = attributes.get('type')
		if(attrNode == None):
			return "";
			
		parserType = attrNode.nodeValue
		if(parserType == 'multiline'):
			return DescriptionParserFlatFile(grammarNode)			
		elif(parserType == 'xml'):
			return DescriptionParserXml(grammarNode)		
		
		
	
