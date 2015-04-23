

![https://romcollectionbrowser.googlecode.com/svn/wiki/screenshots/screen_addonsettings_launch_2.0.12.jpg](https://romcollectionbrowser.googlecode.com/svn/wiki/screenshots/screen_addonsettings_launch_2.0.12.jpg)

You can access RCBs global settings via the context menu in addons / scripts list in XBMC (press C on the keyboard).

# Use VB script in solo mode (Windows only) #
This will use vb scripts instead of batch files to stop and restart XBMC. This can help to get around the "CApplication:: create() failed" error message when restarting XBMC.

# Solo mode startup delay #
Adds a short delay before RCB is started on first XBMC launch after solo mode. Especially when you are using the RCB widget (currently supported by Aeon Nox and Ace) it might be useful to wait some time before starting RCB when you return to XBMC.

# Escape Emulator Cmd #
This will escape the rom file names passed to the emulatorCmd. Try to change this if you are running into problems with launching games.

# Pre-Launch delay #
Adds a short delay before the game is launched. Useful when you notice focus issues when launching games.

# Post-Launch delay #
Adds a short delay when the game is closed and focus should go back to XBMC. Useful when you notice focus issues when launching games.

# Suspend Audio #
With this option enabled RCB will suspend XBMC audio before launching the emulator and resumes it when you quit the emulator. This option may be useful when you face audio issues while playing games.

# Minimize XBMC #
With this option enabled RCB will minimze XBMC before launching the emulator and restores it when you quit the emulator. This option may be useful when you are experiencing focus issues or similar while launching emulators.

# Path to emu\_autoconfig.xml (Android only) #
With this option you can set the path to your emu\_autoconfig file that is used to autoconfigure emulators on Android devices.