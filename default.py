
import os
import sys

# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

#import xbmc
# create our language object
#__language__ = xbmc.Language( os.getcwd() ).getLocalizedString

# Start the main gui
if __name__ == "__main__":
    # only run if compatible
    #if ( _check_compatible() ):
        # main window
        import gui