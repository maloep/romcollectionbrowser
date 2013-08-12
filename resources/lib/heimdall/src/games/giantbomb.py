
import resources.lib.heimdall.src.heimdall
from resources.lib.heimdall.src import util
from resources.lib.heimdall.src.heimdall import tasks
from resources.lib.heimdall.src.heimdall import resources
from resources.lib.heimdall.src.heimdall import supplies, demands
from resources.lib.heimdall.src.heimdall.predicates import *

from resources.lib.heimdall.src.game_item import comparePlatforms

import datetime, urllib, json


def getNameDetailListFromJson(result, key):
    dictList = []
    try:
        if(result[key]):
            for item in result[key]:
                dict = {}
                dict['name'] = item['name']
                dict['detail_url'] = item['api_detail_url']
                dictList.append(dict)
    except KeyError:
        return None
    return dictList



class PersonPredicateObject(tasks.SubjectTask):
    demand = [
        demands.required('person_detail_url'),
        demands.required('apikey'),
        demands.requiredClass('item.person', True)
    ]

    supply = [
        supplies.emit(dc.title),
        supplies.emit('birthdate'),
        supplies.emit('deathdate'),
        supplies.emit(dc.description),        
        supplies.emit('country'),
        supplies.emit('hometown'),
        supplies.emit('gender'),
        supplies.emit('personart')        
    ]

    def require(self):
        apiKey = self.subject['apikey']
        uri = self.subject['person_detail_url']
        uri = '%s?api_key=%s&format=json&field_list=birth_date,country,death_date,deck,gender,hometown,image,name' %(uri, apiKey)
        return resources.SimpleResource(uri)
        

    def run(self, resource):
        
        jsonResult = json.loads(resource)
        
        #status_code 1 = OK
        if(jsonResult['status_code'] != 1):
            self.subject.emit('error', 'GamePredicateObject: %s' %jsonResult['error'])
            return
              
        result = jsonResult['results']
        
        #HACK: use replace instead of emit. Otherwise subject will add information for each other subject
        self.subject.replace(dc.title, result['name'])
        self.subject.replace('birthdate', result['birth_date'])
        self.subject.replace('deathdate', result['death_date'])
        self.subject.replace(dc.description, result['deck'])        
        self.subject.replace('country', result['country'])
        self.subject.replace('gender', result['gender'])
        self.subject.replace('hometown', result['hometown'])
        if(result['image']):
            self.subject.replace('personart', result['image']['super_url'])


class PlatformPredicateObject(tasks.SubjectTask):
    demand = [
        demands.required('platform_detail_url'),
        demands.required('apikey'),
        demands.requiredClass('item.platform', True)
    ]

    supply = [
        supplies.emit(dc.title),
        supplies.emit(dc.date),
        supplies.emit('manufacturer'),
        supplies.emit(dc.description),        
        supplies.emit('hasonlinefeatures'),
        supplies.emit('originalprice'),
        supplies.emit('platformart')        
    ]

    def require(self):
        apiKey = self.subject['apikey']
        uri = self.subject['platform_detail_url']
        uri = '%s?api_key=%s&format=json' %(uri, apiKey)
        return resources.SimpleResource(uri)
        

    def run(self, resource):
        
        jsonResult = json.loads(resource)
        
        #status_code 1 = OK
        if(jsonResult['status_code'] != 1):
            self.subject.emit('error', 'GamePredicateObject: %s' %jsonResult['error'])
            return
              
        result = jsonResult['results']
        
        self.subject.emit(dc.title, result['name'])
        self.subject.emit('originalprice', result['original_price'])
        self.subject.emit(dc.description, result['deck'])
        self.subject.emit(dc.date, result['release_date'])
        self.subject.emit('hasonlinefeatures', result['online_support'])
        manufacturerdict = {}
        manufacturerdict['name'] = result['company']['name']
        manufacturerdict['detail_url'] = result['company']['api_detail_url']
        self.subject.emit('manufacturer', manufacturerdict)
        self.subject.emit('platformart', result['image']['super_url'])
                


class GamePredicateObject(tasks.SubjectTask):
    demand = [
        demands.required('game_detail_url'),
        demands.required('apikey'),
        demands.requiredClass('item.game', True)
    ]

    supply = [
        supplies.emit(swo.SWO_0000396), # Developer
        supplies.emit(swo.SWO_0000397), # Publisher
        supplies.emit('shortdesc'),
        supplies.emit(dc.description),
        supplies.emit(dc.type),
        supplies.emit('person'),
        supplies.emit('character')
        
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
            self.subject.emit(swo.SWO_0000396, getNameDetailListFromJson(result, 'developers'))
        
        #Publisher information from Release should be more accurate
        if(not self.subject[swo.SWO_0000397]):
            self.subject.emit(swo.SWO_0000397, getNameDetailListFromJson(result, 'publishers'))
                    
        self.subject.emit('shortdesc', result['deck'])
        self.subject.emit('description', result['description'])
        
        self.subject.emit(dc.type, getNameDetailListFromJson(result, 'genres'))
        self.subject.emit('person', getNameDetailListFromJson(result, 'people'))
        self.subject.emit('character', getNameDetailListFromJson(result, 'characters'))
        


class ReleasePredicateObject(tasks.SubjectTask):
    demand = [
        demands.required('release_detail_url'),
        demands.required('apikey'),
        demands.requiredClass('item.game', True)
    ]

    supply = [
        supplies.emit(swo.SWO_0000396), # Developer
        supplies.emit(swo.SWO_0000397), # Publisher
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
        
        self.subject.emit(swo.SWO_0000396, getNameDetailListFromJson(result, 'developers'))
        self.subject.emit(swo.SWO_0000397, getNameDetailListFromJson(result, 'publishers'))



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
        supplies.emit(edamontology.data_3106),
        supplies.emit('boxfront'),
        supplies.emit('region'),
        supplies.emit(media.rating),
        supplies.emit('release_detail_url'),
        supplies.emit('game_detail_url'),
        supplies.emit('platform_detail_url')
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
                self.subject.emit(media.rating, result['game_rating'])
                self.subject.emit(dc.date, result['release_date'])
                self.subject.emit('release_detail_url', result['api_detail_url'])
                self.subject.emit('game_detail_url', result['game']['api_detail_url'])
                self.subject.emit('platform_detail_url', result['platform']['api_detail_url'])
                self.subject.replace(edamontology.data_3106, result['platform']['name'])
                if(result['image']):
                    self.subject.emit('boxfront', result['image']['super_url'])
                return
            
            foundGameTitles.append(title)
        
        #if we did not find a title return the list of found titles to the client
        if(len(foundGameTitles) > 0):
            self.subject.replace(dc.title, foundGameTitles)
                        
            
            
        
module = [ SearchGameCollector, ReleasePredicateObject, GamePredicateObject, 
          PlatformPredicateObject, PersonPredicateObject ]

