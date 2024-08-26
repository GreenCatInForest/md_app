from django.urls import path
from .views import report_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('report/', report_view, name='report'),
    path('reports/report/<int:report_id>/', report_view, name='report_view'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    