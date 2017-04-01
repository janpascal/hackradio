# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'jukebox'

urlpatterns = [
    url(r'^index.html$', views.index, name='index'),
    url(r'^queue.html$', views.queue, name='queue'),
    url(r'^select_folders.html$', views.select_folders, name='select_folders'),
    url(r'^collections.html$', views.collections_page, name='collections'),
    url(r'^upload.html$', views.upload_page, name='upload'),

    # Data requests
    url(r'^json/now_playing$', views.now_playing, name='now_playing'),
    url(r'^json/queue$', views.json_queue, name='json_queue'),
    url(r'^json/roots$', views.json_roots, name='json_roots'),
    url(r'^json/convert_status$', views.convert_status, name='convert_status'),
    url(r'^json/import_status$', views.import_status, name='import_status'),
    url(r'^json/upload_status$', views.upload_status, name='upload_status'),
    url(r'^folder/(?P<folder_id>[0-9]*)/songs$', views.folder_songs, name='folder_songs'),
    url(r'^folder/search$', views.search_folder, name='search_folder'),
    url(r'^subdirs/(?P<folder_id>[0-9]*)$', views.folder_subdirs, name="folder_subdirs"),
    url(r'^volume/get$', views.get_volume, name="get_volume"),
    url(r'^is_playing$', views.is_playing, name="is_playing"),

    # Actions
    url(r'^import_collection$', views.import_collection, name='import_collection'),
    url(r'^collection/(?P<collection_id>[0-9]+)/refresh$', views.refresh_collection, name='refresh_collection'),
    url(r'^collection/(?P<collection_id>[0-9]+)/delete$', views.delete_collection, name='delete_collection'),
    url(r'^queue/set$', views.set_queue, name='set_queue'),
    url(r'^song/(?P<song_id>[0-9]+)/skip$', views.skip_song, name="skip_song"),
    url(r'^song/(?P<song_id>[0-9]+)/reenable$', views.reenable_song, name="reenable_song"),
    url(r'^folder/(?P<folder_id>[0-9]*)/toggle$', views.toggle_folder, name='toggle_folder'),
    url(r'^folder/(?P<folder_id>[0-9]*)/select$', views.select_folder, name='select_folder'),
    url(r'^folder/(?P<folder_id>[0-9]*)/deselect$', views.deselect_folder, name='deselect_folder'),
    url(r'^folder/(?P<folder_id>[0-9]*)/move/(?P<new_parent_id>[0-9]*)/(?P<new_position>[0-9]*)$', views.move_folder, name='move_folder'),
    url(r'^folder/(?P<folder_id>[0-9]*)/movetop$', views.move_folder_top, name='move_folder_top'),
    url(r'^folder/(?P<folder_id>[0-9]*)/moveup$', views.move_folder_up, name='move_folder_up'),
    url(r'^folder/(?P<folder_id>[0-9]*)/movedown$', views.move_folder_down, name='move_folder_down'),
    url(r'^folder/(?P<folder_id>[0-9]*)/movebottom$', views.move_folder_bottom, name='move_folder_bottom'),
    url(r'^folder/(?P<folder_id>[0-9]*)/rename$', views.rename_folder, name='rename_folder'),
    url(r'^folder/(?P<folder_id>[0-9]*)/delete$', views.delete_folder, name='delete_folder'),
    url(r'^folder/(?P<parent_id>[0-9]*)/create_subfolder$', views.create_subfolder, name='create_folder'),
    url(r'^folder/skipcurrent$', views.skip_current_folder, name='skip_current_folder'),
    url(r'^volume/set/(?P<volume>[0-9]+)$', views.set_volume, name="set_volume"),
    url(r'^pause$', views.pause, name="pause"),
    url(r'^resume$', views.resume, name="resume"),
]

