
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *

DBINDEX_id = 0
DBINDEX_name = 1

class DataBaseObject:
    
    def __init__(self, gdb):
        self.gdb = gdb
    
    def fromDb(self, row):
        pass
    
    def toDbDict(self):
        pass
    
    
    """
    def toDict(self):
        dict = {}
        for property, value in vars(self).iteritems():
            #ignore protected and non-db properties
            if(not property.startswith('_') and not property.endswith('_dbignore')):
                dict[property] = value
                
        return dict
    """
    
    @staticmethod
    def insert(obj):
        
        dbdict = obj.toDbDict()
        
        paramsString = ( "?, " * len(dbdict))
        paramsString = paramsString[0:len(paramsString)-2]
         
        keysString = ''
        for key in dbdict.keys():
            keysString = keysString + ', ' +key
        keysString = keysString[2:len(keysString)]
        insertString = "Insert INTO %(tablename)s (id, %(keys)s) VALUES (NULL, %(paramsString)s)" % {'tablename':obj.tableName, 'keys':keysString, 'paramsString': paramsString }
                    
        obj.gdb.cursor.execute(insertString, dbdict.values())
        return obj.gdb.cursor.lastrowid
        
    
    def updateSingleColumns(self, columns, updateWithNullValues):
        
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
        self._gdb.cursor.execute(updateString, args)
        
        
    def updateAllColumns(self, updateWithNullValues):
        
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
        self._gdb.cursor.execute(updateString, args)
            
        
    def delete(self, id):
        self.deleteObjectByQuery("DELETE FROM '%s' WHERE id = ?" % self._tableName, (id,))
    
    def deleteAll(self):
        self._gdb.cursor.execute("DELETE FROM '%s'" % self._tableName)
    
    def deleteObjectByQuery(self, query, args):
        self._gdb.cursor.execute(query, args)
    
    def getCount(self):
        self._gdb.cursor.execute("SELECT count(*) From '%s'" % self._tableName)
        count = self._gdb.cursor.fetchall()
        return count[0][0]
    
    def getCountByQuery(self, query, args):
        self._gdb.cursor.execute(query, args)
        count = self._gdb.cursor.fetchone()
        return count
        

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
    def getObjectById(gdb, tablename, id):
        gdb.cursor.execute("SELECT * FROM '%s' WHERE id = ?" % tablename, (id,))
        dbRow = gdb.cursor.fetchone()
        return dbRow
    
    @staticmethod
    def getObjectsByWildcardQuery(gdb, query, args):
        #double Args for WildCard-Comparison (0 = 0)
        newArgs = []
        for arg in args:
            newArgs.append(arg)
            newArgs.append(arg)
        return DataBaseObject.getObjectsByQuery(query, newArgs)
            
    @staticmethod
    def getObjectsByQuery(gdb, query, args):
        gdb.cursor.execute(query, args)
        allObjects = gdb.cursor.fetchall()
        allObjectsUtf8 = DataBaseObject.encodeUtf8(allObjects)
        return allObjectsUtf8
          
    @staticmethod
    def getObjectsByQueryNoArgs(gdb, query):
        gdb.cursor.execute(query)
        allObjects = gdb.cursor.fetchall()
        allObjectsUtf8 = DataBaseObject.encodeUtf8(allObjects)
        return allObjectsUtf8

    @staticmethod
    def getObjectByQuery(gdb, query, args):
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