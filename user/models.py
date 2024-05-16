from django.db import models
from django.contrib.auth.models import AbstractUser

class Profile(AbstractUser):
    name = models.CharField(max_length=100,blank=True)
    picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)
    # Initial name as a default picture

    def __str__(self):
        return self.username

class Order(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    