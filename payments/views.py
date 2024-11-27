import stripe
from django.shortcuts import render, redirect
from django.conf import settings
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from core.models import Report

stripe.api_key = settings.STRIPE_PUBLISHABLE_KEY

def get_price(request, report_id):
    try:
        report = get_object_or_404(Report, id=report_id)
        return JsonResponse({"price": float(report.price)}, status=200)  
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
