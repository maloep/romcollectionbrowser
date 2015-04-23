

![http://romcollectionbrowser.googlecode.com/files/screen_addonsettings_import_1.1.1.jpg](http://romcollectionbrowser.googlecode.com/files/screen_addonsettings_import_1.1.1.jpg)

You can access RCBs global settings via the context menu in XBMCs addons list or the context menu inside RCB (press C on the keyboard or menu on the remote to access the context menu).

# Import games on XBMC startup #
The background scraping option is still experimental. Once activated you must launch RCB and it will create an autoexec.py file that is launched at every XBMC startup. This autoexec.py starts the scraping process while you can do everything else in XBMC (but not start RCB). Progress of the current import is only shown in XBMCs home window.

If you want to cancel the current import, just launch RCB and it will ask you to cancel the current import. After this you are able to launch RCB again.

If you want to disable autmatic import on XBMC startup, disable it in Addon settings and launch RCB once. Then it will remove the autoexec.py again.

The progress dialog is designed for Confluence skin. It may look a bit off for other skins. This is a todo for one of the next releases.

# Show import options dialog #
If set to "True" the import options dialog will be shown at every game import. If set to "False" RCB will use the default settings from config.xml and global settings.

# Scraping mode #
  * Automatic: Accurate - Only imports games that can be matched 100%. Only slight changes to the names while finding the correct match (replace sequel numbers, "&" with "and", etc). Will skip a lot of games but should not lead to any mismatches.
  * Automatic: Guess Matches - Tries to find all games with subtitle or fuzzy matching. Will scrape most of your games correctly but will for sure have some mismatches.
  * Interactive: Select Matches - Let the user select the correct game if the game cannot be determined by 100%. Most time consuming option.

# Game matching fuzzy factor #
In scraping mode "Automatic: Guess Matches" RCB will try to guess which game on the scraped site fits best to the currently scraped game by comparing the name of the romfile with the name of the scraped site. The comparison of the two names returns a matching ratio value from 0.0 to 1.0 where 1.0 is a perfect match. You can configure which matching ratio RCB will accept when importing games.

# Create local nfo file while scraping #
Set this option to "True" if you want RCB to create nfo files while scraping. These nfo files contain all game meta information like name, genre, description, release year, etc. They will be saved next to the scanned rom files with a name romfile.nfo. Make sure that the user who runs xbmc has permission to create files in your rom directory.

These nfo files can be edited and reimported into RCBs database. This can be used to add or edit game properties or to save time when rebuilding your database.

# Don't import games without description #
Set this to "True" if you want to skip all games that RCB can't find any description for. RCB will create a file "missingDesc.txt" while scraping. This file contains a list of all skipped games.

# Don't import games without artwork #
Set this to "True" if you want to skip all games that RCB can't find any artwork for. RCB will create a file "missingArtwork.txt" while scraping. This file contains a list of all missing artwork types.

# Rescrape already imported games #
Before scraping game information, RCB checks if the current rom file is already imported to the database. RCB will skip scraping these games unless you set this option to "True".

# Allow overwrite with null values #
When rescraping a game that is already available in your database it may happen that some information is not present on the scraped site anymore (or you are using a different scraper that does not support this type of information). To prevent RCB from overwriting the available information with null values you should disable this setting.

# Use extra nfo folder #
If set to "False", RCB will look for your nfo files next to your rom files. If set to "True", you can select a separate path where RCB should store your nfo files.

# nfo folder path #
Path to your nfo files. Only available if "Use extra nfo folder" is set to "True". You should only specify the base path to your nfo files. RCB will create sub folders per Rom Collection for you.