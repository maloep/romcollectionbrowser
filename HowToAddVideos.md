# How to add videos to your Rom Collection #
Videos are not downloaded automatically with the available online scrapers. But RCB is able to handle your game videos if you have any. A good ressource for game videos is http://emumovies.com (requires paid subscription). Here is a short step by step guide how to get your videos from emumovies and add them to your current setup.

## Get videos from emumovies ##
  * Register at http://emumovies.com and get a monthly, yearly or life-time subscription (paid subscription is required to download videos)
  * Download and install the [Emumovies Download Service Utility](http://emumovies.com/forums/index.php/files/file/321-emumovies-download-service-utility/)
  * Launch the Download Service Utility
  * Enter your emumovies account information
  * Select System, Path to your rom files and the path where the tool should store the downloaded artwork and videos
  * Note: recent versions of the tool won't download videos by default with "Available Media" set to "- All Artwork -". You have to select the preferred video type (Video\_FLV, Video\_MP4, ...) manually in the "Available Media" dropdown list if you want to download video files.
  * Go! -> This will start to download all available information found on emumovies for your Rom Collections. The download tool will automatically rename the downloaded files, so that RCB can easily match the media files with your available rom files.
  * Check the artwork and video files that have been downloaded by the tool. There may also be some artwork files downloaded by the tool that RCB might have missed. So you can also use this tool to complete your already available artwork collections.

## Import existing videos into RCB ##
RCB won't create pathes to video files with the config wizard by default. You have to add the path to your video files manually after you finished the config wizard:

  * In RCB launch the context menu (pressing "C" on the keyboard or "Menu" on the remote) and go to "Edit Rom Collection"
  * Go to the "Import game data" tab
  * Select the Rom Collection that you want to edit
  * Select "Add media path"
  * Select "gameplay (video)"
  * Browse to the path where RCB can find your game videos
  * Enter the file mask. You can leave "`%GAME%.*`" as suggested, this will find all files that are named like your rom files regardless of the file extension. You could also use something like "`%GAME%.MP4`" if you want to make sure RCB only imports .MP4 files.
  * Save the config file when you have added all video pathes for your Rom Collections
  * Launch the context menu again and go to "Import Games"
  * If you already scraped all data for your Rom Collections, just use the scraper "local artwork" (available since version 0.9.6). This will only check for new artwork files that are available locally. RCB won't check online ressources or update other game information.
  * If you did not import data for this Rom Collection before you can use any scrapers you like. Your new video files will be imported together with all other data.
