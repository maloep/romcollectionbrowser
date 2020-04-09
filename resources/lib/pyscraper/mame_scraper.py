# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
import re
import os
import xbmcvfs
import util
from util import __addon__
from util import Logutil as log
from rcbexceptions import *
from file_scraper import FileScraper


class MAME_Scraper(FileScraper):
    """MAME_Scraper parses the MAME history.dat file using a regex, assuming the following format:
         $info=zwackery,
         $<a href="http://www.arcade-history.com/?n=zwackery&page=detail&id=3262&o=2" tit
         le="Edit this entry at Arcade-History.com">Edit this entry at Arcade-History.com
         </a>
         $bio

         Zwackery (c) 1984 Bally Midway.

         Zwackery was a sword-fighting and spell-casting game in which the player control
         s a cartoony wizard Zak Thwacker on a quest to restore an enchanted frog back in
         to the buxom princess she once was
         ...
         $end

    More recent versions of the history.dat file omit the link, have 2 line breaks, and if they are a foreign title
    will have the translated name underneath, e.g.

         $info=aof2,
         $bio

         龍虎の拳2 (c) 1994 SNK Corp.
         (Ryuuko no Ken 2)

         12 selectable characters are available in this martial arts fighting game, each showing progressive...

         - TECHNICAL -

    We don't inherit from the WebScraper since this is a file-based parser

    FIXME TODO Performance considerations when doing this for hundreds of MAME ROMs - might want to open this once
    when the class is initialised and persist access to the file.

    """

    _name = 'MAME'

    # This is only used to persist data between the search and retrieve since the regex should pick up an exact
    # match and there is no point parsing the file twice
    resultdata = []

    def __init__(self):
        pass

    def _get_history_path(self):
        return self.path

    def search(self, gamename, platform=None):
        """ Ignore platform """
        # Newer versions support multi systems, $info=XXX indicates an arcade ROM
        startmarker = "$info=%s," % gamename
        gamedata = False
        data = ""

        historyfile_path = self._get_history_path()

        try:
            fh = xbmcvfs.File(historyfile_path)
            historyfile = fh.read()
            historyfile = util.convertToUnicodeString(historyfile)
            fh.close()
            for line in historyfile.splitlines():
                if line.startswith(startmarker):
                    gamedata = True

                if gamedata:
                    data += line + os.linesep

                if line.startswith("$end"):
                    gamedata = False

        except Exception as e:
            log.error(e)
            raise

        try:
            # Note the regex has to search for either Windows-style line endings (\r\n) or Unix-style (\n)
            # Earlier history.dat files had 3 line breaks, newer versions have 2
            # We also rename manufacturer and Publisher, and Description is all data between the bio heading and the first
            # subheading (e.g. - TECHNICAL - or - CONTRIBUTE -). The romset entry is delimited by the $end.
            # Japanese (or other foreign titles) have the translated name in brackets underneath.
            # Newer versions have an age-based reference (e.g. A 24-year-old SNK Neo-Geo MVS Cart) between the $bio
            # and title line

            pattern = r"\$bio(\r?\n){2}" \
                      "(?P<AgeRef>.*?(\r?\n){2})?" \
                      "(?P<Game>.*?) \(c\) (?P<ReleaseYear>\d{4}) (?P<Publisher>.*?)\.(\r?\n)" \
                      "(\((?P<Translation>.*?)\))?(\r?\n){1,2}" \
                      "(?P<Description>.*?)(\r?\n){2,3}" \
                      "- [A-Z]"

            rdata = re.search(pattern, data, re.DOTALL | re.MULTILINE | re.UNICODE)

            if rdata is None:
                raise ScraperNoSearchResultsFoundException("Unable to find %s in MAME history dat file" % gamename)

        except Exception as e:
            print ("Error searching for game %s using regex: %s" % (gamename, str(e)))
            return []

        self.resultdata = [rdata.groupdict()]
        self.resultdata[0]['id'] = self.resultdata[0]['Game']
        #don't use a search key as we should always have 1 result that perfectly fits
        #search key is used in matcher to compare the rom name with the game name and this will usually not match
        #self.resultdata[0]['SearchKey'] = self.resultdata[0]['Game']

        # HACK - This is only used to retain backwards compatibility with existing scraper, where each key value was a
        # list, even if only one value is in that list
        for k, v in self.resultdata[0].items():
            self.resultdata[0][k] = [v]

        return self.resultdata

    def retrieve(self, gameid, platform):
        # For consistency with the web scrapers, returns a dict containing the game details already found in
        # the search function
        return self.resultdata[0]
