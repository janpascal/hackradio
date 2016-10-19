# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import hashlib
import logging
import os
import os.path

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from models import Folder, Song
import queue_player
import util
import converter

logger = logging.getLogger(__name__)

# HTML pages

def index(request):
    context = {
        "page_id": "index",
        "stream_url": settings.JUKEBOX_STREAM_URL
    }
    return render(request, "jukebox/index.html", context)

def queue(request):
    context = {
        "page_id": "queue",
        "stream_url": settings.JUKEBOX_STREAM_URL
    }
    return render(request, "jukebox/queue.html", context)

def select_folders(request):
    context = {
        "page_id": "select_folders",
        "stream_url": settings.JUKEBOX_STREAM_URL
    }
    return render(request, "jukebox/select_folders.html", context)

def import_page(request):
    context = {
        "page_id": "import",
        "stream_url": settings.JUKEBOX_STREAM_URL
    }
    return render(request, "jukebox/import.html", context)

# JSON data requests

def now_playing(request):
    now_playing,current_folder,current_song = queue_player.now_playing()
    context = {
        "now_playing": [model_to_dict(s) for s in now_playing],
        "current_folder": model_to_dict(current_folder) if current_folder is not None else None,
        "current_song": model_to_dict(current_song) if current_song is not None else None
    }
    #logger.info(u"now_playing context: {}".format(context))
        
    return JsonResponse(context)

def json_queue(request):
    queue = list(Folder.objects.filter(selected=True).order_by('order'))
    try:
        current_folder = Folder.objects.get(now_playing=True)
    except ObjectDoesNotExist:
        current_folder = None
    queue.remove(current_folder)
    queue_hash = hashlib.md5("".join([f.disk_path.encode('ascii','ignore') for f in queue])).hexdigest()
    context = {
        "current": model_to_dict(current_folder),
        "queue": [model_to_dict(f) for f in queue],
        "hash": queue_hash
    }
        
    return JsonResponse(context)

def json_roots(request):
    roots = Folder.objects.filter(parent=None)
    dict_roots = []
    for r in roots:
        d = model_to_dict(r)
        d["has_children"] = r.children.exists()
        dict_roots.append(d)

    context = {
        "roots": dict_roots,
    }
        
    return JsonResponse(context)

def folder_subdirs(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    children = Folder.objects.filter(parent_id=folder_id).all()
    #children = [model_to_dict(c) for c in children]
    dict_children = []
    for c in children:
        d = model_to_dict(c)
        d["has_children"] = c.children.exists()
        dict_children.append(d)
    #logger.info("Returning children: {}".format(dict_children))
    return JsonResponse({"children":dict_children})

def convert_status(request):
    running = converter.get_running();
    queued = converter.get_queued();
    result = {
        "running": [model_to_dict(s) for s in running],
        "queued": [model_to_dict(s) for s in queued]
    }
    return JsonResponse(result);

def import_status(request):
    result = {
        "current_import_dir": util.current_import_dir(),
    }
    logger.info("Returning import status: {}".format(result))
    return JsonResponse(result);

def folder_songs(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    songs = folder.songs.all()
    response  = {
        "songs": [model_to_dict(s) for s in songs],
    }
    return JsonResponse(response)

# Actions

def skip_song(request, song_id):
    song = Song.objects.get(pk=song_id)
    song.skipped = True
    song.save()

    return HttpResponse("OK")

def reenable_song(request, song_id):
    song = Song.objects.get(pk=song_id)
    song.skipped = False
    song.save()

    return HttpResponse("OK")

def skip_current_folder(request):
    queue_player.skip_current_folder()
    return HttpResponse("OK")

def toggle_folder(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    #logger.info("Toggling folder {} ({})".format(folder.name, folder.id))
    folder.selected = folder.selectable and not folder.selected
    converting = False
    if folder.selected:
        folder.bottom()
        converter.queue_convert_folder(folder)
        converting = bool(converter.get_running()) or bool(converter.get_queued())
    folder.save()

    return JsonResponse({"selected": folder.selected, "converting": converting})

def move_folder_top(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    folder.top()

    return HttpResponse("OK")

def move_folder_up(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    folder.up()

    return HttpResponse("OK")

def move_folder_down(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    folder.down()

    return HttpResponse("OK")

def move_folder_bottom(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    folder.bottom()

    return HttpResponse("OK")

def import_collection(request):
    root_dir = request.POST['root_dir']
    logger.info("Importing collection from {}".format(root_dir))
    util.import_collection(root_dir)
    return HttpResponse("OK")

