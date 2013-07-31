import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


DBINDEX_GENREGAME_genreId = 1
DBINDEX_GENREGAME_gameId = 2


class LinkGenreGame(DataBaseObject):
                    
    filterQueryByGenreIdAndGameId = "Select * from GenreGame \
                    where genreId = ? AND \
                    gameId = ?"
    
    def __init__(self, gdb):        
        self.gdb = gdb
        self.tableName = "GenreGame"
        
        self.id = None
        self.genreId = None
        self.gameId = None
        
    
    def fromDb(self, row):
        
        if(not row):
            return

        self.id = row[databaseobject.DBINDEX_id]
        self.genreId = row[DBINDEX_GENREGAME_genreId]
        self.gameId = row[DBINDEX_GENREGAME_gameId]
        
        
    def getGenreGameByGenreIdAndGameId(self, genreId, gameId):
        genreGame = self.getOneByQuery(self.filterQueryByGenreIdAndGameId, (genreId, gameId))
        return genreGame
        


DBINDEX_RELEASEPERSONROLE_releaseId = 1
DBINDEX_RELEASEPERSONROLE_personId = 2
DBINDEX_RELEASEPERSONROLE_roleId = 3


class LinkReleasePersonRole(DataBaseObject):
                    
    filterQuery = "Select * from LinkReleasePersonRole \
                    where releaseId = ? AND \
                    personId = ? AND \
                    roleId = ?"
    
    def __init__(self, gdb):        
        self.gdb = gdb
        self.tableName = "LinkReleasePersonRole"
        
        self.id = None
        self.releaseId = None
        self.personId = None
        self.roleId = None
        
        
    def toDbDict(self):
        dbdict = {}
        dbdict['id'] = self.id
        dbdict['releaseId'] = self.releaseId
        dbdict['personId'] = self.personId 
        dbdict['roleId'] = self.roleId
        return dbdict
        
    
    def fromDb(self, row):
        
        if(not row):
            return

        self.id = row[databaseobject.DBINDEX_id]
        self.releaseId = row[DBINDEX_RELEASEPERSONROLE_releaseId]
        self.personId = row[DBINDEX_RELEASEPERSONROLE_personId]
        self.roleId = row[DBINDEX_RELEASEPERSONROLE_roleId]
        
        
    def insert(self, allowUpdate):
        obj = LinkReleasePersonRole.getReleasePersonRoleByIds(self.gdb, self.releaseId, self.personId, self.roleId)
        if(obj.id):
            self.id = obj.id
        else:
            self.id = DataBaseObject.insert(self)
        
    
    @staticmethod
    def getReleasePersonRoleByIds(gdb, releaseId, personId, roleId):
        dbRow = DataBaseObject.getOneByQuery(gdb, LinkReleasePersonRole.filterQuery, (releaseId, personId, roleId))
        obj = LinkReleasePersonRole(gdb)
        obj.fromDb(dbRow)
        return obj
        
