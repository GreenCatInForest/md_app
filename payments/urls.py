from django.urls import path
from . import views

urlpatterns = [
    path('get-price/<uuid:report_id>/', views.get_price, name='get_price'),
    path('checkout-session', views.checkout_session, name='checkout-session' ),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('payment-status/<uuid:uuid>/', views.payment_status, name='payment_status'),
    path('payment-success/', views.payment_success, name='payment-success'),
    path('payment-cancel/', views.payment_cancel, name='payment-cancel'),
]