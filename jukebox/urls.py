# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

from django.conf.urls import url

from . import views

app_name = 'jukebox'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^now_playing$', views.now_playing, name='now_playing'),
    url(r'^import_collection$', views.ImportCollectionView.as_view(), name='import_collection'),
    url(r'^select_folders$', views.select_folders, name='select_folders'),
    url(r'^now_playing$', views.now_playing, name='now_playing'),
    url(r'^json/queue$', views.json_queue, name='json_queue'),
    url(r'^song/(?P<song_id>[0-9]+)/skip$', views.skip_song, name="skip_song"),
    url(r'^song/(?P<song_id>[0-9]+)/reenable$', views.reenable_song, name="reenable_song"),
    url(r'^folder/(?P<folder_id>[0-9]*)/toggle$', views.toggle_folder, name='toggle_folder'),
    url(r'^folder/(?P<folder_id>[0-9]*)/moveup$', views.move_folder_up, name='move_folder_up'),
    url(r'^folder/(?P<folder_id>[0-9]*)/movedown$', views.move_folder_down, name='move_folder_down'),
    url(r'^folder/skipcurrent$', views.skip_current_folder, name='skip_current_folder'),
    url(r'^subdirs/(?P<folder_id>[0-9]*)$', views.folder_subdirs, name="folder_subdirs"),
    #url(r'^tweet/job/create$', views.create_job, name='create_job'),
    #url(r'^job/create$', views.create_job, name='create_job'),
    #url(r'^job/list$', views.list_jobs, name='list_jobs'),
    #url(r'^job/(?P<job_id>[0-9]+)/delete$', views.delete_job, name='delete_job'),
    #url(r'^job/(?P<job_id>[0-9]+)/download/excel/(?P<excel>.*)$', views.download_excel, name='download_excel'),
    #url(r'^job/(?P<job_id>[0-9]+)/zip$', views.download_zip, name='download_zip'),
    #url(r'^job/(?P<job_id>[0-9]+)/config$', views.download_config, name='download_config'),
    #url(r'^job/(?P<job_id>[0-9]+)/log$', views.download_log, name='download_log'),
    #url(r'^job/(?P<job_id>[0-9]+)/status$', views.job_status, name='job_status'),
    #url(r'^stream/list$', views.list_stream, name='list_stream'),
    #url(r'^stream/edit_terms$', views.edit_stream_terms, name='edit_stream_terms'),
    #url(r'^stream/download$', views.download_stream, name='download_stream'),
    #url(r'^stream/export$', views.export_stream, name='export_stream'),
    #url(r'^stream/export/progress$', views.export_stream_progress, name='export_stream_progress'),
    #url(r'^stream/(?P<tweet_id>[0-9]+)/delete$', views.delete_tweet, name='delete_tweet')
]

