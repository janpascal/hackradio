# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import fnmatch
import logging
import os
import os.path
import pipes
import subprocess

from django.conf import settings

from .models import Folder, Song

logger = logging.getLogger(__name__)

def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


def import_collection(root_dir):
    recurse_import_dir(root_dir, None)

# returns True if any song were including in this subtree
def recurse_import_dir(root_path, parent):
    logger.info(u"Importing recursively from dir {}".format(root_path))
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

def convert_flac_to_mp3(disk_path, cache_path):
    flac_quoted = pipes.quote(disk_path)
    mp3_quoted = pipes.quote(cache_path)

    commandline = "/usr/bin/flac --decode --stdout " + flac_quoted + " | /usr/bin/lame --preset extreme - " + mp3_quoted
    logger.info("Command line: {}".format(commandline))

    subprocess.call(commandline, shell=True)

def convert_ogg_to_mp3(oggfile, mp3file):
    ogg_quoted = pipes.quote(oggfile)
    mp3_quoted = pipes.quote(mp3file)
    commandline = "/usr/bin/oggdec " + ogg_quoted + " -o - | /usr/bin/lame --preset extreme - " + mp3_quoted
    logger.info("Command line: {}".format(commandline))

    subprocess.call(commandline, shell=True)

def convert_mpc_to_mp3(mpcfile, mp3file):
    mpc_quoted = pipes.quote(mpcfile)
    mp3_quoted = pipes.quote(mp3file)
    commandline = "/usr/bin/mpcdec " + mpc_quoted + " - | /usr/bin/lame --preset extreme - " + mp3_quoted
    logger.info("Command line: {}".format(commandline))

    subprocess.call(commandline, shell=True)

def convert_m4a_to_mp3(m4afile, mp3file):
    m4a_quoted = pipes.quote(m4afile)
    mp3_quoted = pipes.quote(mp3file)
    commandline = "/usr/bin/ffmpeg -i " + m4a_quoted + " " + mp3_quoted
    logger.info("Command line: {}".format(commandline))

    subprocess.call(commandline, shell=True)

# folder should be a models.Folder
def convert_files(folder):
    for song in folder.songs.filter(convertable=True):
        logger.info("song.converted_path: {}".format(song.converted_path))
        if not song.converted_path:
            disk_path = song.disk_path()
            _,extension = os.path.splitext(disk_path)
            logger.info("Converting song {}".format(disk_path))
            cache_path = os.path.join(settings.JUKEBOX_CACHE_DIR, disk_path.replace("/","_")) + "_"
            logger.info("Generic cache path: {}".format(cache_path))
            for i in xrange(65535):
                if not os.path.exists(cache_path + str(i) + ".mp3"):
                    break
            cache_path = cache_path + str(i) + ".mp3"
            logger.info("Definitive cache path: {}".format(cache_path))
            logger.info("extension: {}".format(extension))

            if extension == ".flac":
                convert_flac_to_mp3(disk_path, cache_path)
            elif extension == ".ogg":
                convert_ogg_to_mp3(disk_path, cache_path)
            elif extension == ".mpc":
                convert_mpc_to_mp3(disk_path, cache_path)
            elif extension == ".m4a":
                convert_m4a_to_mp3(disk_path, cache_path)
            else:
                logger.warning("Unable to convert files of this type: {}".format(disk_path))
                continue
            song.converted_path = cache_path
            song.save()

