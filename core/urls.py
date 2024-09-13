from django.urls import path

from .views import index_view, custom_404, custom_500

urlpatterns = [
    path('', index_view, name='index'),
]

# handler404 = 'core.views.handler404'
# handler500 = 'core.views.handler500'
