

# Launching savestates #
Some emulators (I tested with zsnes(w) and (Win)uae) support launching savestates from command line. RCB is able to detect the saved files and directly launches into the saved version of your game (try it out, its really cool).

The path to your savestate files and the parameters that you need to launch your saved files can be configured on the [Launch games](EditRomCollectionLaunchGames.md) tab of the "Edit Rom Collection" dialog.

General note on savestates: Usually a statefile is just a complete dump of the emulated machine at the time you save it. When you launch the statefile the game will continue at the exact point that you left it the last time. This is the same like playing the game in one turn without ever reloading it. This means when you save the statefile, the emulator will save everything as is, with all errors that may have occured in the game. When you launch the savestate again these errors will remain and  it may happen that the game becomes unplayable at a certain point. So, if there is an option inside the game to save it, you should use this option from time to time. This will just save some game related properties but reloads the complete game from scratch when you start it (like rebooting a computer).

The following describes how to use savestates with zsnes(w) and (Win)uae. If you know more emulators that support launching savestates from command line please let me know and I will add them here.

## zsnes(w) ##
Zsnes saves its statefiles at the path that you specify in zsnes configuration ("SRAMPath" in `zsnes*.cfg` or Config->Paths->Saves in the UI). While playing the game you can select a save slot in zsnes with "F3" (there are 10 slots available per game) and save to this slot with "F2". The statefiles are named like the romfile with an extension "`.zs*`" (zst, zs1, zs2, ...). You can launch a saved state with the command line option "-zs #" (where # is the number of the slot (0-9)).

In RCB you need the following configuration:

### Savestate path ###
The path that you told zsnes to save your statefiles.

### Savestate file mask ###
```
%ROMNAME%.zs*
```

%ROMNAME% will be replaced with the name of the rom file you want to launch and "`.zs*`" is needed because the extension can vary from "zst" to "zs9".

### Savestate params ###
```
-m -zs %ASKNUM% "%ROM%"
```

%ASKNUM% will popup a selection of numbers from 0-9. This will select the save slot you want to launch.

%ROM% will be replaced with the complete path to the rom file as usual. Note that the order of the params is important. The "%ROM%" parameter must occur at the end of the command line.

## (Win)uae ##
In uae you can select the path and the name of the statefile every time you save the statefile. You can directly launch the file with the option -statefile=pathtofile. Savestate files are saved with the extension .uss.

In RCB you need the following configuration:

### Savestate path ###
The path that you told uae to save your statefiles.

### Savestate file mask ###
```
%GAME%*.uss
```

%GAME% will be replaced with the gamename that you see while browsing your games in RCB. As you specify the statefile name every time you save a statefile, take care that you always choose the correct gamename. With the `*` in saveStatePath (`%GAME%*`) it is possible to find all files that start with the gamename and end with .uss. So it is possible to have more than one statefile per game and RCB lets you select one of them to launch.

### Savestate params ###
```
-statefile="%STATEFILE%"
```
%STATEFILE% will be replaced with the complete path of the selected statefile.