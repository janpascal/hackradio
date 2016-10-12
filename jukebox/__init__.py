# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import logging
from threading import Thread
import time

logger =logging.getLogger(__name__)

def startup():
    def _thread_func():
        logger.info("Waiting 3 seconds before starting stream...")
        time.sleep(3)
        logger.info("Starting queue player...")
        import queue_player
        queue_player.start()

    thread = Thread(target=_thread_func)
    thread.start()
