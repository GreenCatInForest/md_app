from django.shortcuts import render

def index_view (request): 
    return render(request, 'core/index.html')

def custom_404(request, exception):
    return render(request, 'core/404.html', status=404)

def custom_500(request):
    return render(request, 'core/500.html', status=500)
