from django.db import models
from django.conf import settings

class Item(models.Model):
    STATUS_CHOICES = [('Lost', 'Lost'), ('Found', 'Found'), ('Returned', 'Returned')]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='item_images/')
    date_reported = models.DateTimeField(auto_now_add=True)
    date_lost_or_found = models.DateTimeField()
    location = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Lost')
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.status}"
