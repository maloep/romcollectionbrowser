
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class Developer(DataBaseObject):

    developerIdByGameIdQuery = "SELECT developerId From Game Where Id = ?"
    
    developerIdCountQuery = "SELECT count(developerId) 'developerIdCount' \
                    from Game \
                    where developerId = ? \
                    group by developerId"
    
    developerDeleteQuery = "DELETE FROM Developer WHERE id = ?"


    def __init__(self, gdb):        
        self._gdb = gdb
        self._tableName = "Developer"
        
        self.id = None
        self.name = ''
        
    
    def fromDb(self, row):
        developer = Developer(self._gdb)
        
        if(not row):
            return developer
        
        developer.id = row[util.ROW_ID]
        developer.name = row[util.ROW_NAME]
        
        return developer
    

    def getDeveloperIdByGameId(self, gameId):
        developerId = self.getObjectByQuery(self.developerIdByGameIdQuery, (gameId,))
        if(developerId == None):
            return None
        else:
            return developerId[0]
    
    def delete(self, gameId):
        developerId = self.getDeveloperIdByGameId(gameId)
        if(developerId != None):
            object = self.getObjectByQuery(self.developerIdCountQuery, (developerId,))
            if (object[0] < 2):
                util.Logutil.log("Delete Developer with id %s" % str(developerId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.developerDeleteQuery, (developerId,))
