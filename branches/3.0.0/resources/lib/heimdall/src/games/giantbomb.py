
import resources.lib.heimdall.src.heimdall
from resources.lib.heimdall.src import util
from resources.lib.heimdall.src.heimdall import tasks
from resources.lib.heimdall.src.heimdall import resources
from resources.lib.heimdall.src.heimdall import supplies, demands
from resources.lib.heimdall.src.heimdall.predicates import *

from resources.lib.heimdall.src.game_item import comparePlatforms

import datetime, urllib, json


class GamePredicateObject(tasks.SubjectTask):
    demand = [
        demands.required('game_detail_url'),
        demands.required('apikey'),
        demands.requiredClass('item.game', True)
    ]

    supply = [
        supplies.emit(swo.SWO_0000396), # Developer
        supplies.emit(swo.SWO_0000397), # Publisher
        supplies.emit('developer_detail_url'),
        supplies.emit('publisher_detail_url'),
    ]

    def require(self):
        apiKey = self.subject['apikey']
        uri = self.subject['game_detail_url']
        uri = '%s?api_key=%s&format=json' %(uri, apiKey)
        return resources.SimpleResource(uri)
        

    def run(self, resource):
        
        jsonResult = json.loads(resource)
        
        #status_code 1 = OK
        if(jsonResult['status_code'] != 1):
            self.subject.emit('error', 'GamePredicateObject: %s' %jsonResult['error'])
            return
              
        result = jsonResult['results']
        
        #Developer information from Release should be more accurate
        if(not self.subject[swo.SWO_0000396]):
            try:
                for developer in result['developers']:
                    self.subject.emit(swo.SWO_0000396, developer['name'])
                    self.subject.emit('developer_detail_url', developer['api_detail_url'])
            except KeyError:
                pass
        
        #Publisher information from Release should be more accurate
        if(not self.subject[swo.SWO_0000397]):
            try:
                for publisher in result['publishers']:
                    self.subject.emit(swo.SWO_0000397, publisher['name'])
                    self.subject.emit('publisher_detail_url', publisher['api_detail_url'])
            except KeyError:
                pass
            
        print result
        self.subject.emit('shortdesc', result['deck'])
        self.subject.emit('description', result['description'])
        
        for genre in result['genres']:
            self.subject.emit(dc.type, genre['name'])
            self.subject.emit('genre_detail_url', genre['api_detail_url'])
            
        for person in result['people']:
            self.subject.emit('person', person['name'])
            self.subject.emit('person_detail_url', person['api_detail_url'])
            
        for character in result['characters']:
            self.subject.emit('character', character['name'])
            self.subject.emit('character_detail_url', character['api_detail_url'])
        


class ReleasePredicateObject(tasks.SubjectTask):
    demand = [
        demands.required('release_detail_url'),
        demands.required('apikey'),
        demands.requiredClass('item.game', True)
    ]

    supply = [
        supplies.emit(swo.SWO_0000396), # Developer
        supplies.emit(swo.SWO_0000397), # Publisher
        supplies.emit('developer_detail_url'),
        supplies.emit('publisher_detail_url'),
    ]

    def require(self):
        apiKey = self.subject['apikey']
        uri = self.subject['release_detail_url']
        uri = '%s?api_key=%s&format=json' %(uri, apiKey)
        return resources.SimpleResource(uri)
        

    def run(self, resource):
        
        jsonResult = json.loads(resource)
        
        #status_code 1 = OK
        if(jsonResult['status_code'] != 1):
            self.subject.emit('error', 'ReleasePredicateObject: %s' %jsonResult['error'])
            return
              
        result = jsonResult['results']
        
        try:
            for developer in result['developers']:
                self.subject.emit(swo.SWO_0000396, developer['name'])
                self.subject.emit('developer_detail_url', developer['api_detail_url'])
        except KeyError:
            pass
        
        try:
            for publisher in result['publishers']:
                self.subject.emit(swo.SWO_0000397, publisher['name'])
                self.subject.emit('publisher_detail_url', publisher['api_detail_url'])
        except KeyError:
            pass
            



class SearchGameCollector(tasks.SubjectTask):
    demand = [
        demands.required(dc.title),
        demands.required(edamontology.data_3106), # Platform
        demands.required('apikey'),        
        demands.requiredClass('item.game', True)
    ]

    supply = [
        supplies.emit(dc.title),        
        supplies.emit(dc.date),        
        supplies.emit('boxfront'),
        supplies.emit('region'),
        supplies.emit('rating_giantbomb'),
        supplies.emit('release_detail_url'),
        supplies.emit('game_detail_url')
    ]

    def require(self):
        title = self.subject[dc.title]
        title = title.encode('utf-8')
        apiKey = self.subject['apikey']
        platform = self.subject[edamontology.data_3106]
        uri = 'http://www.giantbomb.com/api/releases/?api_key=%s&filter=name:%s,platform:%s&format=json' %(apiKey, title, platform) 
        
        return resources.SimpleResource(uri)
        

    def run(self, resource):
        
        jsonResult = json.loads(resource)
        
        #status_code 1 = OK
        if(jsonResult['status_code'] != 1):
            self.subject.emit('error', 'SearchGameCollector: %s' %jsonResult['error'])
            return
              
        foundGameTitles = []      
        for result in jsonResult['results']:
            region = ''
            if(result['region']):
                region = result['region']['name']
                
            preferredregion = self.subject['preferredregion']
            if(preferredregion):                
                if(preferredregion != region):
                        continue
            
            title = result['name']
            if(title == self.subject[dc.title]):
                self.subject.emit('region', region)
                self.subject.emit('rating_giantbomb', result['game_rating'])
                self.subject.emit(dc.date, result['release_date'])
                self.subject.emit('release_detail_url', result['api_detail_url'])
                self.subject.emit('game_detail_url', result['game']['api_detail_url'])
                if(result['image']):
                    self.subject.emit('boxfront', result['image']['super_url'])
                break
            
            foundGameTitles.append(title)
        
        #if we did not find a title return the list of found titles to the client
        if(len(foundGameTitles) > 0):
            self.subject.replace(dc.title, foundGameTitles)
                        
            
            
        
module = [ SearchGameCollector, ReleasePredicateObject, GamePredicateObject ]

