import os, glob, urllib, time

from resources.lib.heimdall.src.heimdall import tasks, demands
from resources.lib.heimdall.src.heimdall.predicates import *


class ArtworkDownloader(tasks.SubjectTask):
    demand = [
        demands.requiredClass("item.artwork", True),        
        demands.required("artworkurl"),
        demands.required("artworkpath"),
        demands.required(dc.title)
    ]
    
    supply = []
    

    def run(self):
        print 'Download Artwork: %s' %self.subject["artworkurl"]
        url = self.subject["artworkurl"]
        folder = self.subject["artworkpath"]
        title = self.subject[dc.title]
        self.downloadArtwork(url, folder, title)
        
        
    def downloadArtwork(self, url, folder, title):
        searchPath = os.path.join(folder, title +".*")
        #TODO glob has some limitations (i.e. issues with [])
        files = glob.glob(searchPath)
        if(len(files) == 0):
            fileExtension = os.path.splitext(url)[1]
            newFile = os.path.join(folder, "%s%s" %(title, fileExtension))
            print "File does not exist. Start download: " +newFile
            
            try:
                urllib.urlretrieve( url, newFile)
            except Exception, (exc):
                print "Could not create file: '%s'. Error message: '%s'" %(newFile, str(exc))
        else:
            print "File already exist. Won't download artwork for " +title


module = [ ArtworkDownloader ]

        