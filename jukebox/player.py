# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import logging
import threading
import time

from concurrent import futures

from django.conf import settings

class Player:

    PLAYER_NEEDS_CONVERT = 1
    PLAYER_SUPPORTS_PAUSE = 2
    PLAYER_SUPPORTS_VOLUME = 4
    PLAYER_HAS_PLAY_URL = 8

    flags = 0

    def __init__(self):
        self._stopped_event = threading.Event()
        self.logger = logging.getLogger(__name__)
        self._thread = None
        self.volume = 100

    def _fake_play(self):
        for t in range(0,300):
            if self.should_stop:
                break
            time.sleep(0.1)

        self._stopped_event.set()
        self._thread = None

    def play(self, filename, display_name):
        if self.is_playing():
            raise "Cannot start new stream, already playing"

        self._stopped_event.clear()
        self._thread = threading.Thread(target=self._fake_play)

    def is_playing(self):
        return self._thread is not None

    def wait_for_end(self, timeout=30.0):
        return self._stopped_event.wait(timeout)

    def stop(self):
        self.should_stop = True
        if not self.wait_for_end(30.0):
            self.logger.error("Did NOT receive message that thread actually stopped, will cause trouble later!")

    def set_volume(self, volume):
        self.volume = volume

    def get_volume(self):
        return self.volume

    def needs_convert(self):
        return False
