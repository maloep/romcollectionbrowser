import unittest
import os, sys

# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), ".." )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

import re, string
from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *
import dbupdate, importsettings


class TestAlterTable(unittest.TestCase):
	def setUp(self):
		self.databasedir = os.path.join( os.getcwd(), 'TestDataBase')
		self.gdb = GameDataBase(self.databasedir)
		self.gdb.connect()
		self.gdb.dropTables()		
		
		
	def test_V03toV04(self):
		#create Table V0.3
		self.gdb.executeSQLScript(os.path.join(self.databasedir, 'SQL_CREATE_V0.3.txt'))
		#insert data
		self.gdb.executeSQLScript(os.path.join(self.databasedir, 'SQL_INSERT_TEST_DATA_V0.3.txt'))

		self.gdb.checkDBStructure()
		
		#TODO Test SELECT
		
		
		
		
			
		
unittest.main()