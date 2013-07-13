
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


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
        
    
    def __init__(self, gdb):        
        self._gdb = gdb
        self._tableName = "File"
        
        self.id = None
        self.name = ''
        self.fileTypeId = None
        self.parentId = None
        
        
    def fromDb(self, row):
        
        if(not row):
            return None
        
        file = File(self._gdb)
        
        file.id = row[util.ROW_ID]
        file.name = row[util.ROW_NAME]
        file.fileTypeId = row[util.FILE_fileTypeId]
        file.parentId = row[util.FILE_parentId]
        
        return file
            
    def getFileByNameAndType(self, name, type):
        file = self.getObjectByQuery(self.filterQueryByNameAndType, (name, type))
        return file
        
    def getFileByNameAndTypeAndParent(self, name, type, parentId):
        file = self.getObjectByQuery(self.filterQueryByNameAndTypeAndParent, (name, type, parentId))
        return file
        
    def getFilesByNameAndType(self, name, type):
        files = self.getObjectsByQuery(self.filterQueryByNameAndType, (name, type))
        return files
        
    def getFilesByGameIdAndTypeId(self, gameId, fileTypeId):
        files = self.getObjectsByQuery(self.filterQueryByGameIdAndTypeId, (gameId, fileTypeId))
        return files
        
    def getRomsByGameId(self, gameId):
        files = self.getObjectsByQuery(self.filterQueryByGameIdAndFileType, (gameId, 0))
        return files
        
    def getFilesForGamelist(self, fileTypeIds):                
        
        files = self.getObjectsByQueryNoArgs(self.filterFilesForGameList %(','.join(fileTypeIds)))
        return files
        
    def getFilesByParentIds(self, gameId, romCollectionId, publisherId, developerId):
        files = self.getObjectsByQuery(self.filterQueryByParentIds, (gameId, romCollectionId, publisherId, developerId))
        return files
    
    def delete(self, gameId):
        util.Logutil.log("Delete Files with gameId %s" % str(gameId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.__deleteQuery, (gameId,))
    
    def deleteByFileId(self, fileId):
        util.Logutil.log("Delete File with id %s" % str(fileId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.deleteFileQuery, (fileId,))
        
    def getFilesList(self):
        files = self.getObjectsByQueryNoArgs(self.getFileList)
        return files
    
    def getFileAllFilesByRCId(self, id):
        self._gdb.cursor.execute('select File.name from File, Game where Game.romcollectionid=? and File.parentId=Game.id and File.fileTypeId=0', (id,))
        objects = self._gdb.cursor.fetchall()
        results = [r[0] for r in objects]
        return results