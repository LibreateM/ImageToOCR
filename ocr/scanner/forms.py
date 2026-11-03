from django import forms
from django.conf import settings

from .models import Scan


class UploadForm(forms.Form):
    image = forms.ImageField()
    language = forms.ChoiceField(choices=Scan.LANG_CHOICES, initial="eng")
    mode = forms.ChoiceField(choices=Scan.MODE_CHOICES, initial="bw")

    def clean_image(self):
        f = self.cleaned_data["image"]
        if f.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
            raise forms.ValidationError(f"Max {settings.MAX_UPLOAD_MB} MB allowed.")
        return f
