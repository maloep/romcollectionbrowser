# Enable fullscreen video browser #
RCB creates a video playlist with every game video in your current filter selection and starts playback in fullscreen if you hit the "Play/Pause" button on your remote or "Space" on the keyboard. You can zap through the videos of this playlist and use the builtin Info Overlay with title, thumbnail and duration. RCB uses standard XBMC playlist and fullscreen player so there are not more options to interact with the playback from RCB.

If you have created your config.xml with the wizard you will already have the required tags in your config file. To add fullscreen support manually you have to add this line to your [ImagePlacing](DynamicImagePlacing.md)-configuration:
```
<fileTypeForMainViewFullscreenVideo>gameplay</fileTypeForMainViewFullscreenVideo>
```

## Enable zapping in fullscreen browser ##
You may have to make some changes to your keymap.xml to enable the zapping feature. These changes make sure that you have access to "SkipNext" and "SkipPrevious" in FullscreenVideo and FullscreenInfo.

See [XBMC wiki page](http://wiki.xbmc.org/index.php?title=Keymap.xml) for more info about keymap.xml.

Windows/Linux keyboard.xml:
```
<FullscreenVideo>
    <keyboard>
      ...
      <period>SkipNext</period>
      <comma>SkipPrevious</comma>
      ...
    </keyboard>
</FullscreenVideo>
<FullscreenInfo>
    <keyboard>
      ...
      <period>SkipNext</period>
      <comma>SkipPrevious</comma>
      ...
    </keyboard>
</FullscreenInfo>
```

Xbox keymap.xml
```
<FullscreenVideo>
    ...
    <gamepad>
      ...
      <dpadup>SkipNext</dpadup>
      <dpaddown>SkipPrevious</dpaddown>
      ...
    </gamepad>
</FullscreenVideo>
```