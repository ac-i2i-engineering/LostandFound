# items/views.py
from django.shortcuts import render, redirect
from .models import Item
from locations.models import Location
from .forms import ItemForm  # Import your new form!

def item_list(request):
    items = Item.objects.all().select_related('location')
    locations = Location.objects.all()

    location = request.GET.get('location')
    status = request.GET.get('status')

    if location:
        items = items.filter(location__id=location)
    if status:
        items = items.filter(status=status)

    context = {
        'items': items,
        'locations': locations,
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
    return render(request, 'home.html')

