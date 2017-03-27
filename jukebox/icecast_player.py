# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import logging
import os.path
from Queue import Queue
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
        self.connected = False
        self.should_stop = False
        self.stopped_event = threading.Event()
        self._thread = None
        self.logger = logging.getLogger(__name__)

        self.silence_path = os.path.join(settings.MEDIA_ROOT, "silence_1s.mp3")
    
        self.shout = shout.Shout()
        self.shout.host = settings.JUKEBOX_SHOUT_HOST
        self.shout.port = settings.JUKEBOX_SHOUT_PORT
        self.shout.user = settings.JUKEBOX_SHOUT_USER
        self.shout.password = settings.JUKEBOX_SHOUT_PASSWORD
        self.shout.mount = settings.JUKEBOX_SHOUT_MOUNT
        self.shout.name =settings.JUKEBOX_SHOUT_NAME
        self.shout.genre =settings.JUKEBOX_SHOUT_GENRE
        self.shout.url = settings.JUKEBOX_SHOUT_URL
        self.shout.public = settings.JUKEBOX_SHOUT_PUBLIC

        self._thread = threading.Thread(target=self._play_thread)

        self._queue = Queue()
    
# self.shout.audio_info = { 'key': 'val', ... }
#  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
#   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)

        self.shout.format = b"mp3"

    def connect(self, force=False):
        if force or not self.connected or self.shout.get_connected() != shout.SHOUTERR_CONNECTED:
            self.logger.info("Trying to connect to server at {}:{}".format(self.shout.host, self.shout.port))
            try:
                self.shout.open()
                self.connected = True
            except Exception as e:
                self.logger.warning(e)
                return False
        return True

    def disconnect(self):
        if self.connected and self.shout.get_connected() == shout.SHOUTERR_CONNECTED:
            try:
                self.shout.close()
            except Exception as e:
                self.logger.warning(e)
        self.connected = False

    def reconnect(self):
        self.disconnect()
        self.connect(True)

    def _play_file(self, filename, display_name, quiet=False):
        total = 0
        st = time.time()
        if not quiet:
            self.logger.info("Playing {} to icecast server {}:{}".format(filename, self.shout.host, self.shout.port))
        try:
            f = open(filename)

            self.shout.set_metadata({b'song': display_name.encode('utf-8', 'ignore')})

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
                    if not quiet:
                        self.logger.info("Delaying for {} milleseconds before starting next stream".format(delay))
                    time.sleep(delay / 1000.0)

            f.close()
            
            if not quiet:
                et = time.time()
                br = total*0.008/(et-st)
                self.logger.info("Sent {} bytes in {} seconds ({} kbps)".format(total, et-st, br))
        except ShoutException as e:
            self.logger.warning(e)
            self.logger.warning("Exception during play (see above), sleeping for one second")
            self.logger.warning("shout.get_connected(): {}".format(self.shout.get_connected()))
            time.sleep(1.0)
            self.reconnect()

        if not self.quiet:
            self.logger.info("Finished player._play_file()")

    def _play_thread(self):
        self.connect() 

        while True:
            while not self.should_stop:
                time.sleep(0.1)

        self.disconnect()
        self._thread = None
        self.stopped_event.set()

        self.logger.info("Finished player._play_thread()")

    def _fake_play_thread(self, filename, display_name):
        time.sleep(30)
        self.stopped_event.set()

    def play(self, filename, display_name):
        if self.is_playing():
            raise "Cannot start new stream, already playing"

        #self._thread = threading.Thread(target=self._fake_play_thread, args=(filename,))
        #self._thread = threading.Thread(target=self._play_thread, args=(filename, display_name))
        self.idle = True
        self.should_stop = False
        self.stopped_event.clear()
        self._thread.start()

    def _play_silence(self):
        self.play(self.silence_path, "Nothing here at the moment", quiet=True)
        while not self.wait_for_end(0.1):
            if self.should_stop:
                self.stop()
                break

    def is_playing(self):
        return self.playing

    def wait_for_end(self, timeout):
        return self.stopped_event.wait(timeout)

    def stop(self):
        self.should_stop = True
        self.logger.info("Send player thread signal to stop, waiting at most 30 seconds for it to actually stop...")
        stopped = self.stopped_event.wait(30.0)
        if not stopped:
            self.logger.error("Did NOT receive message that thread actually stopped, will cause trouble later!")

    def set_volume(self, volume):
        pass

    def get_volume(self):
        return 100

    def needs_convert(self):
        return True
