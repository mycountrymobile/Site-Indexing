from django.http import HttpResponse
import csv
from django.contrib import admin
from .models import SiteInfo

@admin.register(SiteInfo)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('get_project_name', 'url', 'is_indexed')
    search_fields = ('url',)
    list_filter = ('is_indexed', 'project__name')

    def get_project_name(self, obj):
        return obj.project.name if obj.project else ''

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


