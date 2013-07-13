import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

import urlparse

mime_types = {
    ".mkv": "video/x-matroska",
    ".avi": "video/avi",
    ".mp3": "audio/mpeg",
    ".flac": "audio/flac"
}

mime_type_to_class = {
    "video/x-matroska": "item.video",
    "video/avi": "item.video",
    "audio/mpeg": "item.audio",
    "audio/flac": "item.audio"
}

class ItemPredicateObject(tasks.SubjectTask):
    demand = [
        demands.required(dc.identifier, "\.\w+$"),
    ]

    supply = [
        supplies.emit(rdf.Class, "item"),
        supplies.emit(dc.title),
        supplies.emit(dc.format)
    ]

    def run(self):
        path = urlparse.urlparse(self.subject[dc.identifier]).path
        ext = path[path.rindex("."):].lower()
        mime_type = mime_types.get(ext, None)

        title = path
        if "." in title:
            title = title[ : title.rindex(".") - len(title)]
        for slash in ["/", "\\"]:
            if slash in title:
                title = title[title.rindex(slash) + 1:]
        title = title.replace(".", " ")

        self.subject.emit(dc.title, title)
        self.subject.emit(dc.format, mime_type)

        self.subject.extendClass(mime_type_to_class.get(mime_type, "item"))

module = [ ItemPredicateObject ]
