

On first run when there is no config file available RCB will ask you to create a config file with the wizard. You can also launch the wizard anytime from context menu via "Add Rom Collection".

First you have to choose a scenario: Online scraping or local data. In online scraping scenario you will usually just have a set of rom files and nothing else. RCB will scrape different web sites for game infos and artwork and adds them to your collection. In local data scenario you already have all this data somewhere on your system. In this case you just have to tell RCB where to find artwork, videos and game descriptions on your system. You can also mix both scenarios and use your local available artwork but scrape game information online. In this case you should choose the option "Game info and artwork are available locally" to tell RCB the path to your artwork.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%201%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%201%20-%20small.jpg)

# Online scraping scenario #

## Platform ##
Select a platform from the list. If you don't find your platform in the list, select "Other" and type the name of your platform. Note: Some scrapers won't work properly without a known platform.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%202%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%202%20-%20small.jpg)

## Emulator path ##
Select the path to the emulator (executable) for the given platform.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%203%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%203%20-%20small.jpg)

## Emulator params ##
Enter the parameters for the emulator. Use "%ROM%" as placeholder if you need to pass the rom filename to the emulator. Check section [Emulator params](EditRomCollectionLaunchGames#Emulator_Params.md) for a complete list of available placeholders.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%204%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%204%20-%20small.jpg)

## Path to your rom files ##
Select the path to your rom files. RCB will also check all sub directories below the given path.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%205%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%205%20-%20small.jpg)

## Rom file mask ##
Enter one or more file masks (comma-separated). RCB will search the rom path and all sub folders for files that match the given file mask. Make sure that you use the `*` as wildcard. E.g. use "`*`.zip,`*`.smc" to search for all zip and smc files below the given rom path.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%206%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%206%20-%20small.jpg)

## Artwork path ##
Select the path where you want to store your artwork (or where your artwork is already stored). This folder can be empty. You should store your artwork separated per platform (Rom Collection), so there should be one folder SNES artwork, Amiga artwork or whatever.

In online scraping scenario RCB will create the following sub folders (one for every different artwork type):

MAME: boxfront, action, title, cabinet and marquee

all other: boxfront, boxback, cartridge, screenshot and fanart


If you want to add your own artwork to RCB in online scraping scenario, make sure that your artwork is placed in the correct sub folders. The user that runs xbmc needs write access to these folders. The downloaded files will be named like the rom file with the extension of the downloaded image file.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%207%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%207%20-%20small.jpg)

Repeat these steps for every Rom Collection you want to add.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%208%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%208%20-%20small.jpg)


# Local data scenario #

The first steps of this wizard are equal to the online scraping scenario. You have to choose a platform, the path to your emulator and rom files. After this is done there will be some local data specific configuration steps.

## Local artwork type ##
Choose an artwork type.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%201%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%201%20-%20small.jpg)

## Local artwork path ##
Select the path to the artwork of this type. RCB will search for image files with the same names as your rom files.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%202%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%202%20-%20small.jpg)

Repeat the last two steps for every artwork type you want to import

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%203%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%203%20-%20small.jpg)

## Game description type ##
Choose the type of description files. There may be large files with descriptions for all of your games or single description files that only contain description for one game. If you just want to use your local artwork and scrape game info online, select "Scrape game info online".

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%204%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%204%20-%20small.jpg)

## Game description path ##
Select the path to your description files.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%205%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%205%20-%20small.jpg)

## Parse instruction path ##
Select the path to the parse instruction for the given description file.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%206%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Offline%206%20-%20small.jpg)

Repeat these steps for every Rom Collection you want to add.

> ![http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%208%20-%20small.jpg](http://romcollectionbrowser.googlecode.com/files/Wizard%20-%20Online%208%20-%20small.jpg)


# Emulator autoconfig (Android only) #
On Android devices emulator params might become quite long and tricky to enter. Thats why RCB supports emulator auto configuration. There is a file called "emu\_autoconfig.xml" where you can add emulator arguments for all emulators and platforms. There is already a big number of emulators covered in this file, so chances are good that the emulator of your choice is already available. By default this file will be copied to RCBs userdata directory (XBMC/userdata/addon\_data/script.games.rom.collection.browser) but you can specify a new path via addon settings. RCB also scans your system to check if the emulators available in autoconfig are installed on your system.

In the config wizard you only have to select the emulator of your choice (you can also choose an emulator that is not yet installed on your device and do this later on).
> ![https://romcollectionbrowser.googlecode.com/svn/wiki/screenshots/screen_configwizard_autoconfig1.jpg](https://romcollectionbrowser.googlecode.com/svn/wiki/screenshots/screen_configwizard_autoconfig1.jpg)

Afterwards you can edit the parameters of the chosen emulator.
> ![https://romcollectionbrowser.googlecode.com/svn/wiki/screenshots/screen_configwizard_autoconfig2.jpg](https://romcollectionbrowser.googlecode.com/svn/wiki/screenshots/screen_configwizard_autoconfig2.jpg)

The rest of the config wizard is the same as described above for all systems.