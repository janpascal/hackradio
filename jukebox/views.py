# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import os
import os.path

from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic.edit import FormView

from models import Album, Song
from forms import ImportCollectionForm
import manage
import queue_player
from util import locate

# Create your views here.

def index(request):
    queue = Album.objects.filter(selected=True).order_by('order')
    current_album = queue[0]
    context = {
        "current_album": current_album,
        "queue": queue
    }
        
    return render(request, "jukebox/index.html", context)

def now_playing(request):
    pass

def start(request):
    queue_player.start()
    return redirect("index")

def skip_song(request, album_id, song_id):
    print("song_id, {}, {}".format(album_id, song_id))
    song = Song.objects.get(pk=song_id)
    print(u"Song: {}".format(song))
    if song.album.pk != int(album_id):
        print("Wrong album id: got {}, expected {}".format(album_id, song.album.pk))
    song.skipped = True
    song.save()

    return HttpResponse("OK")

def album_subdirs(request, root):
    children = []
    root_fullpath = os.path.normpath(os.path.join(settings.JUKEBOX_ROOT_DIR, root))
    if not root_fullpath.startswith(settings.JUKEBOX_ROOT_DIR):
        return HttpResponse(500)
    # [d in os.listdir(root) if os.path.isdir(os.path.join(root,d))]
    for d in os.listdir(root_fullpath):
        album_fullpath = os.path.join(root_fullpath,d)
        if os.path.isdir(album_fullpath):
            has_music_files = not list(locate("*.mp3", album_fullpath)).empty()
            child = {
                    "name": d,
                    "parent": root,
                    "id": album_fullpath,
                    "selected": Album.objects.filter(path=child_id).exists(),
                    "selectable": has_music_files
                    }
            children.append(child)

    return JsonResponse({"children":children})


def select_album(request, album_path):
    album_fullpath = os.path.normpath(os.path.join(settings.JUKEBOX_ROOT_DIR,
        album_path))
    if not album_fullpath.startswith(settings.JUKEBOX_ROOT_DIR):
        return HttpResponse(500)
    album,_ = Album.objects.get_or_create(path=album_path)
    album.selected=True
    album.save()
    song_files = [f for f in os.listdir(album_fullpath) if f.endswith('.mp3') ]
    songs = [Song(filename=f, album=album) for f in song_files]
    for song in songs:
        song.save()

    return HttpResponse("OK")


def select_albums(request):
    roots = []
    root = settings.JUKEBOX_ROOT_DIR
    for d in os.listdir(root):
        if os.path.isdir(os.path.join(root,d)):
            roots.append(d)
    context = {
            "roots": roots
            }
    return render(request, "jukebox/select_albums.html", context)

class ImportCollectionView(FormView):
    template_name = 'jukebox/import_collection.html'
    form_class = ImportCollectionForm
    success_url = "/"

    def form_valid(self, form):
        form.do_import()
        return super(ImportCollectionView,self).form_valid(form)


