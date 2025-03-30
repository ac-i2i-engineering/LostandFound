# items/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('new/', views.item_create, name='item_create'),  # New line for form submission
    path('register/', views.register, name='register'),  # new
    path('login/', views.user_login, name='login'),      # new
    path('logout/', views.user_logout, name='logout'),
]
