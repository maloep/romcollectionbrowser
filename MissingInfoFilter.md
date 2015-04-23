

![http://romcollectionbrowser.googlecode.com/files/screen_missinginfofilter_1.1.1.jpg](http://romcollectionbrowser.googlecode.com/files/screen_missinginfofilter_1.1.1.jpg)

This one is made for completists. Usually when you scrape your game collection online you will end up with several games that have incomplete information. Some games are missing box art, some screenshots, some games won't have developer information or are lacking something else. Especially missing artwork can be annoying as you may have visible gaps while browsing through your rom collection.

The missing info filter allows you to filter your games by missing information (artwork or game description). These filter settings will be added to all other filters that you have specified in the common filter pane (console, genre, ...). The filter is saved permanently and will be used for every game query. You can specify which items should be used to filter your games and what action should take place when the filter matches any games.

In Confluence skin you can access the missing info filter on the bottom pane next to the "Change View" button.

# Filter mode #
The missing info filter supports 3 modes:
## Ignore filter ##
Simply ignores everything that you setup on this page.

## Hide games with missing items ##
Games with missing items will not be shown while browsing the game list. It acts like these games are not part of your rom collection anymore. This is useful if you want to have a clean look on your rom collection. You can still import every game even with incomplete information. But while browsing your rom collection your views won't be messed up with games that are lacking information.

## Show only games with missing items ##
This is kind of a maintenance mode. It will only show games that are lacking information. This is useful when you want to check the accuracy of your rom collection from time to time and rescrape games with missing information.

# Filter games with missing artwork #
Add all artwork types that should be used to filter your games.

## ONE of these items missing ##
This is used like an OR-statement. In the example above you won't see any games in your game list that have no boxfront OR no screenshot artwork.

## ALL of these items missing ##
This is used like an AND-statement. A game is only matched by this filter if it is lacking all of the listed artwork types.

# Filter games with missing info #
Add all game infos that should be used to filter your games.

## ONE of these items missing ##
This is used like an OR-statement. A game is matched by this filter if it is lacking ONE of the listed game infos.

## ALL of these items missing ##
This is used like an AND-statement. A game is only matched by this filter if it is lacking ALL of the listed game infos.