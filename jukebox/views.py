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
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import FormView

from models import Folder, Song
from forms import ImportCollectionForm
import queue_player
from util import locate, import_collection

logger = logging.getLogger(__name__)

def index(request):
    context = {
        "stream_url": settings.JUKEBOX_STREAM_URL
    }
    return render(request, "jukebox/index.html", context)

def now_playing(request):
    now_playing,current_folder,current_song = queue_player.now_playing()
    context = {
        "now_playing": [model_to_dict(s) for s in now_playing],
        "current_folder": model_to_dict(current_folder) if current_folder is not None else None,
        "current_song": model_to_dict(current_song) if current_song is not None else None
    }
    #logger.info(u"index context: {}".format(context))
        
    return JsonResponse(context)

def json_queue(request):
    queue = Folder.objects.filter(selected=True).order_by('order')
    try:
        current_folder = Folder.objects.get(now_playing=True)
    except ObjectDoesNotExist:
        current_folder = None
    if queue_player.is_playing() and len(queue)>0 and current_folder == queue[0]:
        # Do not show currently playing folder in queue
        queue = queue[1:]
    queue_hash = hashlib.md5("".join([f.disk_path.encode('ascii','ignore') for f in queue])).hexdigest()
    context = {
        "queue": [model_to_dict(f) for f in queue],
        "hash": queue_hash
    }
        
    return JsonResponse(context)

def start(request):
    queue_player.start()
    return redirect("index")

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

def folder_subdirs(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    children = Folder.objects.filter(parent_id=folder_id).all()
    children = [model_to_dict(c) for c in children]
    #logger.info("Returning children: {}".format(children))
    return JsonResponse({"children":children})

def skip_current_folder(request):
    queue_player.skip_current_folder()
    return HttpResponse("OK")

def toggle_folder(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    #logger.info("Toggling folder {} ({})".format(folder.name, folder.id))
    folder.selected = folder.selectable and not folder.selected
    folder.save()

    return JsonResponse({"selected": folder.selected})

def move_folder_up(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    folder.up()

    return HttpResponse("OK")

def move_folder_down(request, folder_id):
    folder = Folder.objects.get(pk=folder_id)
    folder.down()

    return HttpResponse("OK")

def select_folders(request):
    roots = Folder.objects.filter(parent=None).all()
    context = {
            "roots": roots
            }
    return render(request, "jukebox/select_folders.html", context)

class ImportCollectionView(FormView):
    template_name = 'jukebox/import_collection.html'
    form_class = ImportCollectionForm
    success_url = '/jukebox/select_folders' # reverse('select_folders')

    def form_valid(self, form):
        root_dir = form.cleaned_data['root_dir']
        import_collection(root_dir)
        return super(ImportCollectionView,self).form_valid(form)


