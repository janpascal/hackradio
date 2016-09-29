# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os
import os.path

from django import forms

from .models import Album, Song

class ImportCollectionForm(forms.Form):
    root_dir = forms.CharField(label='Collection root directory', max_length=4096)

    def do_import(self):
        root_dir = self.cleaned_data['root_dir']
        for root, dirs, files in os.walk(root_dir, followlinks = True):
            songs = sorted([f for f in files if f.endswith(".mp3")])
            if songs:
                album,_ = Album.objects.get_or_create(path=root)
                album.save()
                for f in songs:
                    song,_ = Song.objects.get_or_create(filename=f, album=album)
                    song.save()

