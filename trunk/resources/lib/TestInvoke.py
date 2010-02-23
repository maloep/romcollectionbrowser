
import os, sys

import getpass, ntpath, re, string
from xml.dom.minidom import Document, parseString
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *


class InvokeTest:
	
	gdb = GameDataBase(os.path.join(os.getcwd(), '..', 'database'))
	
	def __init__(self):
		# Changing the three varibles passed won't change, anything
		# Doing strXMLname = "bah.xml" will not change anything.
		# don't put GUI sensitive stuff here (as the xml hasn't been read yet
		# Idea to initialize your variables here		
		print "Invoke ShowConsoles"
		self.showConsoles()	
	
	
	def showConsoles(self):
		# Fill list
		print "Begin ShowConsoles"
		
		#self.gdb.prepareTestData()
		consoles = Console(self.gdb).getAll()
		
		print "ShowConsoles " +str(consoles)				
		
		for console in consoles:
			print "ShowConsoles " +str(console)
			
	
	def showGames(self):
		# Fill list
		print "Begin ShowConsoles"
		
		#self.gdb.prepareTestData()
		games = Game(self.gdb).getAll()
		
		print "ShowConsoles " +str(consoles)				
		
		for console in consoles:
			print "ShowConsoles " +str(console)


def main():  
	#ui = InvokeTest()

	gdb = GameDataBase(os.path.join(os.getcwd(), '..', 'database'))
	gdb.connect()
	gdb.dropTables()		
	gdb.createTables()
	gdb.commit()
	#gdb.prepareTestDataBase()
	gdb.close()

	#game = Game(gdb)
	#print str(game.getAll())

#del gdb

	

main()