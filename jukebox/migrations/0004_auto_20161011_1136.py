# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-11 11:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jukebox', '0003_folder_selectable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='disk_path',
            field=models.CharField(max_length=4096, verbose_name='disk_path'),
        ),
    ]
