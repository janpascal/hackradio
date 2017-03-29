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

from player import Player


BITRATE="160k"

class PlayerThread(threading.Thread):
    def __init__(self):
        super(PlayerThread, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating PlayerThread")
        self.play_q = Queue()
        self.is_playing = False
        self.connected = False
        self.pause_request = threading.Event()
        self.stop_request = threading.Event()
        # shutdown_request always implies stop_request
        # Always set stop_request when shutdown_request is set!
        self.shutdown_request = threading.Event()

        #self.silence_path = os.path.join(settings.MEDIA_ROOT, "silence_1s.mp3")
        self.silence_path = os.path.join(settings.MEDIA_ROOT, "small_silence.mp3")
        self.mp3_silence = open(self.silence_path).read()
    
        self.shout = shout.Shout()
        self.shout.host = settings.JUKEBOX_SHOUT_HOST
        self.shout.port = settings.JUKEBOX_SHOUT_PORT
        self.shout.user = settings.JUKEBOX_SHOUT_USER
        self.shout.password = settings.JUKEBOX_SHOUT_PASSWORD
        self.shout.mount = settings.JUKEBOX_SHOUT_MOUNT
        self.shout.name = settings.JUKEBOX_SHOUT_NAME
        self.shout.genre = settings.JUKEBOX_SHOUT_GENRE
        self.shout.url = settings.JUKEBOX_SHOUT_URL
        self.shout.public = settings.JUKEBOX_SHOUT_PUBLIC
# self.shout.audio_info = { 'key': 'val', ... }
#  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
#   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)
        self.shout.format = b"mp3"


    # Interface from other threads

    def join(self, timeout=None):
        self.stop_request.set()
        self.shutdown_request.set()
        super(PlayerThread, self).join(timeout)

    def play(self, filename, display_name):
        self.stop_request.clear()
        self.pause_request.clear()
        self.logger.info("Putting {} into the queue".format(filename))
        self.play_q.put((filename,display_name))

        start_time = time.clock()
        while not self.is_playing and time.clock()-start_time < 10:
            time.sleep(0.05)
        if not self.is_playing:
            self.logger.info("Failed to start playing {}".format(filename))

    def pause(self):
        self.pause_request.set()

    def resume(self):
        self.pause_request.clear()

    def stop(self):
        self.logger.info("PlayerThread.stop()")
        self.stop_request.set()

    # Main thread functions

    def run(self):
        self.logger.info("In PlayerThread.run()!")
        self.connect()
        while not self.shutdown_request.is_set():
            while not self.shutdown_request.is_set() and (self.play_q.empty() or self.pause_request.is_set() or self.stop_request.is_set()):
                self.is_playing = False
                self._play_file(self.silence_path, "Nothing here at the moment", 
                    quiet=True, pausing=True)
            try:
                filename,display_name = self.play_q.get_nowait()
                self.logger.info("Fetched {} from queue".format(filename))
                self.is_playing = True
                self._play_file(filename, display_name)
            except Queue.Empty:
                pass

        self.is_playing = False
        self.disconnect()

        self.logger.info("Finished PlayerThread.run()")


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

    # Play file until it it finished
    # Stop (and return) when stop_request or shutdown_request is set
    # If not pausing, pause while pause_request is set
    
    def _play_file(self, filename, display_name, quiet=False, pausing=False):
        total = 0
        st = time.time()
        if not quiet:
            self.logger.info("Playing {} to icecast server {}:{}".format(filename, self.shout.host, self.shout.port))
        try:
            f = open(filename)

            self.shout.set_metadata({b'song': display_name.encode('utf-8', 'ignore')})

            nbuf = f.read(4096)
            while not self.stop_request.is_set():
                buf = nbuf
                nbuf = f.read(4096)
                total = total + len(buf)
                if len(buf) == 0:
                    break
                #if not quiet:
                #    self.logger.info("Playing {} bytes from {}".format(len(buf), filename))
                self.shout.send(buf)
                self.shout.sync()

                if not pausing and self.pause_request.is_set():
                    self.shout.set_metadata({b'song': "Pause ({})".format(display_name).encode('utf-8', 'ignore')})
                    while self.pause_request.is_set():
                        self.shout.send(self.mp3_silence)
                        self.shout.sync()
                    self.shout.set_metadata({b'song': display_name.encode('utf-8', 'ignore')})

            if self.stop_request.is_set():
                delay = self.shout.delay()
                if delay > 0:
                    if not quiet:
                        self.logger.info("Delaying for {} milleseconds before starting next stream".format(delay))
                    time.sleep(delay / 1000.0)
                self.stop_request.clear()

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

        if not quiet:
            self.logger.info("Finished PlayerThread._play_file({})".format(filename))

class IcecastPlayer:
    flags = Player.PLAYER_NEEDS_CONVERT | Player.PLAYER_HAS_PLAY_URL | Player.PLAYER_SUPPORTS_PAUSE

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._thread = PlayerThread()
        self._thread.start()

    def play(self, filename, display_name):
        if self.is_playing():
            raise "Cannot start new stream, already playing"

        self._thread.play(filename, display_name)


    def is_playing(self):
        return self._thread.is_playing

    def wait_for_end(self, timeout):
        start_time = time.clock()
        while self.is_playing() and time.clock()-start_time < timeout:
            time.sleep(0.05)
        if not self.is_playing():
            self.logger.info("End reached in {} seconds".format(time.clock() - start_time))
        return not self.is_playing()

    def stop(self):
        self.logger.info("IcecastPlayer.stop()")
        self._thread.stop()
        self.wait_for_end(30.0)
        if self.is_playing():
            self.logger.error("Did NOT receive message that thread actually stopped, will cause trouble later!")

    def shutdown(self):
        self._thread.join()

    def set_volume(self, volume):
        pass

    def get_volume(self):
        return 100

    def pause(self):
        self._thread.pause()

    def resume(self):
        self._thread.resume()

