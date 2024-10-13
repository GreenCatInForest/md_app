from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('create-checkout-session/<int:report_id>/', views.create_checkout_session, name='create-checkout-session'),
    path('webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('success/<str:task_id>/', views.payment_success, name='success'),
    path('cancel', views.payment_cancel, name='cancel'),
]