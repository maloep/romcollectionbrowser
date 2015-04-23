

![http://romcollectionbrowser.googlecode.com/files/screen_addonsettings_general_1.1.1.jpg](http://romcollectionbrowser.googlecode.com/files/screen_addonsettings_general_1.1.1.jpg)

You can access RCBs global settings via the context menu in XBMCs addons list or the context menu inside RCB (press C on the keyboard or menu on the remote to access the context menu).

# RCB skin #
You can run RCB with different skins if you don't like the look and feel of the default one. Just select the skin you want in Addon settings. See section [Change skins](ChangeSkins.md) for details (e.g. how to enable skin specific fonts).

# Log Level #
Set RCBs log level. Allowed values: ERROR, WARNING, INFO or DEBUG

# Caching Option #
Controls RCBs caching behaviour. Allowed values: CACHEALL, CACHEITEM, CACHEITEMANDNEXT.

CACHEALL: loads and caches all media files at startup. Best for large rom collections on fast PCs with enough RAM. Scrolling down the game list may be a bit slower with this setting because XBMC renders all images that it passes by.

CACHEITEM: loads only the media files shown in the game list when the game list is built. All extra info will be loaded when a game is selected.
Best for slow PCs with little RAM or xbox. Fast list scrolling is possible because XBMC does not render all images. Game list flickers while browsing because every game info has to be loaded when a game is selected.

CACHEITEMANDNEXT: same as CACHEITEM. This will also load the media files and description for the item before and after the selected one. This will reduce flickering while browsing the game list (if not browsing too fast).

# Save Viewstate On Exit #
If set to "True" RCB will save the current view state (selected filter criteria and focused control) and restores it when you launch it the next time. This option will be used when exiting RCB.

# Save Viewstate On Launch Emu #
If set to "True" RCB will save the current view state (selected filter criteria and focused control) and restores it when you launch it the next time. This option will be used when launching an emulator in "solo" mode.