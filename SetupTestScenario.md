

Note: the config.xml file that is shipped with these test scenarios is not compatible with RCB version > 0.8.6! But you can still use the data and create your config file with the wizard. I am working on current test sets with up-to-date files.


To show you how this script will work and how data should (could) be organized I also provide two zip files with testdata. First zip file demonstrates a simple online scraping scenario. It just contains some dummy rom files (empty text files) and an empty artwork folder. You can setup RCB to download descriptions and artwork for all these games.
The second zip file shows how to use RCB with local available data. It includes covers, game screenshots, game description files and sample configuration files for 7 Amiga and 8 SNES games. I also added 3 gameplay videos to show you how videos will look like in RCB. It also includes placeholder files for the roms (empty text files). The test scenarios are not really meant to play the games, they should just show how to configure this script.

There is also a "video tuorial" available that shows how to setup the online scraping scenario with the configuration wizard: [Youtube](http://www.youtube.com/watch?v=_xvGM8eHWB0)

# online scraping #
  1. Install RCB like described in chapter Installation
  1. Download "Testdata 0.7.x - online scraping" (http://romcollectionbrowser.googlecode.com/files/Testdata%200.7.x%20-%20online%20scraping.zip)
  1. Unzip it somewhere
  1. You can create a configuration file with the configuration wizard at startup. If you want to use the example config files that are shipped with the test scenario, read on:
  1. Go to the new Testdata folder
  1. Edit "config\_Windows.xml" or "config\_Linux.xml": Replace every occurance of "PathToTestData" with the absolute path to your Testdata folder (e.g. "/home/user/Testdata 0.7.x - online scraping" or "D:\Downloads\RCB\Testdata 0.7.x - online scraping")
  1. Rename "config\_Windows.xml" or "config\_Linux.xml" to "config.xml"
  1. Copy "config.xml" to your userdata folder ("script\_data/script.games.rom.collection.browser" (Camelot) or "addon\_data/script.games.rom.collection.browser" (Dharma))
  1. Start xbmc and launch RCB
  1. RCB will notice that there is no database and asks you if you would like to import games. Click "Yes".
  1. RCB will start to download all available information and imports it to your database. Downloaded artwork ist stored in the folder "Artwork" in your testdata folder.

Now you should be able to browse the games by filter criteria and watch all information and artwork.

If you want to launch roms with the test scenario you have to take these additional steps:
  1. Go to your Testdata folder and replace the placeholder rom files with real ones (e.g. Testdata 0.7.x - online scraping/Collection V1/roms/).
  1. Edit the value of property "emulatorCmd" and "emulatorParams". This command will be invoked when you launch a rom file. %ROM% will be replaced with the name of the rom file to be launched. If you have multiple rom files for one game %I% will be replaced with the (zero-based) index of the current file.


# local data #
  1. Install RCB like described in chapter Installation
  1. Download "Testdata 0.7.x - local data" (http://romcollectionbrowser.googlecode.com/files/Testdata%200.7.x%20-%20local%20data.zip)
  1. Unzip it somewhere
  1. You can create a configuration file with the configuration wizard at startup. If you want to use the example config files that are shipped with the test scenario, read on:
  1. Go to the new Testdata folder
  1. Edit "config\_Windows.xml" or "config\_Linux.xml": Replace every occurance of "PathToTestData" with the absolute path to your Testdata folder (e.g. "/home/user/Testdata 0.7.x - local data" or "D:\Downloads\RCB\Testdata 0.7.x - local data")
  1. Rename "config\_Windows.xml" or "config\_Linux.xml" to "config.xml"
  1. Copy "config.xml" to your userdata folder ("script\_data/script.games.rom.collection.browser" (Camelot) or "addon\_data/script.games.rom.collection.browser" (Dharma))
  1. Start xbmc and launch RCB
  1. RCB will notice that there is no database and asks you if you would like to import games. Click "Yes".
  1. RCB will import all available data to its database.

Now you should be able to browse the games by filter criteria and watch all information and artwork.

If you want to launch roms with the test scenario you have to take these additional steps:
  1. Go to your Testdata folder and replace the placeholder rom files with real ones (e.g. Testdata 0.7.x - local data/Collection V1/roms/).
  1. Edit the value of property "emulatorCmd" and "emulatorParams". This command will be invoked when you launch a rom file. %ROM% will be replaced with the name of the rom file to be launched. If you have multiple rom files for one game %I% will be replaced with the (zero-based) index of the current file.