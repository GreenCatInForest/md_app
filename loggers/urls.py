from django.urls import path
from .views import (
    LoggerDataCreateView,
    LoggerDataListView,
    LoggerDataDetailView,
    LoggerHealthListView,
    LoggerHealthDetailView,
    LoggerDataSearchView,
    LoggerDataDeleteView,
    LoggerHealthDeleteView, 
)

urlpatterns = [
    path('logger-data/', LoggerDataCreateView.as_view(), name='logger-data-list-create'),
    path('logger-data-list/', LoggerDataListView.as_view(), name='logger-data-list'),
    path('logger-data-detail/<int:pk>/', LoggerDataDetailView.as_view(), name='logger-data-detail'),
    path('logger-data-delete/<int:pk>/', LoggerDataDeleteView.as_view(), name='logger-data-delete'),
    path('logger-health-list/', LoggerHealthListView.as_view(), name='logger-health-list'),
    path('logger-health-detail/<int:pk>/', LoggerHealthDetailView.as_view(), name='logger-health-detail'),
    path('logger-data-search/', LoggerDataSearchView.as_view(), name='logger-data-search'),
    path('logger-data/', LoggerDataCreateView.as_view(), name='logger-data-delete-all'),
    path('logger-health-delete/', LoggerHealthDeleteView.as_view(), name='logger-health-delete-all'),
]