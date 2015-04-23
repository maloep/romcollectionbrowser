

![http://romcollectionbrowser.googlecode.com/files/screen_editofflinescrapers_1.1.1.jpg](http://romcollectionbrowser.googlecode.com/files/screen_editofflinescrapers_1.1.1.jpg)

With this dialog you can edit offline scrapers. Offline scrapers are used to import local available game descriptions. They always consist of one or more game description file(s) and a parser file. The game description file(s) contain the game info that you want to import (name, release year, publisher, ...), the parser file tells RCB how to parse the description file. After adding new scrapers with this dialog you can select the scraper in the ["Edit Rom Collection" dialog](EditRomCollectionImportGameData.md) or ["Import games" dialog](ImportGames.md).

You will find some pre-built sets of game descriptions and parsers [here](UseOfflineGameDescriptions.md).

# Scraper #
Select the scraper that you want to edit. If there is no scraper available the box will just conatin a "None" entry.

# Use description per game #
There can be one big description file with descriptions for all games or you can have one description file per game.

In the first case (Use description per game = False) RCB will parse the complete file and tries to find the parsed games in your rom collection. You must be sure that the game name in the description file matches exactly the name of your rom file (without disk prefix and extension) or that the crc value of the rom file matches the crc value inside the description file.

In second case (Use description per game = True) the gamename must occur somewhere in the path to the game description and "Game desc file mask" should contain a %GAME%-placeholder. The complete path to the game description (Path game desc + Game desc file mask) could look like this: "/home/user/emu/Amiga/description/%GAME%/description.txt" or this: "/home/user/emu/Amiga/description/%GAME%.txt" where the part starting with %GAME% always should be the Game desc file mask.

# Path game desc #
The path to the game description file. With the select dialog you will only navigate to the folder where the description file can be found. You have to specify the file name with the property "Game desc file mask". (This behaviour will be changed in one of the next releases)

# Game desc file mask #
Usually just the name of the description file. In "Use description per game"-mode the file mask could contain the placeholder %GAME%. This will be replaced by the gamename when searching for description files. This option is ignored when "Use description per game" is set to False.

# Parse instruction #
Path to the file that tells RCB how to parse the description file(s).

# Search game by crc #
In "One description file for all games"-scenario the description file may contain crc values to perform the matching between your rom files and the game descriptions. RCB can compute the crc values of your roms and uses this to search for the corresponding game description in your description file. Set this option to "True" if your description files support crc values (e.g. most game descriptions listed [here](UseOfflineGameDescriptions.md) support crc values).

# Use foldername as crc #
Compare the crc value in the description file with the foldername of the current rom file. May be used in some special cases when you can't rely on rom filenames and computing crc values is not possible, too (e.g. Xbox game files are all named default.xbe and too large to compute a crc value).

# Use filename as crc #
Compare the crc value in the description file with the filename (without extension) of the current rom file.

# Remove scraper #
Removes an existing scraper. You have to choose which scraper you want to remove. RCB will check if the selected scraper is in use in any of your Rom Collections before removing the scraper.

# Add scraper #
Adds a new scraper. You have to choose the name of the new scraper. It is a good idea to use the same name as the name of the Rom Collection where you want to use the new scraper. After that you can edit all scraper properties with the available controls.

# Save Config #
Saves all changes to all scrapers that you made in this dialog. Changes will be saved to the file config.xml in your userdata folder. You will find the scraper section at the end of the file.

# Cancel #
Closes this dialog without any changes.