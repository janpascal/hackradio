#!/usr/bin/env python2

from __future__ import unicode_literals

import sys
import string
import threading
import time

from django.core.exceptions import ObjectDoesNotExist

from models import Folder, Song
from player import IcecastPlayer

player = IcecastPlayer()
player_thread = None

def _play_thread():
    while(True):
        current_folder = Folder.objects.filter(selected=True).order_by('order').first()
        print(u"Current folder: {}".format(current_folder))
        current_folder.now_playing = True
        current_folder.save()
        
        for song in current_folder.songs.all():
            del song.skipped
            if song.skipped:
                print(u"Skipping {}".format(song.filename))
                song.skipped = False
                song.save()
                continue

            print(u"Playing {}".format(song.filename))
            song.now_playing = True
            song.save()
            player.play(song.disk_path())
            while player.is_playing():
                time.sleep(0.1)
                del song.skipped
                if song.skipped:
                    player.stop()
                    break
            song.now_playing = False
            song.save()

        current_folder.now_playing = False
        current_folder.save()
        current_folder.bottom()

def start():
    global player_thread
    if player_thread is None:
        print("Starting queue player!")
        Folder.objects.filter(now_playing=True).update(now_playing=False)
        Song.objects.filter(now_playing=True).update(now_playing=False)
        player_thread = threading.Thread(target=_play_thread)
        player_thread.start()

def is_playing():
    global player_thread

    return player_thread is not None

def now_playing():
    if not is_playing():
        return [], None, None
    current_folder = None
    current_song = None
    try:
        current_folder = Folder.objects.get(now_playing=True)
        current_song = Song.objects.get(now_playing=True)
    except ObjectDoesNotExist:
        pass
    if current_folder:
        song_list = current_folder.songs.all()
    else:
        song_list = []
    return song_list, current_folder, current_song

