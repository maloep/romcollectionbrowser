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

baseImageUrl = "http://thegamesdb.net/banners/"


class PlatformPredicateObject(tasks.SubjectTask):
    demand = [
        demands.requiredClass("item.platform", True),
        demands.required(edamontology.data_3106) # Platform
    ]

    supply = [
        supplies.emit(dc.title),
        supplies.emit(dc.type),
        supplies.emit(dc.description),
        supplies.emit(dc.date)        
    ]
    
    
    def require(self):
       
        platform = self.subject[edamontology.data_3106]
        uri = 'http://thegamesdb.net/api/GetPlatform.php?id=%s' %platform
        return resources.SimpleResource(uri)
            

    def run(self, resource):
        
        root = ET.fromstring(resource)
        platform = root.find('Platform')
        if(not platform):
            return
        
        self.subject.emit(dc.title, util.readTextElement(platform, 'Platform'))
        self.subject.emit(dc.description, util.readTextElement(platform, 'overview'))
        self.subject.emit(swo.SWO_0000396, util.readTextElement(platform, 'developer'))
        self.subject.emit('manufacturer', util.readTextElement(platform, 'manufacturer'))
        
        self.subject.emit('cpu', util.readTextElement(platform, 'cpu'))
        self.subject.emit('memory', util.readTextElement(platform, 'memory'))
        self.subject.emit('graphics', util.readTextElement(platform, 'graphics'))
        self.subject.emit('sound', util.readTextElement(platform, 'sound'))
        self.subject.emit('display', util.readTextElement(platform, 'display'))
        self.subject.emit('media', util.readTextElement(platform, 'media'))
        self.subject.emit('maxcontrollers', util.readTextElement(platform, 'maxcontrollers'))
        
        for boxartRow in platform.findall('Images/boxart'):
            side = boxartRow.attrib.get('side')
            if side == 'front' and boxartRow.text:
                self.subject.emit("boxfront", baseImageUrl + boxartRow.text)
            if side == 'back' and boxartRow.text:
                self.subject.emit("boxback", baseImageUrl + boxartRow.text)
        for fanartRow in platform.findall('Images/fanart'):
            original = util.readTextElement(fanartRow, 'original')
            if original:
                thumb = util.readTextElement(fanartRow, 'thumb')
                if thumb:
                    self.subject.emit("fanart", {"fanart": baseImageUrl + original, "thumbnail": baseImageUrl + thumb})
                else:
                    self.subject.emit("fanart", baseImageUrl + original)
        for bannerRow in platform.findall('Images/banner'):
            self.subject.emit("banner", baseImageUrl + bannerRow.text)
        for consoleRow in platform.findall('Images/consoleart'):
            self.subject.emit("consoleart", baseImageUrl + consoleRow.text)
        for controllerRow in platform.findall('Images/controllerart'):
            self.subject.emit("controllerart", baseImageUrl + controllerRow.text)


class GamePredicateObject(tasks.SubjectTask):
    demand = [
        demands.required("gameElement")
    ]

    supply = [
        supplies.emit(dc.title),
        supplies.emit(dc.type),
        supplies.emit(dc.description),
        supplies.emit(dc.date),
        supplies.emit(media.rating),
        supplies.emit(swo.SWO_0000396), # Developer
        supplies.emit(swo.SWO_0000397), # Publisher
        supplies.emit(edamontology.data_3106), # Platform
        supplies.emit("players"),
        supplies.emit("boxfront"),
        supplies.emit("boxback"),
        supplies.emit("fanart"),
        supplies.emit("banner"),
        supplies.emit("trailer"),
    ]
    

    def run(self):
        gameRow = ET.fromstring(self.subject["gameElement"])
        self.subject.replace('gameElement', '')        
        gameTitle = util.readTextElement(gameRow, "GameTitle")
        self.subject.replace(dc.title, gameTitle)
        for genre in gameRow.findall("Genres/genre"):
            self.subject.emit(dc.type, genre.text)
        self.subject.emit(dc.description, util.readTextElement(gameRow, "Overview"))
        try:
            # Deserialize MM/DD/YYYY
            dateobject = datetime.datetime.strptime(util.readTextElement(gameRow, "ReleaseDate"), "%m/%d/%Y")
            self.subject.emit(dc.date, dateobject.strftime("%Y-%m-%d"))
        except ValueError:
            # can't be parsed by strptime()
            pass
        self.subject.emit(media.rating, util.readTextElement(gameRow, 'ESRB'))
        self.subject.emit(swo.SWO_0000396, util.readTextElement(gameRow, 'Developer'))
        self.subject.emit(swo.SWO_0000397, util.readTextElement(gameRow, 'Publisher'))
        self.subject.replace(edamontology.data_3106, util.readTextElement(gameRow, 'Platform'))
        self.subject.emit("players", util.readTextElement(gameRow, 'Players'))

        for boxartRow in gameRow.findall('Images/boxart'):
            side = boxartRow.attrib.get('side')
            if side == 'front' and boxartRow.text:
                self.subject.emit("boxfront", baseImageUrl + boxartRow.text)
            if side == 'back' and boxartRow.text:
                self.subject.emit("boxback", baseImageUrl + boxartRow.text)
        for fanartRow in gameRow.findall('Images/fanart'):
            original = util.readTextElement(fanartRow, 'original')
            if original:
                thumb = util.readTextElement(fanartRow, 'thumb')
                if thumb:
                    self.subject.emit("fanart", {"fanart": baseImageUrl + original, "thumbnail": baseImageUrl + thumb})
                else:
                    self.subject.emit("fanart", baseImageUrl + original)
        for bannerRow in gameRow.findall('Images/banner'):
            self.subject.emit("banner", baseImageUrl + bannerRow.text)
        self.subject.emit("trailer", util.readTextElement(gameRow, 'Youtube'))


class SearchGameCollector(tasks.SubjectTask):
    demand = [
        demands.required(dc.title),
        demands.required(edamontology.data_3106), # Platform
        demands.requiredClass("item.game", True),
        demands.none(owl.sameAs, "http://thegamesdb.net/game/[0-9]*")
    ]

    supply = [
        supplies.emit("gameElement")
    ]

    def require(self):
        title = self.subject[dc.title]
        title = title.encode('utf-8')
        platform = self.translatePlatform(self.subject[edamontology.data_3106])
        if platform:
            uri = "http://thegamesdb.net/api/GetGame.php?name=%s&platform=%s" % \
                    (urllib.quote_plus(title), urllib.quote_plus(platform))
            return resources.SimpleResource(uri)
        else:
            return []

    def run(self, resource):
        root = ET.fromstring(resource)
        gameRows = root.findall("Game")
        
        foundGameTitles = []
        for gameRow in gameRows:
            gameTitle = util.readTextElement(gameRow, "GameTitle")
            if gameTitle == self.subject[dc.title]:                
                self.subject.emit("gameElement", ET.tostring(gameRow))
                return
            foundGameTitles.append(gameTitle)
            
        #if we did not find a title return the list of found titles to the client
        if(len(foundGameTitles) > 0):
            self.subject.replace(dc.title, foundGameTitles)
        

    def translatePlatform(self, platform):
        uri = "http://thegamesdb.net/api/GetPlatformsList.php"
        resource = resources.CachedSimpleResource(uri)
        platformXML = resource.run(resource.require())

        root = ET.fromstring(platformXML)
        for tgdb_platform in root.findall("Platforms/Platform"):
            nametag = tgdb_platform.find("name")
            if nametag == None or nametag.text == None:
                continue
            if comparePlatforms(nametag.text, platform):
                return nametag.text
        return None

module = [ GamePredicateObject, SearchGameCollector, PlatformPredicateObject ]
