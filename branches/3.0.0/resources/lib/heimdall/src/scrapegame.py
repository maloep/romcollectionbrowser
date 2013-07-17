#!/usr/bin/python

from resources.lib.heimdall.src.heimdall.core import Engine, Subject
from resources.lib.heimdall.src.heimdall.predicates import *
from resources.lib.heimdall.src.heimdall.threadpools import MainloopThreadPool

from resources.lib.heimdall.src.games import thegamesdb
from resources.lib.heimdall.src.games import giantbomb

import json
import time
import urlparse
import sys

import logging
logging.basicConfig()
logging.getLogger("heimdall").setLevel(logging.DEBUG)

def main(uri):
    
    pool = MainloopThreadPool()
    engine = Engine(pool)
    engine.registerModule(giantbomb.module)

    def c(error, subject):
        if error:
            pass
            #raise error
        print subject
        pool.quit()

    metadata = dict()
    metadata[dc.title] = 'Super Mario Kart'
    #metadata[dc.title] = 'Final Fantasy V Advance'
    metadata[edamontology.data_3106] = '9'
    metadata['apikey'] = '279442d60999f92c5e5f693b4d23bd3b6fd8e868'
    metadata['preferredregion'] = 'United States'
    subject = Subject("", metadata)
    subject.extendClass("item.game")

    engine.get(subject, c)

    try:
        pool.join()
    except KeyboardInterrupt:
        pool.quit()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) >= 2 else None)
