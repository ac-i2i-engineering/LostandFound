# items/views.py
from django.shortcuts import render, redirect
from .models import Item
from locations.models import Location
from .forms import ItemForm  # Import your new form!
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm

def item_list(request):
    items = Item.objects.all().select_related('location')
    locations = Location.objects.all()

    # Get search and filter parameters
    keyword = request.GET.get('keyword')
    location = request.GET.get('location')
    status = request.GET.get('status')

    # Apply filters
    if keyword:
        items = items.filter(name__icontains=keyword)  # Search by keyword in item name
    if location:
        items = items.filter(location__id=location)
    if status:
        items = items.filter(status=status)

    context = {
        'items': items,
        'locations': locations,
        'keyword': keyword,
        'selected_location': location,
        'selected_status': status,
    }
    return render(request, 'items/item_list.html', context)

# New view for item submission
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()

    context = {'form': form}
    return render(request, 'items/item_form.html', context)

def home(request):
    return render(request, 'base.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('item_list')
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

