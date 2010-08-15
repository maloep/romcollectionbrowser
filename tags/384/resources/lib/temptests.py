
import os, sys
from datetime import * 

#from dateutil import parser

nowdt = datetime.now()
print nowdt

#nowstring = '2010-08-12 21:07:10.158000'
#dt = parser.parse(nowstring)

fname = "C:\\Users\\malte\\AppData\\Roaming\\XBMC\\scripts\\Rom Collection Browser\\resources\\database\\config.xml"
dt = os.path.getmtime(fname)

print dt


