
Change the skin in Addon settings:

![http://romcollectionbrowser.googlecode.com/files/screen_addonsettings_general_1.1.1.jpg](http://romcollectionbrowser.googlecode.com/files/screen_addonsettings_general_1.1.1.jpg)

# Available RCB skins #
## Skins available via RCB ##
Atm these skins are available for RCB:
  * Confluence
  * Night (thanks to mcborzu)
  * Simplicity (thanks to igotdvds)

These skins are shipped with RCB and can be used with any other XBMC skin. See chapter "Change skin" for more details. If you are using an XBMC skin that already ships RCB skin files (see next chapter "Skins available via XBMC skins") you won't be able to change the RCB skin by default (why should you?). This is because XBMC will always launch the skin files that it finds next to the skin, not the files that are shipped with the script. Anyway, if you want to use another RCB skin than the one that is shipped with your XBMC skin you have to remove or rename the RCB specific files in the XBMC skin directory. Go to XBMCs addon directory and search for the directory of the skin that you are using (XBMC/addons/skin.yourskin). Go to the 720p directory of your skin and remove or rename alle files that start with "script-RCB..." and the file "script-Rom\_Collection\_Browser-main.xml".

## Skins available with XBMC skins ##
Atm these XBMC skins ship RCB specific skin files:
  * Aeon MQ3 (thanks to MarcosQui)
  * Aeon MQ4 (thanks to MarcosQui)
  * Aeon Nox (thanks to Phil65 and Big\_Noid)

# Change skin #
In [Addon settings](AddonSettingsGeneral.md) you can choose to run RCB with any of the available RCB skins regardless what skin you are using as default skin in XBMC. To use one of the built-in skins you don't have to do anything else on your side than just select the skin in RCB settings. But by default you won't see the skin specific fonts in RCB. XBMC will use the fonts of your default skin if it can't find the specific fonts. If you want to use the skin specific fonts just check the section below.

## Optional steps to enable skin specific fonts ##
To get the skin specific fonts working in different default skins you have to do the following:
  * go to "RCB install dir\resources\skins\fonts" and copy the `*`.ttf files to your default skins fonts dir
  * copy the content of the file "RCB install dir\resources\skins\Font.xml" to the "720p\Font.xml" file of your default skin (details are explained in the file itself)
  * restart XBMC

Unfortunately, you have to redo these steps every time you update your default skin (if you update it via XBMC addon manager).

Where to find the default skin files:

Confluence: "XBMC install dir/addons/skin.confluence"

All other: "XBMC userdata/addons/skin.xxx"