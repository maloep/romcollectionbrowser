
import os
import sys
import time


# Shared resources

BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )

sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "pyparsing" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "pyscraper" ) )

# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
if env == 'Windows_NT':
    env = 'win32'
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", 'Linux' ) )
import xbmc
import xbmcgui

from pysqlite2 import dbapi2 as sqlite
from gamedatabase import *
from util import *
import dbupdate
import config



class ProgressDialogBk:
    
    def __init__(self, *args, **kwargs):      
        self.itemCount = 0         
        self.head = None
        self.label = None
        #self.progress = xbmcgui.ControlProgress(100, 250, 125, 75)
        #self.progress.setVisible(True)
        
    def onInit(self): 
        self.head = self.getControl(701)
        self.label = self.getControl(702)
        self.progress = self.getControl(703)
    
    def writeMsg(self, line1, line2, line3, count=0):
        percent = int(count * (float(100) / self.itemCount))
        #self.progress.setPercent(percent)
        if not self.head:
          return True  
        elif (not count):
            self.head.setLabel(line1)
        elif (count > 0):
            percent = int(count * (float(100) / self.itemCount))
            self.head.setLabel(line1)
            self.label.setLabel(line2)
            self.progress.setPercent(percent)
            
        else:
            self.close()
            
        return True

def runUpdate():
    gdb = GameDataBase(util.getAddonDataPath())
    gdb.connect()
    configFile = config.Config()
    statusOk, errorMsg = configFile.readXml()
    progress = ProgressDialogBk("script-RCB-scanDialog.xml", util.getAddonInstallPath(), "Default", "PAL")
    dbupdate.DBUpdate().updateDB(gdb, progress, 0, configFile.romCollections)
    del progress
    
    
if __name__ == "__main__":
    runUpdate()




