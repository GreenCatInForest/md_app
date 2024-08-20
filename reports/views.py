from django.shortcuts import render

report_view = lambda request: render(request, 'reports/report.html')

