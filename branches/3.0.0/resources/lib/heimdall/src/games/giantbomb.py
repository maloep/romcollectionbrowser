
import resources.lib.heimdall.src.heimdall
from resources.lib.heimdall.src import util
from resources.lib.heimdall.src.heimdall import tasks
from resources.lib.heimdall.src.heimdall import resources
from resources.lib.heimdall.src.heimdall import supplies, demands
from resources.lib.heimdall.src.heimdall.predicates import *

from resources.lib.heimdall.src.game_item import comparePlatforms

import datetime, urllib, json


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
        apiKey = self.subject['apikey']
        platform = self.subject[edamontology.data_3106]
        uri = "http://www.giantbomb.com/api/releases/?api_key=%s&filter=name:%s,platform:%s&format=json" %(apiKey, title, platform) 
        
        return resources.SimpleResource(uri)
        

    def run(self, resource):
        
        jsonResult = json.loads(resource)
        
        #status_code 1 = OK
        if(jsonResult['status_code'] != 1):
            self.subject.emit("error", jsonResult['error'])
            return
              
        foundGameTitles = []      
        for result in jsonResult['results']:
            print result['name']
                        
            region = ''
            if(result['region']):
                region = result['region']['name']
                
            preferredregion = self.subject['preferredregion']
            if(preferredregion):                
                if(preferredregion != region):
                        continue
            
            title = result['name']
            if(title != self.subject[dc.title]):
                foundGameTitles.append(title)
                continue
            
            self.subject.replace(dc.title, title)
            self.subject.emit("region", region)
            break
        
        #if we did not find a title return the list of found titles to the client
        self.subject.replace(dc.title, foundGameTitles)
                        
            
            
        
module = [ SearchGameCollector ]

