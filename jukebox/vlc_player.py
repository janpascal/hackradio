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
        #self.instance = vlc.Instance("--verbose 3 --rc-fake-tty")
        # rc-fake-tty option is necessary when running as a WSGI process
        self.instance = vlc.Instance("--rc-fake-tty")
        self.player = self.instance.media_player_new()
        self.stopped_event = threading.Event()
        self.logger = logging.getLogger(__name__)
        def end_callback(event):
            self.logger.info('End of media stream (event {})'.format(event.type))
            self.stopped_event.set()
        event_manager = self.player.event_manager()
        event_manager.event_attach(EventType.MediaPlayerEndReached, end_callback)
        event_manager.event_attach(EventType.MediaPlayerStopped, end_callback)

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
            self.logger.warning('%s: %s (%s %s vs LibVLC %s)' % (e.__class__.__name__, e,
                                                   sys.argv[0], __version__,
                                                   libvlc_get_version()))
            return

        self.player.set_media(media)
        self.stopped_event.clear()
        self.logger.info("Using VLC to play {}".format(filename))
        self.player.play()
        self.logger.info("Started play")

    def is_playing(self):
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

    def set_volume(self, volume):
        self.player.audio_set_volume(volume)

    def get_volume(self):
        return self.player.audio_get_volume()

    def needs_convert(self):
        return False

    def pause(self):
        self.player.set_pause(True)

    def resume(self):
        self.player.set_pause(False)
