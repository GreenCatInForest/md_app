from django.urls import path
from . import views

urlpatterns = [
    path('get-price/<int:report_id>/', views.get_price, name='get_price'),
]