# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class UserProfile(models.Model):
#     user = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
#     bio = models.TextField(blank=True)
#     # Add other profile fields as needed

#     def __str__(self):
#         return self.user.username + "'s Profile"

# class Order(models.Model):
#     user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='orders')
#     product_name = models.CharField(max_length=100)
#     order_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Order {self.id} by {self.user.username}"

# class CustomUser(AbstractUser):
#     # Add custom fields here
#     name = models.CharField(max_length=150, blank=True)
#     email = models.EmailField(unique=True)
#     # Add other fields as needed

#     def __str__(self):
#         return self.username