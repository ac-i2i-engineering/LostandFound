from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "status", "location", "reported_by",
                    "is_deleted", "deleted_at", "date_reported", "date_lost_or_found")
    list_filter  = ("status", "location", "is_deleted")
    search_fields = ("name", "description", "reported_by__username", "reported_by__email")
    ordering = ("-date_reported",)
    list_select_related = ("location", "reported_by")

    # Hide bulk hard delete
    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    # Prevent object hard delete in admin
    def has_delete_permission(self, request, obj=None):
        return False
