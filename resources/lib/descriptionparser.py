# -*- coding: iso-8859-15 -*-

import os, sys, re
import codecs

#taken from apple movie trailer script (thanks to Nuka1195 and others)
# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

from pyparsing import *
from string import lowercase

from xml.dom.minidom import Document, Node, parseString


class DescriptionParser:
	
	def parseDescription(self, descFile, descParseInstruction, gamename):
		
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
			results = self.parseMultiline(descFile, grammarNode, gamename)
			
		return results
		
		
		
	def parseMultiline(self, descFile, grammarNode, gamename):
		
		grammarList = []
		rolGrammar = SkipTo(LineEnd()) +Suppress(LineEnd())
	
		appendNextNode = False
		appendToPreviousNode = False
		lastNodeGrammar = Empty()
		
		for node in grammarNode.childNodes:			
			
			if (node.nodeType != Node.ELEMENT_NODE):
				continue
			
			#appendToPreviousNode was set at the end of the last loop
			if(appendToPreviousNode):				
				nodeGrammar = lastNodeGrammar
			else:					
				nodeGrammar = Empty()
			
			literal = None
			if (node.hasChildNodes()):				
				literal = Literal(node.firstChild.nodeValue)
							
			rol = node.attributes.get('restOfLine')
			if(rol != None and rol.nodeValue == 'true'):
				isRol = True
				#appendNextNode is used in the current loop
				appendNextNode = False
			else:
				isRol = False
				appendNextNode = True
				
			skipTo = node.attributes.get('skipTo')
			if(skipTo != None):
				nodeGrammar += SkipTo(Literal(skipTo.nodeValue))

			if(node.nodeName == 'SkippableContent'):				
				if(literal != None):
					nodeGrammar += Suppress(literal)			
				
			delimiter = node.attributes.get('delimiter')
			if(delimiter != None):				
				nodeGrammar += (Optional(~LineEnd() +commaSeparatedList))
			elif (isRol):		
				nodeGrammar += rolGrammar
				
			nodeGrammar = nodeGrammar.setResultsName(node.nodeName)
						
			if(appendNextNode == False):				
				grammarList.append(nodeGrammar)	
				
			if(isRol == True):			
				appendToPreviousNode = False
				lastNodeGrammar = Empty()
			else:
				appendToPreviousNode = True
				lastNodeGrammar += nodeGrammar
				

		grammar = ParserElement()
		for grammarItem in grammarList:			
			grammar += grammarItem
		
		gameGrammar = Group(grammar)
		
		all = OneOrMore(gameGrammar)		
		
		fh = open(str(descFile), 'r')
		fileAsString = fh.read()		
		fileAsString = fileAsString.decode('iso-8859-15')		
		
		results = all.parseString(fileAsString)		
				
		return results



def main():
	dp = DescriptionParser()
	results = dp.parseDescription('E:\\Emulatoren\\data\\Test synopsis\\xtras.txt', 
		'E:\\Emulatoren\\data\\Test synopsis\\xtras.xml', '')
	for result in results:
		print result.asDict()
	del dp
	
#main()