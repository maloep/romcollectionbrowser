import databaseobject
from databaseobject import DataBaseObject
from filetype import FileType

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


DBINDEX_fileTypeId = 2
DBINDEX_parentId = 3


class File(DataBaseObject):
        
    fileDict = None
    fileDictForGameList = None
    
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
        
    
    def insert(self, gdb, allowUpdate):
        
        if(self.name == ''):
            return
        
        obj = File.getFileByName(gdb, self.name)
        if(obj.id):
            self.id = obj.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
            
    @staticmethod
    def getFileDictForGamelist(gdb):
        # 0 = cacheAll
        if(File.fileDictForGameList != None):
            return File.fileDictForGameList
        else:
            #TODO: get list of file types
            fileType = FileType.getCachedFileType(gdb, 'boxfront')
            files = File.getFilesForGamelist(gdb, (str(fileType.id),))
            if(files == None):
                Logutil.log("fileRows == None in getFileDictForGamelist", util.LOG_LEVEL_WARNING)
                return None
                    
            File.fileDictForGameList = File.cacheFiles(files)
        
        return File.fileDictForGameList
    
    
    @staticmethod
    def cacheFiles(files):
        Logutil.log("Begin cacheFiles" , util.LOG_LEVEL_DEBUG)
        
        fileDict = {}
        for file in files:
            key = '%i;%i' % (file.parentId , file.fileTypeId)
            item = None
            try:
                item = fileDict[key]
            except:
                pass
            if(item == None):
                fileRowList = []
                fileRowList.append(file)
                fileDict[key] = fileRowList
            else:                
                fileRowList = fileDict[key]
                fileRowList.append(file)
                fileDict[key] = fileRowList
                
        Logutil.log("End cacheFiles" , util.LOG_LEVEL_DEBUG)
        return fileDict
    
    
    @staticmethod
    def getCachedFiles(gdb, fileType, parentId, fileDict):
                    
        Logutil.log("File.getCachedFiles", util.LOG_LEVEL_DEBUG)
        Logutil.log("fileType: %s" %str(fileType), util.LOG_LEVEL_DEBUG)
                        
        fileType = FileType.getCachedFileType(gdb, fileType)
        
        if(parentId == None or fileType == None):
            return None
            
        key = '%i;%i' %(parentId, int(fileType.id))
        try:                                
            files = fileDict[key]
        except:
            files = None
        
        if(files == None):
            Logutil.log("file == None in getCachedFiles", util.LOG_LEVEL_DEBUG)
        
        return files
    
    
    @staticmethod
    def getFilesForGamelist(gdb, fileTypeIds):
        dbRows = DataBaseObject.getByQueryNoArgs(gdb, File.filterFilesForGameList %(','.join(fileTypeIds)))
        objs = []
        for dbRow in dbRows:
            obj = File()
            obj.fromDb(dbRow)
            objs.append(obj)
        return objs
            
                                                
    @staticmethod
    def getFileByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'File', name)
        obj = File()
        obj.fromDb(dbRow)
        return obj
        
        
        
        
        
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