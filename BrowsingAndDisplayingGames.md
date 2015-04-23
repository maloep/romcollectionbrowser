# Browsing and displaying games #
## dynamic image placing ##
### Rom Collection ###
#### imagePlacing ####
With the `imagePlacing` tag you can select one of the `imagePlacing` options that control which image types are shown in which image controls. When running the config.xml creation wizard RCB will create a set of default options for you. If you are not satisfied with these options or you have other `FileTypes` that are not covered by the defaults, you can change the existing options or create a new one.

### Image Placing ###
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
      <fileTypeForGameInfoViewBackground>title</fileTypeForGameInfoViewBackground>
      <fileTypeForGameInfoViewBackground>boxfront</fileTypeForGameInfoViewBackground>
      <fileTypeForGameInfoViewBackground>action</fileTypeForGameInfoViewBackground>
      <fileTypeForGameInfoViewGamelist>boxfront</fileTypeForGameInfoViewGamelist>
      <fileTypeForGameInfoViewGamelist>action</fileTypeForGameInfoViewGamelist>
      <fileTypeForGameInfoView1>boxfront</fileTypeForGameInfoView1>
      <fileTypeForGameInfoView2>title</fileTypeForGameInfoView2>
      <fileTypeForGameInfoView3>cartridge</fileTypeForGameInfoView3>
      <fileTypeForGameInfoView4>action</fileTypeForGameInfoView4>
    </fileTypeFor>
  </ImagePlacing>
  ...
</config>
```

#### fileTypeFor... ####
With the fileTypeFor...-elements you can associate each of the available image controls in RCBs UI with a specific media type. You  can configure multiple fileTypeFor...-elements of the same type. They will be used as fallback: if there is no image or video of file type 1, it will try to load an image or video of file type 2. The file types must exactly match the value of `type` attribute that you used in `mediaPath` and `FileType` configuration.

In this example RCB will show your boxfront images as background image in the main window:
```
<fileTypeForMainViewBackground>boxfront</fileTypeForMainViewBackground>
```

If you want to see your title screenshots as background, change it to:
```
<fileTypeForMainViewBackground>title</fileTypeForMainViewBackground>
```

There are two controls in the main window (fileTypeForMainViewVideoWindowBig and fileTypeForMainViewVideoWindowSmall) and one control in the game details page (fileTypeForGameInfoViewVideoWindow) that are able to display video. If you use these fileTypeFor...-elements and a video is available for the selected game, the video playback is started automatically.


All available image placing options:

Main Window

![http://romcollectionbrowser.googlecode.com/files/screenshot_dip_mv_info2_small.jpg](http://romcollectionbrowser.googlecode.com/files/screenshot_dip_mv_info2_small.jpg)

  1. fileTypeForMainViewGameInfoUpperLeft - not available in Thumbs view
  1. fileTypeForMainViewGameInfoUpperRight - not available in Thumbs view
  1. fileTypeForMainViewGameInfoLowerLeft - not available in Thumbs view
  1. fileTypeForMainViewGameInfoLowerRight - shared with fileTypeForMainViewVideoWindowSmall, not available in Thumbs view
  1. fileTypeForMainView1
  1. fileTypeForMainView2 - if empty, RCB will show the console name
  1. fileTypeForMainView3
  1. fileTypeForMainViewBackground
<br></li></ul>

<img src='http://romcollectionbrowser.googlecode.com/files/screenshot_dip_mv_info_big.jpg' />

<ol><li>fileTypeForMainViewGameInfoBig - shared with fileTypeForMainViewVideoWindowBig, not available in Thumbs view<br>
</li><li>fileTypeForGameList - not available in Info 2 view<br>
</li><li>fileTypeForGameListSelected - not available in Info 2 view<br>
</li><li>fileTypeForMainView1<br>
</li><li>fileTypeForMainView2 - if empty, RCB will show the console name<br>
</li><li>fileTypeForMainView3<br>
</li><li>fileTypeForMainViewBackground<br>
<br></li></ol>

Game Details

![http://romcollectionbrowser.googlecode.com/files/screenshot_dip_gd.jpg](http://romcollectionbrowser.googlecode.com/files/screenshot_dip_gd.jpg)

  1. fileTypeForGameInfoViewGamelist
  1. fileTypeForGameInfoViewBackground
  1. fileTypeForGameInfoView1
  1. fileTypeForGameInfoView2
  1. fileTypeForGameInfoView3
  1. fileTypeForGameInfoView4 - shared with fileTypeForGameInfoViewVideoWindow
<br>