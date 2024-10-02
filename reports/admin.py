from django.contrib import admin
from django.db import models

from core.models import Downloads

# Register your models here.

class DownloadsAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'file']
    list_display = ['name', 'description', 'file']
    search_fields = ['name']

admin.site.register(Downloads, DownloadsAdmin)