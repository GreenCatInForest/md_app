from django.contrib import admin
from django.db import models

from core.models import Downloads, Report

# Register your models here.

class DownloadsAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'file']
    list_display = ['name', 'description', 'file']
    search_fields = ['name']

class ReportAdmin(admin.ModelAdmin):
    fields = ['user', 'start_time', 'end_time', 'report_timestamp', 'property_address',
              'external_logger', 'company', 'surveyor', 'report_file']
    list_display = ['user', 'company', 'surveyor', 'property_address', 'start_time', 'end_time', 'report_timestamp',
              'external_logger', 'report_file']
    search_fields = ['user', 'start_time', 'end_time', 'report_timestamp', 'property_address',
              'external_logger', 'company', 'surveyor', 'report_file']

admin.site.register(Downloads, DownloadsAdmin)
admin.site.register(Report, ReportAdmin)