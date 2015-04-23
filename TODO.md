This TODO list / roadmap is a working document. It will change quite frequently as I am always adding, removing or reordering issues that I want to work on for the next release. If you made a request or reported an issue that you don't find on the list please remind me because chances are that I just forgot to add it.

# this release #
> X**'Game Boy Advance' and not 'Game Boy Advanced' in autoconfig
  * dummyGUI instance has no attribute 'xbmcversionNo'
  * disable screensaver before launching roms
  * escape xml characters before writing files (nfo, ...)
  * I noticed a strange thing with the "Export game database (nfo files)" function. Some of the nfo files exported don't have the Plot information even for the games that display it correctly in RCB.**

# next relase #
  * launch RCB with filter settings as arguments
  * include heimdall scrapers
  * non-ascii characters in kodi
  * it is possible to add in the selection system "Cave" "Capcom Play System 1" "Capcom Play System 2" "Capcom Play System 3" "Sammy Atomiswave" please ?
  * Feature request - add in the ability to hard set the artwork per ROM/game. We just select the .png, .jpeg/jpg., .bmp and on we go with our lives. Same for boxfront, back. etc.

## reported bugs ##
  * script to fix focus issues: http://forum.kodi.tv/showthread.php?tid=70115&pid=1877457#pid1877457
  * convert skin files to 1080P
> fix by somawhite402: http://forum.kodi.tv/showthread.php?tid=70115&pid=1901014#pid1901014
    * patch for [issue 147](https://code.google.com/p/romcollectionbrowser/issues/detail?id=147) (arucard)
    * new MAME offline files (1.54 by ricardo85x)
    * differ between local and remote errors whils scraping games. Don't interrupt import on remote errors.
    * better handling of subprocess (Application::create() error): http://forum.kodi.tv/showthread.php?tid=70115&pid=1853788#pid1853788
    * when you have videos selected for games, whilst browsing the video will still play if the next game does not have a video.
    * enable fullscreen video if video in small window is playing
    * when deleting games, jump to the next game in the list (not at the beginning)
    * after exiting games in Confluence list view the focus goes to the filter pane
    * start RCB twice: atomic init routine
    * XBMC frequently locks up on shutdown
    * import games with multiple . or - causes errors (like "WCW vs. NWO - world tour") --> "." interpreted as separator
    * still missing the possibility to define "Rom File Mask" as **.tzx.zip or**.tap.zip
    * pylzma for python 2.7 (http://pypi.python.org/pypi/pylzma/)
      * Linux 32bit
      * Linux 64bit
    * autoplay video in Info window not reliable
    * check windowed mode with popen
    * filter controls in Aeon Nox (1080p issue?)
    * It seems that "/" will not work as a delimiter? Could I add that as a feature request? (offline scrapers)
    * Is there a way to trigger the video to adjust to the focused game when the scroll bar is used?
    * ricardo85x: I did "hacked" RCB to run FBA roms using the Virtual Boy config.
> Could you tell me how can I rename the Virtual boy to Final burn on platform select list?
    * Home button returns to XBMC main screen. RCB can not be started anymore.


## features ##
  * replace %GAMECMD% if present, otherwise replace complete parameter
  * default view per rom collection


# "near"-future releases #
## General ##
  * game sets
  * home screen with platform selection
  * Android Games
  * Include Final Burn Alpha (same file names as MAME?)

## Import games ##
  * ignore MAME bios files
  * import games with original game names, allowing several versions of the same game
  * import on startup: adjust for other skins (e.g. Aeon Nox) --> new XBMC feature background progress dialog?

## Browse Games ##
  * add option to allow media to keep playing. --> test with libretro
  * view images fullscreen by pressing enter upon the art or similar
  * option to hide game infos in main view (show up on pressing I or similar)
  * add option to play a video only once
  * change view for Info to Thumbs -> stop video
  * option to hide filters and view options while browsing games

## Launch games ##
  * show message box before extracting games
  * add launch settings to addon settings. add option to overwrite settings per rom collection
  * try to use "at" to restart XBMC: http://forum.xbmc.org/showthread.php?tid=134913 (Linux only?)
  * new placeholders in emuParams: %EMUPATH%, %ROMPATH%
  * Random game option ([Issue 82](https://code.google.com/p/romcollectionbrowser/issues/detail?id=82))
  * popen options (suspend, pause, ...)
  * option to always launch the last savestate
  * open cmd window minimized


# Future releases #
### General ###
  * check for errors in scrapeonstartup
> > --> error handling when there are errors in config?
  * check how to refresh XBMC artwork cache
  * RPi support
  * backup MyGames.db and config.xml before editing or game import
  * Edit offline scrapers:
    * move encoding from scraper to site
    * scraper encoding: add to dialog
  * config wizard:
    * create local data config file with wizard: search game by crc (or check how to remove this option completely)
    * configuration templates (emumovies, emuxtras, ...)
    * improve config wizard (suggest options, paths, more options)
  * better handling of configuration errors (allow to launch RCB and edit configuration)
  * new option: Delete Selection
  * Edit Game dialog
  * Map button to "Add to Favorites"
  * new wizards (recently played, recently added)

#### Data model ####
  * game completed (bool)
  * game broken (bool)
  * game added (datetime)
  * game updated (datetime)
  * game played (datetime)
  * viewstate on RC basis

### Import games ###
  * add filename matching (instead of crc) to offline scraper
  * apple makes a shadow folder called '.AppleDouble' and makes an identically named file entry in that directory for every file in the real directory.
  * refactor dbupdate (requires data model changes)
    * check preconditions before game import
  * create scrape statistics
    * time taken
    * games total
    * missing info
    * missing artwork (per type)
  * Scraper improvements
    * scraping option: use subtitle search
    * only search for subtitles with : and - (and maybe only when sequel number)
    * support a.k.a. titles from mobygames
  * new option: crc from complete zip or first entry
  * option to hide progress bar in background mode
  * http://www.mobygames.com/game/ps2/ace-combat-5-the-unsung-war/credits
  * http://www.thecoverproject.net/
  * ask before cancel
  * skip 2nd and 3rd scraper if all info is found with first one
  * manually enter name of scraped game (rescrape or interactive)
  * select artwork during import
  * support for default images (if no image was found)

### Browse games ###
  * remap home button
  * video playback in non-Confluence skins
  * add imageplacing options to Night skin
  * add counter to Night skin
  * show previous and next console in Nights console filter
  * option to keep artwork ratio
  * check if browsing options have changed and reload the list
  * filetypeformainview2 is missing
  * remove imageplacing mechanism?
    * define several views with large and small images
    * check for fallback images
  * Simplicity
    * relative position of favorite stars in thumbs view
  * create skin specific game info view
  * if game has url: option to launch in browser
  * ability to view PDF manual
  * Container.NextSortMethod

### Launch games ###
  * use Popen for pre and post launch commands
  * add option to use json api instead of kill command
> > Linux
> > wget -q -O/dev/null --header='Content-Type: application/json' --post-data='{"jsonrpc": "2.0", "method": "Application.Quit", "id":"1"}' http://localhost/jsonrpc
> > Windows (http://sourceforge.net/projects/gnuwin32/files/wget/)
> > "%PROGRAMFILES%\GnuWin32\bin\wget.exe" -q --header="Content-Type: application/json" --post-data="{\"jsonrpc\":\"2.0\", \"method\": \"Application.Quit\", \"id\":\"1\"}" http://localhost/jsonrpc
  * add option to autostart RCB everytime in RCB service
  * per game emulator and config (e.g. Amiga)
  * try to write black background before launch


# Support topics #
  * check launching games (after playing a few minutes the window resize does not work anymore)

> --> XBMC power saving?
    * provide pysqlite libraries for linux
    * "Resident Evil (USA) (Disc 1)" --> video playback issues
    * launch other scripts while RCB is running
    * howto openelec and xbmcbuntu
    * http://forum.xbmc.org/showthread.php?tid=70115&pid=1593289#pid1593289
    * http://forum.xbmc.org/showthread.php?tid=70115&pid=1714015#pid1714015

# Hints / Tipps #
  * launch games with saturn emulator ssf: http://forum.xbmc.org/showthread.php?tid=70115&pid=1429511#pid1429511
  * using RCB artwork as screensaver: http://forum.xbmc.org/showthread.php?tid=70115&pid=1431809#pid1431809
  * closing games with eventghost (and insert coin in MAME): http://forum.xbmc.org/showthread.php?tid=70115&pid=1432755#pid1432755
> http://forum.xbmc.org/showthread.php?tid=70115&pid=1434934#pid1434934
> http://forum.xbmc.org/showthread.php?tid=70115&pid=1435200#pid1435200
> http://forum.xbmc.org/showthread.php?tid=70115&pid=1435476#pid1435476
    * closing emulator on xbox360 X button: http://forum.xbmc.org/showthread.php?tid=70115&pid=1434773#pid1434773
    * delete art with no games: http://forum.xbmc.org/showthread.php?tid=70115&pid=1439452#pid1439452
    * http://forum.xbmc.org/showthread.php?tid=70115&pid=1697983#pid1697983 (offline descs)
    * http://forum.xbmc.org/showthread.php?tid=70115&pid=1699360#pid1699360 (offline descs)


# string id update #
> id="350 -> id="320
> id="400 -> id="321
> id="401 -> id="322
> id="450 -> id="323
> id="500 -> id="324
> id="510 -> id="325
> id="520 -> id="326
> id="530 -> id="327
> id="5400 -> id="3275
> id="5500 -> id="3280
> id="5600 -> id="3285
> id="5700 -> id="3290
> id="30000 -> id="32999


# new XBMC features to consider #
  * background progress dialog during import
  * xbmcvfs.exists
  * dialog.notification
  * 

&lt;label&gt;

$LOCALIZE[SCRIPTXXX](SCRIPTXXX.md)

&lt;/label&gt;

  --> 

&lt;label&gt;

$ADDON[

<script\_id>

 

<string\_id>

]

Unknown end tag for &lt;/label&gt;




# Wiki #
## new features ##
  * new repository

## General ##
  * startup guide:
    * suggested file structure
    * install emulators
  * In-Depth guide, RCBs inner workings
    * game import, scrapers
    * imageplacing

## FAQ ##
  * FAQ update: images are not shown correctly
  * looking into the db with SQLite Studio
  * how to reset RCB
  * retroarch: http://forum.xbmc.org/showthread.php?tid=165163
  * clear image cache
  * startup configuration error
  * Error in scrape on startup
  * control XBMC in background:
    * solo mode
    * scripts to disable events (LIRC.stop, LIRC.start)
      * http://forum.xbmc.org/showpost.php?p=800073&postcount=1273
      * http://forum.xbmc.org/showpost.php?p=1004261&postcount=1994
  * Home button crashes RCB
  * encoding issues

## Improvements ##
  * Offline scraper explanation
  * Link to config wiki in Launch games / Browse games sub sections
  * Link to SQLite Browser