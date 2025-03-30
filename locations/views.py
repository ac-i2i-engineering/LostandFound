# locations/views.py
from django.shortcuts import render
from .models import Location

def campus_map(request):
    locations = Location.objects.all()
    return render(request, 'locations/campus_map.html', {'locations': locations})