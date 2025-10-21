from django.db import models
from django.conf import settings
from django.utils import timezone
from simple_history.models import HistoricalRecords

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

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.name} - {self.status}"

    def soft_delete(self, user=None):
        """Soft delete the item"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user is not None:
            self._history_user = user
        self.save()

    def restore(self):
        """Restore a soft-deleted item"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    class Meta:
        indexes = [
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["status"]),
            models.Index(fields=["-date_reported"]),
            models.Index(fields=["date_lost_or_found"]),
        ]
        permissions = [
            ("can_soft_delete_item", "Can soft delete item"),
        ]
