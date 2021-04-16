
import os, re
from urllib.parse import quote_plus

import xbmc, xbmcgui
import xbmcvfs

import util
from util import Logutil as log

class ArchiveHandler(object):

    compressedExtensions = ['7z', 'zip', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz', 'rar', 'tgz', 'tbz2', 'gz', 'bz2', 'xz', 'cbr']

    def is_archive(self, rom):
        log.info("ArchiveHandler.is_archive")
        if rom is None:
            return False
        return rom.split('.')[-1] in self.compressedExtensions

    def extract_archive(self, rom_collection, rom, emu_params):
        log.info("ArchiveHandler.extract_archive")

        temp_dir = self.__get_temp_dir_path(rom_collection.name)

        self.__delete_temp_files(temp_dir)

        try:
            files_in_archive = self.__get_rom_names_from_archive(rom)
        except Exception as exc:
            log.error("Error handling compressed file: " + str(exc))
            return []

        if files_in_archive is None or len(files_in_archive) == 0:
            log.error("Error handling compressed file")
            return []

        roms = self.__handle_indexed_roms(rom_collection.diskPrefix, files_in_archive, emu_params, rom, temp_dir)
        if roms:
            return roms

        try:
            # Extract all files to %TMP%
            extracted_files = self.__extract_files(rom, files_in_archive, temp_dir)
        except Exception as exc:
            log.error("Error handling compressed file: " + str(exc))
            return []

        if extracted_files is None:
            log.warn("Error handling compressed file")
            return []

        chosen_rom = 0
        if len(files_in_archive) > 1:
            log.info("The Archive has %d files" % len(files_in_archive))
            chosen_rom = xbmcgui.Dialog().select('Choose a ROM', files_in_archive)
        # Point file name to the chosen file and continue as usual
        roms = [os.path.join(temp_dir, files_in_archive[chosen_rom])]

        log.debug("roms decompressed = " + str(roms))
        if len(roms) == 0:
            return []

        return roms

    def __get_temp_dir_path(self, romcollection_name):
        log.info("ArchiveHandler.__get_temp_dir_path")
        temp_dir = os.path.join(util.getTempDir(), 'extracted', romcollection_name)
        # check if folder exists
        if not xbmcvfs.exists(temp_dir + '\\'):
            log.info("Create temporary folder: " + temp_dir)
            xbmcvfs.mkdirs(temp_dir)

        return temp_dir

    def __delete_temp_files(self, temp_dir):
        log.info("ArchiveHandler.__delete_temp_files")
        try:
            if xbmcvfs.exists(temp_dir + '\\'):
                log.info("Trying to delete temporary rom files")
                #can't use xbmcvfs.listdir here as it seems to cache the file list and RetroPlayer won't find newly created files anymore
                files = os.listdir(temp_dir)
                for f in files:
                    #RetroPlayer places savestate files next to the roms. Don't delete these files.
                    fname, ext = os.path.splitext(f)
                    if ext not in ('.sav', '.xml', '.png'):
                        xbmcvfs.delete(os.path.join(temp_dir, f))
        except Exception as exc:
            log.error("Error deleting files after launch emu: " + str(exc))
            self.gui.writeMsg(util.localize(32036) + ": " + str(exc))

    """
    Special handling of emulators that accept multiple roms per index (i.e. Amiga): -0 rom1 -1 rom2  
    """
    def __handle_indexed_roms(self, disk_prefix, names, emu_params, rom, temp_dir):
        log.info("ArchiveHandler.__handle_indexed_roms")
        if disk_prefix == '':
            return None

        match = re.search(disk_prefix.lower(), str(names).lower())

        if '%I%' not in emu_params or not match:
            return None

        log.info("Extracting %d files" % len(names))

        try:
            extracted_files = self.__extract_files(rom, names, temp_dir)
        except Exception as exc:
            log.error("Error handling compressed file: " + str(exc))
            return None

        if extracted_files is None:
            log.warning("Error handling compressed file")
            return None

        return extracted_files

    """
    Parts of the code taken from here:
    https://forum.kodi.tv/showthread.php?tid=323321&page=3
    Thanks to zachmorris
    """
    def __extract_files(self, archive_file, filenames, directory_to):
        log.info("ArchiveHandler.__extract_files")
        files_out = list()

        if self.__is_7z_on_windows(archive_file):
            return self.__getArchives7z(archive_file, filenames, directory_to)

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

    def __get_rom_names_from_archive(self, filename):
        log.info("ArchiveHandler.__get_rom_names_from_archive")

        if self.__is_7z_on_windows(filename):
            return self.__getNames7z(filename)

        archive_file = self.__get_archive_file_name(filename)
        (dirs, files) = xbmcvfs.listdir(archive_file)

        return files

    #HACK: 7z files are crashing Kodi on Windows. So we have to use py7zlib here
    def __is_7z_on_windows(self, filename):
        fileext = filename.split('.')[-1]
        current_os = util.current_os()

        log.info('fileext = {0}, current_os = {1}'.format(fileext, current_os))

        if(fileext == '7z' and current_os == 'Windows'):
            log.info('Launching 7z game on Windows. Need to use py7zlib to extract 7z file.')
            return True
        return False

    def __get_archive_file_name(self, filename):
        log.info("ArchiveHandler.__get_archive_file_name")
        archive_file_name = 'archive://%(archive_file)s' % {'archive_file': quote_plus(xbmcvfs.translatePath(filename))}
        log.debug("archive_file_name: {0}".format(archive_file_name))
        return archive_file_name

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
        log.debug('names = {0}'.format(names))
        fp.close()
        return names

    def __getArchives7z(self, filepath, archiveList, directory_to):
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

        if archivesDecompressed is None:
            log.warn("Error handling compressed file")
            return []
        for archive in archivesDecompressed:
            newPath = os.path.join(directory_to, archive[0])
            log.info("Putting extracted file in %s" % newPath)
            fo = open(str(newPath), 'wb')
            fo.write(archive[1])
            fo.close()

        return archivesDecompressed
