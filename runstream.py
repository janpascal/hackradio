#!/usr/bin/env python2
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import os
import sys
import time
import logging

import django

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hackradio.settings")
    django.setup()

    from jukebox import queue_player
    queue_player.start()
