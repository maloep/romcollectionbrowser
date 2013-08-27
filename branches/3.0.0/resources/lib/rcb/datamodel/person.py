import databaseobject
from databaseobject import DataBaseObject
from namedentities import PersonRole
from links import LinkReleasePersonRole
from file import File
from filetype import FileType

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


"""
DB Index
"""
DBINDEX_description = 2
DBINDEX_country = 3
DBINDEX_city = 4
DBINDEX_gender = 5
DBINDEX_birthdate = 6
DBINDEX_deathdate = 7


class Person(DataBaseObject):
    def __init__(self):
        self.tableName = "Person"
        
        self.id = None
        self.name = ''
        self.description = ''
        self.country = ''
        self.city = ''
        self.birthdate = ''
        self.deathdate = ''
        self.gender = ''
                
        #releaseId is only used for temporary storage
        self.releaseId = None
        
        self.role = ''
        self.mediaFiles = {}
        
        
    def fromDb(self, row):
        if(not row):
            return
                        
        self.id = row[databaseobject.DBINDEX_id]
        self.name = row[databaseobject.DBINDEX_name]
        
        self.description = row[DBINDEX_description]
        self.country = row[DBINDEX_country]
        self.city = row[DBINDEX_city]
        self.birthdate = row[DBINDEX_birthdate]
        self.deathdate = row[DBINDEX_deathdate]
        self.gender = row[DBINDEX_gender]
        
        
    def toDbDict(self):
        dbdict = {}
        dbdict['id'] = self.id
        dbdict['name'] = self.name 
        dbdict['description'] = self.description
        dbdict['country'] = self.country
        dbdict['city'] = self.city
        dbdict['birthdate'] = self.birthdate
        dbdict['deathdate'] = self.deathdate
        dbdict['gender'] = self.gender
        
        
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
        
        for fileTypeName in self.mediaFiles.keys():
            fileType = FileType()
            fileType.name = fileTypeName
            fileType.insert(gdb)
            
            file = File()
            file.name = self.mediaFiles[fileTypeName]
            file.parentId = self.id
            file.fileTypeId = fileType.id
            file.insert(gdb) 
            
            
    @staticmethod
    def getPersonByName(gdb, name):
        dbRow = DataBaseObject.getOneByName(gdb, 'Person', name)
        obj = Person()
        obj.fromDb(dbRow)
        return obj
    
    
    @staticmethod
    def getPersonById(gdb, id):
        dbRow = DataBaseObject.getOneById(gdb, 'Person', id)
        obj = Person()
        obj.fromDb(dbRow)
        return obj
    