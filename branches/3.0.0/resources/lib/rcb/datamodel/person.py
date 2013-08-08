import databaseobject
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *
from resources.lib.rcb.datamodel.namedentities import PersonRole
from resources.lib.rcb.datamodel.links import LinkReleasePersonRole


class Person(DataBaseObject):
    def __init__(self):
        self.tableName = "Person"
        
        self.id = None
        self.name = ''
        self.description = ''
        #releaseId is only used for temporary storage
        self.releaseId = None
        
        self.birthdate = ''
        self.deathdate = ''
        self.country = ''
        self.hometown = ''
        self.gender = ''
        self.role = ''
        
        self.artworkurls = {}
        
        
    def fromDb(self, row):
        if(not row):
            return
                        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        
        
    def toDbDict(self):
        dbdict = {}
        dbdict['id'] = self.id
        dbdict['name'] = self.name 
        dbdict['description'] = self.description
        return dbdict
    
    
    def insert(self, gdb, allowUpdate):
        
        if(self.name == ''):
            return
        
        #store self
        person = Person.getPersonByName(gdb, self.name)
        if(person.id):
            self.id = person.id
            if(allowUpdate):
                self.updateAllColumns(gdb, False)
        else:
            self.id = DataBaseObject.insert(gdb, self)
            
        #store role
        if(self.releaseId):
            personRole = PersonRole()
            if(self.role != ''):
                personRole.name = self.role
                personRole.insert(gdb, allowUpdate)
            
            #TODO: handle persons without role
            #insert link between release, person and role
            linkReleasePersonRole = LinkReleasePersonRole()
            linkReleasePersonRole.releaseId = self.releaseId
            linkReleasePersonRole.personId = self.id
            linkReleasePersonRole.roleId = personRole.id
            linkReleasePersonRole.insert(gdb, allowUpdate)
            
            
    @staticmethod
    def getPersonByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Person', name)
        obj = Person()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getPlatformById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Person', id)
        obj = Person()
        obj.fromDb(dbRow)
        return obj
    