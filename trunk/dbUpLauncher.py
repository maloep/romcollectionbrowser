
import os
import sys
import time


# Shared resources

BASE_RESOURCE_PATH = os.path.join( '/home/jaime/Desarrollo/romcollectionbrowser/trunk', "resources" )

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


ALLOWEDWINDOWS = [10000]

class ProgressDialogBk:
    
    itemCount = 1
    label = None
    progress = None
    windowID = None
    
    
    def __init__(self):
        self.paintProgress()
    
    def paintProgress(self):
        self.windowID = xbmcgui.getCurrentWindowId()
        self.window = xbmcgui.Window(self.windowID)
        self.image = xbmcgui.ControlImage(880, 630, 400, 60, "InfoMessagePanel.png", colorDiffuse='0xC0C0C0C0')
        self.window.addControl(self.image)
        self.image.setVisible(False)
        animations = [('Conditional', 'effect=slide start=1280,0 time=2000 condition=Control.IsVisible(%d)' % self.image.getId())]
        self.image.setAnimations(animations)
        
        self.header = xbmcgui.ControlLabel(900, 635, 400, 60, 'Scraping RCB', font='font10_title', textColor='0xFFEB9E17')
        self.window.addControl(self.header)
        self.header.setVisible(False)
        self.header.setAnimations(animations)
        
        self.label = xbmcgui.ControlLabel(900, 655, 400, 60, 'Scraping RCB', font='font10')
        self.window.addControl(self.label)
        self.label.setVisible(False)
        self.label.setAnimations(animations)

        self.progress = xbmcgui.ControlProgress(900, 675, 370, 8)
        self.window.addControl(self.progress)
        self.progress.setVisible(False)
        self.progress.setAnimations(animations)
        
        self.label.setVisible(True)
        self.image.setVisible(True)
        self.progress.setVisible(True)
        self.header.setVisible(True)
            
    def writeMsg(self, line1, line2, line3, count=0):
        
        print "estoy en la ventana: %d" % xbmcgui.getCurrentWindowId()
        if self.windowID != xbmcgui.getCurrentWindowId():
            self.windowID = xbmcgui.getCurrentWindowId()
            if xbmcgui.getCurrentWindowId() in ALLOWEDWINDOWS:
                self.paintProgress()
        
        if not self.label:
          return True  
        elif (count > 0):
            percent = int(count * (float(100) / self.itemCount))
            self.header.setLabel(line1)
            self.label.setLabel("%d %% - %s" % (percent, line2))
            self.progress.setPercent(percent)
            
        else:
            self.window.remove(self.image)
            self.window.remove(self.header)
            self.window.remove(self.label)
            self.window.remove(self.progress)
            
        return True

def runUpdate():
    gdb = GameDataBase(util.getAddonDataPath())
    gdb.connect()
    configFile = config.Config()
    statusOk, errorMsg = configFile.readXml()
    progress = ProgressDialogBk()
    dbupdate.DBUpdate().updateDB(gdb, progress, 0, configFile.romCollections)
    
    
if __name__ == "__main__":
    runUpdate()




