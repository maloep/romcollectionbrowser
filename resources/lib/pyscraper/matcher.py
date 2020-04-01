# coding=utf-8
from __future__ import print_function
from __future__ import absolute_import
import sys
print ("sys version: {0}".format(sys.version_info))
if (sys.version_info > (3, 0)):
    from html.parser import HTMLParser
else:
    from HTMLParser import HTMLParser

import xbmcgui

import util
from util import __addon__
from util import Logutil as log
from gamename_utils import GameNameUtil


class Matcher(object):
    """This object performs the comparison of a game name against the result set
    """

    """ Initial defaults """
    update_option = 0  # Automatic: Accurate

    def __init__(self):
        self.update_option = self.getScrapingMode()

    def getScrapingMode(self):
        mode = 0
        scrape_options = {util.SCRAPING_OPTION_AUTO_ACCURATE_TXT: 0,
                          util.SCRAPING_OPTION_INTERACTIVE_TXT: 1}
        try:
            mode = scrape_options[__addon__.getSetting(util.SETTING_RCB_SCRAPINGMODE)]
        except KeyError:
            pass

        log.info("Scraping mode: {0}".format(mode))

        return mode

    def getBestResults(self, results, gamenameFromFile):

        """
        Compare a game name against each item in a result set to work out which is the likely match
        Args:
            results: A list of dicts with the SearchKey key being the game title in the result set
            gamenameFromFile: The title of the game we are trying to match

        Returns:
            Either None if no match was found, or the title of the matching game (SearchKey key in the dict)
        """

        log.info("getBestResults")

        if results is None or len(results) == 0:
            log.info("No results found with current scraper")
            return None

        log.info("Searching for game: " + gamenameFromFile)
        log.info("%s results found. Try to find best match." % str(len(results)))

        result = self.matchGamename(results, gamenameFromFile)

        if result:
            # get name of found result
            foundgame = self.resolveParseResult(result, 'SearchKey')
            log.info("Using result %s" % foundgame)
            return result

        # stop searching in accurate mode
        if self.update_option == util.SCRAPING_OPTION_AUTO_ACCURATE:
            log.warn("No game found with scraping option 'Accurate'. Game will be skipped")
            return None

        # Ask for correct result in Interactive mode
        if self.update_option == util.SCRAPING_OPTION_INTERACTIVE:
            res = self.ask_user_for_result(gamenameFromFile, results)
            if res == 0:  # Skip Game
                log.info("No result chosen by user")
                return None
            else:
                selectedGame = self.resolveParseResult(results[res - 1], 'Game')
                log.info("Result chosen by user: " + str(selectedGame))
                return results[res - 1]

    def ask_user_for_result(self, gamename, results):
        options = ['Skip Game']
        for result in results:
            options.append(self.resolveParseResult(result, 'SearchKey'))

        resultIndex = xbmcgui.Dialog().select('Search for: ' + gamename, options)
        return resultIndex

    def matchGamename(self, results, gamenameFromFile):
        for idx, result in enumerate(results):
            try:
                # Check if the result has the correct platform (if needed)
                found_platform = self.resolveParseResult(result, 'PlatformSearchKey')
                if found_platform != '' and self.expected_platform != found_platform:
                    log.info("Platform mismatch. %s != %s. Result will be skipped." % (
                        self.expected_platform, found_platform))
                    continue

                searchKey = self.resolveParseResult(result, 'SearchKey')
                # keep it for later reference
                searchkey_orig = searchKey
                gamename_orig = gamenameFromFile

                # if no searchkey is specified first result is valid (1 file per game scenario)
                if searchkey_orig == '':
                    log.info("No searchKey found. Using first result")
                    return result

                log.info("Comparing %s with %s" % (gamename_orig, searchkey_orig))
                if gamename_orig == searchkey_orig:
                    # perfect match
                    return result

                # normalize name and searchkey before comparison
                gnu = GameNameUtil()
                gamename_normalized = gnu.normalize_name(gamename_orig)
                searchkey_normalized = gnu.normalize_name(searchkey_orig)
                log.info("Try normalized names. Comparing %s with %s" % (gamename_normalized, searchkey_normalized))
                if gamename_normalized == searchkey_normalized:
                    # perfect match
                    return result

                #strip additional info from gamename
                gamename_stripped = gnu.strip_addinfo_from_name(gamename_orig)
                gamename_stripped = gnu.normalize_name(gamename_stripped)
                log.info("Try with stripped additional info. Comparing %s with %s" % (
                    gamename_stripped, searchkey_normalized))
                if gamename_stripped == searchkey_normalized:
                    # perfect match
                    return result

            except Exception as exc:
                log.warn("An error occured while matching the best result: " + str(exc))

        log.info("No result found for gamename %s" % gamenameFromFile)
        return None

    def compareNames(self, gamename, searchkey, checkSubtitle):
        if checkSubtitle:
            if searchkey.find(gamename) > -1:
                log.info("%s is a subtitle of %s. Using result %s" % (gamename, searchkey, searchkey))
                return True
        else:
            if gamename == searchkey:
                log.info("Perfect match. Using result %s" % searchkey)
                return True

        return False

    def resolveParseResult(self, result, itemName):
        """ This method is due to the fact that our result set is a list of dicts """

        resultValue = ""

        try:
            resultValue = result[itemName][0]
            resultValue = util.html_unescape(resultValue)
            resultValue = resultValue.strip()
            # unescape ugly html encoding from websites
            resultValue = HTMLParser().unescape(resultValue)

        except Exception as e:
            # log.warn("Error while resolving item: " + itemName + " : " + str(exc))
            log.warn("Error while resolving item: {0} : {1} {2}".format(itemName, type(e), str(e)))

        try:
            log.debug("Result " + itemName + " = " + resultValue)
        except:
            pass

        return resultValue
