#!/usr/bin/python

from heimdall.core import Engine, Subject
from heimdall.predicates import *
from heimdall.threadpools import MainloopThreadPool

import themoviedb
import theaudiodb
import item
import video_item
import audio_item
import media_item
import json

import time
import urlparse
import sys

import logging
logging.basicConfig()
logging.getLogger("heimdall").setLevel(logging.DEBUG)

def main(uri):
    if uri == None:
        uri = "file:///home/SomeUser/movies/Horrible Bosses.mkv" # A file which doesn't exist, just used for testing

    if urlparse.urlparse(uri).scheme == "":
        uri = urlparse.urlunparse(("file", "", uri, "", "", ""))

    print "Running heimdall upon", uri

    pool = MainloopThreadPool()
    engine = Engine(pool)
    engine.registerModule(themoviedb.module)
    engine.registerModule(theaudiodb.module)
    engine.registerModule(item.module)
    engine.registerModule(video_item.module)
    engine.registerModule(audio_item.module)
    engine.registerModule(media_item.module)

    def c(error, subject):
        if error:
            raise error

        print subject
        pool.quit()

    metadata = dict()
    metadata[dc.identifier] = uri
    subject = Subject("", metadata)

    print "Running heimdall upon", subject

    engine.get(subject, c)

    try:
        pool.join()
    except KeyboardInterrupt:
        pool.quit()

#    print json.dumps(s.dump(), sort_keys=True, indent=4)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) >= 2 else None)
