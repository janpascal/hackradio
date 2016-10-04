# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from __future__ import unicode_literals

import os
import os.path

from django import forms

class ImportCollectionForm(forms.Form):
    root_dir = forms.CharField(label='Collection root directory', max_length=4096)

