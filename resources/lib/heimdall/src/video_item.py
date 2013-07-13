import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

class GuessVideoOrEpisode(tasks.SubjectTask):
    demand = [
        demands.requiredClass("item.video"),
        demands.required("duration")
    ]

    supply = [
        supplies.replace(rdf.Class, "item.video.Movie"),
        supplies.replace(rdf.Class, "item.video.Episode"),
    ]

    def run(self):
        duration = self.subject["duration"]

        if duration > 3600: # if longer than an hour, just guess movie
            self.subject.extendClass("item.video.Movie")
        else:
            self.subject.extendClass("item.video.Episode")

module = [ GuessVideoOrEpisode ]
