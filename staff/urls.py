from django.urls import path
from . import views

app_name = "staff"

urlpatterns = [
    path("", views.DashboardHome.as_view(), name="home"),
    path("items/", views.ItemList.as_view(), name="items"),
    path("items/<int:pk>/", views.ItemDetail.as_view(), name="item_detail"),
    path("items/<int:pk>/delete/", views.item_soft_delete, name="item_delete"),
    path("items/<int:pk>/restore/", views.item_restore, name="item_restore"),
    path("items/bulk/", views.items_bulk_action, name="items_bulk"),
]
