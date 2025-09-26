# items/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from locations.models import Location
from .forms import ItemForm  # Import your new form!
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from PIL import Image
import json
import pillow_heif  # Adds HEIC support to Pillow
from torchvision.models import ResNet50_Weights

from django.conf import settings
import os

def item_list(request):
    items = Item.objects.all().select_related('location')
    locations = Location.objects.all()

    # Get search and filter parameters
    keyword = request.GET.get('keyword', '')
    location = request.GET.get('location')
    status = request.GET.get('status')
    item_type = request.GET.get('item_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Apply filters
    if keyword:
        items = items.filter(
            Q(name__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(location__name__icontains=keyword) |
            Q(date_reported__icontains=keyword) |
            Q(reported_by__username__icontains=keyword) |
            Q(image_recognition_result__icontains=keyword)
        )
    if location:
        items = items.filter(location__id=location)
    if status:
        items = items.filter(status=status)
    if item_type:
        # If model/table has an `item_type` field, filter that column.
        # Otherwise, treat the item_type input as a semantic category and
        # fallback to searching name and description to avoid returning everything.
        try:
            field_names = [f.name for f in Item._meta.get_fields()]
            if 'item_type' in field_names:
                items = items.filter(item_type__icontains=item_type)
            else:
                items = items.filter(
                    Q(name__icontains=item_type) |
                    Q(description__icontains=item_type)
                )
        except Exception:
            # If any error occurs (schema/inspection), fallback to name/description search
            items = items.filter(
                Q(name__icontains=item_type) |
                Q(description__icontains=item_type)
            )

    # Filter by date range (date_reported)
    from django.utils.dateparse import parse_datetime, parse_date
    try:
        if date_from:
            # accept date or datetime strings; parse_date for date-only
            parsed = parse_date(date_from) or parse_datetime(date_from)
            if parsed:
                items = items.filter(date_reported__date__gte=parsed)
        if date_to:
            parsed2 = parse_date(date_to) or parse_datetime(date_to)
            if parsed2:
                items = items.filter(date_reported__date__lte=parsed2)
    except Exception:
        # If parsing fails, ignore date filters
        pass

    context = {
        'items': items,
        'locations': locations,
        'keyword': keyword,
        'selected_location': location,
        'selected_status': status,
        'selected_item_type': item_type,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'items/item_list.html', context)

def home(request):
    context = {
        'items_reunited': 55,
        'success_rate': 97,  # Rounded to 2 decimal places
        'avg_response_time': 24,  # Placeholder for average response time
    }
    return render(request, 'base.html', context)

# In items/views.py
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'items/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('item_list')
    else:
        form = AuthenticationForm()

    return render(request, 'items/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('item_list')

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            # Only assign reported_by if user is authenticated
            if request.user.is_authenticated:
                item.reported_by = request.user
            # If user is not authenticated, reported_by remains None

            item.save()
            return redirect('item_list')
    else:
        form = ItemForm()

    context = {'form': form}
    return render(request, 'items/item_form.html', context)

@login_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk, reported_by=request.user)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)

    return render(request, 'items/item_form.html', {'form': form, 'item': item})

@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk, reported_by=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')

    return render(request, 'items/item_confirm_delete.html', {'item': item})

@login_required
def user_profile(request):
    user_items = Item.objects.filter(reported_by=request.user)
    return render(request, 'items/profile.html', {'user_items': user_items})

def about(request):
    return render(request, 'home/about.html')

def faq(request):
    return render(request, 'home/faq.html')

def policies(request):
    return render(request, 'home/policies.html')
