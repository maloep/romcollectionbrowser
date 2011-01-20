from dbupdate import *
from gamedatabase import *

gdb = GameDataBase('./')
gdb.connect()
gdb.checkDBStructure()
db = DBUpdate()
db.updateDB(gdb)
