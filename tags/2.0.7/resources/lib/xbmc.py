"""
    This is a dummy file for testing and debugging XBMC plugins from the
    command line. The file contains definitions for the functions found
    in xbmc, xbmcgui and xbmcplugin built in modules
"""

import os


_loglevel = 1
_settings = {'external_filemanaging': 'true'}
_filename = 'dummy.log'
_logentry = 0


def _write_to_file(msg):
    global _filename
    global _logentry
    filepath = os.path.join( os.getcwd(), _filename )
    if _logentry == 0: mode = 'w'
    else: mode = 'a'
    fh = open(filepath, mode)
    fh.write( '%003d -- %s\n' % ( _logentry, msg ) )
    fh.close()
    _logentry += 1
    

    
# ------------------------------------------------------------------------------
#                     xbmc module functions and constants
# ------------------------------------------------------------------------------

LOGNONE    = -1
LOGNORMAL  = 0
LOGDEBUG   = 1
LOGNOTICE  = 'NOTICE'
LOGDEBUG   = 'DEBUG'
LOGWARNING = 'WARNING'
LOGERROR   = 'ERROR'

def log(msg, level=LOGNOTICE):
    """
        msg     : string - text to output.
        level   : [opt] integer - log level to ouput at. (default=LOGNOTICE)

        *Note, You can use the above as keywords for arguments and skip certain
               optional arguments. Once you use a keyword, all following
               arguments require the keyword.

        Text is written to the log for the following conditions.
            XBMC loglevel == -1
                NONE, nothing at all is logged)
            XBMC loglevel == 0
                NORMAL, shows LOGNOTICE, LOGERROR, LOGSEVERE and LOGFATAL
            XBMC loglevel == 1
                DEBUG, shows all

        example:
            xbmc.log(msg='This is a test string.', level=xbmc.LOGDEBUG)
    """
    global _loglevel
    if _loglevel == -1:
        return
    elif _loglevel == 0:
        if level == LOGNOTICE:
            msg = '%s: %s' % (level, msg)
            print msg
            _write_to_file(msg)
    else:
        msg = '%s: %s' % (level, msg)
        print msg
        _write_to_file(msg)

log('%s::Logging initiated!' % __name__)

def translatePath(path):
    b, t = os.path.split( path )
    return os.path.join( os.getcwd(), t )
    
class Keyboard:
    def __init__(self, default='', heading=None, hidden=False):
        self.default = default
        if not heading:
            heading = 'Keyboard Input'
        self.heading = heading
        self.hidden = hidden

    def doModal(self):
        self.text = raw_input('%s\n-->' % self.heading)
        
    def getText(self):
        return self.text
        
    def isConfirmed(self):
        return True







# ------------------------------------------------------------------------------
#                  xbmcplugin module functions and constants
# ------------------------------------------------------------------------------

_items_added = 0

class ListItem:
    def __init__(self, *args, **kwargs):
        pass
    def setProperty(self, *args, **kwargs):
        pass
    
def addDirectoryItem(handle, url, listitem, isFolder=False, totalItems=None):
    """
        Callback function to pass directory contents back to XBMC.
        Returns a bool for successful completion.

        handle      : integer - handle the plugin was started with.
        url         : string  - url of the entry. would be plugin:// for another
                                virtual directory
        listitem    : ListItem - item to add.
        isFolder    : [opt] bool    - True=folder / False=not a folder(default).
        totalItems  : [opt] integer - total number of items that will be passed.
                                      used for progressbar
        "\"
        *Note, You can use the above as keywords for arguments and skip certain
               optional arguments. Once you use a keyword, all following
               arguments require the keyword.

        example:
            hndl = int(sys.argv[1])
            url = 'F:\\\\Trailers\\\\300.mov'
            if not xbmcplugin.addDirectoryItem(hndl, url, listitem, False, 50):
                break
    """
    global _items_added
    _items_added += 1

    
    
def addDirectoryItems(handle, items, totalItems=None):
    """
        Callback function to pass directory contents back to XBMC as a list.
        Returns a bool for successful completion.

        handle      : integer - handle the plugin was started with.
        items       : List - list of (url, listitem[, isFolder])
                      as a tuple to add.
        totalItems  : [opt] integer - total number of items that
                      will be passed.(used for progressbar)

        *Note, You can use the above as keywords for arguments.

               Large lists benefit over using the standard addDirectoryItem()
               You may call this more than once to add items in chunks

        example:
            hndl = int(sys.argv[0])
            items = [(url, listitem, False,)]
            if not xbmcplugin.addDirectoryItems(hndl, items):
                raise Exception
    """
    global _items_added
    _items_added += len(items)

    
    
def endOfDirectory(handle, succeeded=True, updateListing=False, cacheToDisk=True):
    """
        Callback function to tell XBMC that the end of the directory listing in
        a virtualPythonFolder module is reached

        handle           : integer - handle the plugin was started with.
        succeeded        : [opt] bool - True  = script completed successfully
                                        False = script did not.
        updateListing    : [opt] bool - True  = this folder should update the
                                                current listing
                                        False = Folder is a subfolder.
        cacheToDisc      : [opt] bool - True  = Folder will cache if
                                                extended time
                                        False = this folder will never
                                                cache to disc.

        *Note, You can use the above as keywords for arguments and skip certain
               optional arguments. Once you use a keyword, all following
               arguments require the keyword.

        example:
            xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=False)
    """
    global _items_added
    print '%s -> %d items added' % (__func)



def getSetting(id):
    """
        Returns the value of a setting as a string.

        id        : string - id of the setting that the module needs to access.

        *Note, You can use the above as a keyword.

        example:
            apikey = xbmcplugin.getSetting('apikey')
    """
    global _settings
    if _settings.has_key(id):
        return _settings[id]
       

class Settings:
	def __init__(self, path):
		pass
	def getSetting(self, name):
		return ''