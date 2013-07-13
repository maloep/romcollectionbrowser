import heimdall
from heimdall import tasks
from heimdall import resources
from heimdall import supplies, demands
from heimdall.predicates import *

import json
from urllib import unquote_plus, quote_plus

tmdb_api_base = "http://api.themoviedb.org/3/"

class MoviePredicateObject(tasks.SubjectTask):
    demand = [
        demands.required(dc.identifier, "http://themoviedb.org/movie/")
    ]

    supply = [
        supplies.emit(dc.title),
        supplies.emit(dc.description),
        supplies.emit(dc.date),
        supplies.emit(dc.type),
        supplies.emit(owl.sameAs),
        supplies.emit(foaf.homepage),
        supplies.emit(foaf.thumbnail),
        supplies.emit("fanart")
    ]

    def require(self):
        uri = self.subject[dc.identifier]
        ID = uri[len("http://themoviedb.org/movie/"):]

        getConfiguration = tmdb_api_base + "/configuration?api_key=57983e31fb435df4df77afb854740ea9"
        getMovie = tmdb_api_base + "movie/" + ID + "?api_key=57983e31fb435df4df77afb854740ea9"

        return [
            resources.CachedSimpleResource(getConfiguration, "application/json"),
            resources.SimpleResource(getMovie, "application/json")
        ]

    def run(self, configuration, resource):
        c = json.loads(configuration)
        movie = json.loads(resource)

        self.subject.replace(dc.title, movie["original_title"])
        self.subject.emit(dc.description, movie["overview"])
        self.subject.emit(dc.date, movie["release_date"]) # Format is YYYY-MM-DD
        for genre in movie["genres"]:
            self.subject.emit(dc.type, genre["name"])
        self.subject.emit(owl.sameAs, "http://www.imdb.com/title/" + movie["imdb_id"])
        self.subject.emit(foaf.homepage, movie["homepage"])

        images = c["images"]
        image_base = images["base_url"]

        for size in images["poster_sizes"]:
            self.subject.emit(foaf.thumbnail, image_base + size + movie["poster_path"])

        for size in images["backdrop_sizes"]:
            self.subject.emit("fanart", image_base + size + movie["backdrop_path"])

class SearchMovieCollector(tasks.SubjectTask):
    demand = [
        demands.required(dc.title),
        #demands.optional(dc.date),
        demands.requiredClass("item.video.Movie", True),
        demands.none(owl.sameAs, "http://themoviedb.org/movie/[0-9]*")
    ]

    supply = [
        supplies.emit(owl.sameAs, "http://themoviedb.org/movie/")
    ]

    def require(self):
        title = self.subject[dc.title]
        path = "http://api.themoviedb.org/3/search/movie?api_key=57983e31fb435df4df77afb854740ea9&query=" + quote_plus(title)

        return resources.SimpleResource(path, "application/json")

    def run(self, resource):
        result = json.loads(resource)

        if "results" in result and len(result["results"]) > 0 and "id" in result["results"][0]:
            ID = result["results"][0]["id"]
            tm = "http://themoviedb.org/movie/" + str(ID)

            self.subject.emit(owl.sameAs, tm)

module = [ SearchMovieCollector, MoviePredicateObject ]
