from __future__ import absolute_import
from builtins import str
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import SubElement

from config import *
import dialogprogress
from gamedatabase import *
from rcbxmlreaderwriter import RcbXmlReaderWriter
from util import *
import util
import xbmcvfs


class NfoWriter(RcbXmlReaderWriter):
    Settings = util.getSettings()

    def __init__(self):
        pass

    def exportLibrary(self, gdb, romCollections):
        Logutil.log("Begin exportLibrary", util.LOG_LEVEL_INFO)

        progressDialog = dialogprogress.ProgressDialogGUI()
        progressDialog.writeMsg(util.localize(32169), "", "")
        continueExport = True
        rccount = 1

        for romCollection in list(romCollections.values()):

            progDialogRCHeader = util.localize(32170) + " (%i / %i): %s" % (
            rccount, len(romCollections), romCollection.name)
            rccount = rccount + 1

            Logutil.log("export Rom Collection: " + romCollection.name, util.LOG_LEVEL_INFO)
            gameCount = 1

            #get all games for this Rom Collection
            games = GameView(gdb).getFilteredGames(romCollection.id, 0, 0, 0, 0, 0, 0, 0, 0, '0 = 0', '', 0)
            progressDialog.itemCount = len(games) + 1

            for game in games:

                continueExport = progressDialog.writeMsg(progDialogRCHeader,
                                                         util.localize(32171) + ": " + str(game[GameView.COL_NAME]), "", gameCount)
                if not continueExport:
                    Logutil.log('Game export canceled by user', util.LOG_LEVEL_INFO)
                    break

                gameCount = gameCount + 1

                romfiles = File(gdb).getRomsByGameId(game[GameView.COL_ID])
                first_rom = romfiles[0]

                gamenameFromFile = romCollection.getGamenameFromFilename(first_rom[0])
                artworkfiles = {}
                artworkurls = []

                self.createNfoFromDesc(game,
                                       romCollection.name,
                                       first_rom[0],
                                       gamenameFromFile,
                                       artworkfiles,
                                       artworkurls)

        progressDialog.writeMsg("", "", "", -1)
        del progressDialog

    def createNfoFromDesc(self, game, platform, romFile, gameNameFromFile, artworkfiles, artworkurls):

        Logutil.log("Begin createNfoFromDesc", util.LOG_LEVEL_INFO)

        nfoFile = self.getNfoFilePath(platform, romFile, gameNameFromFile)
        if nfoFile == '':
            log.debug(u"Not writing NFO file for {0}".format(gameNameFromFile))
            return

        root = ET.Element('game')
        #reference to eventually existing nfo
        existing_nfo = None

        #Read info from existing nfo file. New info and existing info will be merged
        if xbmcvfs.exists(nfoFile):
            fh = xbmcvfs.File(nfoFile)
            existing_nfo = ET.fromstring(fh.read())
            fh.close()

        self.write_from_db_or_nfo(game[GameView.COL_NAME], existing_nfo, root, 'title')
        self.write_from_db_or_nfo(game[GameView.COL_originalTitle], existing_nfo, root, 'originalTitle')
        self.write_from_db_or_nfo(game[GameView.COL_alternateTitle], existing_nfo, root, 'alternateTitle')
        self.write_from_db_or_nfo(platform, existing_nfo, root, 'platform')
        self.write_from_db_or_nfo(game[GameView.COL_description], existing_nfo, root, 'plot')
        self.write_from_db_or_nfo(game[GameView.COL_publisher], existing_nfo, root, 'publisher')
        self.write_from_db_or_nfo(game[GameView.COL_developer], existing_nfo, root, 'developer')
        self.write_from_db_or_nfo(game[GameView.COL_year], existing_nfo, root, 'year')
        self.write_from_db_or_nfo(game[GameView.COL_url], existing_nfo, root, 'detailUrl')
        self.write_from_db_or_nfo(game[GameView.COL_maxPlayers], existing_nfo, root, 'maxPlayer')
        self.write_from_db_or_nfo(game[GameView.COL_region], existing_nfo, root, 'region')
        self.write_from_db_or_nfo(game[GameView.COL_media], existing_nfo, root, 'media')
        self.write_from_db_or_nfo(game[GameView.COL_perspective], existing_nfo, root, 'perspective')
        self.write_from_db_or_nfo(game[GameView.COL_controllerType], existing_nfo, root, 'controller')
        self.write_from_db_or_nfo(game[GameView.COL_version], existing_nfo, root, 'version')
        self.write_from_db_or_nfo(game[GameView.COL_rating], existing_nfo, root, 'rating')
        self.write_from_db_or_nfo(game[GameView.COL_numVotes], existing_nfo, root, 'votes')
        self.write_from_db_or_nfo(game[GameView.COL_isFavorite], existing_nfo, root, 'isFavorite')
        self.write_from_db_or_nfo(game[GameView.COL_launchCount], existing_nfo, root, 'launchCount')

        """
        for elem in ['title', 'originalTitle', 'alternateTitle', 'platform', 'plot', 'publisher', 'developer', 'year',
                     'detailUrl', 'maxPlayer', 'region', 'media', 'perspective', 'controller', 'version', 'rating',
                     'votes', 'isFavorite', 'launchCount']:
            elemText = locals()[elem]
            #if new info is empty, check if the existing file has it
            if existing_nfo and not elemText:
                try:
                    elemText = existing_nfo.find(elem).text
                except:
                    pass
            ET.SubElement(root, elem).text = elemText
        """

        genreList = []
        if game[GameView.COL_genre]:
            for genre in game[GameView.COL_genre].split(', '):
                if genre != 'None':
                    genreList.append(genre)

        #if no genre was given, use genres from existing file
        if existing_nfo and len(genreList) == 0:
            for genre in existing_nfo.findall("genre"):
                genreList.append(genre.text)

        for genre in genreList:
            ET.SubElement(root, 'genre').text = genre

        for artworktype in list(artworkfiles.keys()):

            local = ''
            online = ''
            try:
                local = artworkfiles[artworktype][0]
                online = artworkurls[artworktype.name]
            except:
                pass

            try:
                SubElement(root, 'thumb', {'type': artworktype.name, 'local': local}).text = online
            except Exception as exc:
                Logutil.log('Error writing artwork url: ' + str(exc), util.LOG_LEVEL_WARNING)

        self.writeNfoElementToFile(root, platform, romFile, gameNameFromFile, nfoFile)

    def write_from_db_or_nfo(self, value_from_db, existing_nfo, root, elementname):

        val = ''
        if value_from_db:
            val = value_from_db
        else:
            if existing_nfo:
                try:
                    val = existing_nfo.find(elementname).text
                except:
                    pass
        ET.SubElement(root, elementname).text = val

    def writeNfoElementToFile(self, root, platform, romFile, gameNameFromFile, nfoFile):
        # write file
        try:
            self.indentXml(root)
            tree = ElementTree(root)

            log.info(u"Writing NFO file {0}".format(nfoFile))
            localFile = util.joinPath(util.getTempDir(), os.path.basename(nfoFile))
            tree.write(localFile, encoding="UTF-8", xml_declaration=True)
            xbmcvfs.copy(localFile, nfoFile)
            xbmcvfs.delete(localFile)

        except Exception as exc:
            log.warn(u"Error: Cannot write game nfo for {0}: {1}".format(gameNameFromFile, exc))

    def getNfoFilePath(self, romCollectionName, romFile, gameNameFromFile):
        nfoFile = ''

        nfoFolder = self.Settings.getSetting(util.SETTING_RCB_NFOFOLDER)

        if nfoFolder != '' and nfoFolder != None:
            # Add the trailing slash that xbmcvfs.exists expects
            nfoFolder = os.path.join(os.path.dirname(nfoFolder), '')
            if not xbmcvfs.exists(nfoFolder):
                Logutil.log("Path to nfoFolder does not exist: " + nfoFolder, util.LOG_LEVEL_WARNING)
            else:
                nfoFolder = os.path.join(nfoFolder, romCollectionName)
                if not os.path.exists(nfoFolder):
                    os.mkdir(nfoFolder)

                nfoFile = os.path.join(nfoFolder, gameNameFromFile + '.nfo')

        if nfoFile == '':
            romDir = os.path.dirname(romFile)
            Logutil.log('Romdir: ' + romDir, util.LOG_LEVEL_INFO)
            nfoFile = os.path.join(romDir, gameNameFromFile + '.nfo')

        log.debug(u"%s returns %s for %s (%s) on platform %s" % (
        __name__, nfoFile, gameNameFromFile, romFile, romCollectionName))

        return nfoFile
