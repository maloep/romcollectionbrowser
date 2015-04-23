

![http://romcollectionbrowser.googlecode.com/files/screen_Config_02_Import_game_data_wiki.jpg](http://romcollectionbrowser.googlecode.com/files/screen_Config_02_Import_game_data_wiki.jpg)

To edit your Rom Collections just launch the context menu (pressing "C" on the keyboard or "Menu" on the remote) and select "Edit Rom Collection".

# Rom Collection #
With the Rom Collection selector you can select which Rom Collection you want to edit. All controls in the dialog will be updated with the data of the selected Rom Collection.

# Scrapers #
The selected scrapers will be executed in the order they are selected in this dialog. The results of the scrapers will be merged together. Merging results is done with "first come, first go"-logic. This means if the first scraper finds a publisher for example, RCB will use the publisher returned by the first scraper. But if the first scraper does not find a publisher but it is provided by the second scraper, RCB will use the publisher from the second one.

The scraper settings of the Rom Collection may be overwritten by the selection in the import options dialog.

## local nfo Scraper ##
One special scraper is the "local nfo" scraper. During a game import, RCB creates a .nfo file for every game with all scraped game information (if you did not disable this in Addon settings). These files can be used to rebuild your database in case of an error or if you want to change game properties.

# Media type #
Media types are logical types of your artwork or video files (e.g. boxfront, screenshot, gameplay, ...). Media types are defined in config.xml as `FileTypes`. If you want to add new `FileTypes` see this [section](http://code.google.com/p/romcollectionbrowser/wiki/ImportGamesAndMedia#FileTypes) for more info.

With the "Media type" selector you can select which media type you want to edit. "Media path" and "Media file mask" will be updated with the values of the selected media type.

## Media path ##
The path to your image or video files of the selected media type. RCB will use this path to search for available artwork or to store artwork while scraping from online sources. In this dialog you can directly navigate to the folder.

## Media file mask ##
The file mask used to search for media files in the specified folder. You can use the following placeholders: %GAME%, %ROMCOLLECTION%, %PUBLISHER%, %DEVELOPER% (will be replaced with the according game property). If you have a Game "Mygame" its rom file may be named "Mygame.zip". All screenshots must be named "Mygame.jpg" (or png, gif, ...).

Note: In online scraping scenario RCB will save the downloaded artwork files as `%GAME%.*`.

## Remove media path ##
Removes an existing media path. You have to choose which type you want to remove.

## Add media path ##
Adds a new media path. You have to choose the type of the new path. After that you can edit path and file mask with the available controls.