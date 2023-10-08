# upload_files/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('validate/', views.validate_files, name='validate_files'),
]
