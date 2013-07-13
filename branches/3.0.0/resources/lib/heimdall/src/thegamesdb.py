import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

from game_item import comparePlatforms

import datetime
import difflib
import urllib
import xml.etree.ElementTree as ET

baseImageUrl = "http://thegamesdb.net/banners/"

def readTextElement(parent, elementName):
    element = parent.find(elementName)
    return element.text if (element != None and element.text != None) else ''

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
        supplies.emit(foaf.thumbnail),
        supplies.emit("fanart"),
        supplies.emit("banner"),
        supplies.emit("trailer"),
    ]
    

    def run(self):
        gameRow = ET.fromstring(self.subject["gameElement"])
        
        gameTitle = readTextElement(gameRow, "GameTitle")
        self.subject.replace(dc.title, gameTitle)
        for genre in gameRow.findall("Genres/genre"):
            self.subject.emit(dc.type, genre.text)
        self.subject.emit(dc.description, readTextElement(gameRow, "Overview"))
        try:
            # Deserialize MM/DD/YYYY
            dateobject = datetime.datetime.strptime(readTextElement(gameRow, "ReleaseDate"), "%m/%d/%Y")
            self.subject.emit(dc.date, dateobject.strftime("%Y-%m-%d"))
        except ValueError:
            # can't be parsed by strptime()
            pass
        self.subject.emit(media.rating, readTextElement(gameRow, 'ESRB'))
        self.subject.emit(swo.SWO_0000396, readTextElement(gameRow, 'Developer'))
        self.subject.emit(swo.SWO_0000397, readTextElement(gameRow, 'Publisher'))
        self.subject.replace(edamontology.data_3106, readTextElement(gameRow, 'Platform'))
        self.subject.emit("players", readTextElement(gameRow, 'Players'))

        for boxartRow in gameRow.findall('Images/boxart'):
            side = boxartRow.attrib.get('side')
            if side == 'front' and boxartRow.text:
                self.subject.emit(foaf.thumbnail, baseImageUrl + boxartRow.text)
        for fanartRow in gameRow.findall('Images/fanart'):
            original = readTextElement(fanartRow, 'original')
            if original:
                thumb = readTextElement(fanartRow, 'thumb')
                if thumb:
                    self.subject.emit("fanart", {"fanart": baseImageUrl + original, "thumbnail": baseImageUrl + thumb})
                else:
                    self.subject.emit("fanart", baseImageUrl + original)
        for bannerRow in gameRow.findall('Images/banner'):
            self.subject.emit("banner", baseImageUrl + bannerRow.text)
        self.subject.emit("trailer", readTextElement(gameRow, 'Youtube'))

    def readTextElement(self, parent, elementName):
        element = parent.find(elementName)
        return element.text if (element != None and element.text != None) else ''


class SearchGameCollector(tasks.SubjectTask):
    demand = [
        demands.required(dc.title),
        demands.required(edamontology.data_3106), # Platform
        demands.requiredClass("item.game", True),
        demands.none(owl.sameAs, "http://thegamesdb.net/game/[0-9]*")
    ]

    supply = [
        supplies.emit(owl.sameAs, "http://thegamesdb.net/game/")
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

        # TheGamesDB has search ordering problems. Sucks for XML scrapers... not for difflib!
        possibilities = [readTextElement(gameRow, "GameTitle") for gameRow in gameRows]
        gameTitle = difflib.get_close_matches(self.subject[dc.title], possibilities, 1)
        if gameTitle:
            gameTitle = gameTitle[0]
            for gameRow in gameRows:
                if gameTitle == readTextElement(gameRow, "GameTitle"):
                    gameId = readTextElement(gameRow, "id")
                    if gameId:
                        self.subject.emit("gameElement", ET.tostring(gameRow))
                    break

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

module = [ GamePredicateObject, SearchGameCollector ]
