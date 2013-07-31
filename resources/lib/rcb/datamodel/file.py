import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


DBINDEX_fileTypeId = 2
DBINDEX_parentId = 3


class File(DataBaseObject):
    filterQueryByGameIdAndFileType = "Select * from File \
                    where parentId = ? AND \
                    filetypeid = ?"
                    
    filterQueryByNameAndType = "Select * from File \
                    where name = ? AND \
                    filetypeid = ?"
                    
    filterQueryByNameAndTypeAndParent = "Select * from File \
                    where name = ? AND \
                    filetypeid = ? AND \
                    parentId = ?"
                    
    filterQueryByGameIdAndTypeId = "Select * from File \
                    where parentId = ? AND \
                    filetypeid = ?"
                    
    filterFilesForGameList = "Select * from File Where FileTypeId in (%s)"
                    
    filterQueryByParentIds = "Select * from File \
                    where parentId in (?, ?, ?, ?)"
    
    getFileList = "SELECT * FROM File WHERE filetypeid = 0"
    
    __deleteQuery = "DELETE FROM File WHERE parentId= ?"
    
    deleteFileQuery = "DELETE FROM File WHERE Id= ?"
        
    
    def __init__(self):
        self.tableName = "File"
        
        self.id = None
        self.name = ''
        self.fileTypeId = None
        self.parentId = None
        
        
    def fromDb(self, row):
        
        if(not row):
            return None
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        self.fileTypeId = row[DBINDEX_fileTypeId]
        self.parentId = row[DBINDEX_parentId]
        
        return file
            
            
    def getFileByNameAndType(self, name, type):
        file = self.getOneByQuery(self.filterQueryByNameAndType, (name, type))
        return file
        
    def getFileByNameAndTypeAndParent(self, name, type, parentId):
        file = self.getOneByQuery(self.filterQueryByNameAndTypeAndParent, (name, type, parentId))
        return file
        
    def getFilesByNameAndType(self, name, type):
        files = self.getByQuery(self.filterQueryByNameAndType, (name, type))
        return files
        
    def getFilesByGameIdAndTypeId(self, gameId, fileTypeId):
        files = self.getByQuery(self.filterQueryByGameIdAndTypeId, (gameId, fileTypeId))
        return files
        
    def getRomsByGameId(self, gameId):
        files = self.getByQuery(self.filterQueryByGameIdAndFileType, (gameId, 0))
        return files
        
    def getFilesForGamelist(self, fileTypeIds):                
        
        files = self.getByQueryNoArgs(self.filterFilesForGameList %(','.join(fileTypeIds)))
        return files
        
    def getFilesByParentIds(self, gameId, romCollectionId, publisherId, developerId):
        files = self.getByQuery(self.filterQueryByParentIds, (gameId, romCollectionId, publisherId, developerId))
        return files
    
    def delete(self, gameId):
        util.Logutil.log("Delete Files with gameId %s" % str(gameId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.__deleteQuery, (gameId,))
    
    def deleteByFileId(self, fileId):
        util.Logutil.log("Delete File with id %s" % str(fileId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.deleteFileQuery, (fileId,))
        
    def getFilesList(self):
        files = self.getByQueryNoArgs(self.getFileList)
        return files
    
    def getFileAllFilesByRCId(self, id):
        gdb.cursor.execute('select File.name from File, Game where Game.romcollectionid=? and File.parentId=Game.id and File.fileTypeId=0', (id,))
        objects = gdb.cursor.fetchall()
        results = [r[0] for r in objects]
        return results