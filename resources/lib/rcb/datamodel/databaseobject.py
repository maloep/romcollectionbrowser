
from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class DataBaseObject:
    
    def __init__(self, gdb):
        self._gdb = gdb
    
    def fromDb(self, row):
        pass
    
    
    def toDict(self):
        dict = {}
        for property, value in vars(self).iteritems():
            if(not property.startswith('_')):            
                dict[property] = value
                
        return dict
                
    
    def insertold(self, args):
        paramsString = ( "?, " * len(args))
        paramsString = paramsString[0:len(paramsString)-2]
        insertString = "Insert INTO %(tablename)s VALUES (NULL, %(args)s)" % {'tablename':self._tableName, 'args': paramsString }        
        self._gdb.cursor.execute(insertString, args)
    
    
    def insert(self, obj):
        
        dict = obj.toDict()
        
        paramsString = ( "?, " * len(dict))
        paramsString = paramsString[0:len(paramsString)-2]
         
        keysString = ''
        for key in dict.keys():
            keysString = keysString + ', ' +key
        keysString = keysString[2:len(keysString)]
        insertString = "Insert INTO %(tablename)s (id, %(keys)s) VALUES (NULL, %(paramsString)s)" % {'tablename':self._tableName, 'keys':keysString, 'paramsString': paramsString }
                    
        self._gdb.cursor.execute(insertString, dict.values())
    
    
    def updateold(self, columns, argsOrig, id, updateWithNullValues):
        
        if(len(columns) != len(argsOrig)):
            util.Logutil.log("len columns != len args in _gdb.update()", util.LOG_LEVEL_WARNING)            
            return
            
        args = []
        updateString = "Update %s SET " %self._tableName
        for i in range(0, len(columns)):
            #don't update with empty values
            if(not updateWithNullValues and (argsOrig[i] == '' or argsOrig[i] == None)):
                continue
            
            args.append(argsOrig[i])
            updateString += columns[i] +  " = ?"
            if(i < len(columns) -1):
                updateString += ", "
                
        updateString += " WHERE id = " +str(id)
        self._gdb.cursor.execute(updateString, args)
        
    
    def updateSingleColumns(self, columns, obj, updateWithNullValues):
        
        updateString = "Update %s SET " %self._tableName
        args = []
                
        for column in columns:
            val = getattr(obj, column)
            
            if(not updateWithNullValues and (val == '' or val == None)):
                continue
            
            args.append(val)
            updateString = "%s%s = ?, " %(updateString, column)
        
        updateString = updateString[0:len(updateString)-2]
        updateString += " WHERE id = " +str(obj.id)
        self._gdb.cursor.execute(updateString, args)
        
        
    def updateAllColumns(self, obj, updateWithNullValues):
        
        updateString = "Update %s SET " %self._tableName
        args = []
        
        dict = obj.toDict()
        for key in (dict.keys()):
            val = getattr(obj, key)
            
            if(not updateWithNullValues and (val == '' or val == None)):
                continue
            
            args.append(val)
            updateString = "%s%s = ?, " %(updateString, key)
        
        updateString = updateString[0:len(updateString)-2]
        updateString += " WHERE id = " +str(obj.id)
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
        
    def getAllold(self):
        self._gdb.cursor.execute("SELECT * FROM '%s'" % self._tableName)
        allObjects = self._gdb.cursor.fetchall()
        newList = self.encodeUtf8(allObjects)
        return newList
    
    
    def getAll(self):
        self._gdb.cursor.execute("SELECT * FROM '%s'" % self._tableName)
        allObjects = self._gdb.cursor.fetchall()
        newList = self.encodeUtf8(allObjects)
        
        dbObjects = []
        for dbRow in newList:            
            dbObjects.append(self.fromDb(dbRow))
        
        return dbObjects
        
        
    def getAllOrderedold(self):        
        self._gdb.cursor.execute("SELECT * FROM '%s' ORDER BY name COLLATE NOCASE" % self._tableName)
        allObjects = self._gdb.cursor.fetchall()
        newList = self.encodeUtf8(allObjects)
        return newList
    

    def getAllOrdered(self):
        self._gdb.cursor.execute("SELECT * FROM '%s' ORDER BY name COLLATE NOCASE" % self._tableName)
        allObjects = self._gdb.cursor.fetchall()
        newList = self.encodeUtf8(allObjects)
        
        dbObjects = []
        for dbRow in newList:            
            dbObjects.append(self.fromDb(dbRow))
        
        return dbObjects   
        
        
    def getOneByNameold(self, name):
        self._gdb.cursor.execute("SELECT * FROM '%s' WHERE name = ?" % self._tableName, (name,))
        object = self._gdb.cursor.fetchone()
        return object
    
    
    def getOneByName(self, name):
        self._gdb.cursor.execute("SELECT * FROM '%s' WHERE name = ?" % self._tableName, (name,))
        dbRow = self._gdb.cursor.fetchone()
        obj = self.fromDb(dbRow)
        return obj
    
        
    def getObjectByIdold(self, id):
        self._gdb.cursor.execute("SELECT * FROM '%s' WHERE id = ?" % self._tableName, (id,))
        object = self._gdb.cursor.fetchone()        
        return object
    
    
    def getObjectById(self, id):
        self._gdb.cursor.execute("SELECT * FROM '%s' WHERE id = ?" % self._tableName, (id,))
        dbRow = self._gdb.cursor.fetchone()
        obj = self.fromDb(dbRow)
        return obj
    
    
    def getObjectsByWildcardQuery(self, query, args):        
        #double Args for WildCard-Comparison (0 = 0)
        newArgs = []
        for arg in args:
            newArgs.append(arg)
            newArgs.append(arg)
                    
        return self.getObjectsByQuery(query, newArgs)        
        
    def getObjectsByQueryold(self, query, args):
        self._gdb.cursor.execute(query, args)
        allObjects = self._gdb.cursor.fetchall()        
        return allObjects
    
    def getObjectsByQuery(self, query, args):
        self._gdb.cursor.execute(query, args)
        allObjects = self._gdb.cursor.fetchall()
        allObjectsUtf8 = self.encodeUtf8(allObjects)
        
        dbObjects = []
        for dbRow in allObjectsUtf8:            
            dbObjects.append(self.fromDb(dbRow))
                
        return dbObjects
        
    def getObjectsByQueryNoArgsold(self, query):
        self._gdb.cursor.execute(query)
        allObjects = self._gdb.cursor.fetchall()
        return allObjects
    
    
    def getObjectsByQueryNoArgs(self, query):
        self._gdb.cursor.execute(query)
        allObjects = self._gdb.cursor.fetchall()
        dbObjects = []
        for dbRow in allObjects:            
            dbObjects.append(self.fromDb(dbRow))
                
        return dbObjects


    def getObjectByQueryold(self, query, args):        
        self._gdb.cursor.execute(query, args)
        object = self._gdb.cursor.fetchone()        
        return object
    
    def getObjectByQuery(self, query, args):        
        self._gdb.cursor.execute(query, args)
        dbRow = self._gdb.cursor.fetchone()
        obj = self.fromDb(dbRow)
        return obj
    
    def encodeUtf8(self, list):
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