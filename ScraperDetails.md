

There are different types of scrapers that are supported by RCB: scrapers in RCB can scrape online or offline (local) content and they can be built-in or external. Online scrapers will fetch information and artwork from various internet sites like thegamesdb or mobygames, offline (local) scrapers will import information and/or artwork that is already stored on your computer. Built-in scrapers are already shipped with RCB. This means you don't have to configure anything, these scrapers will always be available in RCBs import games dialog. External scrapers are new scrapers that RCB does not know when it is shipped. You have to tell RCB where it can find the game description and the parse instruction. This can be done in the config wizard or the "Edit Offline Scrapers" dialog.

This site will explain all the built-in scrapers that are shipped with RCB. It also collects what is provided by certain scrapers (sometimes there is not more information available on the site, sometimes I just have to update my scrapers to get more info).

# local built-in scrapers #
There are two special built-in scrapers that will look for local content on your computer.
## local nfo ##
One special scraper is the "local nfo" scraper. During a game import, RCB creates a .nfo file for every game with all scraped game information (if you did not disable this feature in Addon settings). These files can be used to rebuild your database in case of an error or if you want to change game properties. You can create or modify these files by hand.

## local artwork ##
As the name says this scraper will just check your configured artwork folders for new files. It won't do any online searching or scraping and won't change any other game information. This is useful if you updated your artwork folders outside of RCB.

# online built-in scrapers #
Please note: all of these sites need help to update and maintain their databases. Think about registering and contributing to (one of) these projects.
## thegamesdb ##
http://thegamesdb.net/
### Info ###
  * Description
  * Genre
  * Developer
  * Publisher
  * Players
  * ReleaseYear

### Artwork ###
  * fanart
  * boxfront
  * boxback
  * screenshot

## archive.vg ##
http://archive.vg/
### Info ###
  * Description
  * Genre
  * Developer
  * Publisher
  * ReleaseYear
  * Region

### Artwork ###
  * boxfront

## giantbomb ##
http://www.giantbomb.com/
### Info ###
  * Description
  * Genre
  * Developer
  * Publisher
  * ReleaseYear

### Artwork ###
  * screenshot

## mobygames ##
http://www.mobygames.com/
### Info ###
  * Description
  * Genre
  * Developer
  * Publisher
  * ReleaseYear

### Artwork ###
  * boxfront
  * boxback
  * screenshot
  * cartridge

## MAWS ##
http://maws.mameworld.info
### Info ###
  * Description
  * Genre
  * Developer
  * ReleaseYear
  * Players
  * Controller

### Artwork ###
  * boxfront
  * action
  * title
  * marquee
  * cabinet