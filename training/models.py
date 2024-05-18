from django.db import models
from products.models import Products

class TrainingVideo(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    youtube_url = models.URLField()
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title
    
