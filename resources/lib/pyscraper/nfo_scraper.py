# -*- coding: utf-8 -*-

from __future__ import absolute_import
import xml.etree.ElementTree as ET

import xbmcvfs

from file_scraper import FileScraper
from nfowriter import NfoWriter
from util import Logutil as log


class NFO_Scraper(FileScraper):
    """
    NFO_Scraper parses local nfo files using ElementTree

    Example nfo file:
    <game>
      <title>Arkanoid</title>
      <originalTitle />
      <alternateTitle />
      <platform>Amiga</platform>
      <plot>The original Breakout concept involves controlling a bat at the bottom of the screen and using it to catch and direct a ball so as to hit all the bricks which are arranged at the top of the screen. It was unpopular for over a decade, before Taito revived it with some new ideas in this arcade game.

    The game's plot redefines the bat as a Vaus spaceship, the ball as an energy bolt, and the bricks form a mysterious wall stopping the ship from progressing to safety.</plot>
      <publisher>Discovery</publisher>
      <developer>Taito</developer>
      <year>1987</year>
      <genre>Action</genre>
      <detailUrl />
      <maxPlayer>1</maxPlayer>
      <region />
      <media>Floppy</media>
      <perspective>Top-Down</perspective>
      <controller>Joystick</controller>
      <version />
      <rating>3.8</rating>
      <votes></votes>
      <isFavorite>0</isFavorite>
      <launchCount>0</launchCount>
      <thumb local="" type="fanart" />
      <thumb local="E:\Games\Testsets\RCB Testset\Testdata - online scraping\Artwork\Amiga\boxfront\Arkanoid I.jpg" type="boxfront">http://thegamesdb.net/banners/boxart/original/front/9580-1.jpg</thumb>
      <thumb local="" type="cartridge" />
      <thumb local="" type="boxback" />
      <thumb local="" type="screenshot" />
    </game>
    """

    _name = 'nfo'

    #nfo_file is created in nfo_file_exists and will be used in retrieve
    nfo_file = ''

    # Mapping between the dict keys and the XML fields in the nfo file
    _game_mapping = {
        'Game': 'title',
        'OriginalTitle': 'originalTitle',
        'AlternateTitle': 'alternateTitle',
        'ReleaseYear': 'year',
        'Description': 'plot',
        'Publisher': 'publisher',
        'Developer': 'developer',
        'Players': 'maxPlayer',
        'Region': 'region',
        'Media': 'media',
        'Perspective': 'perspective',
        'Controller': 'controller',
        'Version': 'version',
        'Rating': 'rating',
        'Votes': 'votes',
        'IsFavorite': 'isFavorite',
        'LaunchCount': 'launchCount'
    }

    def get_nfo_path(self, gamename, platform, romFile):

        self.nfo_file = NfoWriter().getNfoFilePath(platform, romFile, gamename)

        return self.nfo_file

    def search(self, gamename, platform=None):

        results = []

        if not xbmcvfs.exists(self.nfo_file):
            return results

        #do not add a search key as we don't want to match the result in matcher (nfo should always find the correct game via filename)
        results.append({'id': gamename,
                        'title': gamename})

        return results

    def retrieve(self, gameid, platform):

        result = {}

        if not xbmcvfs.exists(self.nfo_file):
            return result

        fh = xbmcvfs.File(self.nfo_file)
        game = ET.fromstring(fh.read())
        fh.close()

        # Standard fields
        for k, v in self._game_mapping.items():
            # HACK - This is only used to retain backwards compatibility with existing scraper, where each key value was a
            # list, even if only one value is in that list
            try:
                result[k] = [game.find(v).text]
            # FIXME TODO When we remove the hack, this will be the code to use:
            # result[k] = game.find(v).text
            except Exception:
                # Typically this result doesn't have this field
                log.debug("Unable to extract data from key {0}".format(k))

        # Custom fields
        result['Genre'] = self._parse_genres(game)

        return result

    def _parse_genres(self, game):
        # <genre>...</genre><genre>...</genre>
        genres = []

        if game is None:
            return genres

        for genre in game.findall("genre"):
            genres.append(genre.text)

        return genres
