# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import os
import os.path

from .models import Folder, Song

def import_collection(root_dir):
    for root, dirs, files in os.walk(root_dir, followlinks = True):
        songs = sorted([f for f in files if f.endswith(".mp3")])
        if songs:
            Folder = Folder(path=root)
            songs = [Song(filename=f, Folder=Folder) for f in songs]
            Folder.save()
            for song in songs:
                song.save()

