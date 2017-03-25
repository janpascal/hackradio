# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

from concurrent import futures
import logging
import os.path
import pipes
import subprocess

from django.conf import settings

logger = logging.getLogger(__name__)

_pool = futures.ThreadPoolExecutor(max_workers=settings.JUKEBOX_CONVERT_CONCURRENCY)

# Maps Future to Song
_jobs = {}

def convert_flac_to_mp3(disk_path, cache_path):
    flac_quoted = pipes.quote(disk_path)
    mp3_quoted = pipes.quote(cache_path)

    commandline = "/usr/bin/flac --decode --stdout " + flac_quoted + " | /usr/bin/lame --preset extreme - " + mp3_quoted
    logger.info("Command line: {}".format(commandline))

    subprocess.call(commandline, shell=True)

def convert_ogg_to_mp3(oggfile, mp3file):
    ogg_quoted = pipes.quote(oggfile)
    mp3_quoted = pipes.quote(mp3file)
    commandline = "/usr/bin/oggdec " + ogg_quoted + " -o - | /usr/bin/lame --preset extreme - " + mp3_quoted
    logger.info("Command line: {}".format(commandline))

    subprocess.call(commandline, shell=True)

def convert_mpc_to_mp3(mpcfile, mp3file):
    mpc_quoted = pipes.quote(mpcfile)
    mp3_quoted = pipes.quote(mp3file)
    commandline = "/usr/bin/mpcdec " + mpc_quoted + " - | /usr/bin/lame --preset extreme - " + mp3_quoted
    logger.info("Command line: {}".format(commandline))

    subprocess.call(commandline, shell=True)

def convert_m4a_to_mp3(m4afile, mp3file):
    m4a_quoted = pipes.quote(m4afile)
    mp3_quoted = pipes.quote(mp3file)
    commandline = "/usr/bin/ffmpeg -i " + m4a_quoted + " " + mp3_quoted
    logger.info("Command line: {}".format(commandline))

    subprocess.call(commandline, shell=True)

def convert_song(song):
    disk_path = song.disk_path()
    _,extension = os.path.splitext(disk_path)
    logger.info("Converting song {}".format(disk_path))
    cache_path = os.path.join(settings.JUKEBOX_CACHE_DIR, disk_path.replace("/","_")) + "_"
    for i in xrange(65535):
        if not os.path.exists(cache_path + str(i) + ".mp3"):
            break
    cache_path = cache_path + str(i) + ".mp3"
    logger.info("Path for converted mp3: {}".format(cache_path))

    if extension == ".flac":
        convert_flac_to_mp3(disk_path, cache_path)
    elif extension == ".ogg":
        convert_ogg_to_mp3(disk_path, cache_path)
    elif extension == ".mpc":
        convert_mpc_to_mp3(disk_path, cache_path)
    elif extension == ".m4a":
        convert_m4a_to_mp3(disk_path, cache_path)
    else:
        logger.warning("Unable to convert files of this type: {}".format(disk_path))
        return
    song.converted_path = cache_path
    song.save()

def convert_done(future):
    global _jobs
    logger.info("Job done converting {}".format(_jobs[future].filename))
    del _jobs[future]

def queue_convert_song(song):
    global _pool
    global _jobs
    future = _pool.submit(convert_song, song)
    _jobs[future] = song
    future.add_done_callback(convert_done)

# folder should be a models.Folder
def queue_convert_folder(folder):
    for song in folder.songs.filter(convertable=True):
        if not song.converted_path or not os.path.exists(song.converted_path):
            queue_convert_song(song)
        else:
            logger.info("Song {} already converted".format(song.filename))

def get_running():
    return [ _jobs[future]  for future in _jobs if future.running() ]

def get_queued():
    return [ _jobs[future]  for future in _jobs if not future.running() and not future.done() ]
