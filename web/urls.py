"""

Web URL Configuration

"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("key/<slug:slug>/", views.key, name="key"),
    path("404", views.index404, name="index404"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
