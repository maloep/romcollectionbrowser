
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class Platform(DataBaseObject):
    def __init__(self, gdb):
        self._gdb = gdb
        self._tableName = "Game"
        
        self.id = None
        self.name = ''
        self.description = ''
        self.manufacturer = None
        self.developer = None
        self.cpu = ''
        self.memory = ''
        self.graphics = ''
        self.sound = ''
        self.display = ''
        self.media = ''
        self.maxcontrollers = ''
        self.releasedate = ''
        self.hasonlinefeatures = ''
        self.originalprice = ''
        
        self.artworkurls = {}
        
        
    def fromDb(self, row):
        if(not row):
            return None
        
        platform = Platform(self._gdb)
        platform.id = row[util.ROW_ID]
        platform.name = row[util.ROW_NAME]
        
        return platform
        
        
    def toDbDict(self, platform):
        platformdict = {}
        platformdict['id'] = platform.id
        platformdict['name'] = platform.name 
        platformdict['description'] = platform.description
        return platformdict