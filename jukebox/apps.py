from __future__ import unicode_literals

import signal

from django.apps import AppConfig


class JukeboxConfig(AppConfig):
    name = 'jukebox'

    def ready(self):
        def _exit(signum, frame):
            import queue_player
            queue_player.stop()
            raise KeyboardInterrupt

        signal.signal(signal.SIGINT, _exit)
