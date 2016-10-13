from __future__ import unicode_literals

import os.path

from django.conf import settings
from django.db import models
from ordered_model.models import OrderedModel

class Folder(OrderedModel):
    name = models.CharField("name", max_length=255)
    disk_path = models.CharField("disk_path", max_length=4096)
    parent = models.ForeignKey('self', null=True, related_name="children")
    selectable = models.BooleanField("selectable", default=False)
    selected = models.BooleanField("selected", default=False)
    now_playing = models.BooleanField(default=False)

    order_with_respect_to = ['selected']

    def __str__(self):
        return self.disk_path

    class Meta:
        ordering = ["parent__id", "name"]
        unique_together = ("parent", "name")

class Song(models.Model):
    filename = models.CharField(max_length=255)
    skipped = models.BooleanField(default=False)
    now_playing = models.BooleanField(default=False)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name="songs")
    convertable = models.BooleanField(default=False)
    converted_path = models.CharField(max_length=4096, default="")
    
    def disk_path(self):
        return os.path.join(self.folder.disk_path, self.filename)

    def mp3_path(self):
        if self.converted_path:
            return self.converted_path
        else:
            return os.path.join(self.folder.disk_path, self.filename)

    def __str__(self):
        return self.disk_path()


    class Meta:
        unique_together = ("folder", "filename")
        ordering = ["folder", "filename"]

