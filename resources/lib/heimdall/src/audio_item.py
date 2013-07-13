import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

import mutagen
from urlparse import urlparse
from urllib import quote_plus, unquote_plus

class ExtractTags(tasks.SubjectTask):
    demand = [
        demands.required(dc.identifier),
        demands.requiredClass("item.audio")
    ]

    supply = [
        supplies.replace(dc.title),
        supplies.emit(upnp.album),
        supplies.emit(upnp.artist),
        supplies.emit(upnp.originalTrackNumber),
    ]

    def run(self):
        uri = urlparse(self.subject[dc.identifier]).path

        if uri:
            f = mutagen.File(uri, easy=True)

            for album in f.get("album", []):
                self.subject.emit(upnp.album, album)

            for artist in f.get("artist", []):
                self.subject.emit(upnp.artist, artist)

            title = f.get("title", [])
            if len(title) > 0:
                self.subject.replace(dc.title, title[0])

            self.subject.extendClass("item.audio.musicTrack")

module = [ ExtractTags ]
