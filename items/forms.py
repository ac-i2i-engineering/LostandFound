# items/forms.py
from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'image', 'date_lost_or_found', 'location', 'status']
        widgets = {
            'date_lost_or_found': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
