"""

Web URL Configuration

"""
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

#from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.home, name='home'),
    path(r'dashboard', views.dashboard, name='dashboard'),
    path(r'key/(?P<slug>[\w-]+)/', views.key, name='key'),
    path('404', views.index404, name='index404'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
