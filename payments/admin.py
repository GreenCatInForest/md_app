from django.contrib import admin
from django.db import models

from core.models import Payment, PriceSetting

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'get_payment_type', 
        'created_at', 'updated_at', 'get_report_number',
        'get_report_date',
        'get_report_link')
    search_fields = ['user', 'amount', 'status', 'get_payment_type', 'created_at']

@admin.register(PriceSetting)
class PriceSettingAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'price', 'currency')
    list_editable = ('price','currency')
    ordering = ('service_type',)
    search_fields = ('service_type','price', 'currency')