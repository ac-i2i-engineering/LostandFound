from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView
from django_filters.views import FilterView
from items.models import Item
from .filters import ItemFilter

@method_decorator(staff_member_required, name="dispatch")
class DashboardHome(TemplateView):
    template_name = "staff/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_items"]   = Item.objects.count()
        ctx["active_items"]  = Item.objects.filter(is_deleted=False).count()
        ctx["deleted_items"] = Item.objects.filter(is_deleted=True).count()
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
