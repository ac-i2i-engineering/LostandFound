# locations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.campus_map, name='campus_map'),
]
