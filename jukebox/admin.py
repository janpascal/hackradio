from django.contrib import admin

# Register your models here.

from .models import Folder, Song

admin.site.register(Folder)
admin.site.register(Song)
