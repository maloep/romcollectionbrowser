

Before you can browse or launch any games in RCB you have to import them to RCBs local database. During import RCB will scan your rom folders and data folders and/or scrapes several web sites and imports all game relevant data into its database. Only the path to the roms and artwork files are imported, not the files itself. If you delete or move the files after importing, RCB can't find them anymore.

RCB will ask you to import games after you have run through the configuration wizard. Or you can just launch the context menu (pressing "C" on the keyboard or "Menu" on the remote) and select "Import Games".

On every game import RCB will show an import options dialog that lets you adjust the most important import settings. You can configure in Addon settings if you want to see this dialog or want to use the settings from config.xml.

![http://romcollectionbrowser.googlecode.com/files/screen_importoptions2.jpg](http://romcollectionbrowser.googlecode.com/files/screen_importoptions2.jpg)

# Select Rom Collection #
You can select to import games only for one certain Rom Collection or for all Rom Collections. If you choose to import all Rom Collections the selected settings will be used for all of your Rom Collections.

There is an extra handling for MAME roms. As there is a certain scraper for MAME games (maws.mameworld.info), RCB will always use this scraper if you choose to import all Rom Collections and did select another scraper than "local nfo".

Note for users that use offline scrapers: In combination with offline scrapers (except local nfo) you can only import all Rom Collections if option "Change scrapers for this run" remains unchecked as usually every Rom Collection will need its own scraper.

# Scraping Mode #
  * Automatic: Accurate - Only imports games that can be matched 100%. Only slight changes are made to the names while finding the correct match (replace sequel numbers, "&" with "and", etc). Will skip a lot of games but should not lead to any mismatches.
  * Automatic: Guess Matches - Tries to find all games with subtitle or fuzzy matching. Will scrape most of your games correctly but will for sure have some mismatches.
  * Interactive: Select Matches - Let the user select the correct game if the game cannot be determined by 100%. This is the most time consuming option.

If you want to have a most accurate setup it is a good idea to start in "Automatic: Accurate"-mode to let RCB scrape all games that can be matched automatically. In a second run you should select "Interactive: Select Matches" and select all games that could not be imported in the first run.

# Change scrapers for this run #
If this option is checked RCB will use the scrapers listed below for this one import. Otherwise it will use the scrapers that are already configured in config.xml.

# Scrapers #
The selected scrapers will be executed in the order they are selected in this dialog. The results of the scrapers will be merged together. Merging results is done with "first come, first go"-logic. This means if the first scraper finds a publisher for example, RCB will use the publisher returned by the first scraper. If the first scraper does not find a publisher but it is provided by the second scraper, RCB will use the publisher from the second scraper.

All of these scrapers will also check your local artwork folders for new artwork and import the paths of new files into the database.

## local nfo Scraper ##
One special scraper is the "local nfo" scraper. During a game import, RCB creates a .nfo file for every game with all scraped game information (if you did not disable this feature in Addon settings). These files can be used to rebuild your database in case of an error or if you want to change game properties.

## local artwork Scraper ##
As the name says this scraper will just check your configured artwork folders for new files. It won't do any online searching or scraping and won't change any other game information. This is useful if you updated your artwork folders outside of RCB.

Note: As this scraper does not add any game information (like title etc.) this scraper can not be used to create new collections. It is designed to work as update scraper only. As stated above, all other scrapers check the artwork folders during import, so it is not necessary to use the "local artwork" scraper on initial imports.

# Import #
This will start the import process. If you encounter any errors or miss some game infos after import, check XBMCs logfile. Search for any occurance of "RCB\_ERROR" or "RCB\_WARNING" to see what is missing. RCB will also create three text files ("scrapeResult\_missingArtwork.txt" and "scrapeResult\_missingDesc.txt" and "scrapeResult\_possibleMismatches.txt") with information about missing or inaccurate data. You will find these files in RCBs userdata directory.

If you add new data to one of your rom collections you can use "Import Games" as often as you like. By default RCB will skip your already imported games and just checks for new games or games that could not be imported during previous scans. You can rescrape all games with changing the setting "Always rescan imported games".

Depending on your rom collections size and the number of used scrapers importing games can take a long time.