from __future__ import unicode_literals

import os.path

from django.conf import settings
from django.db import models
from django.db.models import Min, Max

class Folder(models.Model):
    name = models.CharField("name", max_length=255)
    disk_path = models.CharField("disk_path", max_length=4096)
    parent = models.ForeignKey('self', null=True, related_name="children")
    selectable = models.BooleanField("selectable", default=False)
    selected = models.BooleanField("selected", default=False)
    now_playing = models.BooleanField(default=False, db_index=True)
    order = models.IntegerField("order", default=0, db_index=True)

    def __str__(self):
        return self.disk_path

    def swap(self, target):
        target_order = target.order
        target.order = self.order
        self.order = target_order
        target.save()
        self.save()

    def top(self):
        smallest_order = Folder.objects.aggregate(Min('order'))["order__min"]
        self.order = smallest_order - 1
        self.save()

    def up(self):
        target = Folder.objects.filter(selected=True, order__lt=self.order).order_by("-order").first()
        self.swap(target)

    def down(self):
        target = Folder.objects.filter(selected=True, order__gt=self.order).order_by("order").first()
        self.swap(target)

    def bottom(self):
        largest_order = Folder.objects.aggregate(Max('order'))["order__max"]
        self.order = largest_order + 1
        self.save()

    class Meta:
        ordering = ["parent__id", "name"]
        unique_together = ("parent", "name")
        index_together = [
            ["selected", "order"],
        ]


class Song(models.Model):
    filename = models.CharField(max_length=255)
    skipped = models.BooleanField(default=False)
    now_playing = models.BooleanField(default=False)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name="songs", db_index=True)
    convertable = models.BooleanField(default=False)
    converted_path = models.CharField(max_length=4096, default="")
    
    def disk_path(self):
        return os.path.join(self.folder.disk_path, self.filename)

    def mp3_path(self):
        if self.converted_path:
            return self.converted_path
        else:
            return os.path.join(self.folder.disk_path, self.filename)

    def conversion_done(self):
        return bool(self.converted_path)

    def __str__(self):
        return self.disk_path()


    class Meta:
        unique_together = ("folder", "filename")
        ordering = ["folder", "filename"]

