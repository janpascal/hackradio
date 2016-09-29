from __future__ import unicode_literals

import os.path

from django.db import models
from ordered_model.models import OrderedModel

class Album(OrderedModel):
    path = models.CharField("path", max_length=4096, unique=True)
    selected = models.BooleanField("selected", default=False)

    def __str__(self):
        return self.path

    class Meta:
        ordering = ["path"]

class Song(models.Model):
    #title = models.CharField(max_length=256)
    filename = models.CharField(max_length=256)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    def __str__(self):
        return os.path.join(self.album.path, self.filename)

    class Meta:
        unique_together = ("album", "filename")
        ordering = ["album", "filename"]

