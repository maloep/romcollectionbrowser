To edit your Rom Collections just launch the context menu (pressing "C" on the keyboard or "Menu" on the remote) and select "Edit Rom Collection". You can edit all your Rom Collections in this dialog and changes to all Rom Collections will be saved if you select "Save changes".

All Rom Collection specific configuration is stored in the file "config.xml". You will find this file in your userdata folder in "addon\_data/script.games.rom.collection.browser".

See sub sections for more details
  * [Import games](EditRomCollectionImportGames.md)
  * [Import game data](EditRomCollectionImportGameData.md)
  * [Browse games](EditRomCollectionBrowseGames.md)
  * [Launch games](EditRomCollectionLaunchGames.md)

# Save Config #
Saves all changes to all Rom Collections that you made in this dialog.

When saving your configuration RCB will delete and recreate the Rom Collection configuration section in config.xml. Because of this it can happen that the ordering of Rom Collections changes after you have edited the config via this dialog.

Note: With this dialog RCB only supports 1 Rom path (with several extensions) per Rom Collection! If you have edited your config manually and added different paths to your roms per Rom Collection, all pathes besides the first one will be lost.

# Cancel #
Closes this dialog without any changes.