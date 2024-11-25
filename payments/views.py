import stripe
from django.shortcuts import render, redirect
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_PUBLIC_KEY 
