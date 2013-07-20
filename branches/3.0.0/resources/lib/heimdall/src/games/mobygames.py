import resources.lib.heimdall.src.heimdall
from resources.lib.heimdall.src import util
from resources.lib.heimdall.src.heimdall import tasks
from resources.lib.heimdall.src.heimdall import resources
from resources.lib.heimdall.src.heimdall import supplies, demands
from resources.lib.heimdall.src.heimdall.predicates import *

from BeautifulSoup import BeautifulSoup
import urllib

baseUrl = "http://www.mobygames.com"


class GamePredicateObject(tasks.SubjectTask):
    demand = [
        demands.required("game_detail_url"),
        demands.requiredClass("item.game", True)
    ]

    supply = [
        supplies.emit(dc.type),
        supplies.emit(dc.description),
        supplies.emit(dc.date),
        supplies.emit(swo.SWO_0000396), # Developer
        supplies.emit(swo.SWO_0000397), # Publisher
        supplies.emit("players")
    ]
    
    def require(self):
        uri = self.subject["game_detail_url"]
        return resources.SimpleResource(uri)

    def run(self, resource):
        soup = BeautifulSoup(''.join(resource))
        
        self.emitLinkProperty(soup, 'Published by', swo.SWO_0000397, 'publisher_detail_url')
        self.emitLinkProperty(soup, 'Developed by', swo.SWO_0000396, 'developer_detail_url')
        self.emitLinkProperty(soup, 'Released', dc.date, 'release_detail_url')
        self.emitLinkProperty(soup, 'Genre', dc.type, 'genre_detail_url')
        self.emitLinkProperty(soup, 'Perspective', 'perspecitve', 'perspective_detail_url')
        
        rankDiv = soup.find('div', attrs={'class' : 'fr scoreBoxBig scoreHi'})
        self.subject.emit('mobyRank', rankDiv.string)        
        
        scoreDiv = soup.find('div', attrs={'class' : 'fr scoreBoxMed scoreHi'})
        self.subject.emit('mobyScore', scoreDiv.string)
        
        
                        
    
    def emitLinkProperty(self, soup, text, propertyName, detailUrlName=None):
        div = soup.find('div', {}, True, text)
        if(not div):
            return
        nextDiv = div.parent.findNextSibling('div')
        if(not nextDiv):
            return
        
        a = nextDiv.find('a')
        if(not a):
            return
        
        name = a.string
        url = a['href']
        
        self.subject.emit(propertyName, name)
        if(detailUrlName):
            self.subject.emit(detailUrlName, baseUrl +url)


class SearchGameCollector(tasks.SubjectTask):
    demand = [
        demands.required(dc.title),
        demands.required(edamontology.data_3106), # Platform
        demands.requiredClass("item.game", True)
    ]

    supply = []

    def require(self):
        title = self.subject[dc.title]
        title = title.encode('utf-8')
        platform = self.subject[edamontology.data_3106]
        if platform:
            uri = "http://www.mobygames.com/search/quick?game=%s&p=%s" % \
                    (urllib.quote_plus(title), urllib.quote_plus(platform))
            return resources.SimpleResource(uri)
        else:
            return []

    def run(self, resource):
                
        #parse document
        soup = BeautifulSoup(''.join(resource))
        
        searchTitleDivs = soup.findAll('div', attrs={'class' : 'searchTitle'})
        if(not searchTitleDivs):
            self.subject.emit('error', 'SearchGameCollector: no results found')
            return
                
        foundGameTitles = []
        for div in searchTitleDivs:
            a = div.find('a')
            title = a.string
            
            if(title == self.subject[dc.title]):
                link = a['href']
                self.subject.emit('game_detail_url', baseUrl +link)
                self.subject.emit('artwork_detail_url', baseUrl +link +"/cover-art")
                self.subject.emit('screenshot_detail_url', baseUrl +link +"/screenshots")
                return
                
            foundGameTitles.append(title)
        
        #if we did not find a title return the list of found titles to the client
        if(len(foundGameTitles) > 0):
            self.subject.replace(dc.title, foundGameTitles)
            
        
        
module = [ SearchGameCollector, GamePredicateObject ]
