

# Analyzing and reporting problems #
## How to report problems ##
If you encounter any problems and you want to report it in the forum thread or on the issues page, PLEASE ALWAYS add a log file. Unless you really know that you can describe the whole problem without a log file you should always attach one. To attach a log file please do the following things:
  * Install the addon "XBMC Log Uploader" (you will find it in Programs category)
  * Restart XBMC (this will clean the log file and makes it more easy to read).
  * Leave XBMC and RCB in normal log mode. In 99% of the time this will be enough and the debug mode will produce too much information that makes the log unreadable.
  * Reproduce your problem
  * Launch addon "XBMC Log Uploader"
  * On first launch it will ask you to enter your email-address. It will send you the URL of the uploaded log to this address. If you don't want to add your mail address you can also check latest logs and find out the URL of your log [here](http://xbmclogs.com/list.php).
  * Just paste the URL to your log file in RCBs thread or the issues page along with your problem.

## Where do I find the log file ##
XBMC writes a file "xbmc.log" that contains a lot of information what happens during runtime in both: XBMC and RCB. See the [XBMC wiki](http://wiki.xbmc.org/index.php?title=Log_file) for more information and the location where you find the file on your system.

# Known issues or common problems #
## General ##
### The program doesn't load on "No module named pysqlite2" ###
Some distributions don't ship with prebuild pysqlite libraries. You have to get them on your own and copy them to your xbmc lib folder (e.g. /usr/local/lib/xbmc/addons/script.module.pysqlite/lib/pysqlite2). I made an extra package with these libraries if you don't want to build them yourself: http://romcollectionbrowser.googlecode.com/files/platform_libraries.zip.

### XBMC freezes when trying to start RCB ###
This may happen if you accidently try to launch RCB twice. Unfortunately I did not find a way to code around this issue until now. So if you run into this issue make sure that you wait 1-2 seconds to see if RCB will start before you try it a second time.

### I only see my DVD drive in the config wizard ###
Usually this happens if there is still a disc in the drive. Remove all discs and unmount any virtual drives and try again.

It may also happen that you have to add your drives via XBMC File manager. It depends on the skin where to find the File manager. In Confluence you will find it as a sub menu of System on the Home screen (move to the right when System is highlighted).

### I only see location XY (video sources etc.) in the config wizard ###
It may also happen that you have to add your drives via XBMC File manager. It depends on the skin where to find the File manager. In Confluence you will find it as a sub menu of System on the Home screen (move to the right when System is highlighted).

## Import Games ##
### RCB does not import any games ###
Mostly this issue is related to configuration errors. Most common mistake is that you forgot to add a proper file mask to your Rom Collection configuration. You need to specifiy a file mask like "`*.zip`" or "`*.smc`" to let RCB find your files. You can configure the file mask on the  [Import games tab](EditRomCollectionImportGames.md) in Edit Rom Collection dialog.

In current releases it can also happen that RCB won't find any games on smb shares and when the path to your roms contains any non-ascii characters.

### RCB can't access my SMB shares ###
With latest RCB versions (1.0.8 and above) you should be able to add smb paths without any issues.

In case you still have problems with smb paths the easiest way to add roms from smb shares will be to use network drives on Windows or links on Linux.

### I can't import MAME roms using MAWS scraper ###
MAWS site is down since some weeks and as it seems it will stay down for some more weeks or even forever. In the meantime you can use [this guide](http://code.google.com/p/romcollectionbrowser/wiki/HowToAddMAMEOffline) to add your MAME roms to RCB with offline game descriptions.

Check http://www.mameworld.info/ to monitor the progress of MAWS coming back or not.

## Launch Games ##
### Launching games does not work on system X with emulator Y ###
Go to your xbmc.log and search for this string: "RCB\_INFO: cmd:" (without ""). This line will show the complete command that RCB uses to launch your emulator. Copy and paste this line (only the part after "cmd:") to a command line window and try to launch your emulator. Usually there are errors in your command line or your emulator is not yet configured correctly. It will not work inside RCB if it does not work from command line.

### Launching games does not work on Raspberry Pi and Android ###
This is a known issue and is being worked on. No idea if I (or somebody else) will be able to solve it but I will try. If you have any useful information or any ideas how to get around it please let me know.

### Error launching .7z file ###
When launching .7z files RCB just shows a message box with this error message: "Error launching .7z file. Please check XBMC.log for details". This error should only occure if you have installed RCB via the repo browser. Launching .7z files requires certain libraries that are not part of XBMCs python environment. You can download RCBs latest version from the projects home page, this already includes all required libraries.

If RCB ships the wrong libraries you can always get the latest release [url=https://pypi.python.org/pypi/pylzma]here[/url].

### In solo mode I get this error: CApplication:: create() failed - Check log file and that it is writeable ###
In latest RCB releases there is a new option in Addon settings called "Use VB script in solo mode". This option should finally solve this issue.