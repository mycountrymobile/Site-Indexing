# urls.py
from django.urls import path
from .views import upload_file, success,view,download_data

urlpatterns = [
    path('', upload_file, name='upload'),
    path('success/', success, name='success'),
    path('view/', view, name='view'),
    path('download_data/', download_data, name='download_data'),

]
