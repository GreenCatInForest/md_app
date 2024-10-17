from django.urls import path
from .views import report_view, historical_reports_view, download_report, report_detail_view, manuals_view, manual_download, start_task, task_status
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('report/', report_view, name='report'),
    path('reports/report/<int:report_id>/', report_view, name='report_view'),
    path('historical-reports/', historical_reports_view, name='historical_reports'),
    path('reports/', historical_reports_view, name='historical_reports'),
    path('reports/<int:report_id>/', report_detail_view, name='report_detail'),
    path('download-report/<int:report_id>/', download_report, name='download_report'),
    path('manuals/', manuals_view, name='manuals'),
    path('manuals/download/<int:download_id>/', manual_download, name='manual_download'),
    path('start-task/', start_task, name='start_task'),
    path('task-status/<str:task_id>/', task_status, name='task_status'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    