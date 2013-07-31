
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

DBINDEX_id = 0
DBINDEX_name = 1

class DataBaseObject:
    
    def fromDb(self, row):
        pass
    
    def toDbDict(self):
        pass
        
    
    def updateSingleColumns(self, gdb, columns, updateWithNullValues):
        
        updateString = "Update %s SET " %self._tableName
        args = []
                
        for column in columns:
            val = getattr(self, column)
            
            if(not updateWithNullValues and (val == '' or val == None)):
                continue
            
            args.append(val)
            updateString = "%s%s = ?, " %(updateString, column)
        
        updateString = updateString[0:len(updateString)-2]
        updateString += " WHERE id = " +str(self.id)
        gdb.cursor.execute(updateString, args)
        
        
    def updateAllColumns(self, gdb, updateWithNullValues):
        
        updateString = "Update %s SET " %self._tableName
        args = []
        
        dict = self.toDbDict()
        for key in (dict.keys()):
            val = getattr(self, key)
            
            if(not updateWithNullValues and (val == '' or val == None)):
                continue
            
            args.append(val)
            updateString = "%s%s = ?, " %(updateString, key)
        
        updateString = updateString[0:len(updateString)-2]
        updateString += " WHERE id = " +str(self.id)
        gdb.cursor.execute(updateString, args)
            
        
    def delete(self, gdb, id):
        self.deleteObjectByQuery("DELETE FROM '%s' WHERE id = ?" % self._tableName, (id,))
    
    def deleteAll(self, gdb):
        gdb.cursor.execute("DELETE FROM '%s'" % self._tableName)
    
    def deleteObjectByQuery(self, gdb, query, args):
        gdb.cursor.execute(query, args)
    
    def getCount(self, gdb):
        gdb.cursor.execute("SELECT count(*) From '%s'" % self._tableName)
        count = gdb.cursor.fetchall()
        return count[0][0]
    
    def getCountByQuery(self, gdb, query, args):
        gdb.cursor.execute(query, args)
        count = gdb.cursor.fetchone()
        return count
        
        
    @staticmethod
    def insert(gdb, obj):
        
        dbdict = obj.toDbDict()
        
        paramsString = ( "?, " * len(dbdict))
        paramsString = paramsString[0:len(paramsString)-2]
         
        keysString = ''
        for key in dbdict.keys():
            keysString = keysString + ', ' +key
        keysString = keysString[2:len(keysString)]
        insertString = "Insert INTO %(tablename)s (id, %(keys)s) VALUES (NULL, %(paramsString)s)" % {'tablename':obj.tableName, 'keys':keysString, 'paramsString': paramsString }
                    
        gdb.cursor.execute(insertString, dbdict.values())
        return gdb.cursor.lastrowid
        

    @staticmethod
    def getAll(gdb, tablename):
        gdb.cursor.execute("SELECT * FROM '%s'" % tablename)
        allObjects = gdb.cursor.fetchall()
        newList = DataBaseObject.encodeUtf8(allObjects)
        return newList        
        
    @staticmethod
    def getAllOrdered(gdb, tablename):
        gdb.cursor.execute("SELECT * FROM '%s' ORDER BY name COLLATE NOCASE" % tablename)
        allObjects = gdb.cursor.fetchall()
        newList = DataBaseObject.encodeUtf8(allObjects)
        return newList
        
    @staticmethod
    def getOneByName(gdb, tablename, name):
        gdb.cursor.execute("SELECT * FROM '%s' WHERE name = ?" % tablename, (name,))
        dbRow = gdb.cursor.fetchone()
        return dbRow
        
    @staticmethod
    def getOneById(gdb, tablename, id):
        gdb.cursor.execute("SELECT * FROM '%s' WHERE id = ?" % tablename, (id,))
        dbRow = gdb.cursor.fetchone()
        return dbRow
    
    @staticmethod
    def getByWildcardQuery(gdb, query, args):
        #double Args for WildCard-Comparison (0 = 0)
        newArgs = []
        for arg in args:
            newArgs.append(arg)
            newArgs.append(arg)
        return DataBaseObject.getByQuery(query, newArgs)
            
    @staticmethod
    def getByQuery(gdb, query, args):
        gdb.cursor.execute(query, args)
        allObjects = gdb.cursor.fetchall()
        allObjectsUtf8 = DataBaseObject.encodeUtf8(allObjects)
        return allObjectsUtf8
          
    @staticmethod
    def getByQueryNoArgs(gdb, query):
        gdb.cursor.execute(query)
        allObjects = gdb.cursor.fetchall()
        allObjectsUtf8 = DataBaseObject.encodeUtf8(allObjects)
        return allObjectsUtf8

    @staticmethod
    def getOneByQuery(gdb, query, args):
        gdb.cursor.execute(query, args)
        dbRow = gdb.cursor.fetchone()
        return dbRow


    @staticmethod
    def encodeUtf8(list):
        newList = []
        for item in list:
            newItem = []
            for param in item:
                if type(param).__name__ == 'str':
                    newItem.append(param.encode('utf-8'))
                else:
                    newItem.append(param)
            newList.append(newItem)
        return newList