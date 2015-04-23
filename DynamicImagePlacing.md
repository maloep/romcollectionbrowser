# Dynamic Image Placing #
RCB does not rely on a defined set of media files. The user may have small collections with only one image per game or others may have complete sets with 6 or more different image types and maybe video files. Some users want to see title screenshots as background, others prefer boxart images. With image placing you have the option to control where RCB will show which type of artwork.

Detailed configuration of every available image control can be done with the `ImagePlacing` elements in config.xml. If you have built your config.xml with the wizard, RCB will have created some default options for you. You can choose which option to use in the [Edit Rom Collection dialog](EditRomCollection.md) (Browse games tab).

# Image Placing elements in config.xml #
You can fully adjust the Image Placing options in config.xml. Just search for the `ImagePlacing` section like shown below. You can add new options or edit the existing ones. New options will automatically be available in the Edit Rom Collection dialog on the Browse games tab.

```
<config>
  ...
  <ImagePlacing>
    <fileTypeFor name="gameinfobig">
      <fileTypeForGameList>boxfront</fileTypeForGameList>
      <fileTypeForGameList>action</fileTypeForGameList>
      <fileTypeForGameListSelected>boxfront</fileTypeForGameListSelected>
      <fileTypeForGameListSelected>action</fileTypeForGameListSelected>
      <fileTypeForMainViewBackground>title</fileTypeForMainViewBackground>
      <fileTypeForMainViewBackground>boxfront</fileTypeForMainViewBackground>
      <fileTypeForMainViewBackground>action</fileTypeForMainViewBackground>
      <fileTypeForMainViewGameInfoBig>action</fileTypeForMainViewGameInfoBig>
      <fileTypeForMainViewGameInfoBig>boxfront</fileTypeForMainViewGameInfoBig>
    </fileTypeFor>
  </ImagePlacing>
  ...
</config>
```

## fileTypeFor... ##
With the fileTypeFor...-elements you can associate each of the available image controls in RCBs UI with a specific media type. You  can configure multiple fileTypeFor...-elements of the same type. They will be used as fallback: if there is no image or video of file type 1, it will try to load an image or video of file type 2. The file types must exactly match the value of `type` attribute that you used in `mediaPath` and `FileType` configuration.

In this example RCB will show your boxfront images as background image in the main window:
```
<fileTypeForMainViewBackground>boxfront</fileTypeForMainViewBackground>
```

If you want to see your title screenshots as background, change it to:
```
<fileTypeForMainViewBackground>title</fileTypeForMainViewBackground>
```

All available image placing options:

Main Window

![http://romcollectionbrowser.googlecode.com/files/screenshot_dip_mv_info2_small.jpg](http://romcollectionbrowser.googlecode.com/files/screenshot_dip_mv_info2_small.jpg)

  1. fileTypeForMainViewGameInfoUpperLeft - not available in Thumbs view
  1. fileTypeForMainViewGameInfoUpperRight - not available in Thumbs view
  1. fileTypeForMainViewGameInfoLowerLeft - not available in Thumbs view
  1. fileTypeForMainViewGameInfoLowerRight - not available in Thumbs view
  1. fileTypeForMainView1
  1. fileTypeForMainView2 - if empty, RCB will show the console name
  1. fileTypeForMainView3
  1. fileTypeForMainViewBackground
<br></li></ul>

<img src='http://romcollectionbrowser.googlecode.com/files/screenshot_dip_mv_info_big.jpg' />

<ol><li>fileTypeForMainViewGameInfoBig - not available in Thumbs view<br>
</li><li>fileTypeForGameList - not available in Info 2 view<br>
</li><li>fileTypeForGameListSelected - not available in Info 2 view<br>
</li><li>fileTypeForMainView1<br>
</li><li>fileTypeForMainView2 - if empty, RCB will show the console name<br>
</li><li>fileTypeForMainView3<br>
</li><li>fileTypeForMainViewBackground<br>
<br>