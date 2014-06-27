import unittest
import os, sys
import re, string


# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), ".." )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "pyscraper" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "pyparsing" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
if env == 'Windows_NT':
	env = 'win32'
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )


try:
	print "Loading sqlite3 as DB engine"
	from sqlite3 import dbapi2 as sqlite	
except:
	from pysqlite2 import dbapi2 as sqlite
	print "Loading pysqlite2 as DB engine"
	
from gamedatabase import *
from util import *
import dbupdate
import config


class RCBMock:
	
	itemCount = 0
	
	def writeMsg(self, msg1, msg2, msg3, count=0):
		return True


#adjust settings for tests
util.RCBHOME = os.path.join(os.getcwd(), '..', '..')
#util.ISTESTRUN = True

Logutil.currentLogLevel = util.LOG_LEVEL_INFO


#Init database
databasedir = os.path.join( os.getcwd())
gdb = GameDataBase(databasedir)
gdb.connect()
gdb.dropTables()		
gdb.createTables()

util.ISTESTRUN = True

configFile = config.Config(None)
statusOk, errorMsg = configFile.readXml()

newRCs = {}

newRCs[1] = configFile.romCollections['3']

"""
from guppy import hpy
h = hpy()
h.setref()
"""

if(statusOk == True):
	dbupdate.DBUpdate().updateDB(gdb, RCBMock(), 0, newRCs, util.getSettings(), False)

#print h.heap()
