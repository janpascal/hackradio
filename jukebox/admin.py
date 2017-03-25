from django.contrib import admin

# Register your models here.

from .models import Collection, Folder, Song

admin.site.register(Collection)
admin.site.register(Folder)
admin.site.register(Song)
