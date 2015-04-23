

You can launch the context menu with pressing "C" on the keyboard or "Menu" on the remote.

![http://romcollectionbrowser.googlecode.com/files/screen_context_1.1.1.jpg](http://romcollectionbrowser.googlecode.com/files/screen_context_1.1.1.jpg)

# Import Games #
Starts the game import. See section [Import Games](ImportGames.md) for more information.

# Rescrape selected Game #
Starts the game import for the currently selected game. Make sure that addon setting [Always rescan imported games](AddonSettingsImportGames#Always_rescan_imported_games.md) is enabled. See section [Import Games](ImportGames.md) for more information.

# Rescrape Selection #
Starts the game import for all games that are currently shown in the list. Make sure that addon setting [Always rescan imported games](AddonSettingsImportGames#Always_rescan_imported_games.md) is enabled. See section [Import Games](ImportGames.md) for more information.

# Add Rom Collection #
Launches the wizard to add a new Rom Collection. See section [Configuration Wizard](ConfigurationWizard.md) for more information.

# Edit Rom Collection #
Invokes the Edit Rom Collection dialog. See section [Edit Rom Collection](EditRomCollection.md) for more information.

# Edit Offline Scrapers #
Invokes the Edit Offline Scrapers dialog. See section [Edit Offline Scrapers](EditOfflineScrapers.md) for more information.

# Edit Game Command #
This will launch the XBMC keyboard to enter a game specific command. The text that you enter will be saved with the selected game in RCBs database. This text will be used to replace the string %GAMECMD% in "Emulator params" or "Savestate params" before you launch the game. E.g. lots of Amiga games need special parameters for joyports etc. and this is a way to launch one game with mouse and keyboard support and another one with support for two joysticks.

# Add/Remove Game To/From Favorites #
Adds the current selected game to your favorites. If the current game already is a favorite it will be removed from facorites.

# Add/Remove Selection To/From Favorites #
Adds all games of the current filter selection to your favorites. If one or more of the games in the selection already are favorites they will be removed from favorites. All other games remain unchanged.

# Export game database (nfo files) #
This option will export your complete database to nfo files. The nfo files will be created next to your roms or in a separate folder that you can (optionally) specify in Addon settings. You can import these nfo files later with "local nfo" scraper.

# Delete Game #
Deletes the currently selected game. This will only delete the game from RCBs database. The files on your HD keep untouched.

# Delete Rom Collection #
Launches a little dialog to select the Rom Collection to delete and and the removal option. "Delete Rom Collection" has two modes: "Delete games and configuration" or "Delete games only". Both modes will delete all game relevant data from RCBs database. First mode will also delete the Rom Collection entry from RCBs configuration file.

# Clean database #
Checks if you have deleted a rom file outside of RCB and deletes the game entry in database.

# Open Addon settings #
Opens the [Addon Settings](AddonSettings.md).