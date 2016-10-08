#!/usr/bin/env python2

from __future__ import unicode_literals

import sys
import string
import threading
import time

import shout
from shout import ShoutException
from django.conf import settings

BITRATE="160k"

class IcecastPlayer:
    def __init__(self):
        self.playing = False
        self.shout = shout.Shout()
        self.should_stop = False

        self.shout.host = settings.JUKEBOX_SHOUT_HOST
        self.shout.port = settings.JUKEBOX_SHOUT_PORT
        self.shout.user = settings.JUKEBOX_SHOUT_USER
        self.shout.password = settings.JUKEBOX_SHOUT_PASSWORD
        self.shout.mount = settings.JUKEBOX_SHOUT_MOUNT
        self.shout.name =settings.JUKEBOX_SHOUT_NAME
        self.shout.genre =settings.JUKEBOX_SHOUT_GENRE
        self.shout.url = settings.JUKEBOX_SHOUT_URL
        self.shout.public = settings.JUKEBOX_SHOUT_PUBLIC

# self.shout.audio_info = { 'key': 'val', ... }
#  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
#   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)

        self.shout.format = b"mp3"

    def close(self):
        self.shout.close()

    def _play_thread(self, filename):
        total = 0
        st = time.time()
        print("Playing {} to icecast server".format(filename))
        try:
            f = open(filename)

# FIXME race condition
            self.shout.open()

            self.shout.set_metadata({b'song': filename.encode('ascii', 'ignore')})

            nbuf = f.read(4096)
            while not self.should_stop:
                buf = nbuf
                nbuf = f.read(4096)
                total = total + len(buf)
                if len(buf) == 0:
                    break
                self.shout.send(buf)
                self.shout.sync()
            if self.should_stop:
                delay = self.shout.delay()
                if delay > 0:
                    print("Delaying for {} milleseconds before starting next stream".format(delay))
                    time.sleep(delay / 1000.0)
            f.close()
            
            et = time.time()
            br = total*0.008/(et-st)
            print "Sent %d bytes in %d seconds (%f kbps)" % (total, et-st, br)
        except ShoutException as e:
            print("Exception during play, sleeping for one second")
            print(e)
            time.sleep(1.0)
        finally:
            self.playing = False
            self.shout.close()
        print("Finished player._play_thread()")

    def _fake_play_thread(self, filename):
        time.sleep(30)
        self.playing = False

    def play(self, filename):
        #self._thread = threading.Thread(target=self._fake_play_thread, args=(filename,))
        self._thread = threading.Thread(target=self._play_thread, args=(filename,))
        self.playing = True
        self.should_stop = False
        self._thread.start()

    def is_playing(self):
        return self.playing

    def stop(self):
        self.should_stop = True
        while self.playing:
            # FIXME timeout on this wait
            time.sleep(0.1)
        self.playing = False
        self._thread = None
