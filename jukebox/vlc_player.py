# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import logging
import sys
import string
import threading
import time

import vlc
from vlc import EventType

from django.conf import settings

class VLCPlayer:
    def __init__(self):
        #self.instance = vlc.Instance(["--sub-source=marq"])
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.stopped_event = threading.Event()
        self.logger = logging.getLogger(__name__)
        def end_callback(event):
            print('End of media stream (event %s)' % event.type)
            self.stopped_event.set()
        event_manager = self.player.event_manager()
        event_manager.event_attach(EventType.MediaPlayerEndReached, end_callback)

    def connect(self, force=False):
        pass

    def disconnect(self):
        pass

    def reconnect(self):
        pass

    def play(self, filename, display_name, quiet=False):
        try:
            media = self.instance.media_new(filename)
        except (AttributeError, NameError) as e:
            print('%s: %s (%s %s vs LibVLC %s)' % (e.__class__.__name__, e,
                                                   sys.argv[0], __version__,
                                                   libvlc_get_version()))
            return

        self.player.set_media(media)
        self.stopped_event.clear()
        self.logger.info("Using VLC to play {}".format(filename))
        self.player.play()
        self.logger.info("Started play")

    def is_playing(self):
        self.logger.info("VLC playing: {}".format(self.player.is_playing()))
        return self.player.is_playing()

    def wait_for_end(self, timeout):
        return self.stopped_event.wait(timeout)

    def stop(self):
        self.logger.info("Stopping vlc")
        self.player.stop()
        stopped = self.wait_for_end(30.0)
        if not stopped:
            self.logger.error("Did NOT receive message that thread actually stopped, will cause trouble later!")
        
        #self.stopped_event.set()
