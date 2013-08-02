import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


DBINDEX_fileTypeId = 2
DBINDEX_parentId = 3


class File(DataBaseObject):
    filterQueryByGameIdAndFileType = "Select * from File \
                    where parentId = ? AND \
                    filetype = ?"
                    
    filterQueryByNameAndType = "Select * from File \
                    where name = ? AND \
                    filetype = ?"
                    
    filterQueryByNameAndTypeAndParent = "Select * from File \
                    where name = ? AND \
                    filetype = ? AND \
                    parentId = ?"
                    
    filterQueryByGameIdAndTypeId = "Select * from File \
                    where parentId = ? AND \
                    filetype = ?"
                    
    filterFilesForGameList = "Select * from File Where FileTypeId in (%s)"
                    
    filterQueryByParentIds = "Select * from File \
                    where parentId in (?, ?, ?, ?)"
    
    getFileList = "SELECT * FROM File WHERE filetype = 'rom'"
    
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
            return
        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        self.fileTypeId = row[DBINDEX_fileTypeId]
        self.parentId = row[DBINDEX_parentId]
        
        
    def delete(self, gameId):
        util.Logutil.log("Delete Files with gameId %s" % str(gameId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.__deleteQuery, (gameId,))
    
    def deleteByFileId(self, fileId):
        util.Logutil.log("Delete File with id %s" % str(fileId), util.LOG_LEVEL_INFO)
        self.deleteObjectByQuery(self.deleteFileQuery, (fileId,))
            
            
    @staticmethod
    def getAllFiles(gdb):
        dblist = DataBaseObject.getAll(gdb, 'File')
        objs = []
        for dbRow in dblist:
            obj = File()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
            
            
    @staticmethod
    def getFileByNameAndType(gdb, name, type):
        file = DataBaseObject.getOneByQuery(gdb, File.filterQueryByNameAndType, (name, type))
        return file
        
    @staticmethod
    def getFileByNameAndTypeAndParent(gdb, name, type, parentId):
        file = DataBaseObject.getOneByQuery(gdb, File.filterQueryByNameAndTypeAndParent, (name, type, parentId))
        return file
        
    @staticmethod
    def getFilesByNameAndType(gdb, name, type):
        files = DataBaseObject.getByQuery(gdb, File.filterQueryByNameAndType, (name, type))
        return files
        
    @staticmethod
    def getFilesByGameIdAndTypeId(gdb, gameId, fileTypeId):
        files = DataBaseObject.getByQuery(gdb, File.filterQueryByGameIdAndTypeId, (gameId, fileTypeId))
        return files
        
    @staticmethod
    def getRomsByGameId(gdb, gameId):
        files = DataBaseObject.getByQuery(gdb, File.filterQueryByGameIdAndFileType, (gameId, 0))
        return files
        
    @staticmethod
    def getFilesForGamelist(gdb, fileTypeIds):
        files = DataBaseObject.getByQueryNoArgs(gdb, File.filterFilesForGameList %(','.join(fileTypeIds)))
        return files
        
    @staticmethod
    def getFilesByParentIds(gdb, gameId, romCollectionId, publisherId, developerId):
        files = DataBaseObject.getByQuery(gdb, File.filterQueryByParentIds, (gameId, romCollectionId, publisherId, developerId))
        return files
        
    @staticmethod
    def getFilesList(gdb):
        files = DataBaseObject.getByQueryNoArgs(gdb, File.getFileList)
        return files
    
    @staticmethod
    def getFileAllFilesByRCId(gdb, id):
        gdb.cursor.execute('select File.name from File, Release where Release.platformId=? and File.parentId=Release.id and File.fileType="rom"', (id,))
        objects = gdb.cursor.fetchall()
        results = [r[0] for r in objects]
        return results