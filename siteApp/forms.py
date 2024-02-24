from django import forms
from .models import SiteInfo

class UploadFileForm(forms.Form):
    project_name = forms.CharField(max_length=255, label='Project Name', required=True)
    file = forms.FileField()
    
    
