from django.contrib import admin
from django.db import models

from core.models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'get_payment_type', 
        'created_at', 'updated_at', 'get_report_number',
        'get_report_date',
        'get_report_link')
    search_fields = ['user', 'amount', 'status', 'get_payment_type', 'created_at']