"""
Classes and functions to work with files and folders
"""

from builtins import object
import os
import shutil

__author__ = 'Team Kodi <http://kodi.tv>'
__credits__ = 'Team Kodi'
__date__ = 'Fri May 01 16:22:23 BST 2015'
__platform__ = 'ALL'
__version__ = '2.20.0'


class File(object):
    """
    File(filepath, mode=None)

    Creates a file object

    :param filepath: file path
    :param mode: (opt) file access mode. ``None``: read (default), ``'w'``: write.

    Example::

        f = xbmcvfs.File(file, 'w')
    """
    fh = None
    
    
    def __init__(self, filepath, mode=None):
        """
        :param filepath: file path
        :param mode: (opt) file access mode. None: read (default), 'w': write.

        Example::

            f = xbmcvfs.File(file, 'w')
        """
        if(mode):
            self.fh = open(filepath, mode)
        else:
            self.fh = open(filepath)

    def close(self):
        """
        Close the file

        example::

            f = xbmcvfs.File(file)
            f.close()
        """
        self.fh.close()

    def read(self, numBytes=0):
        """
        Read from the file to a string.

        :param numBytes: how many bytes to read [opt]- if not set it will read the whole file
        :returns: str

        example::

            f = xbmcvfs.File(file)
            b = f.read()
            f.close()
        """
        if(numBytes > 0):
            return self.fh.read(numBytes)
        else:
            return self.fh.read()

    def readBytes(self, numBytes=0):
        """
        Read from the file to a bytearray.

        :param numBytes: how many bytes to read [opt]- if not set it will read the whole file
        :return: bytearray

        example::
            f = xbmcvfs.File(file)
            b = f.read()
            f.close()
        """
        if(numBytes > 0):
            return self.fh.read(numBytes).encode()
        else:
            return self.fh.read().encode()

    def seek(self, seekBytes, iWhence):
        """
        Seek the file to the specified position.

        :param seekBytes: position in the file
        :param iWhence: where in a file to seek from [0 begining, 1 current , 2 end possition]

        example::

            f = xbmcvfs.File(file)
            result = f.seek(8129, 0)
            f.close()
        """
        return int()

    def size(self):
        """
        Returns the size of the file

        example::

            f = xbmcvfs.File(file)
            s = f.size()
            f.close()
        """
        return int()

    def write(self, buffer):
        """
        Write to the file.

        :param buffer: buffer to write to the file

        example::

            f = xbmcvfs.File(file, 'w')
            result = f.write(buffer)
            f.close()
        """
        return self.fh.write(buffer)


def copy(strSource, strDestnation):
    """Copy file to destination, returns true/false.

    :param source: string - file to copy.
    :param destination: string - destination file

    Example::

        success = xbmcvfs.copy(source, destination)
    """
    return shutil.copy(strSource, strDestnation)


def delete(file):
    """Delete the file

    :param file: string - file to delete

    Example::

        xbmcvfs.delete(file)
    """
    try:
        os.remove(file)
    except OSError:
        pass


def rename(file, newFile):
    """Renames a file, returns true/false.

    :param file: string - file to rename
    :param newFile: string - new filename, including the full path

    Example::

        success = xbmcvfs.rename(file,newFileName)"""
    return bool(1)


def mkdir(path):
    """Create a folder.

    :param path: folder

    Example::

        success = xbmcfvs.mkdir(path)
    """
    return bool(1)


def mkdirs(path):
    """
    Create folder(s) - it will create all folders in the path.

    :param path: folder

    example::

        success = xbmcvfs.mkdirs(path)
    """
    return bool(1)


def rmdir(path, force=False):
    """Remove a folder.

    :param path: folder

    Example::

        success = xbmcfvs.rmdir(path)
    """
    return bool(1)


def exists(path):
    """Checks for a file or folder existance, mimics Pythons os.path.exists()

    :param path: string - file or folder

    Example::

        success = xbmcvfs.exists(path)
    """
    return os.path.exists(path)


def listdir(path):
    """
    listdir(path) -- lists content of a folder.

    :param path: folder

    example::

        dirs, files = xbmcvfs.listdir(path)
    """
    #path = os.path.normpath(path)
        
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    #print 'dirs: %s' %dirs
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    #print 'files: %s' %files
    
    return dirs, files 


class Stat(object):
    """
    Stat(path)

    Get file or file system status.

    :param path: file or folder

    example::

        print xbmcvfs.Stat(path).st_mtime()
    """
    def __init__(self, path):
        """
        Stat(path) -- get file or file system status.

        :param path: file or folder

        example::

            print xbmcvfs.Stat(path).st_mtime()
        """

    def st_mode(self):
        return int()

    def st_ino(self):
        return int()

    def st_nlink(self):
        return int()

    def st_uid(self):
        return int()

    def st_gid(self):
        return int()

    def st_size(self):
        return int()

    def st_atime(self):
        return int()

    def st_mtime(self):
        return int()

    def st_ctime(self):
        return int()