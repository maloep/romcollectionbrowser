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
        self._gdb = gdb
        self._tableName = "GenreGame"
        
        self.id = None
        self.genreId = None
        self.gameId = None
        
    def fromDb(self, row):
        
        if(not row):
            return None
        
        genreGame = LinkGenreGame(self._gdb)

        genreGame.id = row[databaseobject.DBINDEX_id]
        genreGame.genreId = row[DBINDEX_GENREGAME_genreId]
        genreGame.gameId = row[DBINDEX_GENREGAME_gameId]

        return genreGame
        
    def getGenreGameByGenreIdAndGameId(self, genreId, gameId):
        genreGame = self.getObjectByQuery(self.filterQueryByGenreIdAndGameId, (genreId, gameId))
        return genreGame
        
