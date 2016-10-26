from django import forms

class UploadArchiveForm(forms.Form):
    name = forms.CharField(max_length=50)
    file = forms.FileField()

