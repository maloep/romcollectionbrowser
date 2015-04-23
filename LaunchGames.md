

# Launch games #
If you select a game in RCB it will try to launch the game with the configured emulator or the standalone game itself. In case of emulator rom files you have to setup and configure the emulator first. Find out how to launch the emulator per command line and try out if this works without XBMC and RCB. In RCB you can configure emulator settings in [Edit Rom Collection dialog](EditRomCollectionLaunchGames.md).

# Launch games in solo mode #
Solo mode means that RCB tries to quit XBMC before it launches the emulator. This is useful on small machines where running XBMC and the emulator at the same time may cause performance issues. After you quit the emulator XBMC will be restarted and automatically returns to RCB. You can turn this feature on/off in [Edit Rom Collection dialog](EditRomCollectionLaunchGames.md).

This mechanism invokes a batch (Windows) or bash (Linux) file. When you run a game in solo mode for the first time the batch (or bash) file will be copied to RCBs userdata folder (userdata/addon\_data/script.games.rom.collection.browser). Linux only: make sure the file applaunch.sh is executable. If you have problems with launching the emulator or returning to XBMC please check the commands in the file applaunch.bat (Windows) or applaunch.sh (Linux). You must be able to execute the command that is used to launch XBMC on a command line.

Returning to RCB is done with a service addon. There is an additional addon called "Rom Collection Browser Service" that you have to install to use this functionality. You will find it in the Service category of XBMCs addon browser.

# Launch standalone games #
Standalone games could be launched directly as you don't need an emulator to play your games. A bit tricky is the part of importing your games to RCBs database as you won't have one or more directories with all your games with a distinct file mask. Easiest way to solve this is to create shortcuts to your games and store these shortcuts all in the same folder. To import the games point RCB to your shortcut folder and use `*`.lnk as file mask. To launch the games just use "%ROM%" as emulator and leave the rom params blank.

This is the whole process if you start from scratch:
  * create a folder with shortcuts to your standalone games (e.g. lnk-files)
  * in RCB start the "Add Rom Collection" wizard
  * use Linux, Macintosh or Windows as platform (important for RCB to launch the game correctly)
  * select the path to your shortcuts, the file mask (e.g. `*`.lnk) and the folder to store the artwork
  * RCB will automatically use "%ROM%" as emu cmd and leaves the emu params blank
