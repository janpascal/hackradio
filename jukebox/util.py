# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import fnmatch
import os
import os.path

from .models import Folder, Song


def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


#def import_collection(root_dir):
#    for root, dirs, files in os.walk(root_dir, followlinks = True):
#        songs = sorted([f for f in files if f.endswith(".mp3")])
#        if songs:
#            album = Folder(path=root)
#            songs = [Song(filename=f, album=album) for f in songs]
#            album.save()
#            for song in songs:
#                song.save()

#def import_collection(root_dir):
#    for root, dirs, files in os.walk(root_dir, followlinks = True):
#        songs = sorted([f for f in files if f.endswith(".mp3")])
#        if songs:
#            folder,_ = Folder.objects.get_or_create(disk_path=root,
#            name=os.path.dirname(root), parent=None)
#            folder.save()
#            for f in songs:
#                song,_ = Song.objects.get_or_create(filename=f, folder=folder)
#                song.save()

def import_collection(root_dir):
    recurse_import_dir(root_dir, None)

# returns True if any song were including in this subtree
def recurse_import_dir(root_path, parent):
    print("Importing recursively from dir {}".format(root_path))
    found_something = False
    folder,folder_is_new = Folder.objects.get_or_create(disk_path=root_path, name=os.path.basename(root_path))
    print("Folder is new: {}".format(folder_is_new))
    folder.parent = parent
    folder.save()
    songs = []
    for f in os.listdir(root_path):
        print("Examining file {} in dir {}".format(f, root_path))
        disk_path = os.path.join(root_path, f)
        if os.path.isdir(disk_path):
            print("Directory {}, recursing".format(disk_path))
            found_in_subtree = recurse_import_dir(disk_path, folder)
            found_something = found_something or found_in_subtree
        if os.path.isfile(disk_path) and f.endswith(".mp3"):
            print("Importing song {}".format(disk_path))
            found_something = True
            song,_ = Song.objects.get_or_create(filename=f, folder=folder)
            song.save()

    if folder_is_new and not found_something and len(songs) == 0:
        print("Removing folder without any songs in it: {}".format(root_path))
        print("{}, {}, {}".format(folder_is_new, found_something, songs))
        folder.delete()

    return found_something

