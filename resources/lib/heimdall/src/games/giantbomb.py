
import resources.lib.heimdall.src.heimdall
from resources.lib.heimdall.src import util
from resources.lib.heimdall.src.heimdall import tasks
from resources.lib.heimdall.src.heimdall import resources
from resources.lib.heimdall.src.heimdall import supplies, demands
from resources.lib.heimdall.src.heimdall.predicates import *

from resources.lib.heimdall.src.game_item import comparePlatforms

import datetime
import difflib
import urllib
import xml.etree.ElementTree as ET


class SearchGameCollector(tasks.SubjectTask):
    demand = [
        demands.required(dc.title),
        demands.required(edamontology.data_3106), # Platform
        demands.requiredClass("item.game", True)
    ]

    supply = [
        supplies.emit("todo")
    ]

    def require(self):
        title = self.subject[dc.title]
        title = title.encode('utf-8')
        uri = "http://api.giantbomb.com/search/?api_key=279442d60999f92c5e5f693b4d23bd3b6fd8e868&query=%s&resources=game&field_list=api_detail_url,name&format=json" %title 
        
        return resources.SimpleResource(uri)
        

    def run(self, resource):
        #Do some json stuff here
        print resource
        
module = [ SearchGameCollector ]