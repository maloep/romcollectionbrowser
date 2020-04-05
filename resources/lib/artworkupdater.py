from __future__ import absolute_import

from builtins import str
from builtins import object
import os, re
import xbmcvfs
import util
from util import Logutil as log
from gamedatabase import Game, GameView, File

class ArtworkUpdater(object):

    def __init__(self, progress_dialog, gdb, config_object):
        self.progress_dialog = progress_dialog
        self.gdb = gdb
        self.config = config_object
        self.dialogheader = ''

    def update_artwork_cache(self, console_id, file_type_id):
        log.info('cache_artwork')

        #cache all available artwork
        media_dict = self._cache_mediapaths_for_selection(console_id, {})

        if console_id > 0:
            rom_collection = self.config.romCollections[str(console_id)]
            self.dialogheader = util.localize(32954) + " (%i / %i): %s" % (1, 1, rom_collection.name)
            self._update_artwork_cache_for_romcollection(rom_collection, file_type_id, media_dict)
        else:
            rccount = 1
            rclen = len(self.config.romCollections)
            for rcid in list(self.config.romCollections.keys()):
                self.progress_dialog.itemCount = rclen
                rom_collection = self.config.romCollections[str(rcid)]
                self.dialogheader = util.localize(32954) + " (%i / %i): %s" % (rccount, rclen, rom_collection.name)
                continue_update = self._update_artwork_cache_for_romcollection(rom_collection, file_type_id, media_dict)
                if not continue_update:
                    break
                rccount = rccount +1

        log.info('End cache_artwork')

    def _update_artwork_cache_for_romcollection(self, rom_collection, file_type_id, media_dict):
        log.info('Begin _update_artwork_cache_for_romcollection')
        log.info('Update artwork cache for Rom Collection %s' % str(rom_collection.id))

        continue_update = True
        media_paths_dict = {}
        try:
            media_paths_dict = media_dict[rom_collection.id]
        except KeyError:
            log.warn('No media paths dict found for rom collection %s' % rom_collection.id)
            return continue_update

        games = GameView(self.gdb).getFilteredGames(rom_collection.id, 0, 0, 0, 0, 0, 0, 0, 0, '0 = 0', '', 0)
        gamecount = 1
        for game in games:
            self.progress_dialog.itemCount = len(games)
            #32955 = Scan artwork for Game
            update_message = "%s[CR]%s: %i/%i" %(self.dialogheader, util.localize(32955), gamecount, len(games))
            continue_update = self.progress_dialog.writeMsg(update_message, gamecount)
            if not continue_update:
                log.info('Update canceled')
                break
            gamecount = gamecount + 1
            for media_path in rom_collection.mediaPaths:
                #check if we should handle this file type
                if str(file_type_id) != media_path.fileType.id and file_type_id != 0:
                    continue

                roms = File(self.gdb).getRomsByGameId(game[GameView.COL_ID])
                gamename_from_file = rom_collection.getGamenameFromFilename(roms[0][0])
                #check if artwork is available for this type
                file = self._find_file_in_mediadict(media_path.fileType.id, rom_collection, media_paths_dict,
                                               gamename_from_file)
                #check if filename has changed
                if game[getattr(GameView, "COL_fileType%s" % media_path.fileType.id)] != file:
                    #write result to db
                    # get column name from FIELDNAMES - index is the same as db column index (COL_fileTypeX)
                    column = Game.FIELDNAMES[getattr(Game, "COL_fileType%s" % media_path.fileType.id)]
                    Game(self.gdb).update((column,), (file,), game[Game.COL_ID], True)

        return continue_update

    def _cache_mediapaths_for_selection(self, console_id, media_dict):
        log.info('Begin cache_mediapaths_for_selection')

        if media_dict is None:
            media_dict = {}

        #if this console is already cached there is nothing to do
        if console_id in list(media_dict.keys()):
            log.info('MediaPaths for RomCollection %s are already in cache' % console_id)
            return media_dict

        if console_id > 0:
            self.progress_dialog.itemCount = 1
            rom_collection = self.config.romCollections[str(console_id)]
            #32953 = Caching Artwork for Rom Collection
            self.dialogheader = "%s (%i / %i): %s" % (util.localize(32953), 1, 1, rom_collection.name)
            self.progress_dialog.writeMsg(self.dialogheader, 1)
            self._cache_media_paths_for_console(str(console_id), media_dict)
            return media_dict
        else:
            rccount = 1
            rclen = len(self.config.romCollections)
            for rcid in list(self.config.romCollections.keys()):
                self.progress_dialog.itemCount = rclen
                rom_collection = self.config.romCollections[str(rcid)]
                # 32953 = Caching Artwork for Rom Collection
                self.dialogheader = "%s (%i / %i): %s" % (util.localize(32953), rccount, rclen, rom_collection.name)
                self.progress_dialog.writeMsg(self.dialogheader, rccount)
                if rcid in list(media_dict.keys()):
                    log.info('MediaPaths for RomCollection %s are already in cache' % rcid)
                    continue
                self._cache_media_paths_for_console(rcid, media_dict)
                rccount = rccount + 1

        log.info('End cacheMediaPathsForSelection')
        return media_dict

    def _cache_media_paths_for_console(self, console_id, media_dict):
        log.info('Begin _cache_media_paths_for_console')
        log.info('Caching mediaPaths for Rom Collection %s' % console_id)

        rom_collection = self.config.romCollections[str(console_id)]

        media_path_dict = {}

        for media_path in rom_collection.mediaPaths:
            log.info('media_path = %s' % media_path.path)
            mediadir = media_path.path
            #if foldername is gamename only get content of parent directory
            if rom_collection.useFoldernameAsGamename:
                mediadir = mediadir[0:mediadir.index('%GAME%')]

            mediafiles = []
            self._walk_down_media_directories(os.path.dirname(mediadir), mediafiles)

            media_path_dict[media_path.fileType.id] = mediafiles

        media_dict[console_id] = media_path_dict
        log.info('End cacheMediaPathsForConsole')

    def _walk_down_media_directories(self, mediadir, mediafiles):
        log.info('Begin _walk_down_media_directories')
        log.info('xbmcvfs.listdir')
        mediasubdirs, mediasubfiles = xbmcvfs.listdir(mediadir)
        log.info('Add files')
        for mediasubfile in mediasubfiles:
            mediafiles.append(os.path.normpath(os.path.join(mediadir, mediasubfile)))

        for mediasubdir in mediasubdirs:
            self._walk_down_media_directories(os.path.join(mediadir, mediasubdir), mediafiles)

    def _find_file_in_mediadict(self, filetype_id, rom_collection, media_paths_dict, gamename_from_file):
        log.info("begin _find_file_in_mediadict")

        media_path = rom_collection.getMediaPathByTypeId(filetype_id)

        if not media_path:
            return ''

        pathname_from_file = media_path.replace("%GAME%", gamename_from_file)
        media_paths_list = media_paths_dict[str(filetype_id)]

        image_path = self._find_file_with_correct_extension(pathname_from_file, media_paths_list)
        if image_path:
            return image_path

    def _find_file_with_correct_extension(self, pathnameFromFile, mediaPathsList):
        pathToSearch = re.escape(os.path.normpath(pathnameFromFile.replace('.*', '')))
        pattern = re.compile('%s\..*$' % pathToSearch)
        for imagePath in mediaPathsList:
            match = pattern.search(imagePath)
            if match:
                resultFilename, resultExtension = os.path.splitext(imagePath)
                mediaPathFilename, mediaPathExtension = os.path.splitext(pathnameFromFile)
                return '%s%s' % (mediaPathFilename, resultExtension)