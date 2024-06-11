from django.contrib.auth.models import AbstractUser
from django.db import models
from products.models import Products, ShippingOption, ProductSize

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    shipping_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username + "'s Profile"

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_orders', null=True, blank=True)
    guest_email = models.EmailField(null=True, blank=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='product_orders')
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, null=True, blank=True)  # Ensure size is tracked
    quantity = models.IntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField()
    shipping_option = models.ForeignKey(ShippingOption, on_delete=models.SET_NULL, null=True, blank=True)  # New field

    def __str__(self):
        if self.user:
            return f"Order {self.id} by {self.user.username}"
        else:
            return f"Order {self.id} by guest {self.guest_email}"

    def total_cost(self):
        return self.size.price * self.quantity + (self.shipping_option.cost if self.shipping_option else 0)