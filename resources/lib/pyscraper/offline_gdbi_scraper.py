# -*- coding: utf-8 -*-

from __future__ import absolute_import
import re
import xml.etree.ElementTree as ET
import xbmcvfs
from file_scraper import FileScraper
from gamename_utils import GameNameUtil
import util
from util import Logutil as log


class Offline_GDBI_Scraper(FileScraper):
    """
    Offline_GDBI_Scraper local xml files provided by billyc999:
    https://github.com/billyc999/Game-database-info/tree/master/xml%20files

    Example format:
    <?xml version="1.0"?>
    <menu>
      <header>
        <listname>Atari 2600</listname>
        <lastlistupdate></lastlistupdate>
        <listversion>test</listversion>
        <exporterversion></exporterversion>
      </header>
      <game name="3-D Tic-Tac-Toe (USA)">
        <description>3-D Tic-Tac-Toe</description>
        <year>1980</year>
        <rating>ESRB - E (Everyone)</rating>
        <manufacturer>Atari, Inc.</manufacturer>
        <dev>Atari, Inc.</dev>
        <genre>Puzzle</genre>
        <score>2.4</score>
        <player>1-2 Players</player>
        <story>3-D Tic-Tac-Toe is, as the name implies, a 3D version of Tic-Tac-Toe. </story>
        <enabled>Yes</enabled>
        <crc></crc>
        <cloneof></cloneof>
      </game>
      ...
    </menu>
    """

    _name = 'Game-database-info'

    # Mapping between the dict keys and the XML fields
    _game_mapping = {
        'Game': 'description',
        'ReleaseYear': 'year',
        'Description': 'story',
        'Publisher': 'manufacturer',
        'Developer': 'dev',
        'Players': 'player',
        'Rating': 'score',
        'Votes': 'votes'
    }

    # list of platforms that use MAME style naming scheme (these platforms need a different search pattern)
    _MAME_style_platforms = [
        'MAME',
        'Sega Model 2',
        'Sega Model 3'
    ]

    def _get_xml_path(self):
        return self.path

    def search(self, gamename, platform=None):
        #use description to search for the game name as the name attribute also contains the region
        pattern = "\<description\>(.*%s.*)\</description\>" % GameNameUtil().prepare_gamename_for_searchrequest(gamename)
        if platform in self._MAME_style_platforms:
            pattern = 'name="(.*%s.*)"' % GameNameUtil().prepare_gamename_for_searchrequest(gamename)

        results = []

        try:
            fh = xbmcvfs.File(self._get_xml_path())
            text = fh.read()
            text = util.html_unescape(text)
            fh.close()
            for line in text.splitlines():
                #HACK: Apostrophes are removed in prepare_gamename_for_searchrequest. So we also have to do it here.
                result = re.search(pattern, line.replace("'", ""))
                if result:
                    gamename = result.groups()[0]
                    results.append({'id': gamename,
                                    'title': gamename,
                                    'SearchKey': [gamename]})
        except Exception as e:
            log.error(e)
            raise

        return results

    def retrieve(self, gameid, platform=None):

        result = {}

        fh = xbmcvfs.File(self._get_xml_path())
        tree = ET.fromstring(fh.read())
        fh.close()

        #gameid is the exact name of the game used in <description> or @name (for platforms with MAME style names)
        searchpattern = './/game[description="%s"]'%gameid
        if platform in self._MAME_style_platforms:
            searchpattern = './/game[@name="%s"]' % gameid

        game = tree.find(searchpattern)

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
        # <genre>Genre 1 - Genre 2</genre>
        genres = []

        if game is None:
            return genres

        genre = game.find("genre")
        if genre is None:
            return genres

        genres = genre.text.split(' - ')

        return genres
