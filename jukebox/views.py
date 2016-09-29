# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from django.shortcuts import render
from django.views import generic
from django.views.generic.edit import FormView

from models import Album
from forms import ImportCollectionForm
import manage

# Create your views here.

def index(request):
    queue = Album.objects.all().order_by('order')
    current_album = queue[0]
    context = {
        "current_album": current_album,
        "queue": queue
    }
        
    return render(request, "jukebox/index.html", context)

def now_playing(request):
    pass
   
class ImportCollectionView(FormView):
    template_name = 'jukebox/import_collection.html'
    form_class = ImportCollectionForm
    success_url = "/"

    def form_valid(self, form):
        form.do_import()
        return super(ImportCollectionView,self).form_valid(form)


