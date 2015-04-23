

Note: This information is valid with version 1.1.3 (Eden) or 2.0.1 (Frodo) of the script.

# Skinning RCB #
As a script RCB has full access to XBMCs skinning engine. Every view and dialog can be designed as we want it to look like. But this also means that everything HAS to be designed. Nothing will work out of the box with the views that are already shipped with the users default skin (like it is for a plugin).

Most things in RCBs skin files should be self explanating to a skinner. The current skin files are made for a 720p resolution with Confluence in mind. If you have improvements to my Confluence skin or want to migrate RCB to other skins please feel free to contribute.

Not every dialog in RCB must be ported to other skins. If XBMC does not find one of the skin xml files for the current skin it will just use the file from RCBs default skin. So I think in most cases it will be enough to have the main window and maybe the additional game info window prepared for other skins. All of the little dialogs from RCB can use the default look and feel.

Completed skins can be shipped with RCB or the skin itself. If you to let me ship your RCB skin files with RCB, this will allow users of other skins to use your skin files and vice versa. I could also take "ownership" of your skin files and maintain them to keep them compatible with further RCB changes. You can do all this yourself if you like, of course.


## XML files used with RCB ##
The following skin xml files are used with RCB:

```
script-Rom_Collection_Browser-main.xml (RCBs main window)
script-RCB-gameinfo.xml (Game info view)
script-RCB-contextmenu.xml (Context menu)
script-RCB-importoptions.xml (Import options dialog)
script-RCB-editromcollection.xml (Edit Rom Collection dialog)
script-RCB-editscraper.xml (Edit Scraper dialog)
script-RCB-removeRC.xml (Remove Rom Collection dialog)
script-RCB-missinginfo.xml (Missing info dialog)
```

## Accessing RCBs images and videos ##
One thing that could be special in this script is the "dynamic image placing". RCB does not rely on a defined set of media files. The user may have small collections with only one image per game or others may have complete sets with 6 or more images and maybe video files per game. I want the user to decide where to show which type of image. The skinner should decide how it is presented. I am afraid this approach is not really XBMCish...

Thats why you find several code lines like this in the skin xml:
```
<texture>$INFO[ListItem.Property(background)]</texture>
or
<texture>$INFO[ListItem.Property(gameinfobig)]</texture>
```

The user decides per config what image he wants to use as background image. The skin can display this file with the above code.

Here is a list of all available media controls (valid for main window and game info window):

Images
```
background
gamelist
gamelistselected
gameinfobig
gameinfoupperleft
gameinfoupperright
gameinfolowerleft
gameinfolowerright
gameinfoupper
gameinfolower
gameinfoleft
gameinforight
extraImage1
extraImage2
extraImage3
```

As you see there are gameinfobig and gameinfo(upper)(lower)(left)(right). The idea behind this is that the user can decide if he wants to see one big image in the info pane or 2-4 small images. If you don't like the idea you can just use the gameinfobig tag to display one image.

Videos
```
videowindowbig
videowindowsmall
```

Here you can see how this is done in the current skin: [dynamic image placing](BrowsingAndDisplayingGames#dynamic_image_placing.md) (see the screenshots at the end of the page).

## Accessing RCBs text properties ##
It should also be possible to access all text properties in the skin.

The title of a game is available as ListItem.Label:
```
<label>$INFO[ListItem.Label]</label>
```

All other properties can be accessed like this:
```
<label>$INFO[ListItem.Property(console)]</label>
```

All available tags:
```
romcollection
console
year
plot
publisher
developer
reviewer
genre
maxplayers
rating
votes
url
region
media
perspective
controllertype
isfavorite
playcount
originaltitle
alternatetitle
translatedby
version
```

## Special control ids ##
Some control ids are referenced inside the python code so you should not change them unless you know what you are doing.

### Game lists ###
Lists always have ids 50-59 in XBMC. These lists are available as "view" in the UI. One id is reserved for the game info dialog.

50-58:	views in the main window

59:		game info dialog


### Main Window ###
Some controls that are available in all views should not be changed also.

#### Filter controls ####
```
Console:	500
Genre:		600
Year:		700
Publisher:	800
A-Z:		900
Favorites:	1000
Search:		1100
```


#### Scrollbars ####
For some reason I had trouble with handling scrollbars along with textboxes because they are sometimes present and sometimes not (depending on the length of text). If you use scrollbars in your view make sure they have ids 2200 or 2201. If you need more scrollbars just have a look at the beginning of the file gui.py. There is a list with scrollbar ids (CONROL\_SCROLLBARS = (2200, 2201,)). You can add your id here and tell me that I should add it to the next RCB version.

#### Buttons ####
```
Change View:		2
Missing info filter:	4001
```

#### Labels ####
```
Message label:	4000
```


### Context Menu ###
#### Buttons ####
```
Close Context Menu:				5101
Import Games:					5110
Rescrape Game:					5121
Rescrape Selection:				5122
Add Rom Collection:				5111
Edit Rom Collection:				5112
Edit Scrapers:					5117
Edit Game Command:				5113
(Un)mark game as favorite:			5118
(Un)mark selection as favorite:			5119
Export nfo files:				5120
Delete Game:					5114
Delete Rom Collection:				5115
Clean database:					5116
Open Addon Settings:				5223
```

### Import options dialog ###
#### Buttons ####
```
Close Dialog:			5101
Ok:				5300
Cancel:				5310
Rom Collection Up:		5211
Rom Collection Down:		5212
Scrape Mode Up:			5222
Overwrite settings:		5330
```

#### Lists ####
```
Rom Collections:		5210
Scraping mode:			5220
Fuzzy Factor:			5260
Scraper 1:			5270
Scraper 2:			5280
Scraper 3:			5290
```

### Edit Rom Collection dialog ###
#### Buttons ####
```
Close Dialog:			5101
Save:				6000
Cancel:				6010
Emu Cmd:			5220
Emu Params:			5230
Use emu solo:			5440
Dont extract zip:		5450
Savestate path:			5460
Savestate mask:			5470
Savestate params:		5480
Pre-Launch cmd:			5510
Post-Launch cmd:		5520
Rom Path:			5240
File Mask:			5250
Media Path:			5270
Media File Mask:		5280
Remove Media Path:		5490
Add Media Path:			5500
Ignore on scan:			5330
Allow update:			5400
Max folder depth:		5410
Disk indicator:			5420
Use folder as gamename:		5430
Rom Collection Up:		5211
Rom Collection Down:		5212
Media Type Up:			5261
Media Type Down:		5262
Autoplay video (main)		5350
Autoplay video (info)		5360
```

#### Lists ####
```
Rom Collections:		5210
Media Types:			5260
Scraper 1:			5290
Scraper 2:			5300
Scraper 3:			5310
Image Placing Main:		5320
Image Placing Info:		5340
```

### Edit Scraper dialog ###
#### Buttons ####
```
Close Dialog:			5101
Save:				6000
Cancel:				6010
Scraper Up:			5602
Scraper Down:			5601
Game desc path:			5520
Game desc mask:			5530
Parse instruction:		5540
Desc per game:			5550
Search by crc:			5560
Use folder as crc:		5580
Use file as crc:		5590
Remove scraper:			5610
Add scraper:			5620
```

#### Lists ####
```
Scrapers:			5600
```

### Remove Rom Collection dialog ###
#### Buttons ####
```
Close Dialog:			5101
Ok:				6000
Cancel:				6010
Rom Collection Up:		5411
Rom Collection Down:		5412
Delete Option Up:		5491
Delete Option Down:		5492
```

#### Lists ####
```
Rom Collections:		5410
Delete Options:			5490
```

### Missing info filter dialog ###
#### Buttons ####
```
Close Dialog:			5101
Ok:				6000
Cancel:				6010
Add Artwork (Or)		5230
Remove Artwork (Or)		5240
Add Artwork (And)		5260
Remove Artwork (And)		5270
Add Info (Or)			5290
Remove Info (Or)		5300
Add Info (And)			5320
Remove Info (And)		5330
```

#### Lists ####
```
Filter Modes:			5200
```

#### Labels ####
```
Artwork Or-Group:		5220
Artwork And-Group:		5250
Info Or-Group:			5280
Info And-Group:			5310
```

# Implementing Game widgets on home screen #
RCB also supports being invoked to gather game data for home screen widgets. Atm only the most played roms are available. Other statistics are planned for future releases.

## Gathering data ##
To get a list of the most played roms you should add a line like this in a startup routine of your skin:
```
RunScript(script.games.rom.collection.browser,limit=10)
```

## Accessing data ##
Later on you can access the properties with a command like this:
```
$INFO[Window(Home).Property(MostPlayedROM.1.Title)]
```

This is a list of all available properties:
```
MostPlayedROM.1.Id
MostPlayedROM.1.Console
MostPlayedROM.1.Title
MostPlayedROM.1.Thumb
MostPlayedROM.1.Plot
MostPlayedROM.1.Year
MostPlayedROM.1.Publisher
MostPlayedROM.1.Developer
MostPlayedROM.1.Genre
MostPlayedROM.1.Maxplayers
MostPlayedROM.1.Region
MostPlayedROM.1.Media
MostPlayedROM.1.Perspective
MostPlayedROM.1.Controllertype
MostPlayedROM.1.Playcount
MostPlayedROM.1.Rating
MostPlayedROM.1.Votes
MostPlayedROM.1.Url
MostPlayedROM.1.Originaltitle
MostPlayedROM.1.Alternatetitle
MostPlayedROM.1.LaunchCommand
MostPlayedROM.1.Fanart
MostPlayedROM.2.Id
MostPlayedROM.2.Console
...
```

## Launching games ##
Launching games directly from home screen is done via RCB again. This helps to support more advanced features like solo mode, zip extraction, etc.

You can launch a game via RCB with a command like this:
```
RunScript(script.games.rom.collection.browser,launchid=1234)
```