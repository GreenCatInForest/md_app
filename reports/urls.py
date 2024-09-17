from django.urls import path
from .views import report_view, historical_reports_view, download_report, report_detail_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('report/', report_view, name='report'),
    path('reports/report/<int:report_id>/', report_view, name='report_view'),
    path('historical-reports/', historical_reports_view, name='historical_reports'),
    path('reports/', historical_reports_view, name='historical_reports'),
    path('reports/<int:report_id>/', report_detail_view, name='report_detail'),
    path('download-report/<int:report_id>/', download_report, name='download_report'),
] 
    