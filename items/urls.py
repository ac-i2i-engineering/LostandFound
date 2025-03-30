# items/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('new/', views.item_create, name='item_create'),  # New line for form submission
    path('<int:pk>/edit/', views.item_edit, name='item_edit'),       # Edit URL
    path('<int:pk>/delete/', views.item_delete, name='item_delete'), # Delete URL
    path('register/', views.register, name='register'),  # new
    path('login/', views.user_login, name='login'),      # new
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='user_profile'),

]
