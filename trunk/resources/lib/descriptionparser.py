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
				
			delimiter = node.attributes.get('delimiter')
			if(delimiter != None):				
				nodeGrammar += (Optional(~LineEnd() +commaSeparatedList))		
			elif (isRol):				
				nodeGrammar += rolGrammar
				
			skipTo = node.attributes.get('skipTo')
			if(skipTo != None):
				nodeGrammar += SkipTo(Literal(skipTo.nodeValue))

			if(node.nodeName == 'SkippableContent'):				
				if(literal != None):
					nodeGrammar += Suppress(literal)				
			else:
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
		
		#print results.asList()
		#for result in results:
		#	print result.asDict()
		
		return results
		
	
	
	
	
	def parseDescriptionConfig(self, descFile, descParseInstruction, gamename):
		print descFile
		
		#TODO Entries before game?
		star = Suppress(Literal('*')) +Suppress(LineEnd())
		star = star.setResultsName('star')
		#crc = Optional(~LineEnd() +commaSeparatedList).bug() +Suppress(LineEnd())
		crc = Optional(~LineEnd() +delimitedList(',')) +SkipTo(LineEnd()) +Suppress(LineEnd())
		crc = crc.setResultsName('crc')
		
		#TODO handle different delimiters?
		
		#game = Suppress(SkipTo(Literal())) +Literal(gamename) +Suppress(LineEnd())
		game = Optional(~LineEnd() +delimitedList(',')) +SkipTo(LineEnd())
		game = game.setResultsName('game')		
		platform = Suppress(Literal('Platform: ')) +(Optional(~LineEnd() +commaSeparatedList))
		platform = platform.setResultsName('platform')
		region = Suppress(Literal('Region: ')) +(Optional(~LineEnd() +commaSeparatedList))
		region = region.setResultsName('region')		
		media = Suppress(Literal('Media: ')) +(Optional(~LineEnd() +commaSeparatedList))
		media = media.setResultsName('media').setDebug()		
		controller = Suppress(Literal('Controller: ')) +(Optional(~LineEnd() +commaSeparatedList))
		controller = controller.setResultsName('controller')
		#TODO Item Delimiter		
		genre = Suppress(Literal('Genre: ')) +(Optional(~LineEnd() +commaSeparatedList))
		genre = genre.setResultsName('genre')				
		year = Suppress(Literal('Release Year: ')) +(Optional(~LineEnd() +commaSeparatedList))
		year = year.setResultsName('year')				
		dev = Suppress(Literal('Developer: ')) +(Optional(~LineEnd() +commaSeparatedList))
		dev = dev.setResultsName('developer')				
		publisher = Suppress(Literal('Publisher: ')) +(Optional(~LineEnd() +commaSeparatedList))
		publisher = publisher.setResultsName('publisher')
		players = Suppress(Literal('Players: ')) +(Optional(~LineEnd() +commaSeparatedList))
		players = players.setResultsName('players')
		line = Suppress(Combine(OneOrMore(Literal('_'))))
		line = line.setResultsName('line')
		#star = Suppress(Literal('*') +LineEnd())
		#star = star.setResultsName('star')
		#desc = SkipTo(star)
		desc = ZeroOrMore(unicode(Word(printables + alphas8bit))) +SkipTo(star)
		desc = desc.setResultsName('description')
		delimiter = Suppress(SkipTo(LineEnd()))
		gamegrammar = star +crc +game +platform + region + media + controller + genre \
			+ year + dev +publisher +players +line + star +desc +delimiter
		
		filegrammar = OneOrMore(gamegrammar)
		
		fh = open(str(descFile), 'r')
		fileAsString = fh.read()		
		fileAsString = fileAsString.decode('iso-8859-15')		
				
		results = filegrammar.parseString(fileAsString)
		
		return results



def main():
	dp = DescriptionParser()
	results = dp.parseDescription('E:\\Emulatoren\\data\\Amiga\\Collection V1\\synopsis\\synopsis parserTest.txt', 
		'C:\\Dokumente und Einstellungen\\lom\\Anwendungsdaten\\XBMC\\scripts\\RomCollectionBrowser\\resources\\database\\parserConfig.xml', 'Football Glory')
	print results	
	del dp
	
#main()