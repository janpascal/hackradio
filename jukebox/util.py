# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import fnmatch
import os
import os.path

from .models import Album, Song


def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


def import_collection(root_dir):
    for root, dirs, files in os.walk(root_dir, followlinks = True):
        songs = sorted([f for f in files if f.endswith(".mp3")])
        if songs:
            album = Album(path=root)
            songs = [Song(filename=f, album=album) for f in songs]
            album.save()
            for song in songs:
                song.save()

