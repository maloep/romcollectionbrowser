#!/usr/bin/python

from heimdall.core import Engine, Subject
from heimdall.predicates import *
from heimdall.threadpools import MainloopThreadPool

import item
import game_item
from games import thegamesdb

import urlparse
import sys

import logging
logging.basicConfig()
logging.getLogger("heimdall").setLevel(logging.DEBUG)

def main(uri):
    if uri == None:
        #uri = "file:///E:\\Games\\Testsets\\Scraper tests\\The Legend of Zelda - Links Awakening DX.gbc"
        uri = "file:///E:/Games/Testsets/Scraper Tests/SNES/Roms/Super Mario Kart.zip"

    if urlparse.urlparse(uri).scheme == "":
        uri = urlparse.urlunparse(("file", "", uri, "", "", ""))

    print "Running Heimdall upon:", uri

    pool = MainloopThreadPool()
    engine = Engine(pool)
    engine.registerModule(item.module)
    engine.registerModule(game_item.module)
    engine.registerModule(thegamesdb.module)

    def c(error, subject):
        if error:
            pass
            #raise error
        print subject
        pool.quit()

    metadata = dict()
    metadata[dc.identifier] = uri
    metadata[edamontology.data_3106] = 'Super Nintendo (SNES)'
    subject = Subject("", metadata)

    engine.get(subject, c)

    try:
        pool.join()
    except KeyboardInterrupt:
        pool.quit()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) >= 2 else None)
