from django.contrib import admin
from django.db import models

from core.models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'created_at', 'updated_at')
