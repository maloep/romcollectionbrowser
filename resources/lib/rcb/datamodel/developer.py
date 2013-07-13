
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class Developer(DataBaseObject):
    
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
        
        if(not row):
            return None
        
        developer = Developer(self._gdb)
        
        developer.id = row[util.ROW_ID]
        developer.name = row[util.ROW_NAME]
        
        return developer
    
    
    def delete(self, developerId):
        if(developerId != None):
            object = self.getCountByQuery(self.developerIdCountQuery, (developerId,))
            if (object[0] < 2):
                util.Logutil.log("Delete Developer with id %s" % str(developerId), util.LOG_LEVEL_INFO)
                self.deleteObjectByQuery(self.developerDeleteQuery, (developerId,))
