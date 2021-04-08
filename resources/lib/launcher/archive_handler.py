
import os, re
from urllib.parse import quote_plus

import xbmc
import xbmcvfs

import util
from util import Logutil as log

class ArchiveHandler(object):

    compressedExtensions = ['7z', 'zip']

    def extract_archive(self, romCollection, rom, saveStateParams, emuParams, calledFromSkin):

        log.info("ArchiveHandler.extract_archive")

        # If it's a .7z file
        # Don't extract zip files in case of savestate handling and when called From skin
        filext = rom.split('.')[-1]
        roms = [rom]
        if filext in self.compressedExtensions and not romCollection.doNotExtractZipFiles and saveStateParams == '' and not calledFromSkin:
            roms = self.__handleCompressedFile(romCollection, filext, rom, emuParams)
            log.debug("roms compressed = " + str(roms))
            if len(roms) == 0:
                return None

        return roms

    def __handleCompressedFile(self, romCollection, filext, rom, emuParams):

        log.info("ArchiveHandler.__handleCompressedFile")

        # Note: Trying to delete temporary files (from zip or 7z extraction) from last run
        # Do this before launching a new game. Otherwise game could be deleted before launch
        tempDir = os.path.join(util.getTempDir(), 'extracted', romCollection.name)
        # check if folder exists
        if not xbmcvfs.exists(tempDir + '\\'):
            log.info("Create temporary folder: " + tempDir)
            xbmcvfs.mkdir(tempDir)

        try:
            if xbmcvfs.exists(tempDir + '\\'):
                log.info("Trying to delete temporary rom files")
                #can't use xbmcvfs.listdir here as it seems to cache the file list and RetroPlayer won't find newly created files anymore
                files = os.listdir(tempDir)
                for f in files:
                    #RetroPlayer places savestate files next to the roms. Don't delete these files.
                    fname, ext = os.path.splitext(f)
                    if ext not in ('.sav', '.xml', '.png'):
                        xbmcvfs.delete(os.path.join(tempDir, f))
        except Exception as exc:
            log.error("Error deleting files after launch emu: " + str(exc))
            self.gui.writeMsg(util.localize(32036) + ": " + str(exc))

        roms = []

        log.info("Treating file as a compressed archive")

        try:
            names = self.__getNames(rom)
        except Exception as exc:
            log.error("Error handling compressed file: " + str(exc))
            return []

        if names is None:
            log.error("Error handling compressed file")
            return []

        chosenROM = -1

        # check if we should handle multiple roms
        match = False
        if romCollection.diskPrefix != '':
            match = re.search(romCollection.diskPrefix.lower(), str(names).lower())

        if '%I%' in emuParams and match:
            log.info("Loading %d archives" % len(names))

            try:
                extracted_files = self.__extract_files(rom, names, tempDir)
            except Exception as exc:
                log.error("Error handling compressed file: " + str(exc))
                return []

            if extracted_files is None:
                log.warning("Error handling compressed file")
                return []

            roms.extend(extracted_files)
        elif len(names) > 1:
            log.info("The Archive has %d files" % len(names))
            chosenROM = xbmcgui.Dialog().select('Choose a ROM', names)
        elif len(names) == 1:
            log.info("Archive only has one file inside; picking that one")
            chosenROM = 0
        else:
            log.error("Archive had no files inside!")
            return []

        if chosenROM != -1:
            try:
                # Extract all files to %TMP%
                extracted_files = self.__extract_files(rom, names, tempDir)
            except Exception as exc:
                log.error("Error handling compressed file: " + str(exc))
                return []

            if extracted_files is None:
                log.warn("Error handling compressed file")
                return []

            # Point file name to the chosen file and continue as usual
            roms = [os.path.join(tempDir, names[chosenROM])]

        return roms

    def __getNames(self, filename):
        archive_file = self.__get_archive_file_name(filename)
        (dirs, files) = xbmcvfs.listdir(archive_file)

        return files

    def __get_archive_file_name(self, filename):
        log.info("ArchiveHandler.__get_archive_file_name")
        return 'archive://%(archive_file)s' % {'archive_file': quote_plus(xbmcvfs.translatePath(filename))}

    def __extract_files(self, archive_file, filenames, directory_to):
        log.info("ArchiveHandler.__extract_files")
        files_out = list()
        archive_path = self.__get_archive_file_name(archive_file)

        for ff in filenames:
            file_from = os.path.join(archive_path, ff).replace('\\', '/')
            success = xbmcvfs.copy(file_from, os.path.join(xbmcvfs.translatePath(directory_to), ff))
            if not success:
                log.error('Error extracting file %(ff)s from archive %(archive_file)s' % {'ff': ff, 'archive_file': archive_file})
            else:
                log.debug('Extracted file %(ff)s from archive %(archive_file)s' % {'ff': ff, 'archive_file': archive_file})
                files_out.append(os.path.join(xbmcvfs.translatePath(directory_to), ff))

        return files_out

    # Obsolete functions
    """
    def __getNames(self, compression_type, filepath):
        return {'zip': self.__getNamesZip,
                '7z': self.__getNames7z}[compression_type](filepath)

    def __getNames7z(self, filepath):

        try:
            import py7zlib
        except ImportError as e:
            # 32039 = Error launching .7z file.
            # 32129 = Please check kodi.log for details.
            message = "%s[CR]%s" % (util.localize(32039), util.localize(32129))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            msg = (
                "You have tried to launch a .7z file but you are missing required libraries to extract the file. "
                "You can download the latest RCB version from RCBs project page. It contains all required libraries.")
            log.error(msg)
            log.error("Error: " + str(e))
            return None

        fp = open(str(filepath), 'rb')
        archive = py7zlib.Archive7z(fp)
        names = archive.getnames()
        fp.close()
        return names

    def __getNamesZip(self, filepath):
        fp = open(str(filepath), 'rb')
        archive = zipfile.ZipFile(fp)
        names = archive.namelist()
        fp.close()
        return names        

    def __getArchives(self, compression_type, filepath, archiveList):
        return {'zip': self.__getArchivesZip,
                '7z': self.__getArchives7z}[compression_type](filepath, archiveList)

    def __getArchives7z(self, filepath, archiveList):

        try:
            import py7zlib
        except ImportError:
            # 32039 = Error launching .7z file.
            # 32129 = Please check kodi.log for details.
            message = "%s[CR]%s" % (util.localize(32039), util.localize(32129))
            xbmcgui.Dialog().ok(util.SCRIPTNAME, message)
            msg = (
                "You have tried to launch a .7z file but you are missing required libraries to extract the file. "
                "You can download the latest RCB version from RCBs project page. It contains all required libraries.")
            log.error(msg)
            return None

        fp = open(str(filepath), 'rb')
        archive = py7zlib.Archive7z(fp)
        archivesDecompressed = [(name, archive.getmember(name).read()) for name in archiveList]
        fp.close()
        return archivesDecompressed

    def __getArchivesZip(self, filepath, archiveList):
        fp = open(str(filepath), 'rb')
        archive = zipfile.ZipFile(fp)
        archivesDecompressed = [(name, archive.read(name)) for name in archiveList]
        fp.close()
        return archivesDecompressed
    """


"""

//https://forum.kodi.tv/showthread.php?tid=323321&page=3

file_7z = "C:\\Users\\Malte\\Documents\\Archivetests\\Test.7z"
archive_file = 'archive://%(archive_file)s' % {'archive_file': quote_plus(xbmc.translatePath(file_7z))}
(dirs, files) = xbmcvfs.listdir(archive_file)
print(files)
"""