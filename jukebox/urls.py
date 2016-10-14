# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'jukebox'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^now_playing$', views.now_playing, name='now_playing'),
    url(r'^import_collection$', views.import_collection, name='import_collection'),
    url(r'^json/queue$', views.json_queue, name='json_queue'),
    url(r'^json/roots$', views.json_roots, name='json_roots'),
    url(r'^song/(?P<song_id>[0-9]+)/skip$', views.skip_song, name="skip_song"),
    url(r'^song/(?P<song_id>[0-9]+)/reenable$', views.reenable_song, name="reenable_song"),
    url(r'^folder/(?P<folder_id>[0-9]*)/toggle$', views.toggle_folder, name='toggle_folder'),
    url(r'^folder/(?P<folder_id>[0-9]*)/movetop$', views.move_folder_top, name='move_folder_top'),
    url(r'^folder/(?P<folder_id>[0-9]*)/moveup$', views.move_folder_up, name='move_folder_up'),
    url(r'^folder/(?P<folder_id>[0-9]*)/movedown$', views.move_folder_down, name='move_folder_down'),
    url(r'^folder/(?P<folder_id>[0-9]*)/movebottom$', views.move_folder_bottom, name='move_folder_bottom'),
    url(r'^folder/(?P<folder_id>[0-9]*)/songs$', views.folder_songs, name='folder_songs'),
    url(r'^folder/skipcurrent$', views.skip_current_folder, name='skip_current_folder'),
    url(r'^subdirs/(?P<folder_id>[0-9]*)$', views.folder_subdirs, name="folder_subdirs"),
]

