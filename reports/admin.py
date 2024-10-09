from django.contrib import admin
from django.db import models

from core.models import Downloads, Report, Payment

# Register your models here.

class DownloadsAdmin(admin.ModelAdmin):
    fields = ['name', 'description', 'file']
    list_display = ['name', 'description', 'file']
    search_fields = ['name']

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_status', 'amount', 'currency', 'created_at', 'updated_at')
    can_delete = False
    show_change_link = True  # Allows admin to navigate to the Payment detail page

class ReportAdmin(admin.ModelAdmin):
    fields = ['user', 'start_time', 'end_time', 'report_timestamp', 'property_address',
              'external_logger', 'company', 'surveyor', 'report_file']
    list_display = ['user', 'company', 'surveyor', 'property_address', 'start_time', 'end_time', 'report_timestamp',
              'external_logger', 'report_file']
    search_fields = ['user', 'start_time', 'end_time', 'report_timestamp', 'property_address',
              'external_logger', 'company', 'surveyor', 'report_file']
    inlines = [PaymentInline]


admin.site.register(Downloads, DownloadsAdmin)
admin.site.register(Report, ReportAdmin)
