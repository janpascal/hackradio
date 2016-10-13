#!/usr/bin/env python2

from __future__ import unicode_literals

import logging
import sys
import string
import threading
import time

from django.core.exceptions import ObjectDoesNotExist

from models import Folder, Song
from player import IcecastPlayer

player = IcecastPlayer()
player_thread = None
logger = logging.getLogger(__name__)

skip_rest_of_current_folder = False
stop_playing = False

def _play_thread():
    global skip_rest_of_current_folder
    global stop_playing
    global player
    global player_thread

    while not stop_playing:
        current_folder = Folder.objects.filter(selected=True).order_by('order').first()
        if current_folder is None:
            logger.info("No albums queued, trying again later...")
            time.sleep(30)
            continue
        logger.info(u"Current folder: {}".format(current_folder))
        current_folder.now_playing = True
        current_folder.save()

        player.connect()
        for song in current_folder.songs.all():
            del song.skipped
            if song.skipped:
                logger.info(u"Skipping {}".format(song.filename))
                song.skipped = False
                song.save()
                continue

            logger.info(u"Playing {}".format(song.filename))
            song.now_playing = True
            song.save()

            player.play(song.mp3_path())
            while not player.stopped_event.wait(0.1):
                del song.skipped
                if song.skipped or skip_rest_of_current_folder or stop_playing:
                    player.stop()
                    break
            song.now_playing = False
            song.save()

            if skip_rest_of_current_folder:
                skip_rest_of_current_folder = False
                break

            if stop_playing:
                break

        current_folder.now_playing = False
        current_folder.save()
        current_folder.bottom()

    player_thread = None

def start():
    global player_thread
    global skip_rest_of_current_folder
    global stop_playing
    if player_thread is None:
        logger.info("Starting queue player!")
        Folder.objects.filter(now_playing=True).update(now_playing=False)
        Song.objects.filter(now_playing=True).update(now_playing=False)
        player_thread = threading.Thread(target=_play_thread)
        skip_rest_of_current_folder = False
        stop_playing = False
        player_thread.start()

def stop():
    global player_thread
    global stop_playing
    if player_thread is not None:
        logger.info("Telling player thread to stop, waiting max 10 seconds until it stops")
        stop_playing = True
        count = 0
        while player_thread is not None and count<10:
            logger.info("Still waiting for player to stop...")
            time.sleep(1)
            count += 1

def is_playing():
    global player_thread

    return player_thread is not None

def skip_current_folder():
    global skip_rest_of_current_folder
    skip_rest_of_current_folder = True

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

