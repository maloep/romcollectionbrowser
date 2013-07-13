import tasks

import os
import datetime
import hashlib
import tempfile
import urllib
import urllib2
import urlparse

import logging
log = logging.getLogger("heimdall.resources")

def vfs_read(uri, mime):
    # Headers and the file:// protocol are mutually exclusive. Headers are only
    # supported by urllib2, and the file:// protocol is only supported by urllib
    if mime:
        request = urllib2.Request(uri, headers={"Accept" : mime})
        return urllib2.urlopen(request).read()
    else:
        # urllib handles all protocols, so always fall back to urllib in the
        # absense of headers
        return urllib.urlopen(uri).read()

class Resource(tasks.Task):
    """
    Raw resource task, when acquired as requirement it may be used to access the
    resource in its rawest form. Will behave much like a standard file object.
    """
    def __init__(self, uri, mime = None):
        self.uri = uri
        self.mime = mime

    def run(self):
        return self

    def read(self):
        return vfs_read(self.uri, self.mime)

    def __repr__(self):
        return "heimdall.resources.Resource(\"%s\")" % self.uri

class SimpleResource(tasks.Task):
    """
    Simpler resource access, when acquired as requirement it will give the entire
    resource as result. This is useful when a resource is needed in its entirety
    to process. Examples of can be text files such as xml, json etc. The resource
    is not parsed and its binary form is read.
    """
    def __init__(self, uri, mime = None):
        self.uri = uri
        self.mime = mime

    def require(self):
        return Resource(self.uri, self.mime)

    def run(self, resource):
        return resource.read()

class CachedSimpleResource(SimpleResource):
    """
    Adds a caching layer on top of SimpleResource. duration is a timedelta or
    number of seconds for which the cache is valid (default: one week). Setting
    invalidateCache to True re-caches immediately.
    """
    def __init__(self, uri, mime = None, duration=datetime.timedelta(weeks=1), invalidateCache=False):
        self.needsCaching = invalidateCache or self.isExpired(uri)
        if self.needsCaching:
            super(CachedSimpleResource, self).__init__(uri, mime)
        else:
            super(CachedSimpleResource, self).__init__(self.getCachedURI(uri))

        self.expires = None # When does the current request expire?
        if isinstance(duration, datetime.timedelta):
            self.expires = datetime.datetime.now() + duration
        elif duration > 0:
            self.expires = datetime.datetime.now() + datetime.timedelta(seconds=duration)

    def run(self, resource):
        result = super(CachedSimpleResource, self).run(resource)
        if self.needsCaching:
            try:
                log.debug("Caching resource %s to %s" % (self.uri, self.getCachedURI(self.uri)))
                # Create the cache folder if it doesn't exist
                if not os.path.exists(os.path.join(tempfile.gettempdir(), "heimdall")):
                    os.makedirs(os.path.join(tempfile.gettempdir(), "heimdall"))
                open(self.getCachedURI(self.uri), "wb").write(result)
                if self.expires:
                    # Our serialization format "YYYY-MM-DD HH:MM:SS" mirrors isoformat(' ') with no microseconds
                    open(self.getCachedURI(self.uri) + ".expires", "w").write(self.expires.strftime("%Y-%m-%d %H:%M:%S"))
                elif os.path.exists(self.getCachedURI(self.uri) + ".expires"):
                    # If there's no expiration, make sure old .expires files are removed
                    os.remove(self.getCachedURI(self.uri) + ".expires")
            except Exception as e:
                log.exception("Failed to cache resource: %s" % e)
        return result

    def getCachedURI(self, uri):
        # The URI of the resource is invariant and derivations shouldn't be re-calculated.
        try:
            return self.cachedURI
        except:
            self.cachedURI = os.path.join(tempfile.gettempdir(), "heimdall", hashlib.md5(uri).hexdigest())
            # Cast to URI for vfs_read()
            self.cachedURI = urlparse.urlparse(self.cachedURI).path
            return self.cachedURI

    def isExpired(self, uri):
        # The presence of a .expires file indicates an expiration time
        if os.path.exists(self.getCachedURI(uri) + ".expires"):
            try:
                timestring = open(self.getCachedURI(uri) + ".expires").read()
                # Deserialize YYYY-MM-DD HH:MM:SS
                timeobject = datetime.datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S")
                return timeobject <= datetime.datetime.now()
            except ValueError as e:
                log.error("\"%s\" can't be parsed by strptime(): %s" % (timestring, e))
            except Exception as e:
                log.error(e)
        # If the resource itself doesn't exist, consider it expired
        return not os.path.exists(self.getCachedURI(uri))
