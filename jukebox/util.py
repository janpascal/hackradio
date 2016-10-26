# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import fnmatch
import logging
import os
import os.path
import tempfile
import zipfile

from django.conf import settings
from django.core.files.uploadedfile import TemporaryUploadedFile

from .models import Folder, Song

logger = logging.getLogger(__name__)

_current_dir = ""

def current_import_dir():
    global _current_dir
    return _current_dir

def import_collection(root_dir):
    recurse_import_dir(root_dir, None)

# returns True if any song were including in this subtree
def recurse_import_dir(root_path, parent):
    global _current_dir

    logger.info(u"Importing recursively from dir {}".format(root_path))
    _current_dir = root_path

    found_something = False
    folder,folder_is_new = Folder.objects.get_or_create(disk_path=root_path, name=os.path.basename(root_path))
    logger.debug("Folder is new: {}".format(folder_is_new))
    folder.parent = parent
    folder.save()
    songs = []
    for f in os.listdir(root_path):
        logger.debug(u"Examining file {} in dir {}".format(f, root_path))
        disk_path = os.path.join(root_path, f)
        if os.path.isdir(disk_path):
            logger.debug(u"Directory {}, recursing".format(disk_path))
            found_in_subtree = recurse_import_dir(disk_path, folder)
            found_something = found_something or found_in_subtree
        _,extension = os.path.splitext(f)
        if os.path.isfile(disk_path) and extension in [".mp3", ".flac", ".ogg", ".mpc", ".m4a"]:
            logger.info(u"Importing song {}".format(disk_path))
            folder.selectable = True
            found_something = True
            song,_ = Song.objects.get_or_create(filename=f, folder=folder)
            if extension != ".mp3":
                song.convertable = True
            song.save()

    if folder_is_new and not found_something and len(songs) == 0:
        logger.debug(u"Removing folder without any songs in it: {}".format(root_path))
        logger.debug(u"{}, {}, {}".format(folder_is_new, found_something, songs))
        folder.delete()
    else:
        folder.save()

    return found_something

def import_ziparchive(name, f):
    if not isinstance(f, TemporaryUploadedFile):
        logger.error("Uploaded file should be a TemporaryUploadedFile")
        return

    logger.info("Uploaded tempfile: {}".format(f.temporary_file_path()))
    if not zipfile.is_zipfile(f.temporary_file_path()):
        logger.error("Uploaded file should be a zip file")
        return

    root_dir = tempfile.mkdtemp(prefix='import', dir=settings.JUKEBOX_UPLOAD_DIR)
    archive_dir = os.path.join(root_dir, name)

    try:
        os.mkdirs(archive_dir)
    except:
        pass

    with zipfile.ZipFile(f.temporary_file_path(), 'r') as myzip:
        myzip.extractall(archive_dir)
        import_collection(archive_dir)


