from django.db import models



class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text="Short description of this location")
    image = models.ImageField(upload_to='location_images/', blank=True, null=True)
    latitude = models.FloatField()  # remove null=True, blank=True
    longitude = models.FloatField()
    
    def __str__(self):
        return self.name