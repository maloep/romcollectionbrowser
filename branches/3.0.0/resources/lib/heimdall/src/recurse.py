#!/usr/bin/python
# -*- coding: utf-8 -*-

from heimdall.core import Engine, Subject
from heimdall.predicates import *
from heimdall.threadpools import *

import themoviedb
import theaudiodb
import item
import video_item
import audio_item
import media_item
import json

import time
from urlparse import urlparse
from urlparse import urlsplit, urlunsplit
from urllib import quote_plus, unquote_plus
import sys
import os

import logging
logging.basicConfig()
logging.getLogger("heimdall").setLevel(logging.DEBUG)

def main(folder):
    print "Running heimdall on folder", folder
    pool = MainloopThreadPool()
    engine = Engine(pool)
    engine.registerModule(themoviedb.module)
    engine.registerModule(theaudiodb.module)
    engine.registerModule(item.module)
    engine.registerModule(video_item.module)
    engine.registerModule(audio_item.module)
    engine.registerModule(media_item.module)

    subjects = list()

    fileList = []
    for root, subFolders, files in os.walk(folder):
        for f in files:
            p = os.path.join("file://", root, f)
            fileList.append(p)

    print "Files to process", len(fileList)

    fileList = fileList[:]

    nbrBeforeQuit = len(fileList)

    def c(error, subject):
        if error:
            raise error

        print subject
        subjects.append(subject)

        if len(subjects) >= nbrBeforeQuit:
            pool.quit()

    for uri in fileList:
        metadata = dict()
        metadata[dc.identifier] = uri
        subject = Subject("", metadata)

        engine.get(subject, c)

    try:
        pool.join()
    except KeyboardInterrupt:
        pool.quit()

    print "done"

if __name__ == "__main__":
    main(sys.argv[1])
