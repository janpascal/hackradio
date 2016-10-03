#!/usr/bin/env python2

from __future__ import unicode_literals

import sys
import string
import threading
import time

from player import IcecastPlayer

from models import Album, Song

player = IcecastPlayer()
current_album = None
player_thread = None

def _play_thread():
    while(True):
        current_album = Album.objects.filter(selected=True).order_by('order').first()
        print(u"Current album: {}".format(current_album))
        
        for song in current_album.song_set.all():
            if song.skipped:
                print(u"Skipping {}".format(song.filename))
                song.skipped = False
                song.save()
                continue

            print(u"Playing {}".format(song.filename))
            player.play(song.full_path())
            while player.is_playing():
                time.sleep(0.1)

        current_album.bottom()

def start():
    global player_thread
    if player_thread is None:
        print("Starting queue player!")
        player_thread = threading.Thread(target=_play_thread)
        player_thread.start()


