# Creating your own description parser #
The description file parser can handle simple multiline text files, xml files or html pages. It uses an xml configuration file that defines how to parse the source files. This parserConfig xml file will be read element by element and transferred into parser grammar (using pyparsing for flatfile and html pages or elementtree for xml files). That means you have to take care of the elements order.

This is an example game description text file:
```
Game: Ports Of Call
Platform: Amiga
Region: USA
Media: Disk
Controller: Joystick
Genre: Simulation, Strategy
Release Year: 1987
Developer: Aegis International
Publisher: Aegis International
Players: 4
URL: http://www.mobygames.com/game/amiga/ports-of-call
Description:
Ports of Call gives you the job of a shipowner. First you have to choose your hometown and after that you have to buy your first used ship. Then you have to charter freight and bring it to its destination. With this profit you can buy new ships and so on and on. You also have to repair your ships regularly. If you do not your ships will sink to the oceans.

Ports of Call is a classic German business simulation with some action sequences. In this sequences you must steer your ship into the port or have to rescue some shipwrecked people.

Up to 4 captains can play at one computer.
********************************************************************
Game: Airborne Ranger
Platform: Amiga
Region: 
Media: 
Controller: 
Genre: Action, Simulation
Release Year: 1989
Developer: MicroProse Software, Inc.
Publisher: MicroProse Software, Inc.
Players: ????
URL: http://www.mobygames.com/game/amiga/airborne-ranger
Description:
In this action/simulation game by Microprose the player takes the role of an U.S. Army airborne ranger. These Airborne rangers are dropped behind enemy lines by parachute to perform all kinds of dangerous missions. Gameplay consists of 3 phases:
Reading the mission briefing and outfitting 3 supply pods with machine gun ammo, time bombs, first-aid kits, grenades &amp; LAW rockets depending on this briefing.
Flying over the mission map in a V-22 Osprey plane to drop your 3 supply pods and parachuting out of the plane yourself.
Performing the actual missions and reaching the pick-up point before time runs out. There are 12 different missions which include capturing an enemy officer, blowing up an ammunition depot, photographing an experimental aircraft and liberating P.O.W.'s
Missions take place in either an arctic, desert or temperate setting. Using the mission map the player must decide the route towards the mission objective. This might require them to crawl through trenches, run around minefields or take out enemy soldiers and bunkers. Airborne Ranger was one of the first games with some missions that required a stealthy approach (staying undetected until a certain time, taking out a guard and stealing an enemy uniform etc.).

Airborne Ranger can be played in practice or veteran mode. In practice mode, gameplay is limited to a single mission, while in veteran mode, a series of missions or an entire campaign is played in order to earn medals &amp; promotions. All missions can be played on several difficulty levels.
********************************************************************
```

The parser config for this text file will look like this:

```
<parserConfig>
	<GameGrammar type="multiline">
		<SkippableContent>Game: </SkippableContent>
		<Game restOfLine="true"></Game>		
		<SkippableContent>Platform: </SkippableContent>
		<Platform delimiter="," restOfLine="true"></Platform>
		<SkippableContent>Region: </SkippableContent>
		<Region delimiter="," restOfLine="true"></Region>
		<SkippableContent>Media: </SkippableContent>
		<Media delimiter="," restOfLine="true"></Media>
		<SkippableContent>Controller: </SkippableContent>
		<Controller delimiter="," restOfLine="true"></Controller>
		<SkippableContent>Genre: </SkippableContent>
		<Genre delimiter="," restOfLine="true"></Genre>
		<SkippableContent>Release Year: </SkippableContent>
		<ReleaseYear delimiter="," restOfLine="true"></ReleaseYear>
		<SkippableContent>Developer: </SkippableContent>
		<Developer delimiter="," restOfLine="true"></Developer>
		<SkippableContent>Publisher: </SkippableContent>
		<Publisher restOfLine="true"></Publisher>
		<SkippableContent>Players: </SkippableContent>
		<Players delimiter="," restOfLine="true"></Players>
		<SkippableContent>URL: </SkippableContent>
		<URL delimiter="," restOfLine="true"></URL>
		<SkippableContent restOfLine="true">Description:</SkippableContent>
		<Description skipTo="*"></Description>
		<SkippableContent restOfLine="true"></SkippableContent>		
	</GameGrammar>
</parserConfig>
```

Lets explain the first two lines of the config file:
`<SkippableContent>Game: </SkippableContent>` will search for the exact occurance of "Game: " at the beginning of the text file. If it is not found the parser will raise an exception and stops parsing. If the text is found it will skip this content and executes the next rule: `<Game restOfLine="true"></Game>`. This will take all text from the current position (we are one letter behind "Game: " now) to the end of the line and stores this as a value to the key `Game`. When parsing of the complete file is done RCB can access this value using the given key.

There are not many configuration options at the moment. Actually only `GameGrammar type="multiline`" or `GameGrammar type="xml`" is supported.

## Elements ##
There are only two types of elements in the current version.

### Named Element ###
A named element like `<Game restOfLine="true"></Game>` will return a key value pair where the element name is the key and the parsed content will be the value. All information in your description file that is valuable input to RCB must be declared as a named element in this configuration file.

Supported elements in current version:

Game, crc, Genre, ReleaseYear, Publisher, Description, Reviewer, Region, Media, Controller, Players, Developer, URL, Rating, Votes, Perspective, OriginalTitle, AlternateTitle, TranslatedBy, Version



### Skippable Content ###
As the name says all content that matches the given instruction will be skipped. `SkippableContent` may have an element value. This value must occur exactly at the current position in the description file.


## Attributes ##
### restOfLine ###
If "true" all content from current position to the rest of the line will be matched by this expression

### delimiter ###
If you have delimited values this will specify the used delimiter. Every delimited value will be saved to database as a single entry.

NOTE: Actually only the "," will be recognized as a delimiter.

### skipTo ###
If you have multiline values (like description in the above example) you can specify a token that must occur after the multiline value. This token must be unique enough to not occur in your multiline value. The `*` in the above example may be a bad choice as there is a good chance of a star to occur in a game description.

### optional ###
If set to "true" the parser will raise no error if it can't find the current token.

## Special values ##
### Line Start ###
If you use `LineStart` as an element value the parser will search for the given token at the beginning of a line. The following example will search for a line that starts with a "`*`":
```
<SkippableContent skipTo="LineStart*"></SkippableContent>
```

### Line End ###
If you use `LineEnd` as an element or attribute value the parser will search for the given token at the end of a line. The following example will search for a line that ends with a "`*`":
```
<SkippableContent skipTo="*LineEnd"></SkippableContent>
```

You can use `LineStart` and `LineEnd` together. The following example will search for a line that contains only a "`*`":
```
<SkippableContent skipTo="LineStart*LineEnd"></SkippableContent>
```