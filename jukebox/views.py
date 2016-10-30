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
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from models import Folder, Song
import queue_player
import util
import converter
from forms import UploadArchiveForm

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

def upload_page(request):
    if request.method == 'POST':
        form = UploadArchiveForm(request.POST, request.FILES)
        if form.is_valid():
            name = request.POST['name']
            logger.info("File uploaded: {} ({})".format(name, request.FILES['file']))
            util.import_ziparchive(name, request.FILES['file'])
            return HttpResponseRedirect(reverse('jukebox:select_folders'))
        else:
            logger.warning("Form not valid...")
            logger.info("File data: {}".format(request.FILES))
    else:
        form = UploadArchiveForm()

    context = {
        "page_id": "upload",
        "stream_url": settings.JUKEBOX_STREAM_URL,
        'form': form
    }
    return render(request, "jukebox/upload.html", context)

# JSON data requests

def now_playing(request):
    now_playing,current_folder,current_song = queue_player.now_playing()
    context = {
        "now_playing": [model_to_dict(s) for s in now_playing],
        "current_folder_id": current_folder.id if current_folder is not None else None,
        "current_folder_path": current_folder.tree_path() if current_folder is not None else None,
        "current_song": model_to_dict(current_song) if current_song is not None else None
    }
    #logger.info(u"now_playing context: {}".format(context))
        
    return JsonResponse(context)

def json_queue(request):
    queue = list(Folder.objects.filter(selected=True).order_by('order'))
    try:
        current_folder = Folder.objects.get(now_playing=True)
        queue.remove(current_folder)
    except ObjectDoesNotExist:
        current_folder = None
    queue_hash = hashlib.md5("".join([f.disk_path.encode('ascii','ignore') for f in queue])).hexdigest()

    if current_folder is None:
        dict_current = None
    else:
        dict_current = model_to_dict(current_folder)
        dict_current["path"] = current_folder.tree_path()

    def flatten(f):
        dict_f = model_to_dict(f)
        dict_f["path"] = f.tree_path()
        return dict_f
    dict_queue = [ flatten(f) for f in queue ]

        # model_to_dict(f) for f in queue
    context = {
        "current": dict_current,
        "queue": dict_queue, #[model_to_dict(f) for f in queue],
        "hash": queue_hash
    }
    #logger.info(u"json_queue context: {}".format(context))
        
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

def search_folder(request):
    """ Actually return a list of the nodes that need to be opened to
    reveal the nodes searched for """
    str = request.GET['str']
    context_id = request.GET['context']

    #logger.info("Search string: {}; context node id: {}".format(str, context_id))

    ids = reduce(
        lambda a,b: a + b,
        [folder.parent_ids() for folder in Folder.objects.filter(name__icontains=str)],
        []
    )

    response = {
        "matching_ids": ids
    }

    logger.info("Returning search result: {}".format(response))

    return JsonResponse(response)


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
    #logger.info("Returning import status: {}".format(result))
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

def select_folder(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    logger.info("Selecting folder {} ({})".format(folder.name, folder.id))
    
    if not folder.selectable:
        logger.warning("Folder {} not selectable, not selecting!".format(folder.name))
        return JsonResponse({"selected": False, "converting": False})

    folder.selected = True
    folder.save()
    folder.bottom()
    converter.queue_convert_folder(folder)
    converting = bool(converter.get_running()) or bool(converter.get_queued())

    return JsonResponse({"selected": True, "converting": converting})

def deselect_folder(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    #logger.info("Disabling folder {} ({})".format(folder.name, folder.id))
    folder.selected = False
    folder.bottom()
    folder.save()

    return JsonResponse({"selected": False, "converting": False})

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

def move_folder(request, folder_id, new_parent_id, new_position):
    folder = Folder.objects.get(pk=folder_id)
    #    old_parent = Folder.objects.get(pk=old_parent_id)
    new_parent = Folder.objects.get(pk=new_parent_id)
    #logger.info("Moving folder {} from parent {} position {} to parent {} pos
    #        {}".format(folder.name, old_parent, old_position, new_parent, new_position))
    logger.info("Moving folder {} to parent {} pos {}".format(folder.name,new_parent.name, new_position))
    folder.parent = new_parent
    folder.save()
    #folder.move(int(old_position), int(new_position))

    return HttpResponse("OK")

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

def rename_folder(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    name = request.POST['name']

    logger.info("Renaming folder {} to {}".format(folder.name, name))
    folder.name = name
    folder.save()

    return HttpResponse("OK")

def delete_folder(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)

    logger.info("Deleting folder {}".format(folder.name))
    # Automatically also deletes subfolders, but not the files
    #logger.warning("Warning: subfolder of {} (id: {}) not yet deleted, neither are the songs and the files on disk!".format(folder.name, folder.id))
    folder.delete()

    return HttpResponse("OK")

# TODO delete all subfolders, and items on disk

    return HttpResponse("OK")

def set_queue(request):
    queue = request.POST.getlist('queue[]')
    queue = [int(i) for i in queue]
    logger.info("Set queue order: {}".format(queue))

    Folder.objects.set_queue(queue)

    return HttpResponse("OK")

def import_collection(request):
    root_dir = request.POST['root_dir']
    logger.info("Importing collection from {}".format(root_dir))
    util.import_collection(root_dir)
    return HttpResponse("OK")

