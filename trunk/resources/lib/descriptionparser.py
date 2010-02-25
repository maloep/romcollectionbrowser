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
			self.parseMultiline(descFile, grammarNode, gamename)
		
		
		
	def parseMultiline(self, descFile, grammarNode, gamename):
		
		grammarList = []
		rolGrammar = SkipTo(LineEnd()) +Suppress(LineEnd())
		
		for node in grammarNode.childNodes:			
			
			if (node.nodeType != Node.ELEMENT_NODE):
				continue			
			
			nodeGrammar = Optional('')
			
			literal = None
			if (node.hasChildNodes()):
				print "add ChildNode: " +node.firstChild.nodeValue
				literal = Literal(node.firstChild.nodeValue)
			
			isRol = False
			rol = node.attributes.get('restOfLine')
			if(rol != None and rol.nodeValue == 'true'):
				isRol = True
				
			delimiter = node.attributes.get('delimiter')
			if(delimiter != None):
				print "add delimiter"
				if (isRol):
					nodeGrammar += Optional(~LineEnd() +commaSeparatedList)
				else:
					nodeGrammar += Optional(commaSeparatedList)			
			elif (isRol):
				print "add restOfLine"
				nodeGrammar += rolGrammar
				
			skipTo = node.attributes.get('skipTo')
			if(skipTo != None):
				nodeGrammar += SkipTo(Literal(skipTo.nodeValue))

			if(node.nodeName == 'SkippableContent'):
				print "add SkippableContent"
				if(literal != None):
					nodeGrammar += Suppress(literal)				
			else:
				nodeGrammar = nodeGrammar.setResultsName(node.nodeName)
										
			grammarList.append(nodeGrammar)
				

		grammar = ParserElement()
		for grammarItem in grammarList:			
			grammar += grammarItem
		
		all = OneOrMore(grammar)
		
		fh = open(str(descFile), 'r')
		fileAsString = fh.read()		
		fileAsString = fileAsString.decode('iso-8859-15')		
				
		results = all.parseString(fileAsString)		
		
		print results.asXML()		
		return ""
		
	
	def parseDescriptionConfig(self, descFile, descParseInstruction, gamename):
		print descFile
		
		#TODO Entries before game?
		star = Suppress(Literal('*')) +Suppress(LineEnd())
		star = star.setResultsName('star')
		#crc = Optional(~LineEnd() +commaSeparatedList).setDebug() +Suppress(LineEnd())
		crc = Optional(~LineEnd() +delimitedList(',')) +SkipTo(LineEnd()) +Suppress(LineEnd())
		crc = crc.setResultsName('crc')
		
		#TODO handle different delimiters?
		
		#game = Suppress(SkipTo(Literal())) +Literal(gamename) +Suppress(LineEnd())
		game = Optional(~LineEnd() +delimitedList(',')) +SkipTo(LineEnd()).setDebug()
		game = game.setResultsName('game')
		#TODO csv + \r\n +optional?
		platform = Suppress(Literal('Platform: ')) +(Optional(~LineEnd() +commaSeparatedList))
		platform = platform.setResultsName('platform')
		region = Suppress(Literal('Region: ')) +(Optional(~LineEnd() +commaSeparatedList))
		region = region.setResultsName('region')
		media = Suppress(Literal('Media: ')) +(Optional(~LineEnd() +commaSeparatedList))
		media = media.setResultsName('media')
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




dp = DescriptionParser()
results = dp.parseDescription('E:\\Emulatoren\\data\\Amiga\\Collection V1\\synopsis\\synopsis parserTest.txt', 
	'C:\\Dokumente und Einstellungen\\lom\\Anwendungsdaten\\XBMC\\scripts\\RomCollectionBrowser\\resources\\database\\parserConfig.xml', 'Football Glory')
#print results
#results = dp.parseDescriptionConfig('E:\\Emulatoren\\data\\Amiga\\Collection V1\\synopsis\\synopsis parserTest.txt', '', 'Formula One Grand Prix')
#print results.asDict()
#print results['crc']
del dp