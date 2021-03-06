# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-14 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jukebox', '0003_auto_20161014_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='now_playing',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='folder',
            name='order',
            field=models.IntegerField(db_index=True, default=0, verbose_name='order'),
        ),
        migrations.AlterIndexTogether(
            name='folder',
            index_together=set([('selected', 'order')]),
        ),
    ]
