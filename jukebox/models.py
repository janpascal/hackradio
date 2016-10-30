from __future__ import unicode_literals

import os.path

from django.conf import settings
from django.db import models, transaction
from django.db.models import Min, Max

class FolderManager(models.Manager):

    def set_queue(self, queue):
        """ queue should be an array of folder ids """
        with transaction.atomic():
            Folder.objects.filter(now_playing=True).update(order=0)
            for index,folder_id in enumerate(queue):
                Folder.objects.filter(pk=folder_id).update(order=index+1)

class Folder(models.Model):
    name = models.CharField("name", max_length=255)
    disk_path = models.CharField("disk_path", max_length=4096)
    parent = models.ForeignKey('self', null=True, related_name="children")
    selectable = models.BooleanField("selectable", default=False)
    selected = models.BooleanField("selected", default=False)
    now_playing = models.BooleanField(default=False, db_index=True)
    order = models.IntegerField("order", default=0, db_index=True)

    objects = FolderManager()

    def __str__(self):
        return self.disk_path

    def parents(self):
        """ returns a list of the parents of this folder, up to the root,
        including this folder itself """
        if self.parent is None:
            return [self]
        return self.parent.parents() + [self]

    def parent_ids(self):
        """ returns a list of the ids of the parents of this folder, up to the root """
        return [ p.id for p in self.parents() ]

    def tree_path(self):
        """ returns a list of the ids of the parents of this folder, up to the root """
        return reduce(
            lambda path,folder: path + "/" + folder.name,
            self.parents(),
            ""
        )

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
        target = Folder.objects.filter(selected=True, now_playing=False, order__lt=self.order).order_by("-order").first()
        self.swap(target)

    def down(self):
        target = Folder.objects.filter(selected=True, now_playing=False, order__gt=self.order).order_by("order").first()
        self.swap(target)

    def bottom(self):
        largest_order = Folder.objects.aggregate(Max('order'))["order__max"]
        self.order = largest_order + 1
        self.save()

    def move(self, old_position, new_position):
        # ids of queues folders, in order
        queue = list(Folder.objects.filter(selected=True, now_playing=False).order_by("order"))
        if new_position == old_position:
            return 
        if new_position < old_position:
            # Move up
            # move all folders from new_position to old_position one down
            new_order = queue[new_position].order
            for index in range(new_position, old_position):
                folder = queue[index]
                last = folder.order
                folder.order += 1
                folder.save()
            self.order = new_order
            self.save()
        else:
            # Move down
            # move all folder from old_position to new_position one up
            new_order = queue[new_position].order
            for index in range(old_position+1, new_position+1):
                folder = queue[index]
                folder.order -= 1
                folder.save()
            self.order = new_order
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

