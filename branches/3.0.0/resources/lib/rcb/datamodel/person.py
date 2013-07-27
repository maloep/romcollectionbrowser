
from databaseobject import DataBaseObject

from resources.lib.rcb.utils import util
from resources.lib.rcb.utils.util import *


class Person(DataBaseObject):
    def __init__(self, gdb):
        self._gdb = gdb
        self._tableName = "Game"
        
        self.id = None
        self.name = ''
        self.description = ''
        
        self.birthdate = ''
        self.deathdate = ''
        self.country = ''
        self.hometown = ''
        self.gender = ''
        
        self.artworkurls = {}
        
        
    def fromDb(self, row):
        if(not row):
            return None
                
        person = Person(self._gdb)
        person.id = row[util.ROW_ID]
        person.name = row[util.ROW_NAME]
        
        return person
        
        
    def toDbDict(self, person):
        persondict = {}
        persondict['id'] = person.id
        persondict['name'] = person.name 
        persondict['description'] = person.description
        return persondict