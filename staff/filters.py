# staff/filters.py
import django_filters
from django.db.models import Q
from items.models import Item
from locations.models import Location  # <-- add this import

class ItemFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="search", label="Search")
    status = django_filters.MultipleChoiceFilter(choices=Item.STATUS_CHOICES)
    location = django_filters.ModelChoiceFilter(
        queryset=Location.objects.all(),
        empty_label="(Any location)",
        label="Location",
    )
    date_lost_or_found = django_filters.DateFromToRangeFilter(label="Lost/Found between")
    show_deleted = django_filters.BooleanFilter(method="toggle_deleted", label="Show deleted")

    class Meta:
        model = Item
        fields = ["q", "status", "location", "date_lost_or_found", "show_deleted"]

    def search(self, qs, name, value):
        if value:
            return qs.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value) |
                Q(image_recognition_result__icontains=value)
            )
        return qs

    def toggle_deleted(self, qs, name, value):
        return qs if value else qs.filter(is_deleted=False)
