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

import torch
from torchvision import models, transforms
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
    keyword = request.GET.get('keyword')
    location = request.GET.get('location')
    status = request.GET.get('status')

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

    context = {
        'items': items,
        'locations': locations,
        'keyword': keyword,
        'selected_location': location,
        'selected_status': status,
    }
    return render(request, 'items/item_list.html', context)

# New view for item submission
"""
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
"""

def home(request):
    return render(request, 'base.html')

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

def recognize_image(image):
    # Load ImageNet class labels from a JSON file
    with open(os.path.join(settings.BASE_DIR, "items", "imagenet_classes.json"), "r") as f:
        imagenet_classes = json.load(f)
    imagenet_classes = {idx: label for idx, label in enumerate(imagenet_classes)}


    # Load a pre-trained ResNet model
    model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    model.eval()  # Set the model to evaluation mode


    # Define the image preprocessing pipeline
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Open and preprocess the image
    if image.name.lower().endswith((".heic", ".heif")):
        heif_file = pillow_heif.read_heif(image)
        img = Image.frombytes(
            heif_file.mode, heif_file.size, heif_file.data, "raw"
        ).convert("RGB")
    elif image.name.lower().endswith((".jpg", ".jpeg", ".png")):
        img = Image.open(image).convert("RGB")
    else:
        raise ValueError("Unsupported file format. Please use .jpg, .jpeg, .png, or .heic.")

    img_tensor = preprocess(img).unsqueeze(0)  # Add batch dimension


    # Perform prediction
    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted_idx = torch.max(outputs, 1)
        result = imagenet_classes[predicted_idx.item()]

    return result


def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.reported_by = request.user
            
            # Perform image recognition
            if item.image:
                image_path = item.image.path
                item.image_recognition_result = recognize_image(item.image)

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
