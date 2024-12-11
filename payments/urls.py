from django.urls import path
from . import views

urlpatterns = [
    path('get-price/<uuid:report_id>/', views.get_price, name='get_price'),
    path('checkout-session', views.checkout_session, name='checkout-session' ),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('payment-status/<int:payment_id>/', views.payment_status, name='payment_status'),
]