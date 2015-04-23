


![http://romcollectionbrowser.googlecode.com/files/screen_Config_01_Import_games_wiki.jpg](http://romcollectionbrowser.googlecode.com/files/screen_Config_01_Import_games_wiki.jpg)

To edit your Rom Collections just launch the context menu (pressing "C" on the keyboard or "Menu" on the remote) and select "Edit Rom Collection".

# Rom Collection #
With the Rom Collection selector you can select which Rom Collection you want to edit. All controls in the dialog will be updated with the data of the selected Rom Collection.

# Rom Path #
The path to your rom files. In this dialog you can directly navigate to the folder that contains your roms. RCB also supports scanning sub folders, you should just select the top folder of your rom directory structure.

# Rom File Mask #
The file mask should include wildcards and file extension (`*`.adf for example). You can add more than one file mask separated with commas (`*`.adf, `*`.zip).

# Ignore on scan #
If set to "True" this `RomCollection` will be ignored completely during import. If you have all data for one `RomCollection` in database you can set this to "True" and there won't be any changes to this collection during the next imports.

# Allow update #
If set to "False" RCB won't update your already imported game descriptions. All additional files (e.g. screenshots) will be imported if not already in database.

# Max folder depth #
Limit the number of subfolders that RCB scans while searching for rom files.

# Disk indicator #
This is used to detect multi rom games. RCB should not show every rom file in th UI if they all belong to the same game. Second reason to use this property are emulators that support loading more than one file at once (like uae). RCB can't rely on file numbering because you will also have different releases for one game (Lemmings, Lemmings 2, Lemmings 3).

Example:
If you have some rom files named "`Mygame.adf`", "`Mygame 2_Disk1.adf`" and "`Mygame 2_Disk2.adf`" you should use "`_Disk*.`" as Disk indicator and these files will be detected as two games "`Mygame`" and "`Mygame 2`" where "`Mygame 2`" consists of two rom files. In the UI you will see the "friendly" gamename "`Mygame 2`". If you have your emulatorCmd configured to support multiple rom files you can load both files at once.

You can use regular expressions to support rom names like "MyGame (Disk 1).zip", "MyGame (Disk 2).zip". In this case your disk indicator should look like this: `\(Disk .*\)`

# Use foldername as gamename #
Usually RCB uses the rom filename as gamename (to search by name during online scraping etc.). In some scenarios (e.g. Xbox or DOS games) you will need to use the foldername instead.