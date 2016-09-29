#!/usr/bin/env python2
import sys
import string
import threading
import time

import shout
from django.conf import settings

BITRATE="160k"

class IcecastPlayer:
    def __init__(self):
        self.playing = False
        self.shout = shout.Shout()


        self.shout.host = config.JUKEBOX_SHOUT_HOST
        self.shout.port = config.JUKEBOX_SHOUT_PORT
        self.shout.user = config.JUKEBOX_SHOUT_USER
        self.shout.password = config.JUKEBOX_SHOUT_PASSWORD
        self.shout.mount = config.JUKEBOX_SHOUT_MOUNT
        self.shout.name =config.JUKEBOX_SHOUT_NAME
        self.shout.genre =config.JUKEBOX_SHOUT_GENRE
        self.shout.url = config.JUKEBOX_SHOUT_URL
        self.shout.public = config.JUKEBOX_SHOUT_PUBLIC

# self.shout.audio_info = { 'key': 'val', ... }
#  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
#   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)

        self.shout.format = 'mp3'
        self.shout.open()

    def close(self):
        self.shout.close()

    def _play_thread(self, filename):
        total = 0
        st = time.time()
        f = open(filename)
        self.shout.set_metadata({'song': filename})

        nbuf = f.read(4096)
        while 1:
            buf = nbuf
            nbuf = f.read(4096)
            total = total + len(buf)
            if len(buf) == 0:
                break
            self.shout.send(buf)
            self.shout.sync()
        f.close()
        
        et = time.time()
        br = total*0.008/(et-st)
        #print "Sent %d bytes in %d seconds (%f kbps)" % (total, et-st, br)
        self.playing = False

    def play(self, filename):
        self._thread = threading.Thread(target=self._play_thread, args=(filename,))
        self.playing = True
        self._thread.start()

    def is_playing(self):
        return self.playing

    def stop(self):
        self._process.terminate()
        self.playing = False
        self._process = None

if __name__ == "__main__":
    player = IcecastPlayer()
    player.play("test.mp3")
    while player.is_playing():
        print("Still playing...")
        time.sleep(4)
