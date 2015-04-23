# How to add MAME roms with offline game description #
As [MAWS](http://maws.mameworld.info/maws/) is down since some weeks here is a little guide how to import MAME roms using RCBs offline scrapers and emumovies MAME artwork.

You can monitor the progress of MAWS coming back or not on http://www.mameworld.info. If you want to help to make this happen there is an option to donate to the site maintainers: [link](http://www.mameworld.info/ubbthreads/showthreaded.php?Number=273563).

## Get artwork from emumovies ##
  * Register at http://emumovies.com (paid subscription is only required to download videos)
  * Download and install the [Emumovies Download Service Utility](http://emumovies.com/forums/index.php/files/file/321-emumovies-download-service-utility/)
  * Launch the Download Service Utility
  * Enter your emumovies account information
  * Select System MAME, Path to your MAME rom files and the path where the tool should store the downloaded artwork (and videos)
  * In "Available Media" dropdown list select "- All Artwork"
  * Go! -> This will start to download all available information found on emumovies for your MAME roms. The download tool will automatically rename the downloaded files, so that RCB can easily match the media files with your available rom files.
  * optional: If you also want to use game videos select your favourite video type in "Available Media" dropdown list and download again.

Note: RCB does not support all artwork types out of the box. If you want to save download time just get "Advert", "Cabinet", "Marquee", "Snap" and "Title" artwork one by one.

## Get offline game description for MAME roms ##
Get the file [MAME synopsis RCB 201202.zip](http://romcollectionbrowser.googlecode.com/files/MAME%20synopsis%20RCB%20201202.zip) from RCBs project page. Unzip it somewhere on your computer. It contains the description file "MAME.txt" with all game descriptions and the parse instruction file "parserConfig.xml" that tells RCB how to parse the game description.


## Add MAME Rom Collection with offline scraping ##
If it is the first time you start RCB you will be asked to create a config file. If you already have a config file just launch the context menu and select "Add Rom Collection". The following steps will be the same in both scenarios.

  * Select "Game info and artwork are available locally"
  * Select platform "MAME"
  * Browse to your MAME emulator
  * Leave "%ROM%" as emu param (depending on your emulator you have to alter your emu params for launching games - but you can do this later...)
  * Browse to your MAME roms
  * Use `*.zip` as file mask
  * Choose your artwork types. Here is a short list how I mapped available RCB artwork types with MAME artwork types. Feel free to change this.
    * RCB -> MAME
    * boxfront -> Advert
    * cabinet -> Cabinet
    * marquee -> Marquee
    * action -> Snap
    * title -> Title
    * gameplay (video) -> Video\_MP4
  * Select "One description file for all games" as game description type
  * Browse to the game description file "MAME.txt" that you downloaded before
  * Browse to the parse instruction file "parserConfig.xml" that you downloaded before
  * Select "No" when you are asked to add more Rom Collections (feel free to add more collections ofc)
  * **Cancel Game Import dialog** - you need one more setting that is not offered by the config wizard in the current release
  * Launch RCBs context menu and select "Edit Offline Scrapers"
  * Make sure you have selected "MAME" in the Scraper list
  * Enable the option "Use filename as crc"
  * Make sure that the option "Use foldername as crc" is NOT enabled
  * Save config
  * Launch RCBs context menu again and select "Import Games"
  * Import Games (select Rom Collection "MAME" if you only want to import MAME roms)