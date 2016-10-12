# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-04 11:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jukebox', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='folder',
            options={'ordering': ['parent__id', 'name']},
        ),
        migrations.AddField(
            model_name='folder',
            name='now_playing',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='song',
            name='now_playing',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='song',
            name='folder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='songs', to='jukebox.Folder'),
        ),
    ]
