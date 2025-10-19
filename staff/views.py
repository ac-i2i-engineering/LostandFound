from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView
from django_filters.views import FilterView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from items.models import Item
from locations.models import Location
from .filters import ItemFilter

@method_decorator(staff_member_required, name="dispatch")
class DashboardHome(TemplateView):
    template_name = "staff/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Basic counts
        ctx["total_items"] = Item.objects.count()
        ctx["active_items"] = Item.objects.filter(is_deleted=False).count()
        ctx["deleted_items"] = Item.objects.filter(is_deleted=True).count()
        
        # Status breakdown
        ctx["lost_items"] = Item.objects.filter(status='Lost', is_deleted=False).count()
        ctx["found_items"] = Item.objects.filter(status='Found', is_deleted=False).count()
        ctx["returned_items"] = Item.objects.filter(status='Returned', is_deleted=False).count()
        
        # Location statistics
        ctx["location_stats"] = (
            Item.objects.filter(is_deleted=False)
            .values('location__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        # Time-based statistics
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        ctx["items_today"] = Item.objects.filter(date_reported__date=today).count()
        ctx["items_this_week"] = Item.objects.filter(date_reported__date__gte=week_ago).count()
        ctx["items_this_month"] = Item.objects.filter(date_reported__date__gte=month_ago).count()
        
        # User activity
        ctx["total_reporters"] = Item.objects.filter(reported_by__isnull=False).values('reported_by').distinct().count()
        ctx["anonymous_reports"] = Item.objects.filter(reported_by__isnull=True).count()
        
        # Top reporters
        ctx["top_reporters"] = (
            Item.objects.filter(reported_by__isnull=False, is_deleted=False)
            .values('reported_by__username', 'reported_by__first_name', 'reported_by__last_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        # Monthly trend data (last 6 months)
        monthly_data = []
        for i in range(6):
            month_start = today.replace(day=1) - timedelta(days=30*i)
            if i == 0:
                month_end = today
            else:
                month_end = (today.replace(day=1) - timedelta(days=30*(i-1))) - timedelta(days=1)
            
            count = Item.objects.filter(
                date_reported__date__gte=month_start,
                date_reported__date__lte=month_end
            ).count()
            
            monthly_data.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        
        ctx["monthly_trends"] = list(reversed(monthly_data))
        
        # Recent items
        ctx["recent"] = Item.objects.select_related("location", "reported_by").order_by("-date_reported")[:5]
        
        return ctx

@method_decorator(staff_member_required, name="dispatch")
class ItemList(FilterView):
    model = Item
    template_name = "staff/items_list.html"
    filterset_class = ItemFilter
    paginate_by = 25

    def get_queryset(self):
        return (Item.objects
                .select_related("location", "reported_by")
                .order_by("-date_reported"))

@method_decorator(staff_member_required, name="dispatch")
class ItemDetail(DetailView):
    model = Item
    template_name = "staff/item_detail.html"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        item = self.object
        
        # Similar items in same location
        if item.location:
            ctx["similar_location_items"] = (
                Item.objects.filter(
                    location=item.location,
                    is_deleted=False
                ).exclude(pk=item.pk)[:5]
            )
        
        # Items by same reporter
        if item.reported_by:
            ctx["reporter_other_items"] = (
                Item.objects.filter(
                    reported_by=item.reported_by,
                    is_deleted=False
                ).exclude(pk=item.pk)[:5]
            )
        
        # Similar items by description keywords
        if item.description:
            words = item.description.split()[:3]  # Take first 3 words
            q_objects = Q()
            for word in words:
                if len(word) > 3:  # Only use words longer than 3 characters
                    q_objects |= Q(description__icontains=word)
            
            if q_objects:
                ctx["similar_description_items"] = (
                    Item.objects.filter(q_objects, is_deleted=False)
                    .exclude(pk=item.pk)[:5]
                )
        
        return ctx

@staff_member_required
@permission_required("items.change_item", raise_exception=True)
def item_soft_delete(request, pk):
    if request.method != "POST":
        return redirect("staff:item_detail", pk=pk)
    item = get_object_or_404(Item, pk=pk)
    item.soft_delete(user=request.user)
    messages.success(request, f"Item #{item.pk} soft-deleted.")
    return redirect("staff:items")

@staff_member_required
@permission_required("items.change_item", raise_exception=True)
def item_restore(request, pk):
    if request.method != "POST":
        return redirect("staff:item_detail", pk=pk)
    item = get_object_or_404(Item, pk=pk)
    item.restore()
    messages.success(request, f"Item #{item.pk} restored.")
    return redirect("staff:items")

@staff_member_required
@permission_required("items.change_item", raise_exception=True)
def items_bulk_action(request):
    if request.method != "POST":
        return redirect("staff:items")
    ids = request.POST.getlist("ids")
    action = request.POST.get("action")
    qs = Item.objects.filter(id__in=ids)
    n = 0
    if action == "delete":
        for i in qs:
            if not i.is_deleted:
                i.soft_delete(user=request.user); n += 1
        messages.success(request, f"{n} item(s) soft-deleted.")
    elif action == "restore":
        n = qs.update(is_deleted=False, deleted_at=None)
        messages.success(request, f"{n} item(s) restored.")
    else:
        messages.error(request, "Unknown bulk action.")
    return redirect("staff:items")