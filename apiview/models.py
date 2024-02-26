from django.db import models

# Create your models here.
class StationInfo(models.Model):
    data = models.JSONField()

class UploadFile(models.Model):
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    string_data = models.TextField(null=True, blank=True)