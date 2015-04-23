

# Prio 1 #
## General ##
  * rework of config.xml
    * separate rom path and file mask
    * Platform instead of RomCollection?
    * add sources like for files in XBMC?
    * add region information to source?
    * add several launcher configurations to one RC/Platform entry (and store launcher per game in db)?

## Datamodel ##
  * add all possible properties to dataobjects
  * add rating table with source (thegamesdb, giantbomb, ...)
  * decide if year should be stored as flat property (not as own entity)
  * date format

## Scraping / Game import ##
  * support importing of more than one platform (find game and add releases)
  * implement all possible properties and entities for all scrapers
  * add region filter (get region from rom collection, rom name, rom file, ...)

## Launching ##
  * integrate game launching in new release again
    * decide how to support multi rom games (store all roms in db or just the first rom and find the rest while launching)

## UI/Browsing ##
  * decide if imageplacing should be completely removed
```
	<texture>$INFO[ListItem.Property(gameinfolowerleft)]</texture>
```
> > vs.
```
	<texture>$INFO[ListItem.Property(boxfront)]</texture>
```
  * add minimal support for all scraped game info and extra entities (persons, platform, ...) to check scrape results


# Prio 2 #
## General ##
  * export game database as nfo files
    * add option to overwrite existing files
    * add option to export statisitcal or user specific data (isFavorite, launchCount, ...)

## Datamodel ##
  * add extra info for arcade machines (separate table or properties in platform?)
  * add source (site or url) to downloaded files

## Scraping / Game import ##
  * add config option for number of artwork files (screenshots)
  * add config option for number of items (persons, ...)
  * add config option to ignore artwork from certain scrapers
  * integrate offline scrapers in new release (try to ease configuration of offline scrapers)

## Launching ##
  * support multiple launchers per platform/game

## UI/Browsing ##
  * add full support for all scraped game info and extra entities (persons, platform, ...) to check scrape results
  * Console view / dash board
  * rework game filter (use XBMCs movie filter as template, support dynamic filters of all database properties)
  * decide how to support fallback artwork (general screenshot if no special screenshot is available etc.)

# Prio 3 #
## General ##
  * remove MAWS scraper from config.xml
  * support extra RomCollections (sub RomCollections like "100 best sport games, ...")
  * support for audio files
  * add context menu to mark game as completed
  * add context menu to mark game as broken (in db + .broken in filename?)
  * add scripts to migrate 2.0.7 installations to new db layout and config structure

## Datamodel ##
  * store viewstate on RC basis (favorite view per romcollection)
  * build game groups (releases and sequels)
  * divide outline and plot?
  * support 2 or more developers?

## Scraping / Game import ##
  * add new MAME scraper
  * manually enter name of scraped game (rescrape or interactive)
  * support for game logo or game name logo
  * select artwork during import
  * support for default images (if no image was found)
  * divide data and artwork scraper
  * artwork quality
  * support more than 1 screenshot (and other artwork types)
## Launching ##

## UI/Browsing ##
